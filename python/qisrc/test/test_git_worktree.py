import qisys.qixml
import qisys.worktree
import qisrc.worktree

def test_read_git_configs(tmpdir, test_git):
    tmpdir.mkdir("foo")
    tmpdir.mkdir("bar")
    wt = qisys.worktree.create(tmpdir.strpath)
    foo_proj = wt.add_project("foo")
    bar_proj = wt.add_project("bar")

    git = test_git(foo_proj.path)
    git.initialize()

    git = test_git(bar_proj.path)
    git.initialize(branch="next")

    tmpdir.join(".qi").join("git.xml").write(""" \
<qigit>
 <project src="foo" >
    <branch name="master" tracks="origin" />
 </project>
 <project src="bar" >
    <branch name="next" tracks="origin" />
    <remote name="origin" url="git@srv:bar.git" />
    <remote name="gerrit" url="john@gerrit:bar.git" review="true"/>
 </project>
</qigit>
""")


    git_wt = qisrc.worktree.GitWorkTree(wt)
    git_projects = git_wt.git_projects
    assert len(git_projects) == 2

    foo = git_wt.get_git_project("foo")
    assert foo.src == "foo"
    assert len(foo.branches) == 1
    assert foo.branches[0].name == "master"
    assert foo.branches[0].tracks == "origin"
    assert not foo.remotes

    bar = git_wt.get_git_project("bar")
    assert bar.src == "bar"
    assert len(bar.branches) == 1
    assert len(bar.remotes) == 2
    origin = bar.remotes[0]
    assert origin.name == "origin"
    assert origin.url == "git@srv:bar.git"
    gerrit = bar.remotes[1]
    assert gerrit.name == "gerrit"
    assert origin.url == "git@srv:bar.git"



def test_git_configs_are_persistent(git_worktree):
    foo = git_worktree.create_git_project("foo")
    foo.add_remote("upstream", url="git@srv:bar.git")
    foo.add_branch("master", tracks="upstream")

    def check_config(foo):
        assert len(foo.remotes) == 1
        upstream = foo.remotes[0]
        assert upstream.name == "upstream"
        assert upstream.url == "git@srv:bar.git"
        assert len(foo.branches) == 1
        master = foo.branches[0]
        assert master.name == "master"
        assert master.tracks == "upstream"

    check_config(foo)
    wt2 = qisrc.worktree.open_git_worktree(git_worktree.tmpdir.strpath)
    foo2 = wt2.get_git_project("foo")
    check_config(foo2)


def test_sync_git_configs(git_worktree):
    foo = git_worktree.create_git_project("foo")
    foo.add_remote("upstream", url="git@srv:bar.git")

    git = qisrc.git.Git(foo.path)
    assert git.get_config("remote.upstream.url") == "git@srv:bar.git"

    foo.add_branch("master", tracks="upstream")
    assert git.get_tracking_branch("master") == "upstream/master"

    foo.add_branch("feature", tracks="upstream", remote_branch="remote_branch")
    assert git.get_tracking_branch("feature") == "upstream/remote_branch"

def test_clones_when_missing(git_server, git_worktree):
    foo_repo = git_server.create_repo("foo.git")
    git_xml_path = git_worktree.git_xml
    with open(git_xml_path, "w") as fp:
        fp.write(""" \
<git>
  <project src="foo" >
    <remote name="origin" url="{}" />
    <branch name="master" default="true" tracks="origin" />
  </project>
</git>
""".format(foo_repo.remote_url))
    git_worktree.on_git_xml_changed()
    assert git_worktree.get_git_project("foo")

def test_moving_projects(git_server, git_worktree):
    foo_repo = git_server.create_repo("foo.git")
    git_xml_path = git_worktree.git_xml
    with open(git_xml_path, "w") as fp:
        fp.write(""" \
<git>
  <project src="foo" >
    <remote name="origin" url="{}" />
    <branch name="master" default="true" tracks="origin" />
  </project>
</git>
""".format(foo_repo.remote_url))
    git_worktree.on_git_xml_changed()

    with open(git_xml_path, "w") as fp:
        fp.write(""" \
<git>
  <project src="bar" >
    <remote name="origin" url="{}" />
    <branch name="master" default="true" tracks="origin" />
  </project>
</git>
""".format(foo_repo.remote_url))
    git_worktree.on_git_xml_changed()
    assert len(git_worktree.git_projects) == 1



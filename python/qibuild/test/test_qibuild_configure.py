import os
import subprocess

import qisys.command
import qibuild.cmake

import pytest


# This modules also serves as a test for the
# qibuild cmake API

def test_simple(qibuild_action):
    # Just make sure that the basic stuff works
    # (find qibuild-config.cmake)
    qibuild_action.add_test_project("world")
    qibuild_action("configure", "world")

def test_deps(qibuild_action):
    # Running `qibuild configure hello` should work out of the box
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")

    # As should `qibuild configure --all`
    qibuild_action("configure", "-a")


def test_qi_use_lib(qibuild_action):
    use_lib_proj = qibuild_action.add_test_project("uselib")
    qibuild_action("configure", "uselib")

    # Read cache and check that DEPENDS value are here
    cmake_cache = use_lib_proj.cmake_cache
    cache = qibuild.cmake.read_cmake_cache(cmake_cache)
    assert cache["D_DEPENDS"] == "A;B"
    assert cache["E_DEPENDS"] == "D;A;B;CC"

    # Make sure it builds
    qibuild_action("make", "uselib")

    # Make sure it fails when it should
    with pytest.raises(Exception):
        qibuild_action("configure", "uselib", "-DSHOULD_FAIL=ON")


def test_qi_stage_lib_simple(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    qibuild_action("configure", "stagelib")

def test_qi_stage_lib_but_really_bin(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    with pytest.raises(Exception):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_LIB_BUT_REALLY_BIN=ON")

def test_qi_stage_lib_but_no_such_target(qibuild_action):
    qibuild_action.add_test_project("stagelib")
    with pytest.raises(Exception):
        qibuild_action("configure", "stagelib",
                       "-DSHOULD_FAIL_STAGE_NO_SUCH_TARGET")

def test_preserve_cache(qibuild_action):
    foo_proj = qibuild_action.add_test_project("foo")
    qibuild_action("configure", "foo")

    # Read cache and check that DEPENDS value are here
    cache_before = qibuild.cmake.read_cmake_cache(foo_proj.cmake_cache)

    assert cache_before["EGGS_DEPENDS"] == "SPAM"
    assert cache_before["BAR_DEPENDS"] == "EGGS;SPAM"

    # run cmake .. and check the cache did not change
    qisys.command.call(["cmake", ".."], cwd=foo_proj.build_directory)
    cache_after = qibuild.cmake.read_cmake_cache(foo_proj.cmake_cache)

    assert cache_before == cache_after

def test_config_h(qibuild_action, tmpdir):
    proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    foo = os.path.join(proj.sdk_directory, "bin", "foo")
    process = subprocess.Popen([foo])
    process.wait()
    assert process.returncode == 42
    assert tmpdir.join("include", "foo", "config.h").check(file=1)

#pylint: disable-msg=E110V
@pytest.mark.xfail
def test_config_h_extra_install_rule(qibuild_action, tmpdir):
    proj = qibuild_action.add_test_project("config_h")
    qibuild_action("configure", "config_h", "-DWITH_EXTRA_INSTALL_RULE=ON")
    qibuild_action("make", "config_h")
    qibuild_action("install", "config_h", tmpdir.strpath)
    full_config_h = os.path.join(proj.build_directory,
            "include", "foo", "config.h")
    full_config_h = os.path.join(tmpdir.strpath, full_config_h)
    assert not os.path.exists(full_config_h)

def test_submodule(qibuild_action):
    qibuild_action.add_test_project("submodule")
    qibuild_action("configure", "submodule")
    qibuild_action("make", "submodule")
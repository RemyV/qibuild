""" Install all python projects """
import os
import sys

from qisys import ui
import qisys.command

import qisys.parsers
import qipy.parsers
import qibuild.parsers

def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("dest")

def do(args):
    dest = args.dest
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    projects = qipy.parsers.get_python_projects(python_worktree, args)
    python_builder.projects = projects
    python_builder.install(dest)

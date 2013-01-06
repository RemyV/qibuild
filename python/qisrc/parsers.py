## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Common parsers for qisrc actions """

import qisys.parsers

def worktree_parser(parser):
    qisys.parsers.worktree_parser(parser)

def groups_parser(parser):
    """Parsers settings for groups."""
    parser.add_argument("-g", "--group", dest="groups", action="append",
                        help="Specify a group of projects.")

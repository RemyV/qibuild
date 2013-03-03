## Copyright (c) 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Handling maintainers in git notes."""

import qisrc.git

import qisys.qixml

from xml.etree import ElementTree as etree

class ProjectXML(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ProjectXML, self).__init__(target)

    def _parse_maintainer(self, element):
        maintainer = {'email': element.get('email'), 'name': element.text}
        self.target.append(maintainer)

def to_str(name=None, email=None):
    string = ""
    if name:
        string += name
    if name and email:
        string += " "
    if email:
        string += "<" + email + ">"
    return string

def get_xml_root(project):
    tree = get_xml_tree(project)
    return tree.getroot()

def get_xml_tree(project):
    path = project.qiproject_xml
    tree = qisys.qixml.read(path)
    return tree

def exist(project, name=None, email=None):
    maintainers = get(project)

    for maintainer in maintainers:
        if maintainer.get("name") == name and maintainer.get("email") == email:
            return True

    return False

def get(project):
    maintainers = list()
    project_xml = ProjectXML(maintainers)
    project_xml.parse(get_xml_root(project))
    return maintainers

def remove(project, name=None, email=None):
    if not exist(project, name=name, email=email):
        return False

    tree = get_xml_tree(project)
    root = tree.getroot()
    for elem in root.findall("./maintainer[@email='"+email+"']"):
        if elem.text == name:
            root.remove(elem)

    qisys.qixml.write(tree, project.qiproject_xml)
    return True


def clear(project):
    maintainers = get(project)
    if len(maintainers) == 0:
        return False
    for maintainer in maintainers:
        remove(project, **maintainer)
    return True
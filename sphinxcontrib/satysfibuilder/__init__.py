# -*- coding: utf-8 -*-
"""
    sphinxcontrib-satysfibuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2018 by the WAKAYAMA Shirou
    :license: LGPLv3, see LICENSE for details.
"""

from __future__ import absolute_import

from docutils import nodes

from sphinxcontrib.satysfibuilder import satysfibuilder


# from japanesesupport.py
def trunc_whitespace(app, doctree, docname):
    for node in doctree.traverse(nodes.Text):
        if isinstance(node.parent, nodes.paragraph):
            newtext = node.astext()
            for c in "\n\r\t":
                newtext = newtext.replace(c, "")
            newtext = newtext.strip()
            node.parent.replace(node, nodes.Text(newtext))


def setup(app):
    app.connect("doctree-resolved", trunc_whitespace)
    satysfibuilder.setup(app)

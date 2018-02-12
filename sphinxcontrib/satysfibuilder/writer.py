#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from docutils import nodes, writers

from sphinx import version_info as SPHINX_VERSION
from sphinx.util import logging
from sphinx.writers.text import TextTranslator


if False:
    # For type annotation
    from typing import Any, Callable, Tuple, Union  # NOQA
    from sphinx.builders.text import TextBuilder  # NOQA


logger = logging.getLogger(__name__)


class SATySFiWriter(writers.Writer):
    supported = ('satysfi',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}  # type: Dict

    output = None

    def __init__(self, builder):
        # type: (SATySFiBuilder) -> None
        writers.Writer.__init__(self)
        self.builder = builder

    def translate(self):
        visitor = self.builder.create_translator(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.body


class SATySFiTranslator(TextTranslator):
    def add_lines(self, lines):
        self.states[-1].append((0, lines))

    def new_block(self, text, indent=0):
        self.add_lines([text])
        self.new_state(indent)

    def end_block(self, end=[]):
        self.end_state(end=end)
        self.add_lines(['      }\n'])

    def end_state(self, wrap=True, end=[''], first=None):
        # force disable text wrapping
        TextTranslator.end_state(self, wrap=False, end=end, first=first)

    def visit_document(self, node):
        settings = self.document.settings

        self.add_text(['@require: stdjabook',
                       '@require: code',
                       '@require: itemize',
                       '@require: tabular',
                       '',
                       'document (|',
                       '  title = {{{}}};'.format(settings.title),
                       '  author = {{{}}};'.format(settings.author),
                       '  show-title = true;',
                       '  show-toc = true;',
                       "|) '<",
        ])
        super().visit_document(node)

    def depart_document(self, node):
        self.add_text('>')
        super().depart_document(node)

    def visit_section(self, node):
        self.sectionlevel += 1

    def depart_section(self, node):
        self.add_text('>')

    def visit_paragraph(self, node):
        if isinstance(node.parent, nodes.list_item):
            return
        self.new_block('    +p{')

    def depart_paragraph(self, node):
        if isinstance(node.parent, nodes.list_item):
            return
        self.end_block()

    def visit_title(self, node):
        if isinstance(node.parent, nodes.Admonition):
            self.add_text(node.astext() + ': ')
            raise nodes.SkipNode
        elif isinstance(node.parent, nodes.table):
            raise nodes.SkipNode
        else:
            self.new_state(0)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.section):
            self.end_state()

            if self.sectionlevel < 2:
                marker = "  +section "
            else:
                marker = "    +subsection "

            text = ''.join(self.states[-1].pop()[1])
            if node.parent['ids']:
                title = u'%s ?:(`%s`) {%s}<' % (marker, node.parent['ids'][0], text)
            else:
                title = u'%s {%s}<' % (marker, text)
            self.add_lines([title])
        else:
            logger.warning('unsupperted title type: %s', node.parent)

    def visit_title_reference(self, node):
        """inline citation reference"""
        self.visit_literal(node)

    def depart_title_reference(self, node):
        self.add_text('}')

    def visit_emphasis(self, node):
        self.add_text('\emph{')

    def depart_emphasis(self, node):
        self.add_text('}')

    def visit_literal_emphasis(self, node):
        self.add_text('\emph{')

    def depart_literal_emphasis(self, node):
        self.add_text('}')

    def visit_strong(self, node):
        self.add_text('\emph{')

    def depart_strong(self, node):
        self.add_text('}')

    def visit_literal_strong(self, node):
        self.add_text('\emph{')

    def depart_literal_strong(self, node):
        self.add_text('}')

    def visit_list_item(self, node):
        if self.list_counter[-1] == -1:
            # bullet list
            self.new_state(0)
        elif self.list_counter[-1] == -2:
            # definition list
            pass
        else:
            # enumerated list
            self.list_counter[-1] += 1
            self.new_state(0)

    def visit_bullet_list(self, node):
        TextTranslator.visit_bullet_list(self, node)
        self.add_text('    +listing{')

    def depart_bullet_list(self, node):
        TextTranslator.depart_bullet_list(self, node)
        self.add_text('    }')

    def visit_enumerated_list(self, node):
        TextTranslator.visit_enumerated_list(self, node)
        self.add_text('    +listing{')

    def depart_enumerated_list(self, node):
        TextTranslator.depart_enumerated_list(self, node)
        self.add_text('    }')

    def depart_list_item(self, node):
        # remove trailing space
        content = self.states[-1][-1][1]
        if content and content[-1] == '':
            content.pop()

        if self.list_counter[-1] == -1:
            self.end_state(first=' {} '.format('*' * len(self.list_counter)), end='')
        elif self.list_counter[-1] == -2:
            pass
        else:
            self.end_state(first=' {}. '.format(self.list_counter[-1]), end=None)

    def visit_math(self, node):
        self.add_text("@<m>{")

    def depart_math(self, node):
        self.add_text("}")

    def visit_math_block(self, node):
        self.new_block('//texequation')

    def depart_math_block(self, node):
        self.end_block()

    def visit_figure(self, node):
        self.new_state(0)

    def visit_image(self, node):
        caption = None
        for c in node.parent.children:
            if isinstance(c, nodes.caption):
                caption = c.astext()
        legend = None
        for c in node.parent.children:
            if isinstance(c, nodes.legend):
                legend = c.astext()

        filename = os.path.basename(os.path.splitext(node['uri'])[0])
        if node.get('inline'):
            self.add_text('@<icon>{%s}' % filename)
        else:
            if caption:
                self.new_block('//image[%s][%s]{' % (filename, caption))
            else:
                self.new_block('//image[%s][]{' % filename)

            if legend:
                self.add_lines([legend])

            self.end_block("//}")

        raise nodes.SkipNode

    def visit_legend(self, node):
        raise nodes.SkipNode

    def depart_figure(self, node):
        self.end_state()

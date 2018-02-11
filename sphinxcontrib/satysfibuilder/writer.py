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
    sectionchar = u"="

    admonitionlabels = {
        "note": "note",
        "tip": "tip",
        "info": "info",
        "warning": "warning",
        "important": "important",
        "caution": "caution",
        "notice": "notice",
        "attention": "notice",
        "danger": "caution",
        "error": "caution",
        "hint": "info",
    }

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

    def visit_reference(self, node):
        if 'internal' in node and node['internal']:
            # TODO: ターゲットごとに変える
            self.add_text('@<chap>{%s}' % (node.get('refuri', '').replace('#', '')))
        else:  # URL
            if 'name' in node:
                self.add_text('@<href>{%s,%s}' % (node.get('refuri', ''), node['name']))
            else:
                self.add_text('@<href>{%s}' % (node.get('refuri', '')))
        raise nodes.SkipNode

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

    def visit_abbreviation(self, node):
        self.add_text('')

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

    def depart_term(self, node):
        if not self._classifier_count_in_li:
            self.end_state(first=" : ", end='')

    def depart_definition(self, node):
        pos = len(self.states[-2])
        TextTranslator.depart_definition(self, node)

        # replace a blank line by ``@<br>{}``
        while pos < len(self.states[-1]) - 1:
            item = self.states[-1][pos]
            if item[1] and item[1][-1] == '':
                item[1].pop()
                item[1][-1] += '\dfn{}'
            pos += 1

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

    def visit_literal_block(self, node):
        # TODO: remove highlight args
        lang = node.get('language', 'guess')

        if lang == "bash" and self.builder.config.review_use_cmd_block:
            self.new_block('//cmd{')
            return

        names = False  # get reference if exists
        t = "emlist"
        if 'names' in node and len(node['names']) > 0:
            names = ''.join(node['names'])
            t = "list"

        caption = ""
        if isinstance(node.parent[0], nodes.caption):
            caption = node.parent[0].astext()

        if 'linenos' in node and node['linenos']:
            if 'highlight_args' in node and 'linenostart' in node['highlight_args']:
                n = node['highlight_args']['linenostart']
                self.add_lines(['//firstlinenum[%s]' % n])
                # TODO: remove highlight args line
            t += "num"

        if names:
            self.new_block('//%s[%s][%s][%s]{' % (t, names, caption, lang))
        else:
            self.new_block('//%s[%s][%s]{' % (t, caption, lang))

    def depart_literal_block(self, node):
        self.end_block()

    def visit_caption(self, node):
        raise nodes.SkipNode

    def visit_literal(self, node):
        self.add_text('@<code>{')
        self.add_text(node.astext().replace('\\', '\\\\'))
        self.add_text('}')
        raise nodes.SkipNode

    def _make_visit_admonition(name):
        def visit_admonition(self, node):
            self.new_block('//%s{' % self.admonitionlabels[name])

        return visit_admonition

    def _depart_named_admonition(self, node):
        # remove trailing space
        content = self.states[-1][-1][1]
        while content and content[-1] == '':
            content.pop()

        self.end_block()

    visit_attention = _make_visit_admonition('attention')
    depart_attention = _depart_named_admonition
    visit_caution = _make_visit_admonition('caution')
    depart_caution = _depart_named_admonition
    visit_danger = _make_visit_admonition('danger')
    depart_danger = _depart_named_admonition
    visit_error = _make_visit_admonition('error')
    depart_error = _depart_named_admonition
    visit_hint = _make_visit_admonition('hint')
    depart_hint = _depart_named_admonition
    visit_important = _make_visit_admonition('important')
    depart_important = _depart_named_admonition
    visit_note = _make_visit_admonition('note')
    depart_note = _depart_named_admonition
    visit_tip = _make_visit_admonition('tip')
    depart_tip = _depart_named_admonition
    visit_warning = _make_visit_admonition('warning')
    depart_warning = _depart_named_admonition

    def visit_block_quote(self, node):
        self.new_block('//quote{')
        self.add_text(node.astext())
        self.end_block()
        raise nodes.SkipNode

    def visit_math(self, node):
        self.add_text("@<m>{")

    def depart_math(self, node):
        self.add_text("}")

    def visit_math_block(self, node):
        self.new_block('//texequation')

    def depart_math_block(self, node):
        self.end_block()

    def visit_footnote_reference(self, node):
        self.add_text('@<fn>{%s}' % node['refid'])
        raise nodes.SkipNode

    def visit_footnote(self, node):
        label = node['ids'][0]
        self.new_state(0)
        self.add_text('//footnote[%s][' % label)
        self.new_state(0)

    def depart_footnote(self, node):
        # convert all text inside footnote to single line
        self.end_state(end=None)
        footnote_text = self.states[-1].pop()[1]
        for line in footnote_text:
            self.add_text(line)

        self.add_text(']')

        index = node.parent.index(node)
        if len(node.parent) > index + 1 and isinstance(node.parent[index + 1], nodes.footnote):
            # inside consecutive footnotes (footnote group)
            self.end_state(end=[])
        else:
            # insert a blank line after the footnote group
            self.end_state(end=[''])

    def visit_table(self, node):
        if self.table:
            raise NotImplementedError('Nested tables are not supported.')
        self.table = [[]]
        label = ""
        if len(node['ids']) > 0:
            label = node['ids'][0]

        title = ""
        if isinstance(node.children[0], nodes.title):
            title = node.children[0].astext()

        self.new_block(u'//table[%s][%s]{' % (label, title))

    def visit_entry(self, node):
        if len(node) == 0:
            # Fill single-dot ``.`` for empty table cells
            self.table[-1].append('.')
            raise nodes.SkipNode
        else:
            TextTranslator.visit_entry(self, node)

    def depart_entry(self, node):
        TextTranslator.depart_entry(self, node)

        # replace return codes by @<br>{}
        text = self.table[-1].pop().strip()
        text = text.replace('\n', '@<br>{}')
        self.table[-1].append(text)

    def visit_row(self, node):
        self.table.append([])

    def depart_row(self, node):
        self.add_lines([u'\t'.join(self.table.pop())])

    def depart_thead(self, node):
        self.add_lines(['------------'])

    def depart_table(self, node):
        self.table = None
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

    def visit_comment(self, node):
        if self.builder.config.review_keep_comments is False:
            raise nodes.SkipNode

        comments = ["#@# %s" % line.strip() for line in node.astext().splitlines()]

        index = node.parent.index(node)
        if len(node.parent) > index + 1 and isinstance(node.parent[index + 1], nodes.comment):
            # inside consecutive comments (comment group)
            self.add_lines(comments)
        else:
            # insert a blank line after the comment group
            self.add_lines(comments + [''])

        raise nodes.SkipNode

    def visit_raw(self, node):
        content = node.astext().replace('\n', '\\n')
        self.add_lines(['//raw[|%s|%s]' % (node.get('format'), content)])
        raise nodes.SkipNode

    def visit_subscript(self, node):
        self.add_text('@<u>{')

    def depart_subscript(self, node):
        self.add_text('}')

    def visit_index(self, node):
        raise nodes.SkipNode

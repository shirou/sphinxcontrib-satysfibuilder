#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from os import path
import codecs

from six import iteritems
from docutils import nodes
from docutils.io import StringOutput
from sphinx.util.osutil import make_filename
from sphinx.builders.text import TextBuilder
from sphinx.util.fileutil import copy_asset_file
from sphinx.util.osutil import ensuredir
from sphinx.util.console import bold
from sphinx.util.template import SphinxRenderer

from sphinxcontrib.satysfibuilder.writer import SATySFiWriter, SATySFiTranslator


class SATySFiBuilder(TextBuilder):
    name = 'satysfi'
    format = 'satysfi'
    out_suffix = '.saty'
    out_files = []
    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']
    default_translator_class = SATySFiTranslator

    def prepare_writing(self, docnames):
        self.writer = SATySFiWriter(self)

    def write_doc(self, docname, doctree):
        self.current_docname = docname

        doctree.settings.author = self.config.satisfy_documents[0][3]
        doctree.settings.title = self.config.satisfy_documents[0][2]

        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)

        filename = path.basename(docname) + self.out_suffix
        try:
            with codecs.open(path.join(self.outdir, filename), 'w', 'utf-8') as f:
                f.write(self.writer.output)
            self.out_files.append(filename)
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (filename, err))

        self.post_process_images(docname, doctree)

    def get_target_uri(self, docname, typ=None):
        # type: (unicode, unicode) -> unicode
        return docname

    def post_process_images(self, docname, doctree):
        """Pick the best candidate for all image URIs."""
        for node in doctree.traverse(nodes.image):
            if '?' in node['candidates']:
                # don't rewrite nonlocal image URIs
                continue
            if '*' not in node['candidates']:
                for imgtype in self.supported_image_types:
                    candidate = node['candidates'].get(imgtype, None)
                    if candidate:
                        break
                else:
                    self.warn(
                        'no matching candidate for image URI %r' % node['uri'],
                        '%s:%s' % (node.source, getattr(node, 'line', '')))
                    continue
                node['uri'] = candidate
            else:
                candidate = node['uri']
            if candidate not in self.env.images:
                # non-existing URI; let it alone
                continue
            dest = path.join(path.basename(docname), self.env.images[candidate][1])
            self.images[dest] = candidate

    def finish(self):
        # copy image files
        if self.images:
            self.info(bold('copying images...'), nonl=1)
            for dest, src in iteritems(self.images):
                self.info(' ' + src, nonl=1)
                outdir = path.join(self.outdir, "images")
                outfile = path.join(outdir, dest)
                ensuredir(path.dirname(outfile))
                copy_asset_file(path.join(self.srcdir, src),
                                outfile)
            self.info()


def setup(app):
    app.add_builder(SATySFiBuilder)
    app.add_config_value('satisfy_documents',
                         lambda self: [(self.master_doc,
                                        make_filename(self.project) + '.saty',
                                        self.project,
                                        '')],
                         None)

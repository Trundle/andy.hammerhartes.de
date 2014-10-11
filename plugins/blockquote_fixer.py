# encoding: utf-8

"""
Monkey-patches Pelican's PelicanHTMLTranslator to always add a <p>
inside a <blockquote>.
"""

from docutils import nodes
from pelican.readers import PelicanHTMLTranslator


_real_should_be_compact_paragraph = None


def inside_blockquote(node):
    node = node.parent
    while node is not None:
        if isinstance(node, nodes.block_quote):
            return True
        node = node.parent
    return False

def should_be_compact_paragraph(self, node):
    if inside_blockquote(node):
        return False
    return _real_should_be_compact_paragraph(self, node)


def register():
    global _real_should_be_compact_paragraph
    _real_should_be_compact_paragraph = PelicanHTMLTranslator.should_be_compact_paragraph
    PelicanHTMLTranslator.should_be_compact_paragraph = should_be_compact_paragraph

import re

from docutils.node import NodeVisitor

def process_dollars(app, docname, source):
    r"""
    Replace dollar signs with backticks.

    More precisely, do a regular expression search.  Replace a plain
    dollar sign ($) by a backtick (`).  Replace an escaped dollar sign
    (\$) by a dollar sign ($).  Don't change a dollar sign preceded or
    followed by a backtick (`$ or $`), because of strings like
    "``$HOME``".  Don't make any changes on lines starting with
    spaces, because those are indented and hence part of a block of
    code or examples.

    This also doesn't replaces dollar signs enclosed in curly braces,
    to avoid nested math environments, such as ::

      $f(n) = 0 \text{ if $n$ is prime}$

    Thus the above line would get changed to

      :math:`f(n) = 0 \text{ if $n$ is prime}`
    """
    s = "\n".join(source)
    if s.find("$") == -1:
        return
    # This searches for "$blah$" inside a pair of curly braces --
    # don't change these, since they're probably coming from a nested
    # math environment.  So for each match, we replace it with a temporary
    # string, and later on we substitute the original back.
    global _data
    _data = {}
    def repl(matchobj):
        global _data
        s = matchobj.group(0)
        t = "___XXX_REPL_%d___" % len(_data)
        _data[t] = s
        return t
    # Match $math$ inside of {...} and replace it with dummy text
    s = re.sub(r"({[^{}$]*\$[^{}$]*\$[^{}]*})", repl, s)
    # matches $...$
    dollars = re.compile(r"(?<!\$)(?<!\\)\$([^\$ ][^\$]*?)\$")
    # regular expression for \$
    slashdollar = re.compile(r"\\\$")
    s = dollars.sub(r":math:`\1`", s)
    s = slashdollar.sub(r"$", s)
    # change the original {...} things in:
    for r in _data:
        s = s.replace(r, _data[r])
    # now save results in "source"
    source[:] = [s]


def process_docstring(app, what, name, obj, options, lines):
    if name.endswith('.latex'):
        # Disable in the latex() docstring, as it breaks the example output
        return
    return process_dollars(app, None, lines)

class MathDollarReplacer(NodeVisitor):
    def visit_Text(self, node):
        _data = dollar_parts(node.astext())

def process_doctree(app, doctree):
    pass

def setup(app):
    app.connect("source-read", process_dollars)
    app.connect("doctree-read", process_doctree)
    app.connect("autodoc-process-docstring", process_docstring)
#
#   Copyright (c) 2013, Coverity, Inc. 
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without modification, 
#   are permitted provided that the following conditions are met:
#   - Redistributions of source code must retain the above copyright notice, this 
#   list of conditions and the following disclaimer.
#   - Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or other
#   materials provided with the distribution.
#   - Neither the name of Coverity, Inc. nor the names of its contributors may be used
#   to endorse or promote products derived from this software without specific prior 
#   written permission from Coverity, Inc.
#   
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
#   EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#   OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND INFRINGEMENT ARE DISCLAIMED.
#   IN NO EVENT SHALL THE COPYRIGHT HOLDER OR  CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#   INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#   NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT,  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
#   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY 
#   OF SUCH DAMAGE.
#
import requests
import os
import sys
import re
import random
import itertools
import time
import json

from colorama import Fore
from pygraph.classes.digraph import digraph

import lxml.html as lhtml

matplot_colors = ( "#{:02X}{:02X}{:02X}".format(179, 162, 199),
                   "#{:02X}{:02X}{:02X}".format(195, 214, 155),
                   "#{:02X}{:02X}{:02X}".format(217, 150, 148),
                   "#{:02X}{:02X}{:02X}".format(149, 179, 215),
                   "#{:02X}{:02X}{:02X}".format(247, 150, 70),  # orange
                   "#{:02X}{:02X}{:02X}".format(128, 100, 162),  # teal
                   "#{:02X}{:02X}{:02X}".format(75, 172, 198),
                   "#{:02X}{:02X}{:02X}".format(119, 147, 60),
                   "#{:02X}{:02X}{:02X}".format(192, 80, 77),
                   "#{:02X}{:02X}{:02X}".format(79, 129, 189),
                   "#{:02X}{:02X}{:02X}".format(195, 214, 155),
                   "#{:02X}{:02X}{:02X}".format(237, 150, 148),
                   "#{:02X}{:02X}{:02X}".format(189, 179, 215),
                   "#{:02X}{:02X}{:02X}".format(207, 150, 70),
                   "#{:02X}{:02X}{:02X}".format(198, 100, 162),
                   "#{:02X}{:02X}{:02X}".format(125, 172, 198),
                   "#{:02X}{:02X}{:02X}".format(99, 147, 60),
                   "#{:02X}{:02X}{:02X}".format(132, 80, 77),
                   "#{:02X}{:02X}{:02X}".format(59, 129, 189),
                   )

__isiterable = lambda obj: isinstance(obj, basestring) or getattr(obj, '__iter__', False)
__normalize_argmt = lambda x: ''.join(x.lower().split())
__normalize_paths = lambda x: [os.path.abspath(of) for of in x]
__normalize_path = lambda x: os.path.abspath(x)

# Just some terminal shiny things for debugging...
__em = lambda rts: Fore.RED + str(rts) + Fore.RESET
__b = lambda rts: Fore.GREEN + str(rts) + Fore.RESET
__u = lambda rts: Fore.BLUE + str(rts) + Fore.RESET

LABEL_SEPARATOR = ', '
HTML5_TOKENIZATION_SPEC_URL = 'http://www.whatwg.org/specs/web-apps/current-work/multipage/tokenization.html'

REG_NODES = re.compile(r'<h5 id="([\w\-\(\)]+)"><span class="secno">((?!</h5>).*)</h5>', re.I)
REG_DD_TO = re.compile(r'<a href="([^#]*)#([\w\-\(\)]+)"(.*)>', re.I|re.M)
REG_DD_EMIT = re.compile(r'U\+([0-9A-F]{4}) ([A-Z\-\s]+) character token')

EMIT_CHAR_NODE = 'emit-character U+%s'
KNOWN_DD_NODES = {
    'Ignore the character.' : 'ignore-character',
    'Emit an end-of-file token.' : 'end-of-file'
}

REG_SWITCH = re.compile(r'U\+([0-9A-F]{4})')

class StateMachine:
    def __init__(self):
        self.g = digraph()
        self.state_nodes = None

    def getNumNodes(self):
        return len(self.g.nodes())

    def setStatesNodes(self, state_nodes):
        self.state_nodes = state_nodes

    def toJSON(self):
        return convertGraphToJSON(self.g)

    def toDOT(self):
        return makePrettyDOT(self.g, self.state_nodes)

    def toEBNF(self):
        return generateEBNF(self.g, self.state_nodes)


def getLatestSpec():
    r = requests.get(HTML5_TOKENIZATION_SPEC_URL)
    return r.text if r else None


def convertGraphToJSON(g):
    d = {
        'nodes' : [],
        'edges' : []
    }

    for n in g:
        d['nodes'].append(n)

    for e in g.edges():
        n1, n2 = e
        d['edges'].append({
            "from" : n1,
            "to" : n2,
            "label" : g.edge_label(e).split(LABEL_SEPARATOR)
        })

    return json.dumps(d)


def generateEBNF(g, state_nodes):
    raise Exception('Not implemented')


def makePrettyDOT(g, state_nodes):

    def htmlize(rts):
        return rts.replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")

    clusters, non_clustered = generateClustersFromNodes(g.nodes())

    counter = 0
    dstr = 'digraph HTML5Tokenizer {\n'
    dstr += "\torientation=landscape;\n"
    dstr += "\trankdir=TB;\n"
    for cluster in clusters:
        dstr += "\tsubgraph cluster_%s {\n" % cluster
        dstr += "\t\tstyle=filled;\n\t\tcolor=\"%s3f\";\n\t\trank=same;\n" % matplot_colors[counter % len(matplot_colors)] 
        dstr += '\t\tlabel="%s states";\n' % cluster
        
        for node in clusters[cluster]:
            shape = 'box'
            fillcolor = '#efefef'
            if node in state_nodes:
                shape = 'egg'
                fillcolor = matplot_colors[counter % len(matplot_colors)] + '2f'
            dstr += '\t\t"%s" [shape=%s, style=filled, fillcolor="%s"];\n' % (node, shape, fillcolor)
        dstr += "\t}\n"
        counter += 1

    for node in non_clustered:
        shape = 'box'
        if node in state_nodes:
            shape = 'egg'
        dstr += '"%s" [shape=%s, style=filled, fillcolor="#efefef"];\n' % (node, shape)

    dstr += "\n\n"
    for edge in g.edges():
        n1, n2 = edge
        node_type = 'label="%s"' % htmlize(g.edge_label(edge))
        dstr += '"%s" -> "%s" [%s];\n' % (n1, n2, node_type)

    dstr += '}'
    return dstr


CLUSTER_KEYS = ('comment', 'script', 'doctype', 'tag', 'attribute', 'rawtext', 'rcdata', 'plaintext')
def generateClustersFromNodes(nodes):
    clusters = {}
    non_clustered = []

    for n in nodes:
        added = False
        for cl_key in CLUSTER_KEYS:
            if cl_key in n:
                if cl_key not in clusters:
                    clusters[cl_key] = []

                clusters[cl_key].append(n)
                added = True
                break
        if not added:
            non_clustered.append(n)

    return clusters, non_clustered


def buildSwitchTransitions(state_name, sm, switch=None, to=None):
    if not switch or not to:
        return
    gr = sm.g
    if not gr.has_node(state_name):
        gr.add_node(state_name)


    # Find where the transition is going...
    to_start = to.find('<dd>') + len('<dd>') 
    to_end = to.find('</dd>')
    to = to[to_start:to_end]

    to_nodes = []

    to_reg = REG_DD_TO.findall(to)
    if to_reg:
        to_nodes = [k[1] for k in to_reg]

    if to in KNOWN_DD_NODES:
        to_nodes.append(KNOWN_DD_NODES[to])

    emit_reg = REG_DD_EMIT.findall(to)
    if emit_reg:
        if len(emit_reg) > 0:
            print __u(state_name), "emit multiple", emit_reg

        for n in emit_reg:
            to_nodes.append(EMIT_CHAR_NODE % (n[0]))

    if len(to_nodes) > 1:
        print __em(state_name), " ::= ", to_nodes

    for to_node in to_nodes:
        if not gr.has_node(to_node):
            gr.add_node(to_node)

        # Extract the switch stmt labels
        label = []
        for elmt in switch:
            if not elmt:
                continue
            try:
                if '<dt>' in elmt:
                    label.append(summarizeTransitionLink(elmt))
                    continue

                has_unicode = REG_SWITCH.search(elmt)
                if has_unicode:
                    label.append(summarizeUnicode(has_unicode.group(1)))
                else:
                    label.append(elmt)
            except TypeError, e:
                print __em(e), elmt

        label_str = LABEL_SEPARATOR.join(label)
        edge = (state_name, to_node)

        if not gr.has_edge(edge):
            gr.add_edge(edge)
            gr.set_edge_label(edge, label_str)


def summarizeUnicode(unicode_str):
    repr_chr = repr(chr(int(unicode_str, 16)))
    return "%s U+%s" % (repr_chr, unicode_str)


def summarizeTransitionLink(rts):
    hlink = REG_DD_TO.search(rts)
    if not hlink:
        print __em("We got a problem"), rts
    return hlink.group(2)


# The structure is fairly simple. Get all <dt> to know what chars will make
# a transition from this state. 
# <dd> tells us where the transition will be
def buildStatesFromTokenizerElement(state_name, html_snippet, sm):
    print __b(state_name), "in process"
    if state_name == 'tokenizing-character-references':
        return

    dom = lhtml.fromstring(html_snippet)
    switch = dom.cssselect('dl')
    if not switch:
        raise Exception("%s does not have <dl> (switch)" % state_name)
    if len(switch) > 1:
        print __em("%s have too many <dl> (switch)" % state_name)
    switch = switch[0]

    transitions = []

    for elmt in switch:
        if elmt.tag not in ('dt', 'dd'):
            continue
        if elmt.tag == 'dt':
            dt_text = elmt.text
            if not dt_text:
                dt_text = lhtml.tostring(elmt)
            transitions.append(dt_text)
        elif elmt.tag == 'dd':
            # We consume the transitions to jump into the 
            # specified state
            buildSwitchTransitions(state_name, sm, switch=transitions, to=lhtml.tostring(elmt))
            transitions = []


def buildStateMachine(sm, spec_html):
    all_nodes = [n[0] for n in REG_NODES.findall(spec_html)]
    sm.setStatesNodes(all_nodes)

    t = REG_NODES.split(spec_html)
    state_name = None
    for html_snippet in t:
        if '</dl>' in html_snippet:
            buildStatesFromTokenizerElement(state_name, html_snippet, sm)
        elif '</span>' not in html_snippet:
            state_name = html_snippet
    return True


def process(conf):
    sm = StateMachine()
    spec_html = getLatestSpec()

    if not buildStateMachine(sm, spec_html):
        print __em('[ERROR]'), 'while building the state machine'
        return

    if conf['dot']:
        b = open(conf['dot'], 'w')
        b.write(sm.toDOT())
        b.close()

    if conf['json']:
        b = open(conf['json'], 'w')
        b.write(sm.toJSON())
        b.close()


def main(argc, argv):
    conf = {
        'dot' : None,
        'json' : None,
    }

    for i in range(argc):
        s = argv[i]
        if s in ('--dot', '-d'):
            conf['dot'] = __normalize_path(argv[i + 1])
        if s in ('--json', '-j'):
            conf['json'] = __normalize_path(argv[i + 1])

    if not conf['dot'] and not conf['json']:
        print __em('[ERROR]'), 'Add --dot <PATH> or --json <PATH> as args.'
        return
    process(conf)

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
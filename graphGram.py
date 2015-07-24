from graphviz import Digraph

def graphGram(file):
    exec("from %s import *" % file)
    nodes = []
    dot = Digraph(comment=file)
    for [[fr, wds, to], dic] in TRANSITIONS:
        #print(fr, wds, to)
        if fr not in nodes:
            dot.node(str(fr))
            nodes = nodes+[fr]
        if to not in nodes:
            dot.node(str(to))
            nodes = nodes+[to]
        dot.edge(str(fr),str(to), ', '.join(wds)+(' :: '+', '.join(dic.keys()) if dic.keys() else ''))
    dot.render(file+'_graph')
    
        
        

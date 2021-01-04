#!/usr/bin/python3

import pickle
import networkx as nx
import matplotlib.pyplot as plt
from math import ceil, sqrt
from datetime import date

from pubs import Pub, Author, CONFERENCES, AREA_TITLES

def parse_author_cliques(pubs):
    authors = {}
    for pub in pubs:
        # create all author connections
        # iterate through each paper and count author1 -> author2 edges
        # we store the collected data in a hashmap of author1 -> author2 -> count
        for first_name in range(len(pub.authors)):
            for second_name in range(first_name + 1, len(pub.authors)):
                first_idx = first_name
                second_idx = second_name
                if pub.authors[first_name] > pub.authors[second_name]:
                    second_idx = first_name
                    first_idx = second_name
                if not pub.authors[first_idx] in authors:
                    authors[pub.authors[first_idx]] = {}
                if not pub.authors[second_idx] in authors[pub.authors[first_idx]]:
                    authors[pub.authors[first_idx]][pub.authors[second_idx]] = 0
                authors[pub.authors[first_idx]][pub.authors[second_idx]] += 1
    return authors

def parse_graph(authors, num_edges = 10, fname = ''):
    G = nx.Graph()
    #plt.figure(num=None, figsize=(20, 20), dpi=100)
    #plt.axis('off')
    #fig = plt.figure(1)

    author_set = []
    # count all authors with at least num_edges edges:
    for author1 in authors:
        for author2 in authors[author1]:
            if authors[author1][author2] >= num_edges:
                if author1 not in author_set:
                    author_set.append(author1)
                    G.add_node(author1)
                if author2 not in author_set:
                    author_set.append(author2)
                    G.add_node(author2)
                G.add_edge(author1, author2, weight=authors[author1][author2])
    # break large graph into subgraphs (for disconnected parts)
    sub_graphs = list(nx.connected_component_subgraphs(G))
    # if, insted of sub graphs, we want one graph for all cliques, use the following code:
    ##pos=nx.spring_layout(G, k=5, scale=9, iterations=500)
    ##nx.draw_networkx_nodes(G, pos)
    ##nx.draw_networkx_labels(G, pos)
    ##nx.draw_networkx_edges(G, pos)
    nr_cliques = len(sub_graphs)
    print('Found {} cliques'.format(nr_cliques))
    x_cliques = ceil(sqrt(nr_cliques))
    y_cliques = ceil(nr_cliques / x_cliques)
    fig, axes = plt.subplots(nrows=x_cliques, ncols=y_cliques, figsize=(20,20))
    #fig.suptitle(fname)
    if (len(sub_graphs) == 1):
        ax = [axes]
    else:
        ax = axes.flatten()
    for i in range(len(sub_graphs)):
        # create a graph layout based on feedback for each sub graph
        pos=nx.spring_layout(sub_graphs[i], k=0.1, scale=0.6, iterations=80)
        nx.draw_networkx_nodes(sub_graphs[i], pos, ax=ax[i])
        nx.draw_networkx_labels(sub_graphs[i], pos, ax=ax[i])
        nx.draw_networkx_edges(sub_graphs[i], pos, ax=ax[i])
        # adjust borders for sub graph (because we have long lables that spill)
        xmin, xmax, ymin, ymax = ax[i].axis()
        ax[i].set(xlim = (xmin-0.5, xmax+0.5), ylim=(ymin, ymax))
        ax[i].set_axis_off()
    # disable axes for blank subplots (if we have remaining space)
    for i in range(len(sub_graphs), x_cliques*y_cliques):
        ax[i].set_axis_off()
    fig.tight_layout()

    # adjust borders for single graph case
    #l,r = plt.xlim()
    #plt.xlim(l-1, r+1)
    #t, b = plt.ylim()
    #plt.ylim(t-1, b+1)
    plt.savefig('docs/'+fname, bbox_inches="tight")
    #plt.show()
    del fig

if __name__ == '__main__':
    all_pubs = []
    AREAPUBS = 10
    ALLPUBS = 20
    for area in CONFERENCES:
        # Load pickeled data
        with open('pickle/pubs-{}.pickle'.format(area), 'rb') as f:
            pubs = pickle.load(f)
            f.close()
            all_pubs += pubs

        # Prepare per-author information
        authors = parse_author_cliques(pubs)
        print('Analyzed a total of {} authors'.format(len(authors)))

        # Create and draw graph
        parse_graph(authors, num_edges=AREAPUBS, fname=area)

    # Prepare per-author information
    authors = parse_author_cliques(all_pubs)
    print('Analyzed a total of {} authors'.format(len(authors)))

    # Create and draw graph
    parse_graph(authors, num_edges=ALLPUBS, fname='all')

    content = '<div class="row">'
    for area in CONFERENCES:
        content = content + '<div class="text-center"><h3>'+area+' cliques</h3><br/><img src="./'+area+'.png" width="800px"/><br/></div>'
    content = content + '<div class="text-center"><h3>All cliques</h3><br/><img src="./all.png" width="800px"/><br/></div></div>'
    
    template = open('templates/cliques.html', 'r').read()
    template = template.replace('XXXTITLEXXX', 'Author cliques')
    template = template.replace('XXXCONTENTXXX', content)
    template = template.replace('XXXSHAREDXXX', str(AREAPUBS))
    template = template.replace('XXXSHARED2XXX', str(ALLPUBS))
    template = template.replace('XXXDATEXXX', date.today().strftime("%Y-%m-%d"))
    fout = open('docs/cliques.html', 'w')
    fout.write(template)

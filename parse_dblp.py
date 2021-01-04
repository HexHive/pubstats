#!/usr/bin/python3

import lxml.etree as ET
from gzip import GzipFile
import pickle
import csv

from pubs import Pub, Author, CONFERENCES

def parse_dblp(dblp_file = './dblp.xml.gz'):
    pubs = {}
    for area in CONFERENCES:
        pubs[area] = []
    in_pub = False
    total_pub = 0
    selected_pub = 0
    authors = []
    title = ''
    venue = ''
    year = 1900

    dblp_stream = GzipFile(filename=dblp_file)
    for event, elem in ET.iterparse(dblp_stream, events = ('start', 'end',), load_dtd = True):
        if event == 'start':
            if elem.tag == 'inproceedings' or elem.tag == 'article':
                in_pub = True
        if event == 'end':
            if in_pub and elem.tag == 'title':
                title = elem.text
            elif in_pub and (elem.tag == 'booktitle' or elem.tag == 'journal'):
                venue = elem.text
            elif in_pub and elem.tag == 'year':
                year = int(elem.text)
            elif in_pub and elem.tag == 'author':
                authors.append(elem.text)
            elif elem.tag == 'inproceedings' or elem.tag == 'article':
                for area in CONFERENCES:
                    if venue in CONFERENCES[area]:
                        selected_pub += 1
                        pubs[area].append(Pub(venue, title, authors, year))
                in_pub = False
                total_pub += 1
                authors = []
            elem.clear()
    return (pubs, total_pub, selected_pub)

def remove_aliases(confs):
    # parse aliases from csrankins
    aliases = {}
    with open('dblp-aliases.csv', 'r') as f:
        csvaliases = csv.reader(f)
        for row in csvaliases:
            if row[0] == 'alias':
                continue
            aliases[row[0]] = row[1]
    # update all publications with aliased authors
    aliases_replaced = 0
    for area in confs:
        for pub in confs[area]:
            for i in range(len(pub.authors)):
                if pub.authors[i] in aliases:
                    pub.authors[i] = aliases[pub.authors[i]]
                    aliases_replaced += 1
    print('Replaced {} authors'.format(aliases_replaced))

if __name__ == '__main__':
    # Parse security conferences
    pubs, total_pub, selected_pub = parse_dblp()
    print('Selected a grand total of {} out of {} publications'.format(selected_pub, total_pub))

    # Remove aliases
    remove_aliases(pubs)

    # Dump publications into pickle file
    for area in pubs:
        with open('pickle/pubs-{}.pickle'.format(area), 'wb') as f:
            pickle.dump(pubs[area], f)
            f.close()

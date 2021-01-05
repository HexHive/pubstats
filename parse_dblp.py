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
    in_pub = False # flag marking if we're parsing a publication
    total_pub = 0
    selected_pub = 0
    authors = []
    title = ''
    venue = ''
    year = 1900

    # auther affiliations
    affiliations = {}
    all_authors = set() # authors of our selected conferences
    author_homepage = ''
    author_affiliation = ''
    total_affiliations = 0
    in_www = False # flag marking if we're parsing affiliation information

    dblp_stream = GzipFile(filename=dblp_file)
    # Writing streaming XML parsers is fun...
    for event, elem in ET.iterparse(dblp_stream, events = ('start', 'end',), load_dtd = True):
        # mark header tags
        if event == 'start':
            if elem.tag == 'inproceedings' or elem.tag == 'article':
                in_pub = True
            if elem.tag == 'www':
                in_www = True
        # process individual closing tags
        if event == 'end':
            if in_pub and elem.tag == 'title':
                title = elem.text
            elif in_pub and (elem.tag == 'booktitle' or elem.tag == 'journal'):
                venue = elem.text
            elif in_pub and elem.tag == 'year':
                year = int(elem.text)
            # author is needed both for affiliations and pubs
            elif (in_pub or in_www) and elem.tag == 'author':
                authors.append(elem.text)
            elif in_www and elem.tag=='url':
                if author_homepage == '':
                    author_homepage = elem.text
            elif in_www and elem.tag=='note' and elem.get('type') == 'affiliation':
                # note: we only record the first affiliation of an author in the list
                if author_affiliation == '':
                    author_affiliation = elem.text
            elif elem.tag == 'inproceedings' or elem.tag == 'article':
                for area in CONFERENCES:
                    if venue in CONFERENCES[area]:
                        selected_pub += 1
                        pubs[area].append(Pub(venue, title, authors, year))
                        for author in authors:
                            if not author in all_authors:
                                all_authors.add(author)
                in_pub = False
                total_pub += 1
                authors = []
            elif elem.tag == 'www':
                # Process an author affiliation (if available)
                if len(authors) >= 1:
                    if author_affiliation.find(',') != -1:
                        author_affiliation = author_affiliation[0:author_affiliation.find(',')].strip()
                    affiliations[authors[0]] = (author_affiliation, author_homepage, '') # affil, homepage, google scholar
                    author_affiliation = ''
                    author_homepage = ''
                    authors = []
                    total_affiliations += 1
                in_pub = False
            elem.clear()

    # prune authors that have not published at our conferences of interest
    kill_list = []
    for author in affiliations:
        if author not in all_authors:
            kill_list.append(author)
    for author in kill_list:
        del affiliations[author]
    return (pubs, affiliations, total_pub, selected_pub, total_affiliations)

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
    pubs, affiliations, total_pub, selected_pub, total_affiliations = parse_dblp()
    print('Selected a grand total of {} out of {} publications'.format(selected_pub, total_pub))
    print('Selected a grand total of {} out of {} authors (with affiliations)'.format(len(affiliations), total_affiliations))

    # Remove aliases
    remove_aliases(pubs)

    # Dump publications into pickle file
    for area in pubs:
        with open('pickle/pubs-{}.pickle'.format(area), 'wb') as f:
            pickle.dump(pubs[area], f)
            f.close()
    # Dump affiliations into pickle file
    with open('pickle/affiliations.pickle', 'wb') as f:
        pickle.dump(affiliations, f)
        f.close()

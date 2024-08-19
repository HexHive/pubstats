#!/usr/bin/python3

import lxml.etree as ET
from gzip import GzipFile
import pickle
import csv
import re

from pubs import Pub, Author, CONFERENCES, CONFERENCES_NUMBER

MIN_PAPER_PAGES = 6

def get_nr_pages(pages, title, venue, year):
    start = ''
    end = ''
    addon = 0
    # we don't know, so assume it's a paper
    if pages == '':
        # special casing
        if venue == 'USENIX Security Symposium':
            return MIN_PAPER_PAGES
        if venue == 'USENIX Annual Technical Conference' and (year==1998 or year==2007 or year==2009 or year==2010 or year==2011 or year==2016 or year==2017 or year==2019):
            return MIN_PAPER_PAGES
        if venue == 'USENIX Annual Technical Conference, General Track' and (year==2006):
            return MIN_PAPER_PAGES
        if venue == 'FAST' and (year==2003 or year==2005 or year==2007):
            return MIN_PAPER_PAGES
        if venue == 'DAC' and (year<=1980):
            return MIN_PAPER_PAGES
        if venue == 'OSDI' and (year==2002):
            return MIN_PAPER_PAGES
        if venue == 'ICCAD' and (year==2001):
            return MIN_PAPER_PAGES
        if venue == 'MobiSys' and (year==2003 or year==2004):
            return MIN_PAPER_PAGES
        if venue == 'NDSS':
            # TODO this includes NDSS keynotes as papers.
            # The lack of an <ee> tag in the same inproceedings entry may indicate that it's a keynote (checked for 01)
            return MIN_PAPER_PAGES
        if venue == 'NSDI' and (year==2005 or year==2006 or year==2007 or year==2011 or year==2024):
            return MIN_PAPER_PAGES
        if venue == 'SC' and (year==2009):
            return MIN_PAPER_PAGES
        if venue == 'VLDB' and (year==2001 or year==2002):
            return MIN_PAPER_PAGES
        if title.startswith('Front Matter') or title.startswith('Letter from') or title.startswith('Message from') or title.startswith('Session details') or title.startswith('Welcome Message'):
            return 0
        print('No pages: "{}" ({}, {})'.format(title, venue, year))
        return 0
    # find from/to delimeter (or assume it's just one page)
    if pages.find('-') != -1:
        start = pages[0:pages.find('-')]
        end = pages[pages.find('-')+1:]
        # special casing
        if venue == 'HPDC' and (year==2001 or year==2002) and end=='':
            return MIN_PAPER_PAGES
        if venue == 'ICCAD' and (year==2001) and end=='':
            return MIN_PAPER_PAGES
        if venue == 'IEEE Symposium on Security and Privacy' and (year==2004 or year==2003) and end=='':
            return MIN_PAPER_PAGES
        if venue == 'ISCA' and (year==2002) and end=='':
            return MIN_PAPER_PAGES
    else:
        return 1
    if pages.startswith('i-'):
        return 1
    # check for format 90:1-90:28 (e.g., used in journals)
    if start.find(':') != -1:
        start = start[start.find(':')+1:]
    if end.find(':') != -1:
        end = end[end.find(':')+1:]
    # if we have two ranges, recurse
    if start.find(',') != -1:
        addon = get_nr_pages(start[start.find(',')+1:].strip(), title, venue, year)
        start = start[0:start.find(',')]
    if end.find(',') != -1:
        addon = get_nr_pages(end[end.find(',')+1:].strip(), title, venue, year)
        end = end[0:end.find(',')]
    if not start.isnumeric() or not end.isnumeric():
        print('Non-numeric characters: "{}" {} ({}, {})'.format(pages, title, venue, year))
        start = re.sub('[^0-9]','', start)
        end = re.sub('[^0-9]','', end)
    # double check that none of the ranges are empty
    if start=='' or end=='':
        print('Single page: "{}" {} ({}, {})'.format(pages, title, venue, year))
        return 1
    return int(end) - int(start) + addon + 1

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
    number = ''
    pages = ''
    year = 1900
    unhandled_venues = set()

    # author affiliations
    affiliations = {}
    all_authors = set() # authors of our selected conferences
    author_homepage = ''
    author_affiliation = ''
    total_affiliations = 0
    in_www = False # flag marking if we're parsing affiliation information

    # author aliases
    aliases = {}

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
            elif in_pub and elem.tag == 'number':
                number = elem.text
            elif in_pub and elem.tag == 'pages':
                pages = elem.text
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
                if author_affiliation == '' and elem.text != None:
                    author_affiliation = elem.text
            elif elem.tag == 'inproceedings' or elem.tag == 'article':
                for area in CONFERENCES:
                    if venue in CONFERENCES[area] or (venue in CONFERENCES_NUMBER[area] and number in CONFERENCES_NUMBER[area][venue]):
                        if get_nr_pages(pages, title, venue, year) >= MIN_PAPER_PAGES:
                            selected_pub += 1
                            pubs[area].append(Pub(venue, title, authors, year))
                            for author in authors:
                                if not author in all_authors:
                                    all_authors.add(author)
                    elif venue.find(' (') != -1 and venue[0:venue.find(' (')] in CONFERENCES[area]:
                        unhandled_venues.add(venue)
                total_pub += 1
                authors = []
                number = ''
                title = ''
                pages = ''
                year = 0
                venue = ''
                in_pub = False
            elif elem.tag == 'www':
                # Process an author affiliation (if available)
                if len(authors) >= 1:
                    # record affiliation
                    if author_affiliation.find(',') != -1:
                        author_affiliation = author_affiliation[0:author_affiliation.find(',')].strip()
                    affiliations[authors[0]] = (author_affiliation, author_homepage, '') # affil, homepage, google scholar
                    total_affiliations += 1
                    # does this author have aliases?
                    if len(authors) > 1:
                        for i in range(1, len(authors)):
                            aliases[authors[i]] = authors[0]
                # clean for next iteration
                author_affiliation = ''
                author_homepage = ''
                authors = []
                in_www = False
            elem.clear()

    # prune authors that have not published at our conferences of interest
    kill_list = []
    for author in affiliations:
        if author not in all_authors:
            kill_list.append(author)
    for author in kill_list:
        del affiliations[author]
    for venue in unhandled_venues:
        print("Unhandled partial match for venue: {}".format(venue))

    return (pubs, affiliations, aliases, total_pub, selected_pub, total_affiliations)

def remove_aliases(confs, aliases):
    # parse aliases from CSrankins
    #aliases = {}
    #with open('dblp-aliases.csv', 'r') as f:
    #    csvaliases = csv.reader(f)
    #    for row in csvaliases:
    #        if row[0] == 'alias':
    #            continue
    #        aliases[row[0]] = row[1]
    # update all publications with aliased authors
    aliases_replaced = 0
    for area in confs:
        for pub in confs[area]:
            for i in range(len(pub.authors)):
                if pub.authors[i] in aliases:
                    pub.authors[i] = aliases[pub.authors[i]]
                    aliases_replaced += 1
    print('Replaced {} aliases'.format(aliases_replaced))

if __name__ == '__main__':
    # Parse security conferences
    pubs, affiliations, aliases, total_pub, selected_pub, total_affiliations = parse_dblp()
    print('Selected a grand total of {} out of {} publications'.format(selected_pub, total_pub))
    print('Selected a grand total of {} out of {} authors (with affiliations)'.format(len(affiliations), total_affiliations))

    # Remove aliases
    remove_aliases(pubs, aliases)

    # Dump publications into pickle file
    for area in pubs:
        with open('pickle/pubs-{}.pickle'.format(area), 'wb') as f:
            pickle.dump(pubs[area], f)
            f.close()
    # Dump affiliations into pickle file
    with open('pickle/affiliations.pickle', 'wb') as f:
        pickle.dump(affiliations, f)
        f.close()

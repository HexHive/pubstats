#!/usr/bin/python3

import pickle
from statistics import median, mean
from datetime import date
import csv
import matplotlib.pyplot as plt
import sys

from pubs import Pub, Author, CONFERENCES, CONFERENCES_SHORT, AREA_TITLES
from top_authors import parse_authors

if __name__ == '__main__':
    all_pubs = []
    top_values = {}
    if len(sys.argv) != 2:
        print('Print all publications of an author. Call this script with {} "NAME"'.format(sys.argv[0]))
        exit(1)
    for area in CONFERENCES:
        # Load pickeled data
        with open('pickle/pubs-{}.pickle'.format(area), 'rb') as f:
            pubs = pickle.load(f)
            f.close()
            all_pubs += pubs
        
        print('# {}\'s publications in {}'.format(sys.argv[1], area))

        auth_pubs, _, _ = parse_authors(pubs)
        if sys.argv[1] not in auth_pubs:
            continue

        author = auth_pubs[sys.argv[1]]
        for year in sorted(author.years):
            for pub in author.pubs[year]:
                print('{}, {}, {}'.format(pub.title, pub.venue, year))

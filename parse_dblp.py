#!/usr/bin/python3

import lxml.etree as ET
import pickle
import csv

from pubs import Pub, Author

# Conference abbreviations
# booktitle: AsiaCCS
# booktitle: CCS
# booktitle: CODASPY
# booktitle: WOOT
# booktitle: USENIX Security Symposium
# booktitle: NDSS
# booktitle: EuroS&amp;P
# booktitle: USENIX Annual Technical Conference
# booktitle: RTSS
# booktitle: DIMVA
# booktitle: OSDI
# booktitle: ESORICS
# booktitle: IEEE Symposium on Security and Privacy

def parse_dblp(confs, dblp = './dblp.xml'):
    pubs = []
    in_pub = False
    total_pub = 0
    selected_pub = 0
    authors = []
    title = ''
    venue = ''
    year = 1900
    for event, elem in ET.iterparse(dblp, events = ('start', 'end',), load_dtd = True):
        if event == 'start':
            if elem.tag == 'inproceedings':
                in_pub = True
        if event == 'end':
            if in_pub and elem.tag == 'title':
                title = elem.text
            elif in_pub and elem.tag == 'booktitle':
                venue = elem.text
            elif in_pub and elem.tag == 'year':
                year = int(elem.text)
            elif in_pub and elem.tag == 'author':
                authors.append(elem.text)
            elif elem.tag == 'inproceedings':
                if venue in confs:
                    selected_pub += 1
                    pubs.append(Pub(venue, title, authors, year))
                in_pub = False
                total_pub += 1
                authors = []
            elem.clear()
    return (pubs, total_pub, selected_pub)

def remove_aliases(pubs):
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
    for pub in pubs:
        for i in range(len(pub.authors)):
            if pub.authors[i] in aliases:
                pub.authors[i] = aliases[pub.authors[i]]
                aliases_replaced += 1
    print('Replaced {} authors'.format(aliases_replaced))


def parse_authors(pubs):
    authors = {}
    for pub in pubs:
        for name in pub.authors:
            if name not in authors:
                authors[name] = Author(name)
            authors[name].add_publication(pub.venue, pub.year, pub.title)
    return authors

author_head = '''<thead>
<tr>
  <th>Rank</th>
  <th>Name</th>
  <th>Total</th>
  <th>16-20</th>
  <th>20</th>
  <th>19</th>
  <th>18</th>
  <th>17</th>
  <th>16</th>
  <th>15</th>
  <th>14</th>
  <th>13</th>
  <th>12</th>
  <th>11</th>
  <th>10</th>
  <th>09</th>
  <th>08</th>
  <th>07</th>
  <th>06</th>
  <th>05</th>
  <th>04</th>
  <th>03</th>
  <th>02</th>
  <th>01</th>
  <th>00</th>
  <th>&lt;00</th>
</tr>
</thead>
'''
author_entry = '''<tr>
  <td>{}</td>
  <td>{}</td>
  <td>{}</td>
  {}
</tr>
'''

# Max, Slams, Venues, Co-Authors, Avg

def top_authors(authors, title = 'Security Top Authors', tname = 'top-authors.html', fname = 'www/sec-top-authors.html'):
    ranked = {}
    for name in authors:
        total = authors[name].get_total()
        if total > 2:
            if total not in ranked:
                ranked[total] = []
            ranked[total].append(authors[name])

    content = author_head

    rank = 1
    for number in sorted(ranked.keys(), reverse = True):
        for author in ranked[number]:
            yearly = ''
            for year in range(2020, 1999, -1):
                if year not in author.years:
                    yearly += '<td></td>'
                else:
                    yearly += '<td>'+str(author.years[year])+'</td>'
            recent = 0
            for year in author.years.keys():
                if year > 2015:
                    recent += author.years[year]
            if recent == 0:
                yearly = '<td></td>' + yearly
            else:
                yearly = '<td>'+str(recent)+'</td>' + yearly
            ancient = 0
            for year in author.years.keys():
                if year < 2000:
                    ancient += author.years[year]
            if ancient == 0:
                yearly += '<td></td>'
            else:
                yearly += '<td>'+str(ancient)+'</td>'
            content += author_entry.format(rank, author.name, number, yearly)
        rank += len(ranked[number])

    template = open(tname, 'r').read()
    template = template.replace('XXXTITLEXXX', title)
    template = template.replace('XXXCONTENTXXX', content)
    fout = open(fname, 'w')
    fout.write(template)

if __name__ == '__main__':
    # Parse security conferences
    pubs, total_pub, selected_pub = parse_dblp(['CCS', 'USENIX Security Symposium', 'NDSS', 'IEEE Symposium on Security and Privacy'])
    print('Selected a grand total of {} out of {} publications'.format(selected_pub, total_pub))

    # Remove aliases
    remove_aliases(pubs)

    # Dump publications into pickle file
    with open('sec-pubs.pickle', 'wb') as f:
        pickle.dump(pubs, f)
        f.close()

#!/usr/bin/python3

import lxml.etree as ET
import pickle

from pubs import Pub, Author

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
  <td class="name">{}</td>
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
    # Load pickeled data
    with open('sec-pubs.pickle', 'rb') as f:
        pubs = pickle.load(f)
        f.close()

    # Prepare per-author information
    authors = parse_authors(pubs)
    print('Analyzed a total of {} authors'.format(len(authors)))

    # Pretty print HTML
    top_authors(authors)

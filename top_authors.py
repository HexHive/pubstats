#!/usr/bin/python3

import pickle
from statistics import median
from datetime import date

from pubs import Pub, Author, CONFERENCES, AREA_TITLES

def parse_authors(pubs):
    authors = {}
    for pub in pubs:
        for name in pub.authors:
            if name not in authors:
                authors[name] = Author(name)
            authors[name].add_publication(pub.venue, pub.year, pub.title, pub.authors)
    return authors

def top_authors(authors, cons = '', title = 'Top Authors', tname = 'templates/top-authors.html', fname = 'docs/top-authors.html'):
    ranked = {}
    current_year = 0 # max year we have data of
    for name in authors:
        total = authors[name].get_total()
        if total > 2:
            if total not in ranked:
                ranked[total] = []
            ranked[total].append(authors[name])
            if max(authors[name].years.keys()) > current_year:
                current_year = max(authors[name].years.keys())

    author_entry = '''<tr>
<td>{}</td>
<td class="name">{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>'''
    author_head = '''<thead>
<tr>
<th>Rank</th>
<th>Name</th>
<th>Total</th>
<th>(A)</th>
<th>(Rel)</th>'''
    author_head = author_head + '<th>' + str(current_year-2004) + '-' + str(current_year-2000) + '</th>'
    author_head = author_head + '''<th>(A5)</th>
<th>(Rel5)</th>'''

    for year in range(current_year, current_year-21, -1):
        author_head = author_head + '<th>' + str(year-2000) + '</th>'
        author_entry = author_entry + '<td>{}</td>'
    author_head = author_head + '''<th>&lt;00</th>
</tr>
</thead>'''
    author_entry = author_entry + '''<td>{}</td>
</tr>'''

    content = author_head
    rank = 1
    for number in sorted(ranked.keys(), reverse = True):
        for author in ranked[number]:
            values = [rank, author.name, number]

            # Calculate median
            median_data = []
            median_data5 = []
            for year in author.pubs_years:
                median_data = median_data + author.pubs_years[year]
                if year > current_year-5:
                    median_data5 = median_data5 +  author.pubs_years[year]
            med = median(median_data)

            values.append(round(med))
            values.append('{:.2f}'.format(number/sum(median_data)*number))

            # summary of last 5 years
            recent = 0
            for year in author.years.keys():
                if year > current_year-5:
                    recent += author.years[year]
            if recent == 0:
                values.append('')
            else:
                values.append(recent)

            if len(median_data5) != 0:
                med5 = round(median(median_data5))
            else:
                med5 = ''
            values.append(med5)

            if recent == 0:
                values.append('')
            else:
                values.append('{:.2f}'.format(recent/sum(median_data5)*recent))

            # last 20 years individually
            for year in range(current_year, current_year-21, -1):
                if year not in author.years:
                    values.append('')
                else:
                    values.append(author.years[year])

            # add ancient years
            ancient = 0
            for year in author.years.keys():
                if year < current_year-10:
                    ancient += author.years[year]
            if ancient == 0:
                values.append('')
            else:
                values.append(ancient)
            content += author_entry.format(*values)
        rank += len(ranked[number])

    template = open(tname, 'r').read()
    template = template.replace('XXXTITLEXXX', title)
    template = template.replace('XXXCONTENTXXX', content)
    template = template.replace('XXXDATEXXX', date.today().strftime("%Y-%m-%d"))
    template = template.replace('XXXTOPCONSXXX', cons)
    fout = open(fname, 'w')
    fout.write(template)

if __name__ == '__main__':
    all_pubs = []
    for area in CONFERENCES:
        # Load pickeled data
        with open('pickle/pubs-{}.pickle'.format(area), 'rb') as f:
            pubs = pickle.load(f)
            f.close()
            all_pubs += pubs

        # Prepare per-author information
        authors = parse_authors(pubs)
        print('Analyzed a total of {} authors'.format(len(authors)))

        # Pretty print HTML
        top_authors(authors, cons = ', '.join(CONFERENCES[area]), title = AREA_TITLES[area], fname = 'docs/top-authors-{}.html'.format(area))

    # Prepare per-author information
    authors = parse_authors(all_pubs)
    print('Analyzed a total of {} authors'.format(len(authors)))

    # Pretty print HTML
    allcons = []
    for area in CONFERENCES:
        allcons = allcons + CONFERENCES[area]
    top_authors(authors, cons = ', '.join(allcons), title = 'Systems (All Top Conferences)', fname = 'docs/top-authors-sys.html')

    content = ''
    for area in AREA_TITLES:
        content = content + '<li><a href="./top-authors-' + area + '.html">' + AREA_TITLES[area] + '</a></li>\n'
    content = content + '<li><a href="./top-authors-sys.html">' + AREA_TITLES[area] + '</a></li>\n'
    
    template = open('templates/top-index.html', 'r').read()
    template = template.replace('XXXCONTENTXXX', content)
    template = template.replace('XXXDATEXXX', date.today().strftime("%Y-%m-%d"))
    fout = open('docs/index.html', 'w')
    fout.write(template)
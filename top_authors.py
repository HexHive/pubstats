#!/usr/bin/python3

import pickle
from statistics import median
from datetime import date
import csv

from pubs import Pub, Author, CONFERENCES, CONFERENCES_SHORT, AREA_TITLES

# break publications (on venue basis) into per-author statistics
def parse_authors(pubs):
    authors = {}
    # Load aux data from cs rankings first
    aux_data = {}
    max_year = 0
    with open('csrankings.csv', 'r') as f:
        csvaliases = csv.reader(f)
        for row in csvaliases:
            if row[0] == 'alias':
                continue
            if row[0].find('[') != -1:
                name = row[0][0:row[0].find('[')-1]
            else:
                name = row[0]
            aux_data[name] = (row[1], row[2], row[3])
    # Load aux data as parsed from DBLP (as fallback)
    with open('pickle/affiliations.pickle', 'rb') as f:
        aux_data2 = pickle.load(f)
        f.close()
    # parse pubs and split into authors
    for pub in pubs:
        for name in pub.authors:
            if name not in authors:
                if name in aux_data:
                    authors[name] = Author(name, aux_data[name])
                elif name in aux_data2:
                    authors[name] = Author(name, aux_data2[name])
                else:
                    authors[name] = Author(name, ('', '', ''))
            authors[name].add_publication(pub.venue, pub.year, pub.title, pub.authors)
            if pub.year > max_year:
                max_year = pub.year
    return (authors, max_year)

# aggregate the numbers across all conferences in an area
# calculate relative statistics, to normalize a given area
# relative: each publication only counts as 1/n authors
# normalization: top N authors
def aggregate_area(authors, max_year, nr_years=20, top_publishers=1, relative=False):
    max_years = {}
    for name in authors:
        for year in authors[name].years:
            if year < max_year - nr_years:
                continue
            if not year in max_years:
                max_years[year] = []
            if not relative:
                max_years[year].append(authors[name].years[year])
            else:
                # calculate relative fraction (1/n authors)
                max_years[year].append(len(authors[name].nr_authors_year[year])/sum(authors[name].nr_authors_year[year]))
    # aggregate top N values and return yearly medians
    top_values = {}
    for year in max_years:
        top_values[year] = median(sorted(max_years[year], reverse=True)[0:top_publishers])
    return top_values


def top_authors(authors, cons='', title='Top Authors', tname='templates/top-authors.html', fname='docs/top-authors.html'):
    ranked = {}
    current_year = 0 # max year we have data of

    # walk through all authors and sort by class/ranking
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
<th>Affiliation</th>
<th>Total</th>
<th>(A)</th>
<th>(Rel)</th>'''
    author_head = author_head + '<th>' + str(current_year-2004) + '-' + str(current_year-2000) + '</th>'
    author_head = author_head + '<th>(A5)</th><th>(Rel5)</th>'

    for year in range(current_year, current_year-21, -1):
        author_head = author_head + '<th>' + str(year-2000) + '</th>'
        author_entry += '<td>{}</td>'
    author_head += '<th>&lt;00</th>'
    author_entry += '<td>{}</td>'

    author_head += '</tr></thead>'
    author_entry += '</tr>'

    content = author_head
    rank = 1
    for number in sorted(ranked.keys(), reverse = True):
        for author in ranked[number]:
            values = [rank, author.name, author.affiliation, number]

            # Calculate median
            median_data = []
            median_data5 = []
            for year in author.nr_authors_year:
                median_data = median_data + author.nr_authors_year[year]
                if year > current_year-5:
                    median_data5 = median_data5 +  author.nr_authors_year[year]
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
    top_values = {}
    area_authors = {}
    for area in CONFERENCES:
        # Load pickeled data
        with open('pickle/pubs-{}.pickle'.format(area), 'rb') as f:
            pubs = pickle.load(f)
            f.close()
            all_pubs += pubs

        # Prepare per-author information
        authors, max_year = parse_authors(pubs)
        print('Analyzed a total of {} authors for {}'.format(len(authors), area))

        top_values[area] = aggregate_area(authors, max_year=max_year, top_publishers=10, relative=True)
        area_authors[area] = authors

        # Pretty print HTML
        top_authors(authors, cons = ', '.join(CONFERENCES_SHORT[area]), title = AREA_TITLES[area], fname = 'docs/top-authors-{}.html'.format(area))

    # Prepare per-author information
    authors, max_year = parse_authors(all_pubs)
    print('Analyzed a total of {} authors'.format(len(authors)))

    # Pretty print HTML
    allcons = []
    for area in CONFERENCES:
        allcons = allcons + CONFERENCES_SHORT[area]
    top_authors(authors, cons = ', '.join(allcons), title = 'Systems (All Top Conferences)', fname = 'docs/top-authors-sys.html')

    # # normalize across per-area maximum values
    # for author in authors:
    #     for area in CONFERENCES:
    #         if author in area_authors[area]:
    #             for year in area_authors[area][author].years:
    #                 if year < max_year-20:
    #                     continue
    #                 #nr_pubs = area_authors[area][author].years[year]
    #                 nr_pubs = len(area_authors[area][author].nr_authors_year[year])/sum(area_authors[area][author].nr_authors_year[year])
    #                 authors[author].add_norm_area(year, round(nr_pubs/top_values[area][year]*10))

    # for author in authors:
    #     authors[author].years = authors[author].normalized_pubs
    # top_authors(authors, cons = ', '.join(allcons), title = 'Systems (All Top Conferences)', fname = 'docs/top-authors-sys-norm.html', normalize=True)

    content = ''
    for area in AREA_TITLES:
        content = content + '<li><a href="./top-authors-' + area + '.html">' + AREA_TITLES[area] + '</a></li>\n'
    content = content + '<li><a href="./top-authors-sys.html">All systems conferences</a></li>\n'
    
    template = open('templates/top-index.html', 'r').read()
    template = template.replace('XXXCONTENTXXX', content)
    template = template.replace('XXXDATEXXX', date.today().strftime("%Y-%m-%d"))
    fout = open('docs/index.html', 'w')
    fout.write(template)
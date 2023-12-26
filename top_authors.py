#!/usr/bin/python3

import pickle
from statistics import median, mean
from datetime import date
import csv
import matplotlib.pyplot as plt

from pubs import Pub, Author, CONFERENCES, CONFERENCES_SHORT, AREA_TITLES

# TODO normalize data on per-area basis
# Tried for different sub areas but the areas are similar enough so that 
# normalization does not change much (and normalization opens up questions
# about interpretation).

# break publications (on venue basis) into per-author statistics
def parse_authors(pubs):
    authors = {}
    # Load aux data from cs rankings first
    aux_data = {}
    max_year = 0
    total_pubs = {}
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
        # basic statistics
        if not pub.year in total_pubs:
            total_pubs[pub.year] = 0
        total_pubs[pub.year] += 1
        # break up into authors
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
    # now aggreate author data
    per_year_authors = {}
    for name in authors:
        for year in authors[name].years:
            if not year in per_year_authors:
                per_year_authors[year] = []
            if not name in per_year_authors[year]:
                per_year_authors[year].append(name)
    per_author_pubs_years = {}
    for name in authors:
        for year in authors[name].years:
            if not year in per_author_pubs_years:
                per_author_pubs_years[year] = []
            per_author_pubs_years[year].append(authors[name].years[year])
    # aggregate top N values and return yearly medians
    top_values = {}
    for year in per_author_pubs_years:
        # year = (total, max, median, average)
        top100mean = round(mean(sorted(per_author_pubs_years[year], reverse=True)[0:50])*100)/100
        top_values[year] = (total_pubs[year], max(per_author_pubs_years[year]), round(mean(per_author_pubs_years[year])*100)/100, top100mean, len(per_year_authors[year]))

    return (authors, max_year, top_values)


def top_authors(authors, cons='', title='Top Authors', tname='templates/top-authors.html', fname='www/top-authors.html', nr_years=20):
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

    for year in range(current_year, current_year-nr_years, -1):
        author_head = author_head + '<th>' + str(year-2000) + '</th>'
        author_entry += '<td>{}</td>'
    author_head += '<th>&lt;='+str(current_year-2000-nr_years)+'</th>'
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
            rel = 0.0
            rel5 = 0.0
            for year in author.nr_authors_year:
                median_data = median_data + author.nr_authors_year[year]
                for nr in author.nr_authors_year[year]:
                    rel += 1/nr
                    if year > current_year-5:
                        rel5 += 1/nr
                if year > current_year-5:
                    median_data5 = median_data5 +  author.nr_authors_year[year]
            med = median(median_data)

            values.append(round(med))
            values.append('{:.2f}'.format(rel))

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
                values.append('{:.2f}'.format(rel5))

            # last 20 years individually
            for year in range(current_year, current_year-nr_years, -1):
                if year not in author.years:
                    values.append('')
                else:
                    values.append(author.years[year])

            # add ancient years
            ancient = 0
            for year in author.years.keys():
                if year <= current_year-nr_years:
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

def stat_table(top_values, max_year, nr_years=20):
    table_head = '<thead><tr><th>Area</th><th>Total</th>'
    table_entry = '<tr{}><td class="name">{}</td><td>{}</td>'
    for year in range(max_year, max_year-nr_years, -1):
        table_head += '<th class="name">'+str(year-2000)+'</th>'
        table_entry += '<td>{}</td>'
    table_head += '<th class="name">&lt;'+str(max_year-2000-nr_years)+'</th>'
    table_head += '</tr></thead>'
    table_entry += '<td>{}</td></tr>'

    content = table_head

    areas = list(CONFERENCES.keys())
    areas.append('sys')

    fig_tot = {}
    fig_max = {}
    fig_avg50 = {}
    fig_auth = {}

    for area in areas:
        ancient_total = 0
        fresh_total = 0
        for year in top_values[area]:
            if year < max_year-nr_years:
                ancient_total += top_values[area][year][0]
            else:
                fresh_total += top_values[area][year][0]
        row_tot = ['', AREA_TITLES[area], fresh_total+ancient_total]
        row_max = [' class="light"', '', 'max/a']
        row_avg = [' class="light"', '', 'avg/a']
        row_avg50a = [' class="light"', '', 'avg/a50']
        row_auth = [' class="light"', '', '#a']
        for year in range(max_year, max_year-nr_years, -1):
            if not year in top_values[area]:
                top_values[area][year] = ('', '', '', '', '')
            row_tot.append(top_values[area][year][0])
            row_max.append(top_values[area][year][1])
            row_avg.append(top_values[area][year][2])
            row_avg50a.append(top_values[area][year][3])
            row_auth.append(top_values[area][year][4])
        row_tot.append(ancient_total)
        row_max.append('')
        row_avg.append('')
        row_avg50a.append('')
        row_auth.append('')
        content += table_entry.format(*row_tot)
        content += table_entry.format(*row_max)
        content += table_entry.format(*row_avg)
        content += table_entry.format(*row_avg50a)
        content += table_entry.format(*row_auth)
        for i in range(len(row_tot)):
            if row_tot[i] == '':
                row_tot[i] = 0
            if row_max[i] == '':
                row_max[i] = 0
            if row_avg50a[i] == '':
                row_avg50a[i] = 0
            if row_auth[i] == '':
                row_auth[i] = 0
        fig_tot[area] = row_tot[3:-1]
        fig_max[area] = row_max[3:-1]
        fig_avg50[area] = row_avg50a[3:-1]
        fig_auth[area] = row_auth[3:-1]
    stat_figure(fig_tot, 'Total number of publications per year', max_year, nr_years, fname='stat-tot.png')
    stat_figure(fig_max, 'Maximum number of publications of an author per year', max_year, nr_years, average=False, fname='stat-max.png')
    stat_figure(fig_avg50, 'Average number of publications per year for the top 50 authors', max_year, nr_years, average=False, fname='stat-avg50.png')
    stat_figure(fig_auth, 'Average number of active authors per year', max_year, nr_years, fname='stat-auth.png')

    stat_table = '''<div class="text-center"><img src="stat-tot.png" width="800px"/><br/><br/></div>
<div class="text-center"><img src="stat-max.png" width="800px"/><br/><br/></div>
<div class="text-center"><img src="stat-avg50.png" width="800px"/><br/><br/></div>
<div class="text-center"><img src="stat-auth.png" width="800px"/><br/><br/></div>
'''
    return (content, stat_table)

def stat_figure(fig_data, title, max_year, nr_years, average=True, fname=''):
    xaxis = []
    for year in range(max_year, max_year-nr_years, -1):
        xaxis.append(year)
    plt.figure(figsize=(12, 5))
    plt.title(title)
    plt.xticks(xaxis, xaxis)
    plt.xlabel('Year')
    for area in fig_data:
        lbl = area
        lwdt = 1.5
        if area == 'sys':
            if average:
                for i in range(len(fig_data[area])):
                    fig_data[area][i] = fig_data[area][i]/(len(fig_data)-1)
                lbl = 'avg(sys)'
            else:
                lbl = 'all(sys)'
            lwdt = 4
        plt.plot(xaxis, fig_data[area], label=lbl, linewidth=lwdt)
    plt.legend()
    if fname == '':
        plt.show()
    else:
        plt.savefig('www/'+fname, bbox_inches="tight")
    plt.clf()


if __name__ == '__main__':
    all_pubs = []
    top_values = {}
    for area in CONFERENCES:
        # Load pickeled data
        with open('pickle/pubs-{}.pickle'.format(area), 'rb') as f:
            pubs = pickle.load(f)
            f.close()
            all_pubs += pubs

        # Prepare per-author information
        authors, _, top_values[area] = parse_authors(pubs)
        print('Analyzed a total of {} authors for {}'.format(len(authors), area))

        # Pretty print HTML
        top_authors(authors, cons = ', '.join(CONFERENCES_SHORT[area]), title = AREA_TITLES[area], fname = 'www/top-authors-{}.html'.format(area))

    # Prepare per-author information
    authors, max_year, top_values['sys'] = parse_authors(all_pubs)
    print('Analyzed a total of {} authors'.format(len(authors)))

    # Pretty print HTML
    allcons = []
    for area in CONFERENCES:
        allcons = allcons + CONFERENCES_SHORT[area]

    # No researchers from Geneva, Basel, St. Gallen, or Fribourg
    affils = ['ETH Zurich', 'ETH Zürich', 'EPFL', 'Swiss Federal Institute of Technology in Lausanne', 'École Polytechnique Fédérale de Lausanne', 'Università della Svizzera italiana', 'University of Zurich', 'University of Bern']
    filtered_authors = {}
    for author in authors:
        if authors[author].affiliation in affils:
            filtered_authors[author] = authors[author]

    top_authors(authors, cons = ', '.join(allcons), title = 'Systems (All Top Conferences)', fname = 'www/top-authors-sys.html')
    top_authors(filtered_authors, cons = ', '.join(allcons), title = 'Systems (All Top Conferences, CH)', fname = 'www/top-authors-sys-ch.html')

    content = ''
    for area in AREA_TITLES:
        content = content + '<li><a href="./top-authors-' + area + '.html">' + AREA_TITLES[area] + '</a></li>\n'
    
    template = open('templates/top-index.html', 'r').read()
    template = template.replace('XXXCONTENTXXX', content)
    stat_table, stat_img = stat_table(top_values, max_year)
    template = template.replace('XXXAREASTATSXXX', stat_table)
    template = template.replace('XXXAREAIMGSXXX', stat_img)
    template = template.replace('XXXDATEXXX', date.today().strftime("%Y-%m-%d"))
    fout = open('www/index.html', 'w')
    fout.write(template)
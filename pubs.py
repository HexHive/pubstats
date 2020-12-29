#!/usr/bin/python3

class Pub():
    def __init__(self, venue, title, authors, year):
        self.venue = venue
        self.title = title
        self.authors = authors
        self.year = year
        #print('{} {} {} {}\n'.format(authors, year, venue, title))

class Author():
    def __init__(self, name):
        self.name = name
        self.years = {}
        self.pubs_years = {}
        self.venues = []

    def add_publication(self, venue, year, title, authors):
        if not year in self.years:
            self.years[year] = 0
            self.pubs_years[year] = []
        self.years[year] += 1
        self.pubs_years[year].append(len(authors))

        if not venue in self.venues:
            self.venues.append(venue)

    def get_total(self):
        return sum(self.years.values())

if __name__ == '__main__':
    print('Nothing to see here, move along...')

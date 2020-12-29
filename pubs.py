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
        self.venues = []

    def add_publication(self, venue, year, title):
        if not year in self.years:
            self.years[year] = 1
        else:
            self.years[year] += 1

        if not venue in self.venues:
            self.venues.append(venue)

    def get_total(self):
        return sum(self.years.values())

if __name__ == '__main__':
    print('Nothing to see here, move along...')

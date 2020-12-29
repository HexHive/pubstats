#!/usr/bin/python3

# Security conference abbreviations
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

# check out https://github.com/emeryberger/CSrankings/blob/gh-pages/filter.xq for conference names
CONFERENCES = {
    'sys_arch': ['ASPLOS', 'ISCA', 'MICRO'], # HPCA
    'sys_net': ['SIGCOMM', 'NSDI'],
    'sys_sec': ['CCS', 'ACM Conference on Computer and Communications Security', 'USENIX Security', 'USENIX Security Symposium', 'NDSS', 'IEEE Symposium on Security and Privacy'],
    'sys_db': ['SIGMOD Conference', 'VLDB'], # ICDE PODS
    'sys_design': ['DAC', 'ICCAD'],
    'sys_embed': ['EMSOFT', 'RTAS', 'RTSS'],
    'sys_hpc': ['HPDC', 'ICS', 'SC'],
    'sys_mob': ['MobiSys', 'MobiCom', 'MOBICOM', 'SenSys'],
    'sys_mes': ['IMC', 'Internet Measurement Conference', 'Proc. ACM Meas. Anal. Comput. Syst.'],
    'sys_os': ['SOSP', 'OSDI', 'EuroSys', 'USENIX Annual Technical Conference', 'USENIX Annual Technical Conference, General Track', 'FAST'],
    'sys_pl': ['PLDI', 'POPL'], # ICFP OOPSLA
    'sys_se': ['SIGSOFT FSE', 'ESEC/SIGSOFT FSE', 'ICSE', 'ICSE (1)', 'ICSE (2)'], # ASE ISSTA
}

AREA_TITLES = {
    'sys_arch': 'Systems: Architecture',
    'sys_net': 'Systems: Networks',
    'sys_sec': 'Systems: Security',
    'sys_db': 'Systems: Databases',
    'sys_design': 'Systems: Design',
    'sys_embed': 'Embedded System',
    'sys_hpc': 'Systems: HPC',
    'sys_mob': 'Mobile Systems',
    'sys_mes': 'Systems: Measurements',
    'sys_os': 'Systems: OS',
    'sys_pl': 'Systems: Programming Languages',
    'sys_se': 'Systems: Software Engineering',
}

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

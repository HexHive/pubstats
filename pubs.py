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
    'sys_arch': ['ASPLOS', 'ISCA', 'MICRO', 'HPCA'],
    'sys_net': ['SIGCOMM', 'NSDI'],
    'sys_sec': ['CCS', 'ACM Conference on Computer and Communications Security', 'USENIX Security', 'USENIX Security Symposium', 'NDSS', 'IEEE Symposium on Security and Privacy'],
    'sys_db': ['SIGMOD Conference', 'VLDB', 'PVLDB', 'Proc. VLDB Endow.', 'ICDE', 'PODS'],
    'sys_design': ['DAC', 'ICCAD'],
    'sys_embed': ['EMSOFT', 'RTAS', 'RTSS'],
    'sys_hpc': ['HPDC', 'ICS', 'SC'],
    'sys_mob': ['MobiSys', 'MobiCom', 'MOBICOM', 'SenSys'],
    'sys_mes': ['IMC', 'Internet Measurement Conference', 'Proc. ACM Meas. Anal. Comput. Syst.'],
    'sys_os': ['SOSP', 'OSDI', 'EuroSys', 'USENIX Annual Technical Conference', 'USENIX Annual Technical Conference, General Track', 'FAST'],
    'sys_pl': ['PLDI', 'POPL', 'ICFP', 'OOPSLA', 'OOPSLA/ECOOP'],
    'sys_se': ['SIGSOFT FSE', 'ESEC/SIGSOFT FSE', 'ICSE', 'ICSE (1)', 'ICSE (2)', 'ASE', 'ISSTA'],
}

CONFERENCES_NUMBER = {
    'sys_arch': {},
    'sys_net': {},
    'sys_sec': {},
    'sys_db': {},
    'sys_design': {},
    'sys_embed': {},
    'sys_hpc': {},
    'sys_mob': {},
    'sys_mes': {},
    'sys_os': {},
    'sys_pl': {'Proc. ACM Program. Lang.' : ['POPL', 'OOPSLA', 'ICFP']},
    'sys_se': {}
}

CONFERENCES_SHORT = {
    'sys_arch': ['ASPLOS', 'ISCA', 'MICRO', 'HPCA'],
    'sys_net': ['SIGCOMM', 'NSDI'],
    'sys_sec': ['CCS', 'USENIX Security', 'NDSS', 'Oakland'],
    'sys_db': ['SIGMOD', 'VLDB', 'ICDE', 'PODS'],
    'sys_design': ['DAC', 'ICCAD'],
    'sys_embed': ['EMSOFT', 'RTAS', 'RTSS'],
    'sys_hpc': ['HPDC', 'ICS', 'SC'],
    'sys_mob': ['MobiSys', 'MobiCom', 'SenSys'],
    'sys_mes': ['IMC', 'SIGMETRICS'],
    'sys_os': ['SOSP', 'OSDI', 'EuroSys', 'USENIX ATC', 'FAST'],
    'sys_pl': ['PLDI', 'POPL', 'ICFP', 'OOPSLA'],
    'sys_se': ['FSE', 'ICSE', 'ASE', 'ISSTA'],
}

AREA_TITLES = {
    'sys_arch': 'Systems: Architecture',
    'sys_net': 'Systems: Networks',
    'sys_sec': 'Systems: Security',
    'sys_db': 'Systems: Databases',
    'sys_design': 'Systems: Design',
    'sys_embed': 'Embedded Systems',
    'sys_hpc': 'Systems: HPC',
    'sys_mob': 'Mobile Systems',
    'sys_mes': 'Systems: Measurements',
    'sys_os': 'Systems: OS',
    'sys_pl': 'Systems: Programming Languages',
    'sys_se': 'Systems: Software Engineering',
    'sys': 'All Areas'
}

class Pub():
    def __init__(self, venue, title, authors, year):
        self.venue = venue
        self.title = title
        self.authors = authors
        self.year = year
        #print('{} {} {} {}\n'.format(authors, year, venue, title))

class Author():
    def __init__(self, name, aux_data):
        self.name = name
        self.years = {}
        self.nr_authors_year = {}
        self.venues = []
        self.normalized_pubs = {}
        self.affiliation, self.homepage, self.scholar = aux_data

    def add_norm_area(self, year, fraction):
        if not year in self.normalized_pubs:
            self.normalized_pubs[year] = 0
        self.normalized_pubs[year] += fraction

    def add_publication(self, venue, year, title, authors):
        if not year in self.years:
            self.years[year] = 0
            self.nr_authors_year[year] = []
        self.years[year] += 1
        self.nr_authors_year[year].append(len(authors))

        if not venue in self.venues:
            self.venues.append(venue)

    def get_total(self):
        return sum(self.years.values())

if __name__ == '__main__':
    print('Nothing to see here, move along...')

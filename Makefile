.PHONY=process topauthors cliques fresh all deploy

all: fresh process
	# updated data and process new data

process: topauthors cliques

topauthors:
	python3 top_authors.py

cliques:
	python3 author_cliques.py

fresh:
	# freshen raw data files (checking timestamps)
	wget -N https://dblp.uni-trier.de/xml/dblp.xml.gz
	wget -N https://dblp.uni-trier.de/xml/dblp.dtd
	#wget -N https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/dblp-aliases.csv
	wget -N https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/csrankings.csv
	mkdir -p pickle
	mkdir -p www
	# get the pickling started
	python3 parse_dblp.py

deploy:
	for i in www/*.html; do \
		echo $$i ; \
		gzip -f -9 -k $$i ; \
	done
	unison -prefer=newer -batch www/ ssh://ghul.albtraum.org/pubstats/

.PHONY=process topauthors cliques fresh all

process: topauthors cliques

topauthors:
	python3 top_authors.py

cliques:
	python3 author_cliques.py

fresh:
	# freshen raw data files (checking timestamps)
	wget -N https://dblp.uni-trier.de/xml/dblp.xml.gz
	wget -N https://dblp.uni-trier.de/xml/dblp.dtd
	wget -N https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/dblp-aliases.csv 
	mkdir -p pickle
	mkdir -p docs
	# get the pickling started
	python3 parse_dblp.py

all: fresh process
	# updated data and process new data
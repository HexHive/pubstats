#!/bin/bash
wget -c https://dblp.uni-trier.de/xml/dblp.dtd
wget -c https://dblp.uni-trier.de/xml/dblp.xml.gz
gunzip dblp.xml.gz
wget -c https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/dblp-aliases.csv
mkdir -p www

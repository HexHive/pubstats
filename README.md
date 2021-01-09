# Publication statistics

This repository establishes simple statistics for a set of conferences.

Using the DBLP data set, we extract the top conferences and then aggregate them
on per-author basis. Based on different sub groups (e.g., security, embedded
systems, or OS) we then calculate per author statistics in a nice overview.

Processing happens in two stages:

* `parse_dblp.py` extracts all publications and dumps them in a pickle files
  based on the per-area aggregation (this is slow as DBLP is a 3GB XML file).
  To be able to process such a large XML file, we use a stream processor that
  simply dumps interesting publications into `Pub` objects (see `pubs.py`).
* `top_authors.py` leverages the pickle files to process per-area statistics
  and aggregate statistics.
* `author_cliques` leverages the pickle files to calculate per-area author
* cliques.


## Using/Howto

* Easy mode: check out the [homepage](https://hexhive.epfl.ch/pubstats/)
* `make all` to download DBLP data, pickle, and create the html data
* `make fresh` to update DBLP data and pickle it
* `make topauthors` to create the top author pages
* `make cliques` to create the cliques


## Contributing

Ideas, comments, or improvements are welcome! Please reach out to
[Mathias Payer](mailto:mathias.payer@nebelwelt.net) to discuss. You can also
reach out to [@gannimo on Twitter](https://www.twitter.com/gannimo).

## Changelog

* 2020-01-09 remove tutorials and short papers (by parsing pages data)
* 2020-01-05 figures for overview page
* 2020-01-04 new overview table across areas
* 2020-01-02 added author cliques
* 2020-12-30 first version with author statistics


## Acknowledgements

This code and page was developed by [Mathias Payer](https://nebelwelt.net),
initially over the 2020 holiday break. The site includes feedback and
suggestions from too many to list, thank you for that!

We use information from [DBLP](https://dblp.org/xml/) and
[CSRankings](https://raw.githubusercontent.com/emeryberger/CSrankings/gh-pages/dblp-aliases.csv)
for anti-aliasing of authors. The idea for the statistics was inspired by
[Davide's Software Security Circus](http://s3.eurecom.fr/~balzarot/notes/top4_2019/).


## License

All data in this repository is licensed under 
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).

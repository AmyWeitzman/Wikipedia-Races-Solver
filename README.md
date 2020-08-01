# Wikipedia-Races-Solver
Simple web scraping program to solve Wikipedia Races given the starting and ending words.

## How to  Run
```
$ python scraper.py Start_Word End_Word
```
* visited URLs will be printed along with their status codes
* once the ending word is reached, the total number of pages scraped will be printed

**NOTE:** program is not fast; as a web scraping courtesy, the program respects a random time delay of 3-10 seconds between requests

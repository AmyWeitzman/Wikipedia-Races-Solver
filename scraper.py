import requests
import sys
from bs4 import BeautifulSoup
import re
import time
import random

class Scraper():
    def  __init__(self):
        self.already_scraped = set()
        self.found_end = False
        self.start_word = ""
        self.end_word = ""
        self.start_url = ""
        self.end_url = ""
        self.frontier = set()
        self.num_urls = 0
        self.num_pages = 0
        self.headers = {
            "User-Agent": "WikiRacer"
        }
    
    def go(self):
        self.get_args()
        self.set_up()
        self.scrape()

    def get_args(self):
        # arguments: filename  start_word  end-word
        # format:   One   Two_words
        if(len(sys.argv) != 3):   # invalid args
            print("Invalid arguments: Must include start_word, endword")
            sys.exit()
        else:
            self.start_word = sys.argv[1]
            self.end_word = sys.argv[2]

    def set_up(self):
        # determine base/end urls
        self.start_url = "https://en.wikipedia.org/wiki/" + self.start_word
        self.end_url = "https://en.wikipedia.org/wiki/" + self.end_word

    def get_rand_delay(self):
        return random.randrange(3, 10, 1)   # add random delay so less likely blocked as bot

    def scrape(self):
        self.frontier = self.get_links(self.start_url)
        time.sleep(self.get_rand_delay())  # web scraping courtesy
        while((not self.found_end) and (len(self.frontier) > 0)):
            self.frontier |= self.get_links(self.frontier.pop())
            time.sleep(self.get_rand_delay())  # web scraping courtesy

    def get_links(self, url):
        res = requests.get(url, headers=self.headers)
        self.num_urls += 1
        self.already_scraped.add(url)
        print(url + ": " + str(res.status_code))
        if(res.status_code != 404):
            self.num_pages += 1
            chunky_soup = BeautifulSoup(res.content, 'html.parser')
            smooth_soup = self.strain_soup(chunky_soup)  
            links_rel = smooth_soup.find_all('a', href=True)  # get all links
            links_abs = set(map(self.format_link, links_rel))  # convert relative links to absolute links
            new_links = links_abs - self.already_scraped
            #page_name = soup.find(id="firstHeading").text
            if(url == self.end_url):  # finished
                self.found_end = True
                print("Done!")
                print("Total number of urls attempted: " + str(self.num_urls))
                print("Total number of pages scraped: " + str(self.num_pages))

        return new_links

    def strain_soup(self, soup):
        # remove div id='mw-panel', div id=mw-head, div class="reflist", div class="sistersitebox", div class="navbox", div class="catlinks", footer
        soup.find('div', id="mw-panel").decompose()
        soup.find('div', id="mw-head").decompose()
        for el in soup.find_all('div', {'class': 'reflist'}): el.decompose()
        for el in soup.find_all('div', {'class': 'sistersitebox'}): el.decompose()
        for el in soup.find_all('div', {'class': 'navbox'}): el.decompose()
        for el in soup.find_all('div', {'class': 'catlinks'}): el.decompose()
        soup.find('footer').decompose()
        # remove link with id='top', href start with #cite-note, a class='image', href  contains "Template", hhref contains Protection_policy, div id=toc, a class='external', href contains "Special"
        soup.find('a', {'id': 'top'}).decompose()
        for el in soup.find_all('a', {'class': 'image'}): el.decompose()
        for el in soup.find_all('a', href=re.compile(".*Template.*")): el.decompose()
        for el in soup.find_all('a', href=re.compile(".*Protection_policy.*")): el.decompose()
        for el in soup.find_all('a', href=re.compile("^#.*")): el.decompose()
        try:
            soup.find('div', id="toc").decompose()
        except AttributeError:
            pass
        for el in soup.find_all('a', {'class': 'external'}): el.decompose()
        for el in soup.find_all('a', href=re.compile(".*Special.*")): el.decompose()

        return soup

    def format_link(self, link): 
        # Wikipedia links format: /wiki/word
        return "https://en.wikipedia.org" + link['href']

if __name__ == "__main__":
    wikiRacer = Scraper()
    wikiRacer.go()



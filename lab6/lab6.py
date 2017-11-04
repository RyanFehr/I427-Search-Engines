import time

import pickle
from bs4 import BeautifulSoup
from heapq import *
import sys as System
import urllib.request
import nltk
import nltk.stem.porter as p
import re
from nltk.corpus import stopwords
import requests

inverted_token_index = dict() # Links word to Integer representing url
url_index = dict() # Links Integer to Url

def generate_seed():
    url = "https://en.wikipedia.org/wiki/Special:Random"
    web_page = urllib.request.urlopen(url)
    contents = web_page.read().decode(errors="replace")
    web_page.close()
    contents = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', contents)
    contents = '\n'.join(contents)
    contents = re.findall('https://en.wikipedia.org/wiki/.*\n', contents)
    contents = contents[0][:-1]
    return contents

def generate_seeds(number_of_seeds):
    seeds = []
    for i in range(0, number_of_seeds):
        url = generate_seed()
        seeds.append(url)
    return seeds

def web_crawl(seeds, page_limit, generation):
    print("Attempting crawl with seeds:\n", seeds)
    url_request_dict = dict()
    url_request_queue = []
    pages_saved = 0

    # Initialize request queue with seeds
    for i in range(0, len(seeds)):
        new_seed = seeds.pop()
        url_request_dict[new_seed] = time.time()
        heappush(url_request_queue, (0, new_seed))

    # Loop over the request queue until empty
    while len(url_request_queue) > 0 and page_limit > pages_saved:
        new_link_node = heappop(url_request_queue) # Get next link to scrape
        current_generation = new_link_node[0] # Determine the link generation
        new_links = get_links_and_index_html(new_link_node[1]) # Get links on this page and index its' content
        for i in range(0, len(new_links)): # Add all linked pages to the queue
            new_link = new_links.pop()
            if new_link not in url_request_dict and current_generation < generation:
                url_request_dict[new_link] = 1
                heappush(url_request_queue, (current_generation + 1, new_link))
        pages_saved += 1
        print("\r"+pages_saved.__str__()+"/"+page_limit.__str__(), end='')
        System.stdout.flush
    print()
    return pages_saved

def get_links_and_index_html(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # Find all pages linked to by this page
    # Grab all hrefs
    raw_links = soup.find_all(href=True)
    # Remove all non /wiki/ hrefs
    raw_links = re.findall('href=[\'"]?(/wiki/[^\'" >]+)', raw_links.__str__())
    # Make relative paths complete
    raw_links = '\nhttps://en.wikipedia.org'.join(raw_links)
    raw_links = "https://en.wikipedia.org" + raw_links
    # Convert links to a list
    raw_links = raw_links.split("\n")


    # Prep page content for indexing
    # Clean Text
    raw_text = soup.find_all('p')
    clean_text = ""
    for paragraph in raw_text:
        clean_text += paragraph.get_text()
    bad_characters = "\\n\\t\\r\")([]{}|<>'"
    replace_char = clean_text.maketrans("", "", bad_characters)
    clean_text = clean_text.translate(replace_char)
    clean_text = ' '.join(clean_text.split())

    # Tokenize and Stem
    clean_text = nltk.word_tokenize(clean_text)
    clean_text = [word for word in clean_text if word not in stopwords.words('english')]
    p_stem = p.PorterStemmer()
    clean_text = [p_stem.stem(word) for word in clean_text]

    # Index url and index tokens
    # Index url
    global url_index
    url_digit = len(url_index)
    url_index[url_digit] = url

    # Index tokens
    global inverted_token_index
    clean_text = list(set(clean_text)) # Remove duplicates
    for i in clean_text:
        if i in inverted_token_index: # If this is not a new word
            if url_digit in inverted_token_index[i]: # If there are multiple occurrences of this word in the page
                inverted_token_index[i][url_digit] = inverted_token_index[i][url_digit] + 1
            else: # If this is the first occurrence of this word on this page
                inverted_token_index[i][url_digit] = 1
        else: # If this is the first occurrence of this word on any page
            inverted_token_index[i] = dict()
            inverted_token_index[i][url_digit] = 1

    return raw_links


def build_engine_indexing():
    seed = ["https://en.wikipedia.org/wiki/Outer_space"]
    web_crawl(seed, 100, 1)

    with open('inverted_token_index.pickle', 'wb') as iti:
        pickle.dump(inverted_token_index, iti)

    with open('url_index.pickle', 'wb') as ui:
        pickle.dump(url_index, ui)

    # for i in inverted_token_index:
    #     inverted_token_index[i] = len(inverted_token_index[i])
    #
    # sorted_index = sorted(inverted_token_index.items(), key=operator.itemgetter(1))
    # for i in sorted_index:
    #     print(i)


def engine_search(search_query):
    global url_index
    url_index_pickle = open('url_index_big.pickle', 'rb')
    url_index = pickle.load(url_index_pickle)

    global inverted_token_index
    inverted_token_index_pickle = open('inverted_token_index_big.pickle', 'rb')
    inverted_token_index = pickle.load(inverted_token_index_pickle)


    search_query = nltk.word_tokenize(search_query)
    search_query = [word for word in search_query if word not in stopwords.words('english')]
    p_stem = p.PorterStemmer()
    search_query = [p_stem.stem(word) for word in search_query]


    for word in search_query:
        print("Query for word " + word)
        if word in inverted_token_index:
            for url in inverted_token_index[word]:
                print(url_index[url] + " mentions " + word)


def main():
    # build_engine_indexing()
    search_query = input("What is your search query? ")
    engine_search(search_query)




main()
import time
import operator

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

inverted_index = dict()

def index_html(filename, url):
    file_in = open(filename, "r", encoding="utf-8")
    content = file_in.read()
    file_in.close()

    # Clean Text
    soup = BeautifulSoup(content, "html.parser")
    text = soup.find_all(text=True)
    text = "".join(text)
    bad_characters = "\\n\\t\\r\")([]{}|<>'"
    replace_char = text.maketrans("", "", bad_characters)
    text = text.translate(replace_char)
    text = ' '.join(text.split())
    # Tokenize and Stem
    # nltk.download()
    text = nltk.word_tokenize(text)
    text = [word for word in text if word not in stopwords.words('english')]
    p_stem = p.PorterStemmer()
    text = [p_stem.stem(word) for word in text]

    # Index results inversely
    global inverted_index
    text = list(set(text))
    for i in text:
        if i in inverted_index:
            inverted_index[i].append(url)
        else:
            inverted_index[i] = url.split()

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

def url_fetch_index_return_links(url):
    web_page = urllib.request.urlopen(url)
    contents = web_page.read().decode(errors="replace")
    web_page.close()
    url = url.replace(".", "")
    url = url.replace("/", "")
    url = url.replace(":", "")
    filename = "./pages/full-" + url + ".html"
    file_out = open(filename, "w", encoding="utf-8")
    file_out.write(contents)
    file_out.close()

    index_html(filename, url)

    contents = re.findall('href=[\'"]?(/wiki/[^\'" >]+)', contents)
    contents = '\nhttps://en.wikipedia.org'.join(contents)
    contents = "https://en.wikipedia.org" + contents

    return contents.split('\n')

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
        new_link_node = heappop(url_request_queue)
        current_generation = new_link_node[0]
        new_links = url_fetch_index_return_links(new_link_node[1])
        for i in range(0, len(new_links)):
            new_link = new_links.pop()
            if new_link not in url_request_dict and current_generation < generation:
                url_request_dict[new_link] = 1
                heappush(url_request_queue, (current_generation + 1, new_link))
        pages_saved += 1
        print("\r"+pages_saved.__str__()+"/"+page_limit.__str__(), end='')
        System.stdout.flush
    print()
    return pages_saved


def main():

    # big_pickle = open('inverted_index_mapping.pickle', 'rb')
    # inverted_index = pickle.load(big_pickle)

    start_time = time.time()
    number_pages_crawled = web_crawl(generate_seeds(1), 10, 1)
    finish_time = (time.time() - start_time)
    print("Crawled %i urls in %.2fs at an average of %.2fs per page" % (number_pages_crawled, finish_time, finish_time/number_pages_crawled))

    # with open('inverted_index_mapping.pickle', 'wb') as m:
    #     pickle.dump(inverted_index, m)


    # for i in inverted_index:
    #     inverted_index[i] = len(inverted_index[i])
    #
    # sorted_index = sorted(inverted_index.items(), key=operator.itemgetter(1))
    # for i in sorted_index:
    #     print(i)

main()
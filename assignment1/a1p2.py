import time
import operator

import pickle
from bs4 import BeautifulSoup
from heapq import *
import sys as System
import urllib.request
import re
from nltk.corpus import stopwords
import requests
import urllib.robotparser as urp
from urllib import parse


def url_fetch_return_links(url, data_directory, url_saved_dict):
    contents = ""
    if 'http://' not in url:
        url = "http://" + url
    original_url = url
    time.sleep(1)
    try:
        rp = urp.RobotFileParser()
        urlp = parse.urlparse(url)
        rp.set_url(urlp[0] + "://" + urlp[1] + "/robots.txt")
        rp.read()
        if rp.can_fetch("*", url):
            authorized_request = urllib.request.Request(url, headers={'User-Agent':'IUB-I427-rfehr'})
            web_page = urllib.request.urlopen(authorized_request)
            contents = web_page.read().decode(errors="replace")
            web_page.close()
            url = url.replace(".", "")
            url = url.replace("/", "")
            url = url.replace(":", "")
            filename = data_directory + "full-" + url + ".html"
            file_out = open(filename, "w", encoding="utf-8")
            file_out.write(contents)
            file_out.close()
            url_saved_dict[original_url] = time.time()
        else:
            return []
    except:
        print("Unable to fetch website", original_url)

    soup = BeautifulSoup(contents, "html.parser")

    # Find all pages linked to by this page
    # Grab all hrefs
    raw_links = set()
    for link in soup.find_all(href=True):
        raw_links.add(link['href'])
    # find all reference hrefs
    absolute_links = '\n'.join(raw_links)
    # print(raw_links)

    absolute_links = re.findall('.*/{2}.*', absolute_links)

    for link in absolute_links:
        raw_links.remove(link)  # Remove absolute links to be left with only relative links

    # Clean up the absolute links
    absolute_links = '\n'.join(absolute_links)
    absolute_links = re.findall('/{2}.*', absolute_links)

    # Remove leading //
    for i in range(len(absolute_links)):
        absolute_links[i] = absolute_links[i][2:]

    # Make relative paths complete
    urlp = parse.urlparse(original_url)
    original_url = urlp[0] + "://" + urlp[1]

    parent = "\n" + original_url
    raw_links = parent.join(raw_links)
    raw_links = original_url + raw_links
    # Convert links to a list
    raw_links = raw_links.split("\n")



    # Add in all the outward linked websites
    for link in absolute_links:
        raw_links.append(link)

    # for link in raw_links:
    #     print(link)

    if raw_links == None:
        raw_links = []
    return raw_links


def save_file_index(url_saved_dict):
    index_list = ""

    for url in url_saved_dict:
        link = url.replace(".", "")
        link = link.replace("/", "")
        link = link.replace(":", "")
        filename =  "full-" + link + ".html"
        index_list = index_list + filename + " " + url + "\n"

    file_out = open("index.dat", "w", encoding="utf-8")
    file_out.write(index_list)
    file_out.close()


def web_crawl_bfs(seeds, page_limit, data_directory):
    print("Attempting crawl with seeds:\n", seeds)
    url_request_dict = dict()
    url_saved_dict = dict()
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
        new_links = url_fetch_return_links(new_link_node[1], data_directory, url_saved_dict)
        for i in range(0, len(new_links)):
            new_link = new_links.pop()
            if new_link not in url_request_dict:
                url_request_dict[new_link] = time.time()
                heappush(url_request_queue, (current_generation + 1, new_link))
        pages_saved += 1
        print("\r"+pages_saved.__str__()+"/"+page_limit.__str__(), end='')
        System.stdout.flush
    print()
    save_file_index(url_saved_dict)
    return pages_saved

def web_crawl_dfs(seeds, page_limit, data_directory):
    print("Attempting crawl with seeds:\n", seeds)
    url_request_dict = dict()
    url_saved_dict = dict()
    url_request_stack = []
    pages_saved = 0
    # Initialize request queue with seeds
    for i in range(0, len(seeds)):
        new_seed = seeds.pop()
        url_request_dict[new_seed] = time.time()
        url_request_stack.append(new_seed)

    # Loop over the request queue until empty
    while len(url_request_stack) > 0 and page_limit > pages_saved:
        new_link_node = url_request_stack.pop()
        new_links = url_fetch_return_links(new_link_node, data_directory, url_saved_dict)
        for i in range(0, len(new_links)):
            new_link = new_links.pop()
            if new_link not in url_request_dict:
                url_request_dict[new_link] = time.time()
                url_request_stack.append(new_link)
        pages_saved += 1
        print("\r"+pages_saved.__str__()+"/"+page_limit.__str__(), end='')
        System.stdout.flush
    print()
    save_file_index(url_saved_dict)
    return pages_saved


def web_crawl(seeds, page_limit, data_directory, search_type):
    if search_type == "DFS":
        return web_crawl_dfs(seeds, page_limit, data_directory)
    if search_type == "BFS":
        return web_crawl_bfs(seeds, page_limit, data_directory)


def main():

    start_time = time.time()
    number_pages_crawled = web_crawl(["http://www.cnn.com"], 100, "./pages/", "BFS")
    finish_time = (time.time() - start_time)
    print("Crawled %i urls in %.2fs at an average of %.2fs per page" % (number_pages_crawled, finish_time, finish_time/number_pages_crawled))

    # url_fetch_return_links("http://www.cnn.com", "./pages/")

main()
from heapq import *
import urllib.request

import re
import time


def url_request_full(url):
    web_page = urllib.request.urlopen(url)
    contents = web_page.read().decode(errors="replace")
    web_page.close()
    url = url.replace(".", "")
    url = url.replace("/", "")
    url = url.replace(":", "")

    filename = "link-" + url + ".txt"
    contents = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', contents)
    contents = '\n'.join(contents)
    file_out = open(filename, "w", encoding="utf-8")
    file_out.write(contents)
    file_out.close()
    # print(url, "links have been saved in", filename)


def url_request(url):
    start_time = time.time()
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
    # print("Processed url in %.2fs" % (time.time() - start_time))
    # print(url, "has been saved in", filename)

    contents = re.findall('href=[\'"]?(/wiki/[^\'" >]+)', contents)
    contents = '\nhttps://en.wikipedia.org'.join(contents)
    contents = "https://en.wikipedia.org" + contents
    # file_out = open(filename, "w", encoding="utf-8")
    # file_out.write(contents)
    # file_out.close()
    # print(url, "links have been saved in", filename)
    return contents.split('\n')


def generate_seeds():
    url_request_full("https://en.wikipedia.org/wiki/Special:Random")
    file_in = open("link-httpsenwikipediaorgwikiSpecialRandom.txt", "r", encoding="utf-8")
    contents = file_in.read()
    contents = re.findall('https://en.wikipedia.org/wiki/.*\n', contents)
    file_in.close()
    contents = contents[0][:-1]
    print(contents, "added as a seed")
    return contents


def web_crawl(seeds, page_limit, generation):
    url_request_dict = dict()
    url_request_queue = []
    pages_saved = 0

    # Initialize request queue with seeds
    for i in range(0, len(seeds)):
        new_seed = seeds.pop()
        url_request_dict[new_seed] = 1
        heappush(url_request_queue, (0, new_seed))

    # Loop over the request queue until empty
    while len(url_request_queue) > 0 and page_limit > 0:
        page_limit -= 1
        new_link_node = heappop(url_request_queue)

        current_generation = new_link_node[0]
        new_links = url_request(new_link_node[1])
        for i in range(0, len(new_links)):
            new_link = new_links.pop()
            if new_link not in url_request_dict and current_generation < generation:
                url_request_dict[new_link] = 1
                heappush(url_request_queue, (current_generation + 1, new_link))
        pages_saved += 1
        # print(pages_saved)
    return pages_saved

def main():
    # seeds = []
    # for i in range(0, 1):
    #     url = generate_seeds()
    #     seeds.append(url)
    # start_time = time.time()
    # number_pages_crawled = web_crawl(seeds, 50, 2)
    # finish_time = (time.time() - start_time)
    # print("Crawled %i urls in %.2fs at an average of %.2fs per page" % (number_pages_crawled, finish_time, finish_time/number_pages_crawled))

    url_request_full("https://www.nytimes.com/2017/09/15/technology/sofi-cagney-scandal.html")

main()

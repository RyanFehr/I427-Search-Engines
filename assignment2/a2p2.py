import time
import pickle
import nltk
import nltk.stem.porter as p
import re

inverted_index = dict()
document_index = dict()
stopwords = set()


# Loads existing pickles if there are available, else it generates new pickles
def load_indexing_data():
    global inverted_index
    global document_index
    global stopwords

    try:
        inverted_index_pickle = open('invindex.pickle', 'rb')
        inverted_index = pickle.load(inverted_index_pickle)
    except FileNotFoundError:
        print("Missing invindex.pickle")

    try:
        document_index_pickle = open('docs.pickle', 'rb')
        document_index = pickle.load(document_index_pickle)
    except FileNotFoundError:
        print("Missing docs.pickle")

    try:
        stopwords_pickle = open('stopwords.pickle', 'rb')
        stopwords = pickle.load(stopwords_pickle)
    except FileNotFoundError:
        print("Missing stopwords.pickle")


def search_engine(mode, search_query, test=False):
    global document_index
    start_time = time.time()
    load_indexing_data()

    search_query = nltk.word_tokenize(search_query)
    search_query = [word for word in search_query if word not in stopwords]
    p_stem = p.PorterStemmer()
    search_query = [p_stem.stem(word) for word in search_query]

    results = set()

    # We union all word results
    if mode.lower() == "or":
        for word in search_query:
            try:
                documents = inverted_index[word]
                for url in documents:
                    results.add(url)
            except KeyError: # No document contains that keyword
                pass
    # We intersect all word results
    elif mode.lower() == "and":
        # Initialize base set of pages
        try:
            documents = inverted_index[search_query[0]]
            for url in documents:
                results.add(url)
        except KeyError:  # No document contains that keyword
            pass

        for word in search_query:
            new_results = set()
            try:
                documents = inverted_index[word]
                for url in documents:
                    new_results.add(url)
                # We intersect them to only keep the ones that are shared
                results = results.intersection(new_results)
            except KeyError: # No document contains that keyword
                pass
    # We store a word count for each url in a dict and return the ones that meet the "most" criteria
    elif mode.lower() == "most":
        results = dict()
        for word in search_query:
            try:
                documents = inverted_index[word]
                for url in documents:
                    if url in results:
                        results[url] = results[url] + 1
                    else:
                        results[url] = 1
            except KeyError: # No document contains that keyword
                pass
        # Filter the results set based on "most" criteria
        most = set()
        for url in results:
            if results[url] >= (len(search_query) / 2):
                most.add(url)
        results = most
    else:
        print("invalid search mode, please choose one of the following modes:\nor\nand\nmost")

    if(not test):
        print("%s results" % len(results))
        print("Searched %s pages in %.2fs seconds" % (len(document_index), (time.time() - start_time)))

        for page in results:
            print("Title: %s  %s" % (document_index[page][0], page))

    return len(results)

def test_search():
    assert(search_engine("or", "baseball meal", test=True) == 2)
    assert(search_engine("and", "like baseball", test=True) == 1)
    assert (search_engine("most", "like baseball", test=True) == 7)

def main():
    test_search()
    search_query = input("What would you like to search for? ")
    mode = input("Search mode: ")
    search_engine(mode, search_query)


main()

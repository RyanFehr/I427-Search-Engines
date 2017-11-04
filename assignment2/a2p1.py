import time
import operator

import pickle

import nltk
from bs4 import BeautifulSoup
import nltk.stem.porter as p
import sys as System
import urllib.request
import re


index_mapping = dict()
inverted_index = dict()
document_index = dict()
stopwords = set()

def load_index_mapping(index_file):
    global index_mapping

    try:
        file_in = open(index_file, "r", encoding="utf-8")
        page = file_in.readline()
        while page != "":
            page = page.split(" ")
            index_mapping[page[0]] = page[1][:-1]
            page = file_in.readline()
        file_in.close()
    except FileNotFoundError:
        print("No index file found with name " + index_file)
        # Build index

def load_stopwords(stopword_file):
    global stopwords

    try:
        file_in = open(stopword_file, "r", encoding="utf-8")
        word = file_in.readline()
        while word != "":
            stopwords.add(word[:-1])
            word = file_in.readline()
        file_in.close()
    except FileNotFoundError:
        print("No stopword file found with name " + stopword_file)
        # Build index

# Returns total words in document and title of document
def build_inverted_index(url, contents):
    global stopwords

    soup = BeautifulSoup(contents, "html.parser")
    title = soup.title
    if title != None:
        title = title.text
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

    # Tokenize
    clean_text = nltk.word_tokenize(clean_text)
    total_words = len(clean_text)

    # Remove stopwords
    clean_text = [word for word in clean_text if word not in stopwords]

    # Stem
    p_stem = p.PorterStemmer()
    clean_text = [p_stem.stem(word) for word in clean_text]

    # Index tokens
    global inverted_index
    for i in clean_text:
        if i in inverted_index:  # If this is not a new word
            documents = inverted_index[i]
            if url in documents: # This words occurs multiple times in this document
                documents[url] = documents[url] + 1
            else: # First occurrence of this word in this document
                documents[url] = 1
        else: # This is a new word
            inverted_index[i] = dict()
            documents = inverted_index[i]
            documents[url] = 1

    return title, total_words

def index_pages(directory, index_file):
    global document_index

    load_index_mapping(index_file)
    load_stopwords("stopwords.txt")

    for page in index_mapping:
        filename = page
        url = index_mapping[page]
        file_in = open(directory + filename, "r", encoding="utf-8")
        contents = file_in.read()
        file_in.close()

        document_info = build_inverted_index(url, contents)

        document_index[url] = document_info # url : (document title, document length)

    save_pickles()


def save_pickles():
    with open('invindex.pickle', 'wb') as ip:
        pickle.dump(inverted_index, ip)
    with open('docs.pickle', 'wb') as dp:
        pickle.dump(document_index, dp)

def load_indexing_data():
    global inverted_index
    global document_index
    try:
        inverted_index_pickle = open('invindex.pickle', 'rb')
        inverted_index = pickle.load(inverted_index_pickle)
        document_index_pickle = open('docs.pickle', 'rb')
        document_index = pickle.load(document_index_pickle)
    except FileNotFoundError:
        index_pages("./pages/", "index.dat")

def main():

    start_time = time.time()
    load_indexing_data()
        
    finish_time = (time.time() - start_time)

main()
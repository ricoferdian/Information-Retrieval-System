import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import sent_tokenize , word_tokenize
import glob
import re
import os
import numpy as np
import sys
import pdfplumber


def finding_all_unique_words_and_freq(words):
    words_unique = []
    word_freq = {}
    for word in words:
        if word not in words_unique:
            words_unique.append(word)
    for word in words_unique:
        word_freq[word] = words.count(word)
    return word_freq


def finding_freq_of_word_in_doc(word, words):
    freq = words.count(word)


def remove_special_characters(text):
    regex = re.compile('[^a-zA-Z0-9\s]')
    text_returned = re.sub(regex, '', text)
    return text_returned


class Node:
    def __init__(self, docId, freq=None):
        self.freq = freq
        self.doc = docId
        self.nextval = None


class SlinkedList:
    def __init__(self, head=None):
        self.head = head

def search_boolean(inputquery, filenames):
    zeroes_and_ones, file_result, new_sentences = boolean_query(inputquery, filenames, True)
    return file_result, new_sentences

def load_documents(preloaded_documents):
    Stopwords = set(stopwords.words('english'))
    dict_global = {}

    files_with_index = {}
    i = 0
    for key, text in preloaded_documents.items():
        text = re.sub(re.compile('\d'), '', text)
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        words = [word for word in words if len(words) > 1]
        words = [word.lower() for word in words]
        words = [word for word in words if word not in Stopwords]
        dict_global.update(finding_all_unique_words_and_freq(words))
        files_with_index[i] = key
        i += 1
    return dict_global, files_with_index

def load_files(filenames):
    Stopwords = set(stopwords.words('english'))
    dict_global = {}

    files_with_index = {}
    i = 0
    for filename in filenames:
        print('opening filename',filename)
        if filename.lower().endswith('.txt'):
            print('opening text file txt')
            fname = filename
            try:
                with open(filename, 'rt', encoding="utf8") as f:
                    print('reading file')
                    text = f.read()

                    text = re.sub(re.compile('\d'), '', text)
                    sentences = sent_tokenize(text)
                    words = word_tokenize(text)
                    words = [word for word in words if len(words) > 1]
                    words = [word.lower() for word in words]
                    words = [word for word in words if word not in Stopwords]
                    dict_global.update(finding_all_unique_words_and_freq(words))
                    # files_with_index[i] = os.path.basename(fname)
                    files_with_index[i] = fname

                    # files_with_index[i] = text
                    i += 1
            except Exception as e:
                print('Terjadi kesalahan dalam membuka file : ',e)
            else:
                print('nggak mau loooo :(')
        elif(filename.lower().endswith('.pdf')):
            print('pdf',filename)
            fname = filename
            with pdfplumber.open(filename) as pdf:
                total_pages = len(pdf.pages)
                # files_with_index[i] = ''
                text = ''
                for page in range(total_pages):
                    print('extracting pdf page ',page)
                    loaded_page = pdf.pages[page]
                    text +=loaded_page.extract_text()

                text = re.sub(re.compile('\d'), '', text)
                sentences = sent_tokenize(text)
                words = word_tokenize(text)
                words = [word for word in words if len(words) > 1]
                words = [word.lower() for word in words]
                words = [word for word in words if word not in Stopwords]
                dict_global.update(finding_all_unique_words_and_freq(words))
                # files_with_index[i] = os.path.basename(fname)
                files_with_index[i] = fname

                    # files_with_index[i] +=loaded_page.extract_text()
                i += 1
    return dict_global, files_with_index

def boolean_query(inputquery, filenames, is_preloaded):
    Stopwords = set(stopwords.words('english'))
    all_words = []
    file_folder = 'data/*'

    if is_preloaded:
        dict_global, files_with_index = load_documents(filenames)
    else:
        dict_global, files_with_index = load_files(filenames)

    unique_words_all = set(dict_global.keys())

    linked_list_data = {}
    for word in unique_words_all:
        linked_list_data[word] = SlinkedList()
        linked_list_data[word].head = Node(1,Node)

    i = 0
    newsentences = {}
    for filename in filenames:
        sentCount = 0
        newsentences[filename] = ""
        print('opening filename',filename)
        if filename.lower().endswith('.txt'):
            print('opening text file txt')
            fname = filename
            try:
                with open(filename, 'rt', encoding="utf8") as f:
                    print('reading file')
                    text = f.read()

                    text = re.sub(re.compile('\d'), '', text)
                    sentences = sent_tokenize(text)
                    for sent in sentences:
                        words = word_tokenize(sent)
                        words = [word for word in words if len(words) > 1]
                        words = [word.lower() for word in words]
                        words = [word for word in words if word not in Stopwords]
                        word_freq_in_doc = finding_all_unique_words_and_freq(words)
                        for word in word_freq_in_doc.keys():
                            linked_list = linked_list_data[word].head
                            if sentCount < 1:
                                newsentences[filename] += "\n"+sent
                                sentCount += 1
                            while linked_list.nextval is not None:
                                linked_list = linked_list.nextval
                            linked_list.nextval = Node(i ,word_freq_in_doc[word])

                    # files_with_index[i] = text
                    i += 1
            except Exception as e:
                print('Terjadi kesalahan dalam membuka file : ',e)
            else:
                print('NGGAK MAU DI PARSING TETEP PAS NYARI FREQ :(')
        elif(filename.lower().endswith('.pdf')):
            print('pdf',filename)
            fname = filename
            with pdfplumber.open(filename) as pdf:
                total_pages = len(pdf.pages)
                # files_with_index[i] = ''
                text = ''
                for page in range(total_pages):
                    print('extracting pdf page ',page)
                    loaded_page = pdf.pages[page]
                    text +=loaded_page.extract_text()

                text = re.sub(re.compile('\d'), '', text)
                sentences = sent_tokenize(text)
                for sent in sentences:
                    words = word_tokenize(sent)
                    words = [word for word in words if len(words) > 1]
                    words = [word.lower() for word in words]
                    words = [word for word in words if word not in Stopwords]
                    word_freq_in_doc = finding_all_unique_words_and_freq(words)
                    for word in word_freq_in_doc.keys():
                        linked_list = linked_list_data[word].head
                        if sentCount < 1:
                            newsentences[filename] += "\n"+sent
                            sentCount += 1
                        while linked_list.nextval is not None:
                            linked_list = linked_list.nextval
                        linked_list.nextval = Node(i ,word_freq_in_doc[word])

                    # files_with_index[i] +=loaded_page.extract_text()
                i += 1
    query = word_tokenize(inputquery)
    connecting_words = []
    cnt = 1
    different_words = []
    for word in query:
        if word.lower() != "and" and word.lower() != "or" and word.lower() != "not":
            different_words.append(word.lower())
        else:
            connecting_words.append(word.lower())
    print('connecting_words',connecting_words)
    total_files = len(files_with_index)

    zeroes_and_ones = []
    zeroes_and_ones_of_all_words = []
    for word in (different_words):
        if word.lower() in unique_words_all:
            zeroes_and_ones = [0] * total_files
            linkedlist = linked_list_data[word].head
            print(word)
            while linkedlist.nextval is not None:
                print('linkedlist.nextval.doc',linkedlist.nextval.doc)
                zeroes_and_ones[linkedlist.nextval.doc - 1] = 1
                linkedlist = linkedlist.nextval
            zeroes_and_ones_of_all_words.append(zeroes_and_ones)
        else:
            print(word, " not found")
            # return
    print('zeroes_and_ones_of_all_words',zeroes_and_ones_of_all_words)
    print('next')
    if(len(connecting_words)):
        for word in connecting_words:
            print('word in connecting words',word)
            word_list1 = zeroes_and_ones_of_all_words[0]
            word_list2 = zeroes_and_ones_of_all_words[1]
            if word == "and":
                bitwise_op = [w1 & w2 for (w1, w2) in zip(word_list1, word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op)
            elif word == "or":
                bitwise_op = [w1 | w2 for (w1, w2) in zip(word_list1, word_list2)]
                zeroes_and_ones_of_all_words.remove(word_list1)
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.insert(0, bitwise_op)
            elif word == "not":
                bitwise_op = [not w1 for w1 in word_list2]
                bitwise_op = [int(b == True) for b in bitwise_op]
                zeroes_and_ones_of_all_words.remove(word_list2)
                zeroes_and_ones_of_all_words.remove(word_list1)
                bitwise_op = [w1 & w2 for (w1, w2) in zip(word_list1, bitwise_op)]
        print('all words')
        zeroes_and_ones_of_all_words.insert(0, bitwise_op)

        print('okay, done word in connecting words')
        files = []
        print(zeroes_and_ones_of_all_words)
        lis = zeroes_and_ones_of_all_words[0]
        cnt = 1
        for index in lis:
            if index == 1:
                files.append(files_with_index[cnt])
            cnt = cnt + 1

        print('files',files)
        return zeroes_and_ones_of_all_words, files, newsentences
    else:
        print('done')
        files = []
        lis = zeroes_and_ones_of_all_words[0]
        cnt = 1
        for index in lis:
            if index == 1:
                files.append(files_with_index[cnt])
            cnt = cnt + 1
        return zeroes_and_ones_of_all_words, files, newsentences

def rank_docs(score_matrix):
    return {k: v for k, v in sorted(score_matrix.items(), key=lambda item: item[1], reverse=True)}

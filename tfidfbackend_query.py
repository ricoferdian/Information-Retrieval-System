
from nltk import sent_tokenize, word_tokenize, PorterStemmer

from prettytable import PrettyTable

import re
import math

import pdfplumber


def search_tf_idf(inputquery, filenames, dictfile):
    print(inputquery, filenames, dictfile)

    texts = {}
    i = 0
    for filename in filenames:
        print('opening filename',filename)
        if filename.lower().endswith('.txt'):
            print('opening text file txt')
            try:
                with open(filename, 'rt', encoding="utf8") as f:
                    print('reading file')
                    text = f.read()
                    texts[i] = text
                    i += 1

            except Exception as e:
                print('Terjadi kesalahan dalam membuka file : ',e)
            else:
                print('nggak mau wkwkwkwkwk')
        elif(filename.lower().endswith('.pdf')):
            print('pdf',filename)
            with pdfplumber.open(filename) as pdf:
                total_pages = len(pdf.pages)
                texts[i] = ''
                for page in range(total_pages):
                    print('extracting pdf page ',page)
                    loaded_page = pdf.pages[page]
                    texts[i] +=loaded_page.extract_text()
                i += 1

    print('opening dict', dictfile)
    with open(dictfile, 'rt') as f:
        dictionary = f.read()

    # inputquery = 'andi raja hutan siswa indonesia'
    queries = word_tokenize(inputquery)
    print(queries)

    return hitung_tf_idf(texts, queries, dictionary)

def remove_special_characters(text):
    regex = re.compile('[^a-zA-Z0-9\s]')
    text_returned = re.sub(regex, '', text)
    return text_returned

def hitung_tf_idf(texts, queries, dictionary):
    text_sentences = {}
    i = 0
    for text in texts.values():
        text = remove_special_characters(text)
        text_sentences[i] = sent_tokenize(text)
        i += 1
    #hitung total dokumen
    total_documents = len(texts)
    #hitung matriks tf idf
    tf_matrix = term_in_documents_frequency(text_sentences, dictionary, queries)
    #menghitung df
    df_matrix = calc_document_frequency(tf_matrix, queries)
    #menghitung d/df
    ddf_matrix = calc_ddf_matrix(total_documents, df_matrix)
    #menghitung matriks idf dan idf+1
    idf_matrix, idf_matrix_plus = calc_idf_matrix(ddf_matrix)
    #menghitung matriks w
    W_matrix = calc_W_matrix(tf_matrix, idf_matrix_plus)
    #menghitung bobot dokumen
    doc_score_matrix = scoring_matrix(W_matrix)
    print('doc_score_matrix',doc_score_matrix)
    rank = rank_docs(doc_score_matrix)
    print('rank',rank)
    #print tabel hasil di terminal
    print_tabel_hasil(text_sentences, doc_score_matrix, total_documents, tf_matrix, df_matrix, ddf_matrix, idf_matrix,
                      idf_matrix_plus, W_matrix, queries)
    return rank

def print_tabel_hasil(text_sentences, doc_score_matrix, total_documents, tf_matrix, df_matrix, ddf_matrix, idf_matrix, idf_matrix_plus, W_matrix, queries):
    headers = ['Query']
    rows_before = ['', '', '', '']
    for num in range(total_documents):
        rows_before += ['']
        headers = headers + ['t' + str(num + 1)]
    headers = headers + ['df', 'D\df', 'IDF', 'iDF+1']
    for num in range(total_documents):
        headers = headers + ['W' + str(num + 1)]
    t = PrettyTable(headers)
    for query in queries:
        row = [query]
        for tf in tf_matrix.values():
            if query in tf.keys():
                row += [tf[query]]
            else:
                row += ['0']
        if query in df_matrix.keys():
            row += [df_matrix[query], ddf_matrix[query], round(idf_matrix[query], 4), round(idf_matrix_plus[query], 4)]
        for W in W_matrix.values():
            if query in W.keys():
                row += [round(W[query], 4)]
            else:
                row += ['0']
        t.add_row(row)
    row = []
    for docnum in text_sentences.keys():
        row += [round(doc_score_matrix[docnum], 4)]
    rows_before += ['TOTAL']
    t.add_row(rows_before + row)
    print(t)

def term_in_documents_frequency(text_sentences, dict, queries):
    frequency_matrix = {}
    stemmer = PorterStemmer()
    for docnum, sentences in text_sentences.items():
        freq_table = {}
        for sent in sentences:
            words = word_tokenize(sent)
            for word in words:
                word = word.lower()
                word = stemmer.stem(word)
                if word in dict:
                    continue
                if word in queries:
                    if word in freq_table:
                        freq_table[word] += 1
                    else:
                        freq_table[word] = 1
        frequency_matrix[docnum] = freq_table

    return frequency_matrix

def calc_document_frequency(tf_matrix, queries):
    df_matrix = {}
    for query in queries:
        count = 0
        for f_table in tf_matrix.values():
            if query in f_table.keys():
                count+=1
        df_matrix[query] = count

    return df_matrix

def calc_ddf_matrix(d,df_matrix):
    ddf_matrix = {}
    for word,count in df_matrix.items():
        ddf_matrix[word] = d/(count+1)
    return ddf_matrix

def calc_idf_matrix(ddf_matrix):
    idf_matrix = {}
    idf_matrix_plus = {}

    for word, count in ddf_matrix.items():
        if (count != 0):
            idf_matrix[word] = math.log10(count)
            idf_matrix_plus[word] = idf_matrix[word] + 1
        else:
            idf_matrix[word] = 0

    return idf_matrix, idf_matrix_plus

def calc_W_matrix(tf_matrix, idf_matrix):
    W_matrix = {}

    for docnum, f_table in tf_matrix.items():
        freq_table = {}
        for word, count in f_table.items():
            if word in idf_matrix.keys():
                freq_table[word] = count * idf_matrix[word]
        W_matrix[docnum] = freq_table

    return W_matrix

def scoring_matrix(W_matrix):
    scoring_matrix = {}

    for docnum, f_table in W_matrix.items():
        score = 0
        for word, count in f_table.items():
            score += count
        scoring_matrix[docnum] = score

    return scoring_matrix

def rank_docs(score_matrix):
    return {k: v for k, v in sorted(score_matrix.items(), key=lambda item: item[1], reverse=True)}
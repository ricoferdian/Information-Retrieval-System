
from nltk import sent_tokenize, word_tokenize, PorterStemmer

from prettytable import PrettyTable

import re
import math

import pdfplumber

import vectorspacemodelbackend_query as vsm
def search_tf_idf_preloaded(inputquery, preloaded_documents, dictfile, vsm_algorithm):
    texts = {}
    i = 0
    for key, value in preloaded_documents.items():
        print("value",value)
        texts[i] = value
        i += 1
    return search(texts, inputquery, dictfile, vsm_algorithm)

def search(texts, inputquery, dictfile, vsm_algorithm):
    print('opening dict', dictfile)
    with open(dictfile, 'rt') as f:
        dictionary = f.read()
    # inputquery = 'andi raja hutan siswa indonesia'
    queries = word_tokenize(inputquery)
    print(queries)

    return hitung_tf_idf(texts, queries, dictionary, vsm_algorithm)

def search_tf_idf(inputquery, filenames, dictfile, vsm_algorithm):
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
    return search(texts, inputquery, dictfile, vsm_algorithm)

def remove_special_characters_multi(texts):
    newtexts = []
    for text in texts:
        regex = re.compile('[^a-zA-Z0-9\s]')
        newtext = re.sub(regex, '', text)
        newtexts.append(newtext)
    return newtexts

def remove_special_characters(text):
    regex = re.compile('[^a-zA-Z0-9\s]')
    text_returned = re.sub(regex, '', text)
    return text_returned

def hitung_tf_idf(texts, queries, dictionary, vsm_algorithm):
    text_sentences = {}
    i = 0
    for text in texts.values():
        text_sentences[i] = sent_tokenize(text)
        print("text_sentences[i]",text_sentences[i])
        text_sentences[i] = remove_special_characters_multi(text_sentences[i])
        print("text_sentences[i]",text_sentences[i])
        i += 1
    #hitung total dokumen
    total_documents = len(texts)
    if (vsm_algorithm is not None):
        #cari term berkaitan dalam satu kalimat. VSM butuh ini
        queries, token_frequency, found_sentences, fit_queries = get_linked_term_in_documents(text_sentences, dictionary, queries)
        #hitung matriks tf
        tf_matrix = term_in_documents_frequency(text_sentences, dictionary, queries)
        #menghitung df
        df_matrix = calc_document_frequency(tf_matrix, queries)
        #menghitung d/df
        ddf_matrix = calc_ddf_matrix(total_documents, df_matrix)
        #menghitung matriks idf dan idf+1
        idf_matrix, idf_matrix_plus = calc_idf_matrix(ddf_matrix)
        #menghitung matriks w
        W_matrix = calc_W_matrix(tf_matrix, idf_matrix_plus)
        #cari matriks w dari token
        W_token_matrix = calc_W_token_matrix(token_frequency, idf_matrix_plus)
        #menghitung bobot dokumen
        doc_score_matrix = scoring_matrix(W_matrix)
        print('doc_score_matrix',doc_score_matrix)
        #print tabel hasil di terminal
        print_tabel_hasil(text_sentences, doc_score_matrix, total_documents, tf_matrix, df_matrix, ddf_matrix, idf_matrix,
                          idf_matrix_plus, W_matrix, queries, token_frequency, W_token_matrix)
        if (vsm_algorithm is 'dice'):
            new_doc_score_matrix = vsm.getVectorSpaceModel(queries, W_token_matrix,W_matrix, 'dice')
        else:
            new_doc_score_matrix = vsm.getVectorSpaceModel(queries, W_token_matrix,W_matrix, 'cosine')
        rank = rank_docs(new_doc_score_matrix)
        print('rank', rank)
    else:
        #cari term berkaitan dalam satu kalimat. VSM butuh ini
        unused, token_frequency, found_sentences, fit_queries = get_linked_term_in_documents(text_sentences, dictionary, queries)
        #hitung matriks tf
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
        #print tabel hasil di terminal
        print_tabel_hasil(text_sentences, doc_score_matrix, total_documents, tf_matrix, df_matrix, ddf_matrix, idf_matrix,
                          idf_matrix_plus, W_matrix, queries, None, None)
        rank = rank_docs(doc_score_matrix)
        print('rank', rank)
    return rank, found_sentences, fit_queries

def print_tabel_hasil(text_sentences, doc_score_matrix, total_documents, tf_matrix, df_matrix, ddf_matrix, idf_matrix, idf_matrix_plus, W_matrix, queries, token_frequency,W_token_matrix):
    headers = ['Query']
    print("token_frequency",token_frequency)
    print("W_token_matrix",W_token_matrix)
    rows_before = ['', '', '', '']
    if token_frequency is not None:
        headers = headers + ['Q']
        rows_before += ['']
    for num in range(total_documents):
        rows_before += ['']
        headers = headers + ['t' + str(num + 1)]
    headers = headers + ['df', 'D\df', 'IDF', 'iDF+1']
    if W_token_matrix is not None:
        rows_before += ['']
        headers = headers + ['WQ']
    for num in range(total_documents):
        headers = headers + ['W' + str(num + 1)]
    t = PrettyTable(headers)
    for query in queries:
        row = [query]

        if token_frequency is not None:
            if query in token_frequency.keys():
                row += [token_frequency[query]]
            else:
                row += ['0']

        for tf in tf_matrix.values():
            if query in tf.keys():
                row += [tf[query]]
            else:
                row += ['0']

        if query in df_matrix.keys():
            row += [df_matrix[query], ddf_matrix[query], round(idf_matrix[query], 4), round(idf_matrix_plus[query], 4)]

        if W_token_matrix is not None:
            if query in W_token_matrix.keys():
                row += [round(W_token_matrix[query], 4)]
            else:
                row += ['0']

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

def get_linked_term_in_documents(text_sentences, dict, queries):
    stemmer = PorterStemmer()
    newquery = []
    token_frequency = {}
    newsentences = {}
    fitqueries = {}
    for docnum, sentences in text_sentences.items():
        sentCount = 0
        fitqueries[docnum] = ""
        newsentences[docnum] = ""
        for sent in sentences:
            words = word_tokenize(sent)
            for word in words:
                word = word.lower()
                word = stemmer.stem(word)
                if word in dict:
                    continue
                if word in queries:
                    if word not in fitqueries[docnum]:
                        fitqueries[docnum] += word+", "
                    if word in token_frequency:
                        token_frequency[word] += 1
                    else:
                        token_frequency[word] = 1
                    if sentCount < 2:
                        newsentences[docnum] += "\n"+sent
                        sentCount += 1
                    for new_word in words:
                        new_word = remove_special_characters(new_word)
                        if new_word is None:
                            continue
                        new_word = new_word.lower()
                        new_word = stemmer.stem(new_word)
                        if not any(new_word in s for s in newquery) and new_word not in dict:
                            newquery.append(new_word)
    return newquery, token_frequency, newsentences, fitqueries

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

def calc_W_token_matrix(tf_matrix, idf_matrix):
    freq_table = {}

    for word, count in tf_matrix.items():
        if word in idf_matrix.keys():
            freq_table[word] = count * idf_matrix[word]

    return freq_table

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
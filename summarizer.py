from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from nltk import sent_tokenize, word_tokenize

import re
import math

def main():
    text,dict = openfile()
    parag_sent_count, total_documents = tokenize_parag(text)
    # sentences = sent_tokenize(text)
    # total_documents = len(sentences)
    # frequency_matrix = _create_frequency_matrix(sentences,dict)
    # tf_matrix = calc_tf_matrix(frequency_matrix)
    # word_per_doc_table = word_freq_in_doc(frequency_matrix)
    # idf_matrix = calc_idf_matrix(frequency_matrix, word_per_doc_table, total_documents)
    # tf_idf_matrix = calc_tf_idf_matrix(tf_matrix, idf_matrix)
    # sentence_value = sentences_scoring(tf_idf_matrix)
    # average_score = sentences_average_score(sentence_value)
    # summary = create_summary(sentences, sentence_value, average_score)
    # print(summary)


def summarize(text,dict):
    sentences = sent_tokenize(text)
    total_documents = len(sentences)
    frequency_matrix = _create_frequency_matrix(sentences, dict)
    tf_matrix = calc_tf_matrix(frequency_matrix)
    word_per_doc_table = word_freq_in_doc(frequency_matrix)
    idf_matrix = calc_idf_matrix(frequency_matrix, word_per_doc_table, total_documents)
    tf_idf_matrix = calc_tf_idf_matrix(tf_matrix, idf_matrix)
    sentence_value = sentences_scoring(tf_idf_matrix)
    average_score = sentences_average_score(sentence_value)
    summary = create_summary(sentences, sentence_value, average_score)
    return summary

def openfile():
    with open('D:\\Libraries\\Tugas\\NLP\\cerita 3.txt', 'rt') as f:
        text = f.read()
    with open('D:\\Libraries\\Tugas\\NLP\\kamus stopword indonesia 2.txt', 'rt') as f:
        dict = f.read()
    return text, dict

def summarizeParag(parag, dict, total_documents):
    sentences = sent_tokenize(parag)
    frequency_matrix = _create_frequency_matrix(sentences, dict)
    tf_matrix = calc_tf_matrix(frequency_matrix)
    word_per_doc_table = word_freq_in_doc(frequency_matrix)
    idf_matrix = calc_idf_matrix(frequency_matrix, word_per_doc_table, total_documents)
    tf_idf_matrix = calc_tf_idf_matrix(tf_matrix, idf_matrix)
    sentence_value = sentences_scoring(tf_idf_matrix)
    average_score = sentences_average_score(sentence_value)
    summary = create_summary(sentences, sentence_value, average_score)
    return summary

def tokenize_parag(text):
    num = 0
    total_documents = 0
    parag_sent_count = {}
    paragraph = text.split('\n')
    while (num < len(paragraph)):
        parag = sent_tokenize(paragraph[num])
        parag_sent_count[num] = len(parag)
        total_documents += parag_sent_count[num]
        num += 1
    return parag_sent_count, total_documents

def _create_frequency_matrix(sentences,dict):
    frequency_matrix = {}
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    for sent in sentences:
        freq_table = {}
        words = word_tokenize(sent)
        for word in words:
            word = word.lower()
            word = stemmer.stem(word)
            removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", word)
            if word in dict:
                continue

            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1

        frequency_matrix[sent[:15]] = freq_table

    return frequency_matrix


def calc_tf_matrix(freq_matrix):
    tf_matrix = {}

    for sent, f_table in freq_matrix.items():
        tf_table = {}

        count_words_in_sentence = len(f_table)
        for word, count in f_table.items():
            tf_table[word] = count / count_words_in_sentence

        tf_matrix[sent] = tf_table

    return tf_matrix


def word_freq_in_doc(freq_matrix):
    word_per_doc_table = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in word_per_doc_table:
                word_per_doc_table[word] += 1
            else:
                word_per_doc_table[word] = 1

    return word_per_doc_table


def calc_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}

        for word in f_table.keys():
            # Belum ada validasi jika log10(1)
            idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

        idf_matrix[sent] = idf_table

    return idf_matrix


def calc_tf_idf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}

    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}

        for (word1, value1), (word2, value2) in zip(f_table1.items(),
                                                    f_table2.items()):
            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[sent1] = tf_idf_table

    return tf_idf_matrix


def sentences_scoring(tf_idf_matrix) -> dict:
    sentenceValue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0

        count_words_in_sentence = len(f_table)
        for word, score in f_table.items():
            total_score_per_sentence += score

        if (count_words_in_sentence != 0):
            sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence
        else:
            sentenceValue[sent] = 0

    return sentenceValue

def sentences_average_score(sentenceValue) -> int:
    if (len(sentenceValue) == 0):
        average = 0
    else:
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]
        average = (sumValues / len(sentenceValue))

    return average

def create_summary(sentences, sentenceValue, threshold):
    sentence_count = 0
    summary = ''

    # for sentence in sentences:
    #     if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (threshold):
    #         summary += " " + sentence
    #         sentence_count += 1

    for sentence in sentences:
        if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (threshold):
            summary += " " + sentence
            sentence_count += 1

    return summary

if __name__ == "__main__":
    main()
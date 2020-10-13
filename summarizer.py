from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

from nltk import sent_tokenize, word_tokenize

import re
import math


def main():
    text, dict = openfile()
    sentences, total_sentences_in_doc = parag_tokenizer(text)
    frequency_matrix = word_in_sentence_frequency(sentences, dict)
    tf_matrix = calc_tf_matrix(frequency_matrix)
    word_freq_in_doc = oneword_freq_in_doc(frequency_matrix)
    idf_matrix = calc_idf_matrix(frequency_matrix, word_freq_in_doc, total_sentences_in_doc)
    tf_idf_matrix = calc_tf_idf_matrix(tf_matrix, idf_matrix)
    sentence_scores = sentences_scoring(tf_idf_matrix)
    average_score = sentences_average_score(sentence_scores)
    average_score = sentences_parag_average_score(sentence_scores)
    summary = create_summary_byparag(sentences, sentence_scores, average_score)
    print(summary)


def summarize(text, dict):
    sentences, total_sentences_in_doc = parag_tokenizer(text)
    frequency_matrix = word_in_sentence_frequency(sentences, dict)
    tf_matrix = calc_tf_matrix(frequency_matrix)
    word_freq_in_doc = oneword_freq_in_doc(frequency_matrix)
    idf_matrix = calc_idf_matrix(frequency_matrix, word_freq_in_doc, total_sentences_in_doc)
    tf_idf_matrix = calc_tf_idf_matrix(tf_matrix, idf_matrix)
    sentence_scores = sentences_scoring(tf_idf_matrix)
    average_score = sentences_average_score(sentence_scores)
    average_score = sentences_parag_average_score(sentence_scores)
    summary = create_summary_byparag(sentences, sentence_scores, average_score)
    print(summary)
    return summary

def parag_tokenizer(text):
    paragraph = text.split('\n')
    num = 0
    total_sentences_in_doc = 0
    sentences = []
    while (num < len(paragraph)):
        parag_sentences = sent_tokenize(paragraph[num])
        sentences.append(parag_sentences)
        total_sentences_in_doc += len(parag_sentences)
        num += 1
    return sentences, total_sentences_in_doc

def openfile():
    with open('D:\\Libraries\\Tugas\\NLP\\cerita 3.txt', 'rt') as f:
        text = f.read()
    with open('D:\\Libraries\\Tugas\\NLP\\kamus stopword indonesia 2.txt', 'rt') as f:
        dict = f.read()
    return text, dict


def word_in_sentence_frequency(parag, dict):
    parag_matrix = {}
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    parag_num = 0
    for sentences in parag:
        frequency_matrix = {}
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
        parag_matrix[parag_num] = frequency_matrix
        parag_num += 1

    return parag_matrix


def calc_tf_matrix(freq_matrix):
    parag_matrix = {}
    parag_num = 0
    for freq_sentences in freq_matrix.values():
        tf_matrix = {}
        for sent, f_table in freq_sentences.items():
            tf_table = {}

            count_words_in_sentence = len(f_table)
            for word, count in f_table.items():
                tf_table[word] = count / count_words_in_sentence

            tf_matrix[sent] = tf_table
        parag_matrix[parag_num] = tf_matrix
        parag_num += 1

    return parag_matrix

def oneword_freq_in_doc(freq_matrix):
    word_per_doc_table = {}
    for freq_sentences in freq_matrix.values():
        for f_table in freq_sentences.values():
            for word, count in f_table.items():
                if word in word_per_doc_table:
                    word_per_doc_table[word] += 1
                else:
                    word_per_doc_table[word] = 1

    return word_per_doc_table


def calc_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    parag_matrix = {}
    parag_num = 0
    for freq_sentences in freq_matrix.values():
        idf_matrix = {}
        for sent, f_table in freq_sentences.items():
            idf_table = {}
            for word in f_table.keys():
                idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

            idf_matrix[sent] = idf_table
        parag_matrix[parag_num] = idf_matrix
        parag_num += 1
    return parag_matrix


def calc_tf_idf_matrix(tf_matrix, idf_matrix):
    parag_matrix = {}
    parag_num = 0
    for (parag_table1), (parag_table2) in zip(tf_matrix.values(), idf_matrix.values()):

        tf_idf_matrix = {}
        for (sent1, f_table1), (f_table2) in zip(parag_table1.items(), parag_table2.values()):
            tf_idf_table = {}

            for (word1, value1), (value2) in zip(f_table1.items(),
                                                 f_table2.values()):
                tf_idf_table[word1] = float(value1 * value2)

            tf_idf_matrix[sent1] = tf_idf_table
        parag_matrix[parag_num] = tf_idf_matrix
        parag_num += 1

    return parag_matrix


def sentences_scoring(tf_idf_matrix):
    parag_matrix = {}
    parag_num = 0
    for freq_sentences in tf_idf_matrix.values():
        sentenceValue = {}
        for sent, f_table in freq_sentences.items():
            total_score_per_sentence = 0

            count_words_in_sentence = len(f_table)
            for word, score in f_table.items():
                total_score_per_sentence += score

            if (count_words_in_sentence != 0):
                sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence
            else:
                sentenceValue[sent] = 0
        parag_matrix[parag_num] = sentenceValue
        parag_num += 1

    return parag_matrix


def sentences_average_score(sentenceValue):
    for freq_sentences in sentenceValue.values():
        if (len(freq_sentences) == 0):
            average = 0
        else:
            sumValues = 0
            for entry in freq_sentences:
                sumValues += freq_sentences[entry]
            average = (sumValues / len(freq_sentences))

    return average


def sentences_parag_average_score(sentenceValue):
    parag_average = {}
    for parag, freq_sentences in sentenceValue.items():
        if (len(freq_sentences) == 0):
            parag_average[parag] = 0
        else:
            sumValues = 0
            for entry in freq_sentences:
                sumValues += freq_sentences[entry]
            parag_average[parag] = (sumValues / len(freq_sentences))

    return parag_average


def create_summary(parag, sentenceValues, threshold):
    sentence_count = 0
    summary = ''
    for (sentences), (sentenceValue) in zip(parag, sentenceValues.values()):
        sent_parag_added = 0
        for sentence in sentences:
            if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (threshold) and sent_parag_added < 2:
                summary += "" + sentence
                sentence_count += 1
                sent_parag_added += 1

    return summary


def create_summary_byparag(parag, sentenceValues, threshold):
    sentence_count = 0
    summary = ''
    for (sentences), (sentenceValue), (average) in zip(parag, sentenceValues.values(), threshold.values()):
        sent_parag_added = 0
        for sentence in sentences:
            if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (average) and sent_parag_added < 2:
                summary += "" + sentence
                sentence_count += 1
                sent_parag_added += 1

    return summary


if __name__ == "__main__":
    main()

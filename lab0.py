# encoding: utf-8
import string
import os
import sys
import re
import csv
import numpy as np
from decimal import *
def process_book(file_name):
    f = open(file_name,'r')
    book = f.read().decode('utf-8')
    f.close()
    punct = string.punctuation +  u"“‘’--ʺ”"

    end_string = "End of the Project Gutenberg EBook of Heart of Darkness, by Joseph Conrad"
    endex = book.find(end_string)
    book = book[:endex]
    begin_string = "The Nellie, a cruising yawl," 
    begdex = book.find(begin_string)
    #book = book[begdex-4:]


    i=0;
    length = len(book)
    while (i <length):
        
        if book[i] in punct:
            #only remove an apostrophe if it isnt part of a contraction 
            if (book[i] ==u'’' and book[i+1].isalnum()):
                pass
            else:
                book = book[:i] +" "+ book[i+1:]
        i+=1
       
    book = string.upper(book)
    book_li = string.split(book)

    return book_li


def construct_ngram(book, n):
    """book is a string here"""
    grams = []
    for i in range(len(book)-(n-1)):
        buf = ""
        k = 0
        while(k<n):
            buf += book[i+k]
            if k != n-1:
                buf += "|"
            k +=1
        grams.append(buf)
    return grams

def ngram_stat(book):
    """book here is a list"""
    count = {};
    for ngram in book:
        #token_list = for 
        if ngram in count:
            count[ngram] += 1
        else:
            count[ngram] = 1    
    return count 


def generate_csv(book, n):
    """book is a dictionary"""
    outputfile = ("%d-gramFrequency.csv" % n)
    f = open(outputfile, 'w')
    
    freq  = book.items()
    for obj in freq:
        f.write(obj[0].encode('utf-8') + "," + str(obj[1]) + '\n')

def create_freqcsv(token_list, n):
    ngram_list = construct_ngram(token_list, n)
    freq_dict = ngram_stat(ngram_list)
    generate_csv(freq_dict, n)

def gen_norm_probs(ngrams):
    """ ngrams is a dict of the ngrams with their frequencies as values"""
    Vocab = len(ngrams)
    ngram_prob = {}
    tokens_sum = 0
    for item in ngrams:
        tokens_sum += ngrams[item]    
    for item in ngrams:
        ngram_prob[item] = float(ngrams[item])/float(tokens_sum)
    return ngram_prob

def context_prob(probs, context, n):
    """word = previous word context
    probs = dictionary of normalzied probs
    n refers to n gram"""
    nthword_prob = {}
    #we have we want to get
    word = context.split("|")
    for item in probs:
        ngram = item.split("|")
        given = ngram[:n-1]
        if word == given:
            nthword_prob[ngram[-1]] = probs[item]
    return gen_norm_probs(nthword_prob)

def pump_out(norm_ngram):
    """nor_ngram = a dictionary full of potential words for the given context"""

    nthwords = []
    probs = []
    for item in norm_ngram:
        nthwords.append(item)
        probs.append(norm_ngram[item])

    sample = np.random.multinomial(1, probs, 1)
    for i in range(len(sample[0])):
        if sample[0][i] == 1:
            return nthwords[i]


def gen_sentence(words, n, uni, bi, tri):
    """ words is length of sentence > 6
    uni, bi, tri are all normalized dictionaries
    n order of ngram"""
    sent = []
    
    for i in range(words):
        if i == 0 or n == 1:
            sent.append(pump_out(uni))
        elif i == 1 or n == 2:
            sent.append(pump_out(context_prob(bi, sent[i-1], 2)))
        else:
            sent.append(pump_out(context_prob(tri, sent[i-2] + "|" +  sent[i-1], 3)))

    return " ".join(sent) + "."

def main():
    book = process_book("HoD.txt")
    i = 1
    while( i < 4):
        create_freqcsv(book, i)
        i+=1


    unigram_list = construct_ngram(book, 1)
    uni_freq = ngram_stat(unigram_list)
    unigram_probs = gen_norm_probs(uni_freq)

    bigram_list = construct_ngram(book, 2)
    bi_freq = ngram_stat(bigram_list)
    bigram_probs = gen_norm_probs(bi_freq)
    
    trigram_list = construct_ngram(book, 3)
    tri_freq = ngram_stat(trigram_list)
    trigram_probs = gen_norm_probs(tri_freq)
   
    with  open("sentences.txt", 'w') as f:
        for i in range(1,4):
            for k in range(6,11): 
                f.write((gen_sentence(k, i, unigram_probs, bigram_probs, trigram_probs)).encode('utf-8')+ "\n")
            f.write("\n")

if __name__ == "__main__":
    main()

"""n = 2
    gram_list = construct_ngram(book, 2)
    for ent in gram_list:
        print(ent)
    freq = ngram_stat(gram_list)
    generate_csv(freq, n)
    generate_csv(freq, 1)
    generate_csv(freq, 3)"""

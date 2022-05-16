import os
import io
import numpy
from pathlib import Path
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import nltk
import ntpath
from nltk.stem import PorterStemmer
ps = PorterStemmer()
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
directory = '/Users/wise/Documents/Diss Files'

#Returns Text from PDF
def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    if text:
        return text

#Returns names in text
def name_finder(text):
    name_set = set()
    tokens = nltk.word_tokenize(text.lower())
    tagged = nltk.pos_tag(tokens)
    tree = nltk.chunk.ne_chunk(tagged)
    for t in tree:
        if hasattr(t, 'label'):
            if t.label() == "PERSON" or "LOCATION" or "GPE":
                c = 0
                while c < len(t):
                    name_set.add(t[c][0])
                    c += 1
    return name_set

#Filter Noise out of Text (punctuation, single letters, common noise)
def filter_speak(text):
    stop_words = set(stopwords.words("english"))
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    token_text = tokenizer.tokenize(text)
    names = name_finder(text)
    noise = {"__", "know", "like", "discounts", "latest", "iphones", "androids", "six", "gigs", "data", "puretalk", "makeup", "fabiola", "christina", "assistant", "jessica", "uh", "um", 'dailywire', 'com', 'subscribe', "month", "50", "one", "yeah", "daily", "wire", "copyright", "well", "ben", "associate", "bradford", "carrington", "editing", "adam", "audio", "mixed", "mike", "coromina", "hair", "listening", "shapiro", "promo", "code", "bench", "podcast", "radio", "show", "executive", "supervising", "producer", "production", "manager", "mathis", "glover", "jeremy", "boring", "pavo"}
    filtered_speak = []
    for word in token_text:
        if word.casefold() not in stop_words:
            if word.casefold() not in noise:
                if word not in names and len(word) > 1:
                    filtered_speak.append(word) #can also use ps.stem(word) in here
    return filtered_speak

#Filter Noise out of Text (punctuation, single letters, common noise)
def filter_4chan(text):
    stop_words = set(stopwords.words("english"))
    tokenizer = nltk.RegexpTokenizer(r"\w+")
    token_text = tokenizer.tokenize(text)
    names = name_finder(text)
    noise = {"REPLY", "POST", "quotelink", "class", "https", "http"}
    filtered_speak = []
    for word in token_text:
        if word.casefold() not in stop_words:
            if word.casefold() not in noise:
                if word not in names and len(word) > 1:
                    filtered_speak.append(ps.stem(word)) #can also use ps.stem(word) in here
    return filtered_speak

def most_common(word_list):
    c = Counter(word_list)
    return c.most_common(50)

def ngrams_gen(word_list, n):
    grams = [word_list[i:i+n] for i in range(len(word_list) - n+1)]
    gram_list = []
    for gram in grams:
        gram_list.append(str(gram))
    return gram_list

#Look for website changes and export string from updated website
def keyword_finder(directory):
    all_the_words = []
    content = []
    for file in os.scandir(directory):
        file_name, file_extension = os.path.splitext(file)
        if file_extension == ".txt":
            with open(file) as f:
                f_name = ntpath.basename(file).split(".")[0]
                #author_name = f_name.split(" - ", 2)[0]
                #text_name = f_name.split(" - ", 2)[1]
                #content.append([author_name, text_name])
                #print('--- {0} by {1} ---'.format(text_name, author_name))
                content.append([f_name])
                print('--- {0} ---'.format(f_name))
                lines = filter_4chan(f.read())
                all_the_words = [*all_the_words, *lines]
    keywords = most_common(all_the_words)
    two_word_phrases = most_common(ngrams_gen(all_the_words, 2))
    three_word_phrases = most_common(ngrams_gen(all_the_words, 3))
    four_word_phrases = most_common(ngrams_gen(all_the_words, 4))
    print("--- most common single words ---")
    print(keywords)
    print("--- most common two word phrases ---")
    print(two_word_phrases)
    print("--- most common three word phrases ---")
    print(three_word_phrases)
    print("--- most common four word phrases ---")
    print(four_word_phrases)

def keyword_snippet_extractor(directory, keywords):
    content = []
    for file in os.scandir(directory):
        file_name, file_extension = os.path.splitext(file)
        if file_extension == ".txt":
            with open(file) as f:
                f_name = ntpath.basename(file).split(".")[0]
                # author_name = f_name.split(" - ", 2)[0]
                # text_name = f_name.split(" - ", 2)[1]
                # print('--- {0} by {1} ---'.format(text_name, author_name))
                print('--- {0} ---'.format(f_name))
                file_text = word_tokenize(f.read())
                file_text = [y for x in file_text for y in x.split('-')]
                for word in keywords:
                    position = [i for i, x in enumerate(file_text) if x == word]
                    for pos in position:
                        #noise = {"__", "like", "uh", "um", "one", "yeah", "ukraine", "putin", "gas", "inflation", "russia", "russians", "ukrainians"}
                        noise = {}
                        snippet_list = [w for w in file_text[pos-5:pos+25] if w not in noise]
                        snippet = ' '.join(snippet_list)
                        print(snippet)
                        content.append([f_name, pos, word, snippet])
                        #content.append([author_name, text_name, pos, word, snippet])
    return content

def keyphrase_snippet_extractor(directory, keyphrase):
    content = []
    keyphrase_list = [kp.split() for kp in keyphrase]
    for file in os.scandir(directory):
        file_name, file_extension = os.path.splitext(file)
        if file_extension == ".txt":
            with open(file) as f:
                f_name = ntpath.basename(file).split(".")[0]
                author_name = f_name.split(" - ", 2)[0]
                text_name = f_name.split(" - ", 2)[1]
                print('--- {0} by {1} ---'.format(text_name, author_name))
                file_text = word_tokenize(f.read())
                file_text = [y for x in file_text for y in x.split('-')]
                for phrase in keyphrase_list:
                    for word in phrase:
                        if word != phrase[-1]:
                            position = [i for i, x in enumerate(file_text) if x == word]
                            for pos in position:
                                noise = {"__", "like", "uh", "um", "one", "yeah"}
                                snippet = [w for w in file_text[pos - 5:pos + 25] if w not in noise]
                                if snippet[(snippet.index(word) + 1)] == phrase[(phrase.index(word)) + 1]:
                                    snippet_string = (' '.join(snippet))
                                    content.append([author_name, text_name, pos, (' '.join(phrase)), snippet_string])
    return(content)

def csv_gen():
    keyphrase = ["social media"]
    keyword = ["culture"]
    #df = pd.DataFrame(keyphrase_snippet_extractor(directory, keyphrase), columns=['author', 'content name', 'position', 'phrase', 'snippet'])
    df = pd.DataFrame(keyword_snippet_extractor(directory, keyword), columns=['author', 'content name', 'position', 'phrase', 'snippet'])
    df.to_csv("keywords.csv")

def line_counter(directory):
    counter = 0
    for file in os.scandir(directory):
        file_name, file_extension = os.path.splitext(file)
        if file_extension == ".txt":
            with open(file) as f:
                nonempty_lines = [line.strip("\n") for line in f if line != "\n"]
                print(len(nonempty_lines))
                keywords = {"white", "black", "jew", "kike", "nigger"}
                for keyword in keywords:
                    keyword_lines = [line for line in nonempty_lines if keyword in line.split()]
                    counter += len(keyword_lines)
    print(counter)

#line_counter(directory)
#keyword_finder(directory)
keywords = ["cynical"]
keyword_snippet_extractor(directory, keywords)
keyphrase = ["free speech", "freedom of speech"]
#keyphrase_snippet_extractor(directory, keyphrase)
#csv_gen()

#keyphrase snippet extractor notes:
#load this sucka up with loads of data
#produce the CSV and finish coding it
#write like a bat out of hell
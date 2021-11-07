import math
import json
import ast

import numpy as np
import pandas as pd


from sklearn.metrics.pairwise import cosine_similarity

from nltk import sent_tokenize, word_tokenize,WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, SnowballStemmer 

from os.path import exists



def word_preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [word.replace("'","") for word in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if not word in stopwords.words("italian")]
    map(lambda word: SnowballStemmer(word),tokens)
    return tokens

def compute_vector(inverted_index,local_tfidf):
    vector = np.zeros(len(inverted_index))
    i = 0
    for key in inverted_index:
        try:
            vector[i] = local_tfidf[key]
        except:
            pass
        finally:
            i+=1
    return vector

def cosine_similarity__(query,inverted_index,idf,tfidf):
    final_results = []
    tokens = word_preprocess(query)
    # query TFIDF
    local_tfidf = {}
    for token in tokens:
        if token not in local_tfidf:
            try:
                local_tfidf[token] = 1 / len(tokens) * idf[token]
            except:
                local_tfidf[token] = 0
        else:
            local_tfidf[token] = (local_tfidf[token] + 1) / len(tokens) * idf[token]
    # actual similarity
    query_vector = compute_vector(inverted_index,local_tfidf)
    for index, row in df.iterrows():
        print("Cosine Similarity computing: "+str("{:.2f}".format(index/(len(df)-1) *100)) + "%",end="\r")
        doc_vector = compute_vector(inverted_index,tfidf[index])
        assert(len(doc_vector) == len(query_vector) == len(inverted_index))
        sim = np.dot(query_vector, doc_vector)/(np.linalg.norm(query_vector,2)*np.linalg.norm(doc_vector,2))
        final_results.append([index,sim])
        
    return final_results



inverted_index = {}
tf             = {}
idf            = {} 
tfidf          = {}

query = "Programmatore"

lemma = WordNetLemmatizer()
snowball = SnowballStemmer("italian")


df = pd.read_csv("jobs.txt",delimiter='\t',names = ["title","desc","loc","time","href"])

print("Dataset Loaded")


# Check if precomputed files exist
if(not exists("inverted_index.txt") or not exists("tfidf.txt")or not exists("idf.txt")):
    
    df["tok"] = df.apply(lambda row: word_tokenize((row["desc"]+row["title"]).lower()),axis = 1)
    
    # If they do not exist compute everything from scratch
    for index, row in df.iterrows():
        
        local_tf = {}

        print("Document analysis: "+str("{:.2f}".format(index/(len(df)-1) *100)) + "%",end="\r")
        
        tokens = row['tok']
        tokens = [word.replace("'","") for word in tokens]
        tokens = [word for word in tokens if word.isalpha()]
        tokens = [word for word in tokens if not word in stopwords.words("italian")]
        map(lambda word: SnowballStemmer(word),tokens)
        
        
        for token in tokens:
            # Inverted Index
            if token not in inverted_index:
                inverted_index[token] = [[index],1]
            else:
                index_list = inverted_index[token][0]
                if index not in index_list:
                    inverted_index[token][0].append(index)
                inverted_index[token][1] +=  1
            # TF
            if token not in local_tf:
                local_tf[token] = 1 / len(tokens)
            else:
                local_tf[token] = (local_tf[token] + 1) / len(tokens) 
                
        
        tf[index] = local_tf
        
        row["tok"] = tokens
        
    # IDF
    for key in inverted_index:
        idf[key] = math.log10(len(df)/len(inverted_index[key][0]))
    # TFIDF
    for index in tf:
        local_tfidf = {}
        local_tf = tf[index]
        for k in local_tf:
            local_tfidf[k] = local_tf[k] * idf[k]
        tfidf[index] = local_tfidf
    
    # Save on file
    with open('inverted_index.txt', 'w') as convert_file:
        convert_file.write(json.dumps(inverted_index))
    with open('idf.txt', 'w') as convert_file:
        convert_file.write(json.dumps(idf))
    with open('tfidf.txt', 'w') as convert_file:
        convert_file.write(json.dumps(tfidf))
else:
    # If files exist load from file
    with open('inverted_index.txt', 'r') as convert_file:
        contents       = convert_file.read()
        inverted_index = ast.literal_eval(contents)
    with open('idf.txt', 'r') as convert_file:
        contents       = convert_file.read()
        idf          = ast.literal_eval(contents)
    with open('tfidf.txt', 'r') as convert_file:
        contents       = convert_file.read()
        tfidf_         = ast.literal_eval(contents)
        tfidf          = {}
        for key in tfidf_:
            tfidf[int(key)] = tfidf_[key]



mah_cosine = cosine_similarity__(query,inverted_index,idf,tfidf)

sorted_res = sorted(mah_cosine, key = lambda item: item[1],reverse=True)[:20]

print()
print()
print("query: "+query)
print()
print()

print("######### MY RESULTS ##############")
for item in sorted_res:
    print("title: " + df.iloc[item[0],0]+ " score(similarity): "+ str(item[1]))
    #print("href: "+ df.iloc[item[0],4])




####################### TENSORFLOW LIB ############################################
from sklearn.feature_extraction.text import TfidfVectorizer

v = TfidfVectorizer(stop_words={'italian'},smooth_idf=False)
x = v.fit_transform(df['title']+df['desc'])

query_vec = v.transform([query])
results = cosine_similarity(x,query_vec)

print()
print()
print("######### TENSORFLOW RESULTS ##############")

for i in results.argsort(axis=0)[-20:][::-1]:
     print("title: " + df.iloc[item[0],0]+ " score(similarity): "+ str(results[i][0][0]))
#################################################################################

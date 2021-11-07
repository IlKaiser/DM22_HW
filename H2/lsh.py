import string
import hashlib
import math
import time

import numpy as np

four_bytes = 2**32-1

class Shingles:
    def create_shingles(self,document,k):
        result = []
        for i in range(len(document) - k  + 1):
            a = document[i:i + k]
            result.append(a)
        return result



class MinHash:
    
    def hashFamily(self,i):
        # Implement a family of hash functions. It hashes strings and takes an
        # integer to define the member of the family.
        # Return a hash function parametrized by i
        resultSize = 12 # how many bytes we want back
        maxLen = 20 # how long can our i be (in decimal)
        salt = str(i).zfill(maxLen)[-maxLen:].encode("utf-8")
        def hashMember(x):
            return hashlib.sha1(x + salt).digest()[-resultSize:]
        return hashMember
    
    def create_hash_shingles(self,shingles):
        h_s = []
        # four-byte hash shingles
        for shingle in shingles:
            h_s.append(hashlib.sha1(shingle.encode("utf-8")).digest()[-4:])
        return h_s
    
    
    # The set is actually a dict
    def minhash_signature_matrix_from_set(self,set_,n_hash):
        signatures = []
        for key in set_:
            print("Signatures: "+str("{:.2f}".format(key/(len(set_)-1) *100)) + "%",end="\r")
            items = set_[key]
            signature = []
            # for every hash we compute the minhash signature
            # per document, then we merge them to create
            # signature matrix
            for i in range(0,n_hash):
                min_hash = four_bytes.to_bytes(4, 'little')
                for item in items:
                    curr_hash = self.hashFamily(i)(item)
                    if(curr_hash < min_hash):
                        min_hash = curr_hash
                signature.append(min_hash)
            signatures.append(signature)
        return signatures


class LSH:
    
    def lsh_candidates(self,signature_matrix,r,b):
        # Analize minhash signature for b and r
        #assert r == int(len(signature_matrix[0])/b)
        hashes = []
        for i in range(0,len(signature_matrix)):
            for j in range(0,len(signature_matrix[i]),r):
                concat = b''
                for k in range(j,min(j+r,len(signature_matrix[i]))):
                    concat += signature_matrix[i][k]
                hash_ = hashlib.sha1(concat).digest()[-4:]
                hashes.append([hash_,i,j])
                
        #print(hashes)
        print("Hashes Done!")
        print()
        
        # Check similarites
        candidates = []
        for item1 in hashes:
            for item2 in hashes:
                if(item1[0]==item2[0] and item1[2]==item2[2] and item1 != item2):
                    if([item1[1],item2[1]] not in candidates and [item2[1],item1[1]] not in candidates):
                        candidates.append([item1[1],item2[1]])
        return candidates
                
            
    
def jaccard_sim(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
   
    union = s1.union(s2)
    intersection = s1.intersection(s2)
    
    return len(intersection)/len(union)
    
    
s  = Shingles()
mh = MinHash()
lsh = LSH()


# Test on actual data

import pandas as pd


df = pd.read_csv("jobs.txt",delimiter='\t',names = ["title","desc","loc","time","href"])


jobs = {}

time_s = time.time()
for index, row in df.iterrows():
    print("Shingles: "+str("{:.2f}".format(index/(len(df)-1) *100)) + "%",end="\r")
    jobs[index] = mh.create_hash_shingles(s.create_shingles((row["title"]+row["desc"]).lower().strip(),10))
time_shingles = time.time() - time_s

print()
time_mh = time.time()
signatures = mh.minhash_signature_matrix_from_set(jobs,20)
time_minhash = time.time()-time_mh
print()

print("Lsh")
print()
time_l = time.time()
cnd = lsh.lsh_candidates(signatures,20,int(2712/20))
time_lsh = time.time() - time_l

final_js=[]
for item in cnd:
    js = jaccard_sim(jobs[item[0]],jobs[item[1]])
    if(js >= 0.8):
        final_js.append([item[0],item[1],js])
                     
sorted_res = sorted(final_js, key = lambda item: item[2],reverse=True)[:20]


print("#########Final res ##############")

for item in sorted_res:
    print("title1: " + df.iloc[item[0],0]+" title2: "+df.iloc[item[1],0]+" score(similarity): "+ str(item[2]))

print("Brute force")
bf = []
cnt = 0
time_b = time.time()
for key1 in jobs:
    for key2 in jobs:
        print("Brute force similarity: "+str("{:.9f}".format(cnt/(len(jobs)**2-1) * 100)) + "%",end="\r")
        if(key1!=key2):
            js = jaccard_sim(jobs[item[0]],jobs[item[1]])
            if(js >= 0.8):
                bf.append([item[0],item[1],js])
        cnt += 1

time_bruteforce = time.time() - time_b
sorted_res = sorted(bf, key = lambda item: item[2],reverse=True)[:20]
print("#########Final res (brute force)##############")

for item in sorted_res:
    print("title1: " + df.iloc[item[0],0]+" title2: "+df.iloc[item[1],0]+" score(similarity): "+ str(item[2]))


def intersection_(l1,l2):
    int_c = 0
    for item in l1:
        if item in l2:
            int_c += 1
    return int_c
print()
print()
print("##############   REPORT ######################")

print("Total LSH candidates  found: " +str(len(cnd)))
print("Total LSH matches found: " +str(len(final_js)))
print("Total brute force matches found: " +str(len(bf)))
print("Intersection : " +str(intersection_(final_js,bf)))

print()
print("Elapsed times: ")

print("Shingles time: "+ str(time_shingles))
print("Min Hash time: "+ str(time_minhash))
print("LSH time: "+ str(time_lsh))
print("Brute Force similarites time: "+ str(time_bruteforce))

print("MinHash + LSH is "+str(time_bruteforce/(time_minhash+time_lsh)) +" times faster than brute force")

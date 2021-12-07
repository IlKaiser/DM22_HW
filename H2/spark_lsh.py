import pyspark
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import monotonically_increasing_id,desc,col

import hashlib
import unicodedata
import time

# Dear old four bytes limit
four_bytes = 2**32-1

# Dear old hashFamily
def hashFamily(i):
        # Implement a family of hash functions. It hashes strings and takes an
        # integer to define the member of the family.
        # Return a hash function parametrized by i
        resultSize = 12 # how many bytes we want back
        maxLen = 20 # how long can our i be (in decimal)
        salt = str(i).zfill(maxLen)[-maxLen:].encode("utf-8")
        def hashMember(x):
            return hashlib.sha1(x + salt).digest()[-resultSize:]
        return hashMember

sc = pyspark.SparkContext("local[*]")

spark = SparkSession.builder.appName("lsh").config("spark.driver.memory", "8g").getOrCreate()

# Import Data
txt = spark.read.option("delimiter", "\t").csv("jobs.txt",header=False)
data = txt.toDF('title', 'desc', 'local','time','href')

data_i = data.withColumn("index", monotonically_increasing_id())
data_i.show(5)

# k-Shingles (Our case 10-shingle)

def create_shingles(document,k):
        result = []
        for i in range(len(document) - k  + 1):
            a = document[i:i + k]
            result.append(unicodedata.normalize("NFKD",a.lower().strip()))
        return result

ksh = data.rdd.map(lambda row: create_shingles(row.title+row.desc,10)).map(lambda x: Row(x)).flatMap(list).zipWithIndex().toDF(['shingles','index'])

ksh.show(5)

## hash - shingles
def create_hash_shingles(shingles):
        h_s = []
        # four-byte hash shingles
        for shingle in shingles:
            h_s.append(hashlib.sha1(shingle.encode("utf-8")).digest()[-4:])
        return h_s

print("Hash signatures...")
h_ksh = ksh.rdd.map(lambda row: create_hash_shingles(row.shingles)).map(lambda x: Row(x)).flatMap(list).zipWithIndex().toDF(['h_shingles','id'])
print("Hash signatures done!")
#h_ksh.show(5)

# Min Hash Signature
def minhash_signature_matrix_column(shingles,n_hash):
        items = shingles
        
        # for every hash we compute the minhash signature
        # per document, then we merge them to create
        # signature matrix
        signature = []
        for i in range(0,n_hash):
            min_hash = four_bytes.to_bytes(4, 'little')
            
            for item in items:
                curr_hash = hashFamily(i)(item)
                if(curr_hash < min_hash):
                    min_hash = curr_hash
            signature.append(min_hash)
        return signature

print("Signature matrix...")
signature_matrix = h_ksh.rdd.map(lambda row: minhash_signature_matrix_column(row.h_shingles,10)).map(lambda x: Row(x)).flatMap(list).zipWithIndex().toDF(['signatures','id'])

time_m = time.time()
smm = signature_matrix.collect()
time_minhash = time.time() - time_m

print("Signature matrix done!")
#signature_matrix.show(5)


# LSH

og_signature_matrix = signature_matrix.rdd.map(lambda row: row.signatures).collect()


def lsh_candidates(signature_matrix,r,b):
        # Analize minhash signature for b and r
        #assert r == int(len(signature_matrix[0])/b)
        hashes = []
        for i in range(0,len(signature_matrix)):
            for j in range(0,len(signature_matrix[i]),r):
                concat = b''
                #print("j: "+str(j))
                for k in range(j,min(j+r,len(signature_matrix[i]))):
                    #print(i,k)
                    concat += signature_matrix[i][k]
                hash_ = hashlib.sha1(concat).digest()[-4:]
                hashes.append([hash_,i,j])
                
        #print(hashes)
        #print("Hashes Done!")
        #print()
        
        # Check similarites
        candidates = []
        for item1 in hashes:
            for item2 in hashes:
                if(item1[0]==item2[0] and item1[2]==item2[2] and item1 != item2):
                    if([item1[1],item2[1]] not in candidates and [item2[1],item1[1]] not in candidates):
                        candidates.append([item1[1],item2[1]])
        return candidates

print("LSH...")
time_l = time.time()
cnd  = lsh_candidates(og_signature_matrix,10,int(2712/20))
time_lsh = time.time() -time_l
cnd_20 = cnd[:20]
print("LSH done!")


def jaccard_sim(l1,l2):
    s1 = set(l1)
    s2 = set(l2)
    
    union = s1.union(s2)
    intersection = s1.intersection(s2)
    
    return len(intersection)/len(union)





final_js=[]

ksh.persist()
ksh.count()
cntr = 0
for item in cnd:
    
    print("lsh similarity: "+str("{:.9f}".format(cntr/(len(cnd)-1) * 100)) + "%",end="\r")
    one = ksh.filter(ksh.index == item[0]).select("index","shingles").collect()[0]['shingles']
        
    two = ksh.filter(ksh.index == item[1]).select("index","shingles").collect()[0]['shingles']
    js = jaccard_sim(one,two)
    if(js >= 0.8):
        final_js.append([item[0],item[1],js])
    cntr += 1

sorted_res = sorted(final_js, key = lambda item: item[2],reverse=True)[:20]
print()
print("Final res:")

data_i.persist()
data_i.count()

for item in sorted_res:
    print("title1: " + data_i.filter(data_i.index == item[0]).select("title").collect()[0]['title']
     +" title2: "+data_i.filter(data_i.index == item[1]).select("title").collect()[0]['title']
    +" score(similarity): "+ str(item[2]))


print("Elapsed times: ")

print("Total LSH candidates found: " +str(len(cnd)))
print("Hit: "+ str(len(final_js))+" (of 2965)")


print("Min Hash time: "+ str(time_minhash))
print("LSH time: "+ str(time_lsh))


print("Brute force")
ksh1 = ksh.alias('ksh1')
ksh2 = ksh.alias('ksh2')

joint = ksh1.join(ksh2, ksh1.index != ksh2.index, 'outer').toDF('sh1','id1','sh2','id2')


#joint.persist()
#joint.count()

joint = joint.rdd.map(lambda x: (x["sh1"], x["id1"],x["sh2"], x["id2"], jaccard_sim(x["sh1"],x["sh2"]))).toDF(['sh1','id1','sh2','id2','sim'])

joint = joint.filter(joint.sim > 0.8)
joint = joint.orderBy('sim',ascending=False)
joint.collect()

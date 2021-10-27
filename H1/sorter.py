import re
import pandas as pd
import numpy as np

occurrences = {}

uniques = []

i = 0
num_lines = sum(1 for line in open('beers.txt'))
with open("beers.txt","r") as rows:    
    for row in rows:
        print(str("{:.10f}".format(i/num_lines *100)) + "%",end="\r")
        name = row.strip().split('\t')[0]
        #name = re.sub(r'&#40;(?<=&#40;)(.*)(?=&#41;)&#41;', '', name)
        reviews =  int(row.strip().split('\t')[1])
        
        flag = False
        to_pop = ""
        
        if(name not in occurrences):
            occurrences[name] = [reviews,1]
        else:
            occurrences[name][0] += reviews
            occurrences[name][1] += 1
        i+=1
        
            


print("Bash correction: ")
print(sorted(occurrences.items(), key=lambda item: item[1][1],reverse=True)[:10])
print()




def filter_dict(dict_):
    print()
    print("Dict size before pruning (less than 100 reviews): "+str(len(dict_)))
    to_remove = []
    for key in dict_:
        if(dict_[key][1]<100):
            to_remove.append(key)
    for key in to_remove:
        dict_.pop(key)
        
    print("Dict size after pruning: "+str(len(dict_)))
    print()



    to_be_sorted = {}

    for key in dict_:
        to_be_sorted[key]=dict_[key][0]/dict_[key][1]


    print("Top 10:")

    sorted_list = sorted(to_be_sorted.items(), key=lambda item: item[1],reverse=True)[:10]

    for item in sorted_list:
        print(item[0]+' '+str(item[1]))
    

filter_dict(occurrences)




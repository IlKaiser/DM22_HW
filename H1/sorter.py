occurrences = {}

with open("beers.txt","r") as rows:
    for row in rows:
        name = row.strip().split('\t')[0]
        reviews =  int(row.strip().split('\t')[1])
        
        if(name not in occurrences):
            occurrences[name] = [reviews,1]
        else:
            occurrences[name][0] += reviews
            occurrences[name][1] += 1
        
to_remove = []

print("Bash correction: ")
print(sorted(occurrences.items(), key=lambda item: item[1][1],reverse=True)[:10])
print()

print("Dict size before pruning (less than 100 reviews): "+str(len(occurrences)))

for key in occurrences:
    if(occurrences[key][1]<100):
        to_remove.append(key)
for key in to_remove:
    occurrences.pop(key)
    
print("Dict size after pruning: "+str(len(occurrences)))
print()


to_be_sorted = {}

for key in occurrences:
    to_be_sorted[key]=occurrences[key][0]/occurrences[key][1]


print("Top 10:")

sorted_list = sorted(to_be_sorted.items(), key=lambda item: item[1],reverse=True)[:10]

for item in sorted_list:
    print(item[0]+' '+str(item[1]))

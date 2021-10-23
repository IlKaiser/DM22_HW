from bs4 import BeautifulSoup
import re

from requests import Session


URL = "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/"
header = "https://www.kijiji.it"

visited = []
jobs = []


s = Session()
page = s.get(URL)
soup = BeautifulSoup(page.content, "html5lib")
n_jobs = soup.find("h2",class_="page-hed").text.strip()

a = 0 

def crawl(url):
    global a
    visited.append(url)
    
    page = s.get(url)
    soup = BeautifulSoup(page.content, "html5lib")
        
    print(url)
    
    for li in soup.findAll("li",class_="item"):
        if(li != None and li.find("span",class_="flag-YELLOW") is None):
            for item in li.findAll("div",class_="item-content"):
                title       = item.find("a", class_="cta").text.strip()
                desc        = item.find("p",class_="description").text.strip().replace("\n"," ")[0:149]
                locale      = item.find("p",class_="locale").text.strip()
                timestamp   = item.find("p",class_="timestamp").text.strip()
                href        = item.find("a", class_="cta").attrs.get("href")
                quintuple   = [title,desc,locale,timestamp,href]
                if(quintuple not in jobs):
                    jobs.append(quintuple)
        else:
                a+=1
                title       = item.find("a", class_="cta").text.strip()
                desc        = item.find("p",class_="description").text.strip().replace("\n"," ")
                locale      = item.find("p",class_="locale").text.strip()
                timestamp   = item.find("p",class_="timestamp").text.strip()
                href        = item.find("a", class_="cta").attrs.get("href")
                quintuple   = [title,desc,locale,timestamp,href]
                if(quintuple not in jobs):
                    jobs.append(quintuple)
            


    results = soup.findAll("span")
    
    for span in results:
        got_url = span.attrs.get("data-href")
        if( got_url != None and re.match("/offerte-di-lavoro\/offerta\/informatica-e-web\/*",got_url) ):
            if((header + got_url) not in visited):
                crawl(header + got_url)


crawl(URL)

print("Found " + str(len(jobs)) + " job offerings of "+n_jobs)
print("of which the sponsored ads are: " + str(a))

with open("jobs.txt","w") as jobs_txt:
    for job in jobs:
        jobs_txt.write(job[0]+'\t'+job[1]+'\t'+job[2]+'\t'+job[3]+'\t'+job[4]+'\n')


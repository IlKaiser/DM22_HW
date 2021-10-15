from bs4 import BeautifulSoup
import re

from requests import Session
import threading



s = Session()
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
                         'AppleWebKit/537.36 (KHTML, like Gecko) '\
                         'Chrome/75.0.3770.80 Safari/537.36'}
# Add headers
s.headers.update(headers)

URL = "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/"
header = "https://www.kijiji.it"

visited = []
jobs = []
lock = threading.Lock()


def crawl(url):
    
    visited.append(url)
    
    page = s.get(url)
    soup = BeautifulSoup(page.content, "html5lib")

    print(url)
    
    for li in soup.findAll("li",class_="item"):
        if(li != None and li.find("span",class_="flag-YELLOW") is None):
            for item in li.findAll("div",class_="item-content"):
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

print(len(jobs))
with open("jobs.txt","w") as jobs_txt:
    for job in jobs:
        jobs_txt.write(job[0]+'\t'+job[1]+'\t'+job[2]+'\t'+job[3]+'\t'+job[4]+'\n')

import sqlite3
import requests
from bs4 import BeautifulSoup

import utils

def get_meta_score(page = 1,max = 1000):
    meta_list = []
    count = 0
    # headers to prevent 403 denial
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(f"https://www.metacritic.com/browse/games/release-date/available/ios/metascore?page={page}",
    headers = headers)
    # save json for each page scrapped
    # utils.create_json(response.json(),'meta',f'page{page}')
    soup = BeautifulSoup(response.text,'html.parser')
    # findall tables with app and scores
    tables = soup.find_all("table",{"class":"clamp-list"})
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            # skip empty rows "tr":"spacer":(only process a-tag with class=title)
            if count < max:
                if row.find("a",{"class":"title"}):
                    name = row.find("a",{"class":"title"}).find("h3").get_text()
                    # reject 'HD' versions of a game
                    if 'HD' not in name:
                        name = utils.clean_name(name)
                        score = row.find("a",{"class":"metascore_anchor"}).get_text().replace("\n","")
                        meta_list.append((name,score))
                        count += 1 # increase counter for grading option
            else:
                break # esc loop if max num is reacheds
    utils.insert_meta_data(meta_list)
    print(f"{len(meta_list)} apps scrapped metascore on page {page}")
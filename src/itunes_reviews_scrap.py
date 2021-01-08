import time
import json
import requests
import csv

import utils

def review_url(app_id,page=1,country='us'):
    return f'https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json'

def create_fail_review():
    """ create text file storing app failed the search """
    txt = open('data/fail_review.txt','w')
    txt.close()
    # print('fail review list created')

def add_fail_review(name,app_id,reason):
    with open('data/fail_review.txt','a') as txt:
        txt.write(f'{name},{app_id},{reason}\n')
    # print(f'App:{name} add to fail list; Reason:{reason}')

def get_itunes_review(name,app_id,page):
    """ get and store itunes API search result in json """
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(review_url(app_id,page,"us"))
    if response.ok: # API working
        js = response.json()
        try: # save raw review json
            utils.create_json(js,'review',f'{name}_{page}')
        except:
            add_fail_review(name, app_id,'json error')
            print(f'Failed to store json for app: {name}; ID: {app_id}')
            return False
        if 'entry' in js['feed'].keys():
            return js['feed']['entry']
        else:
            print(f'Empty result after:{review_url(app_id,page)}')
            return False
    else: # API failed
        add_fail_review(name,app_id,f'API failure')
        print(f"API Request Error:{response}; SLEEP FOR 70s")
        time.sleep(70) # when API rejects, sleep for 70s
        print(f'RESTART search for {name}')
        return get_itunes_review(name,app_id,page)

def store_itunes_review(name_list,id_list,total_page,max_per_page=50):
    create_fail_review() # create fail txt for future
    """ itunes RSS API freq: 20 inquries/min """
    max_count, inqury_count, pointer = 0, 0, 0
    while pointer < len(name_list):
        name = name_list[pointer]
        app_id = id_list[pointer]
        for page in range(1, total_page+1):
            if inqury_count >= 19: # sleep for 1min every 19 inqury
                time.sleep(61)
                inqury_count = 0
            try:
                reviews = get_itunes_review(name,app_id,page) # get 50 reviews from each page
                inqury_count += 1
            except Exception as e: # unexpected failure(should never happen)
                print(f'Unexpected failure for {name} at page: {page}; /nError:{e}')
                reviews = False
            if reviews:
                if isinstance(reviews,(dict)): # single review is given as a single dict
                    review_info = (
                        name,app_id,reviews['im:rating']['label'],reviews['title']['label'],reviews['content']['label'],
                        reviews['im:voteSum']['label'],reviews['im:voteCount']['label']
                        )
                    utils.insert_itunes_review(review_info)
                elif isinstance(reviews,(list)): # multiple reviews are stored in list
                    for review in reviews:
                        if max_count < max_per_page: # limit total review count for grading
                            review_info = (
                                name,app_id,review['im:rating']['label'],review['title']['label'],review['content']['label'],
                                review['im:voteSum']['label'],review['im:voteCount']['label']
                            )
                            utils.insert_itunes_review(review_info)
                            max_count += 1
                        else: 
                            max_count = 0
                            break
            else: # move to next app when current app review is empty
                break
        pointer += 1
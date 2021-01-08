import time
import json
import requests
import csv

import utils

def search_url(name, country = 'us'):
    name = name.replace(" ","+") # itunes API requires replace from space to "+"
    # limit search results to 2
    return f'https://itunes.apple.com/search?term={name}&country={country}&entity=software&limit=2'

def create_fail():
    """ create text file storing app failed the search """
    txt = open('data/fail_list.txt','w')
    txt.close()
    # print('fail list created')

def add_fail(name,reason):
    with open('data/fail_list.txt','a') as txt:
        txt.write(f'{name},{reason}\n')
    # print(f'App:{name} add to fail list; Reason:{reason}')

def get_itunes_info(name):
    """ get and store itunes API search result in json """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(search_url(name,"us"), headers = headers)
    if response.ok: # API working
        js = response.json()
        if len(js['results']) < 1: # app NOT DOUND
            add_fail(name,'not found')
            return False
        else: # app was found
            try: # save raw json
                utils.create_json(js,'itunes',name)
            except:
                add_fail(name,'json error')
                print(f'Failed to store json for app: {name}')
            try: # save to db
                app = js['results'][0]
                return app
            except Exception as e:
                add_fail(name,'db error')
                print(f'Failed to store db info for app:{name};\n Error: {e}')
    else: # API failed
        print(f"API Request Error:{response}; SLEEP FOR 70s")
        time.sleep(70) # when API rejects, sleep for 70s
        print(f'RESTART search for {name}')
        return get_itunes_info(name)

def store_itunes_info(name):
    """ store interesting app data to db """
    app = get_itunes_info(name) # get app info dict
    if app:
        try:
            info = (name,app['trackId'],app['averageUserRating'],app['artistName'],app['artistId'],app['price'],repr(app['genres']))
        except: # arcade app has no 'price'
            info = (name,app['trackId'],app['averageUserRating'],app['artistName'],app['artistId'],-1,repr(app['genres']))
        utils.insert_itunes_info(info)
    
def store_itunes_db_all(name_list):
    create_fail() # create fail txt for future
    """ itunes search API freq: 20 inquries/min """
    count,pointer = 0, 0
    while pointer < len(name_list):
        name = name_list[pointer]
        try:
            store_itunes_info(name) # get feedback on store operation
        except Exception as e:
            # unexpected failure in storing
            print(f'Unexpected failure at {name};/n Error:{e}')
        count += 1
        if count >= 19: # sleep for 1min every 20 inqury
            time.sleep(61)
            count = 0
        pointer += 1 # move on when API response.ok
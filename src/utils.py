import sys
import os
import numpy as np
import pandas as pd
import json
import sqlite3
from pathlib import Path

def create_path():
    path_data = "data"
    path_itunes = "data/itunes_info"
    path_review = "data/itunes_review"
    paths = (path_data,path_itunes,path_review)
    for path in paths:
        if not os.path.exists(path):
            try:
                Path(path).mkdir(parents = True, exist_ok = True)
            except Exception as e:
                print(f"Error {e} building path:{path}")

""" Json related funcs """
def create_json(data,options,name):
    """ Create and save json file from itunes APIs
        Params:
            data: json object
            options: str, 'itunes' or 'review'
            name: str, app name
    """
    lib = {'meta':'metascore','itunes':'itunes_info','review':'itunes_review'}
    try:
        lib[options]
    except:
        print(f'Invalid Option:{options}')
        sys.exit()
    with open(f"data/{lib[options]}/{name}.json","w") as json_file:
        # make sure non-English char is properly stored
        json.dump(data,json_file,ensure_ascii=False,indent=4)
    return data

def load_json(options,name):
    lib = {'itunes':'itunes_info','review':'itunes_review'}
    try:
        with open(f"data/{lib[options]}/{name}.json","r") as json_file:
            return json.load(json_file)
    except:
        print('data not exist')

""" SQLite related funcs """
def create_connection():
    """ create connection with db and return connnection and cursor object """
    conn = sqlite3.connect("data/iOS_Game.db")
    cur = conn.cursor()
    return conn,cur

def drop_table(name):
    conn, cur = create_connection()
    try:
        cur.execute(f'DROP TABLE {name}')
        print(f'Table {name} DROPPED!')
    except:
        print(f'Table not dropped/ not exist')
    conn.commit()
    conn.close()

def get_df(key,column = "*"):
    conn, _ = create_connection()
    key_convert = {'meta':'meta_score','info':'itunes_info','review':'itunes_review'}
    # print dataframe's head
    try:
        df = pd.read_sql_query(f"SELECT {column} FROM {key_convert[key]}", conn)
    except KeyError:
        print(f"Key supported: 'meta','info','review'")
    except:
        print(f"Cannot access: table {key_convert[key]}, column {column}")
    conn.close()
    # print(df.head())
    return df

def create_meta_data_table():
    """Create 'meta_score' table and drop existing one if exists"""
    conn, cur = create_connection()
    # create a brand new "meta_score" table in db
    try:
        cur.execute('CREATE TABLE meta_score (name TEXT, score INTEGER)')
    except sqlite3.OperationalError:
        print(f"Table meta_score already exist")
    conn.commit()
    conn.close()

# Create 'app_store' table
def create_itunes_info_table():
    conn, cur = create_connection()
    # create a brand new "itunes_info" table in db
    try:
        cur.execute('CREATE TABLE itunes_info (name TEXT, app_id INTEGER, rating FLOAT,\
                    artistName TEXT, artistId INTEGER, price FLOAT, genre TEXT)')
    except sqlite3.OperationalError:
        print(f"Table itunes_info already exist")
    conn.commit()
    conn.close()

def create_itunes_review_table():
    """Create 'meta_score' table and drop existing one if exists"""
    conn, cur = create_connection()
    # create a brand new "meta_score" table in db
    try:
        cur.execute('CREATE TABLE itunes_review (name TEXT, app_id INTEGER, title TEXT, body TEXT,\
                                                vote_useful INTEGER, vote_total INTEGER)')
    except sqlite3.OperationalError:
        print(f"Table itunes_review already exist")
    conn.commit()
    conn.close()

def insert_meta_data(meta):
    """Insert meta score to table in db 
    Param: 
        meta: list of tuples/ single tuple
    """
    conn,cur = create_connection()
    try:
        cur.executemany('INSERT INTO meta_score VALUES (?,?)',meta)
    except sqlite3.ProgrammingError:
        cur.execute('INSERT INTO meta_score VALUES (?,?)',meta)
    except Exception as e:
        print(f"Error {e} inserting into meta_score table;\n meta data:{meta}")
    conn.commit()
    conn.close()

def insert_itunes_info(app_info):
    conn,cur = create_connection()
    try:
        cur.execute('INSERT INTO itunes_info VALUES (?,?,?,?,?,?,?)',app_info)
    except Exception as e:
        print(f'Error:{e} while inserting to TABLE itunes_info')
    conn.commit()
    conn.close()

def insert_itunes_review(review):
    conn,cur = create_connection()
    try:
        cur.execute('INSERT INTO itunes_review VALUES (?,?,?,?,?,?)',review)
    except Exception as e:
        print(f'Error:{e} while inserting to TABLE itunes_review')
    conn.commit()
    conn.close()


"""Others"""
def clean_name(name):
    """ clean name for search """
    name = name.replace('for iPad','').replace('for iOS','').replace('/',' ').replace('-',' ').replace(':',' ').replace('!',' ').replace('?',' ')
    safe_ct = 0
    while "  " in name and safe_ct < 5:
        name = name.replace('  ',' ')
        safe_ct += 1
    return name
import sys
import os
import argparse
import json
import time
import numpy as np
import pandas as pd

import utils
import meta_scrap
import itunes_info_scrap
import itunes_reviews_scrap

def scrape(total_page = 5, review_total_page = 2, grade = False, start_over = False):
    utils.create_path()
    """ drop all tables when starting over """
    if start_over:
        utils.drop_table('meta_score')
        utils.drop_table('itunes_info')
        utils.drop_table('itunes_review')

    """ scrap from metacritics.com """
    utils.create_meta_data_table()
    if not grade:
        for page_num in range(total_page):
            meta_scrap.get_meta_score(page_num)
    else: # only scrape 3 results from page 1 for grading
        meta_scrap.get_meta_score(page = 1,max=3)

    """ scrape from itunes search API """
    utils.create_itunes_info_table()
    name_df = utils.get_df('meta',column='name')
    name_list = name_df['name'].tolist()
    if grade:
        name_list = name_list[:3]
    itunes_info_scrap.store_itunes_db_all(name_list)

    """scrape from itunes rss API for reviews """
    utils.create_itunes_review_table()
    id_df = utils.get_df('info',column='app_id')
    id_list = id_df['app_id'].tolist()
    info_name_df = utils.get_df('info',column='name')
    info_name_list = info_name_df['name'].tolist()
    if not grade:
        itunes_reviews_scrap.store_itunes_review(info_name_list,id_list,review_total_page)
    else:
        itunes_reviews_scrap.store_itunes_review(info_name_list,id_list,1,max_per_page=1)

def grab_all():
    df_meta = utils.get_df('meta')
    df_info = utils.get_df('info')
    df_review = utils.get_df('review')
    return df_meta,df_info,df_review

def main():
    parser = argparse.ArgumentParser(description="Command line control for choose source of data")
    parser.add_argument('--source',type = str,choices=['local','remote'],help="'local' to access local data,'remote' to scrap from web")
    parser.add_argument('--grade',action='store_true',help="call '--grade' to scrape only 3 entries")
    arg = parser.parse_args()

    """ grade mode """
    if arg.grade:
        print('Scrapping for 3 entries only:')
        scrape(total_page=1,review_total_page=1,grade=True,start_over=False)
        meta,info,review = grab_all()
        print(f'3 entries stored to disk:')
        print(meta.head())
        print(info.head())
        print(review.head())
    else:
        """ normal scrape mode """
        if str(arg.source) == 'local':
            print(f'data loaded from local file:')
            meta,info,review = grab_all()
            print(meta.head())
            print(info.head())
            print(review.head())
        elif str(arg.source) == 'remote':
            print(f'data scrapping online:')
            scrape(total_page=5,grade=False,start_over=True)
    print("Completed!")
main()
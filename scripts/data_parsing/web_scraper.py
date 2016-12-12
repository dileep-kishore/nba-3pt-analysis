#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Date:   2016-12-05T01:10:26-05:00
# @Filename: web_scraper.py
# @Last modified by:   dileep
# @Last modified time: December 11, 2016 11:55:15 PM

"""Script to scrape/parse www.basketball-reference.com
    Types of data we wish to get:
        a. Team 3pt shooting
            1. Season summaries for the last decade
            2. Season rosters
        b. Small vs. big players
            3. Player data
"""
import requests
from subprocess import call
import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4 import Comment
import re

def get_weblinks(mainsite, type_of_link, year_range):
    """Generate weblinks based on what data we want to get
        :param type_of_link: summary/leaders/per_game/totals/per_minute/per_poss/advanced
        :return html_data_list: list of html data files from basketball-reference
    """
    url = mainsite + 'leagues/'
    if type_of_link == 'summary':
        stat = '.html'
    else:
        stat = '_'+type_of_link+'.html'
    url_list = [url+'NBA_'+str(year)+stat for year in year_range]
    html_data_list = [requests.get(url).content for url in url_list]
    return html_data_list

def summary_parser(html_data, id_val, year):
    table_list = []
    for tag in html_data.find_all("div", id=id_val):
        html_data = tag.find_all(string=lambda text:isinstance(text,Comment))
        headers = re.findall(string=html_data[0], pattern="<thead>.*</thead>", flags=re.DOTALL)[0]
        data = html_data[0].split(headers)[1]
        if 'misc' in id_val:
            headers = re.findall(string=headers, pattern="<tr.*</tr>", flags=re.DOTALL)[0].split('</tr>')[1]
        if 'shooting' in id_val:
            headers = re.findall(string=headers, pattern="<tr.*</tr>", flags=re.DOTALL)[0].split('</tr>')[2]
        headers = re.findall(string=headers, pattern="<th.*</th>")
        data = re.findall(string=data, pattern="<tr.*</tr>")
        data, average_data = data[:-1], data[-1]
        #Last element is the league average
        pd_data = []
        new_head = []
        for header in headers:
            new_head.append(re.findall(string=header, pattern="\".*?\"")[0][1:-1])
        new_data = []
        for row in data:
            temp = list(filter(None, re.findall(string=row, pattern=r'>(.*?)<')))
            new_data.append([dummy for dummy in temp[1:] if dummy != '*'])
        new_data = np.array(new_data)
        try:
            if 'misc' in id_val:
                temp_table = pd.DataFrame(new_data[:,:-1], columns=new_head[1:-1])
            else:
                temp_table = pd.DataFrame(new_data, columns=new_head[1:])
        # except ValueError or IndexError:
        except:
            temp2 = []
            for temp1 in new_head[1:]:
                if '3' not in temp1:
                    temp2.append(temp1)
            if 'misc' in id_val:
                return pd.DataFrame()
            else:
                temp_table = pd.DataFrame(new_data, columns=temp2)
        table_list.append(temp_table)
    try:
        table = pd.concat(table_list)
    except:
        return pd.DataFrame()
    # table.to_csv(id_val+str(year)+'.csv', sep=',', index=False)
    return table

def pergame_parser(html_data, id_val, year):
    table_list = []
    for tag in html_data.find_all("div", id=id_val):
        table_stuff = tag.find_all("table", id='per_game_stats')[0]
        table_head = table_stuff.find('thead')
        rows = table_head.find_all('tr')
        header = []
        for row in rows:
            elems = row.find_all('th')
            for elem in elems:
                header.append(elem.find(text=True))
        table_body = table_stuff.find_all("tbody")
        data = []
        for table_elem in table_body:
            rows = table_elem.find_all('tr')
            data_elem = []
            for row in rows:
                data_row = []
                elems = row.find_all('td')
                for elem in elems:
                    data_row.append(elem.find(text=True))
                data_elem.append(data_row)
            data += data_elem
            new_data = np.array(data)
        temp_table = pd.DataFrame(data, columns=header[1:])
        table_list.append(temp_table)
    table = pd.concat(table_list).dropna(how='all')
    print(table.head(n=50))
    # table.to_csv(id_val+str(year)+'.csv', sep=',', index=False)
    return table

def win_parser(html_data, id_val, year):
    table_list = []
    div_id = ['all_'+id_val+'E', 'all_'+id_val+'W']
    tab_id = [id_val+'E', id_val+'W']
    for ind in range(2):
        for tag in html_data.find_all("div", id=div_id[ind]):
            table_stuff = tag.find_all("table", id=tab_id[ind])[0]
            table_head = table_stuff.find('thead')
            rows = table_head.find_all('tr')
            header = []
            for row in rows:
                elems = row.find_all('th')
                for elem in elems:
                    header.append(elem.find(text=True))
            table_body = table_stuff.find_all("tbody")
            data = []
            for table_elem in table_body:
                rows = table_elem.find_all('tr')
                data_elem = []
                for row in rows:
                    data_row = []
                    elems = row.find_all('td')
                    tname = row.find_all('th')[0].find_all('a', href=True)
                    if tname != []:
                        data_row.append(tname[0].find(text=True))
                    for elem in elems:
                        data_row.append(elem.find(text=True))
                    data_elem.append(data_row)
                data += data_elem
                new_data = np.array(data)
            new_data = [dat for dat in new_data if dat != []]
            header[0] = 'Team'
            temp_table = pd.DataFrame(data, columns=header).dropna(how='all')
            table_list.append(temp_table)
    table = pd.concat(table_list)
    return table

def webpage_parser(html_data, page_type, year, data_dir):
    """Call appropriate parsers to parse the webpage
    """
    html_soup = BeautifulSoup(html_data, "lxml")
    type_dir = data_dir + page_type + '/'
    data_dict = {}
    if page_type == 'summary':
        if not os.path.exists(type_dir):
            call('mkdir -p ' + type_dir, shell=True)
        win_data = win_parser(html_soup, 'divs_standings_', year)
        win_data_file = type_dir + 'win_data_' + str(year) + '.csv'
        win_data.to_csv(win_data_file, sep=',', index=False)
        team_data = summary_parser(html_soup, 'all_team-stats-per_game', year)
        team_data_file = type_dir + 'team_data_' + str(year) + '.csv'
        team_data.to_csv(team_data_file, sep=',', index=False)
        opponent_data = summary_parser(html_soup, 'all_opponent-stats-per_game', year)
        opponent_data_file = type_dir + 'opponent_data_' + str(year) + '.csv'
        opponent_data.to_csv(opponent_data_file, sep=',', index=False)
        misc_data = summary_parser(html_soup, 'all_misc_stats', year)
        misc_data_file = type_dir + 'misc_data_' + str(year) + '.csv'
        misc_data.to_csv(misc_data_file, sep=',', index=False)
        shooting_data = summary_parser(html_soup, 'all_team_shooting', year)
        shooting_data_file = type_dir + 'shooting_data_' + str(year) + '.csv'
        shooting_data.to_csv(shooting_data_file, sep=',', index=False)
        data_dict['summary'] = [win_data, team_data, opponent_data, misc_data, shooting_data]
    if page_type == 'per_game':
        player_data = pergame_parser(html_soup, 'all_per_game_stats', year)
        data_dict['per_game'] = [player_data]
    return data_dict

def main(out_dir):
    website = 'http://www.basketball-reference.com/'
    year_range = list(range(1977,2017))
    # Types: summary/leaders/per_game/totals/per_minute/per_poss/advanced
    type_of_data = 'summary' #currently support summary and per_game
    html_data_list = get_weblinks(website, type_of_data, year_range)
    for ind, html_data in enumerate(html_data_list):
        print(year_range[ind],'\r')
        data_dict = webpage_parser(html_data, type_of_data, year_range[ind], out_dir)
    return None

if __name__ == '__main__':
    results_dir = '../../data/summary/'
    ans = input("Do you want to delete current data? Y/N \n")
    if ans.upper() == 'Y':
        call('rm -rf ' + results_dir, shell=True)
    if not os.path.exists(results_dir):
        call('mkdir -p ' + results_dir, shell=True)
    main(results_dir)

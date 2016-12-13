#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Date:   December 12, 2016 11:30:21 PM
# @Filename: miscdata_parser.py
# @Last modified by:   dileep
# @Last modified time: December 13, 2016 12:00:34 AM

import os
import sys
from subprocess import call
import pandas as pd
import numpy as np

def get_misc_data(input_dir, stat_type, output_dir, year_range='all'):
    if year_range == 'all':
        year_range = list(range(1981, 2017))
    f_prefix = input_dir + 'misc_data' + '_'
    team_misc_dict = dict()
    for ind, year in enumerate(year_range):
        fname = f_prefix + str(year) + '.csv'
        print(fname)
        table = pd.read_csv(fname)
        # threeptdata = list(table['3-Point Field Goal Percentage'])
        threeptdata = list(table[stat_type])
        # threeptdata = list(table['3-Point Field Goal Attempts'])
        teams = list(table['Team'])
        for i, team in enumerate(teams):
            if team in team_misc_dict.keys():
                team_misc_dict[team].append(threeptdata[i])
            else:
                team_misc_dict[team] = [threeptdata[i]]
        for team in team_misc_dict:
            if not team in teams:
                team_misc_dict[team].append(None)
        for team in team_misc_dict:
            if len(team_misc_dict[team]) <= ind:
                none_list = [None for _ in range(ind+1-len(team_misc_dict[team]))]
                team_misc_dict[team] = none_list + team_misc_dict[team]
    team_misc_data = pd.DataFrame(team_misc_dict)
    team_misc_data.index = year_range
    fname = '_'.join(stat_type.split(' ')) + '.csv'
    output_file = output_dir + fname
    team_misc_data.to_csv(output_file)
    return team_misc_data

def get_combined_teams():
    fname = 'common_teams.csv'
    common_team = []
    with open(fname, 'r') as fid:
        for line in fid:
            common_team.append(line.strip().split(','))
    return common_team

def get_short_teamnames():
    fname = 'team_names.csv'
    teams = []
    abbrev = []
    with open(fname, 'r') as fid:
        for line in fid:
            temp1, temp2 = line.strip().split(',')
            teams.append(temp1)
            abbrev.append(temp2)
    abbrev_dict = dict(zip(teams, abbrev))
    return abbrev_dict

def get_final_dataframe(team_misc_data, common_teams, abbrev_dict, output_dir, stat_type):
    all_common_teams = sum(common_teams, [])
    final_dataframe = pd.DataFrame()
    for team in common_teams:
        curr_teamdata = []
        for t in team:
            curr_teamdata.append(list(team_misc_data[t]))
        temp_list = []
        for i in range(len(curr_teamdata[0])):
            temp = [d[i] for d in curr_teamdata if not np.isnan(d[i])]
            if temp == []:
                temp = [np.nan]
            temp_list.append(temp[0])
        abbrev = abbrev_dict[team[0]]
        final_dataframe[abbrev] = temp_list
    for team in abbrev_dict:
        if team not in all_common_teams:
            final_dataframe[abbrev_dict[team]] = list(team_misc_data[team])
    final_dataframe.index = team_misc_data.index
    fname = 'comb_' + '_'.join(stat_type.split(' ')) + '.csv'
    output_file = output_dir + fname
    final_dataframe.to_csv(output_file)
    return final_dataframe

def main(data_path, data_type, results_path):
    input_dir = data_path + data_type + '/'
    stats_type = 'Free Throws Per Field Goal Attempt' #NOTE: This was changed
    output_path = results_path + 'misc_data' + '/'
    if not os.path.exists(output_path):
        call('mkdir -p ' + output_path, shell=True)
    team_misc_data = get_misc_data(input_dir, stats_type, output_path)
    common_teams = get_combined_teams()
    abbrev_dict = get_short_teamnames()
    get_final_dataframe(team_misc_data, common_teams, abbrev_dict, output_path, stats_type)

if __name__ == '__main__':
    data_dir = '../../data/'
    data_type = 'summary/summary/'
    results_dir = '../../results/'
    if not os.path.exists(results_dir):
        call('mkdir -p ' + results_dir, shell=True)
    main(data_dir, data_type, results_dir)

# @Author: Dileep Kishore <dileep>
# @Date:   December 12, 2016 1:42:37 AM
# @Filename: winrate_parser.py
# @Last modified by:   dileep
# @Last modified time: December 12, 2016 2:51:55 AM

import os
import sys
import numpy as np
import pandas as pd
from subprocess import call
from threepoint_parser import get_combined_teams, get_short_teamnames

def get_win_data(input_dir, stats_type, output_dir, year_range='all'):
    if year_range == 'all':
        year_range = list(range(1980, 2017))
    f_prefix = input_dir + 'win_data_'
    team_win_dict = dict()
    for ind, year in enumerate(year_range):
        fname = f_prefix + str(year) + '.csv'
        print(fname)
        table = pd.read_csv(fname)
        winlossdata = list(table[stats_type])
        teams = list(table['Team'])
        for i, team in enumerate(teams):
            if team in team_win_dict.keys():
                team_win_dict[team].append(winlossdata[i])
            else:
                team_win_dict[team] = [winlossdata[i]]
        for team in team_win_dict:
            if not team in teams:
                team_win_dict[team].append(None)
        for team in team_win_dict:
            if len(team_win_dict[team]) <= ind:
                none_list = [None for _ in range(ind+1-len(team_win_dict[team]))]
                team_win_dict[team] = none_list + team_win_dict[team]
    team_win_data = pd.DataFrame(team_win_dict)
    team_win_data.index = year_range
    output_file = output_dir + 'teamwinrate.csv'
    team_win_data.to_csv(output_file)
    return team_win_data

def get_final_dataframe(team_win_data, common_teams, abbrev_dict, output_dir):
    all_common_teams = sum(common_teams, [])
    final_dataframe = pd.DataFrame()
    for team in common_teams:
        curr_teamdata = []
        for t in team:
            curr_teamdata.append(list(team_win_data[t]))
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
            final_dataframe[abbrev_dict[team]] = list(team_win_data[team])
    final_dataframe.index = team_win_data.index
    output_file = output_dir + 'comb_winrate.csv'
    final_dataframe.to_csv(output_file)
    return final_dataframe

def main(data_path, data_type, results_path):
    input_dir = data_path + data_type + '/'
    stats_type = 'W/L%'
    output_path = results_path + 'win_data/'
    if not os.path.exists(output_path):
        call('mkdir -p ' + output_path, shell=True)
    team_win_data = get_win_data(input_dir, stats_type, output_path)
    common_teams = get_combined_teams()
    abbrev_dict = get_short_teamnames()
    get_final_dataframe(team_win_data, common_teams, abbrev_dict, output_path)

if __name__ == '__main__':
    data_dir = '../../data/'
    data_type = 'summary/summary'
    results_dir = '../../results/'
    if not os.path.exists(results_dir):
        call('mkdir -p ' + results_dir, shell=True)
    main(data_dir, data_type, results_dir)

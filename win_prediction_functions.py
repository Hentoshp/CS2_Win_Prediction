#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing required libraries
import numpy as np
import pandas as pd
import requests
import re
import time


# In[3]:


# Takes player nickname and auth_key as arguements and returns player id and elo as columns of dataframe
def get_player_data(nickname, auth_key):

    # parameters for requests func
    parameters = {
        "nickname": nickname 
    }
    
    # faceit url for player id data
    url_player_id = "https://open.faceit.com/data/v4/players"

    # API key
    headers = {
    "Authorization": auth_key
    }

    # requesting player info from API
    response = requests.get(url_player_id, 
                            headers = headers, 
                            params = parameters)


    # conditional to catch request errors
    if response.status_code == 404:
        print(f"Error 404: Resource not found. Requested URL: {response.url}")
        
        # Return empty dataframe
        stats = pd.DataFrame()
        return stats
        
    elif response.status_code == 200:
        player_data = response.json()

        # try/except statement to catch KeyErrors 
        try:
            player_data_dict = {"player_id": player_data['player_id'],
                            "faceit_elo": player_data["games"]["cs2"]["faceit_elo"]}
            player_data_df = pd.DataFrame([player_data_dict])
            
        except KeyError:
            # KeyErrors generally occur due to CSGO match ID
            print("match_id for CSGO")
            
             # Returns empty dataframe
            stats = pd.DataFrame()
            return stats
            
            
        
        return player_data_df

    # for uncommon request errors
    else:
        print(f"Error {response.status_code}: {response.text}")
        stats = pd.DataFrame()
        return stats
    
    
    
    


# In[5]:


# returns player stats for the last 100 games played (if 100 games exist)
def get_player_stats(player_id, auth_key):
    
    
    # parameters needed for API request
    parameters = {
        "player_id": player_id,
        "limit": 100
    }

    # URL used for API request
    game_id = "cs2"
    url_stats = f"https://open.faceit.com/data/v4/players/{player_id}/games/{game_id}/stats"
    
    headers = {
        "Authorization": auth_key
    }


    # requests player data for last 100 games
    response = requests.get(url_stats, 
                            headers = headers, 
                            params = parameters)

    # Flattens nested json into dataframe
    data = response.json()
    stats_df = pd.json_normalize(data['items'], sep = '_')

    # returns player stats dataframe
    return stats_df


# In[7]:


# Takes player stats dataframe and match map and returns individual player stats for that map
def player_stats_calc(df, map):
    
    # testing if map exists
    try:
        test_df = df[df.stats_Map == map]
    # If map does not exist return empty dataframe
    except:
        stats = pd.DataFrame()
        return stats

    
    # Converting Result and K/R ratio columns to numeric
    test_df.loc[:, ['stats_Result']] = pd.to_numeric(test_df['stats_Result'])
    test_df.loc[:, ['stats_K/R Ratio']] = pd.to_numeric(test_df['stats_K/R Ratio'])
        

    try:
        # Calculating win percentage
        map_win_percentage = (test_df['stats_Result'].sum() / len(test_df)) * 100
        
    except ZeroDivisionError:
        stats = pd.DataFrame()
        print("ZeroDivisonError")
        return stats

        
        
    try:
        # Calculating average K/R ratio
        average_KR_ratio = test_df['stats_K/R Ratio'].mean()
    
    except ZeroDivisionError:    
        stats = pd.DataFrame()
        print("ZeroDivisonError")
        return stats
        
    
    # Combining stats and renaming axis for data frame
    stats = pd.DataFrame({"Win Percentage": map_win_percentage,
                         "Average K/R Ratio": average_KR_ratio}, index = [0])
    # returning stats data frame
    return stats


# In[9]:


# Pulls player ID from leaderboard
def get_ranking_player_ids(offset, auth_key):

    # requests parameters
    parameters = {
        "offset": offset,
        "limit": 100
    }
    region = "NA"
    game_id = "cs2"
    url_leaderboard = f"https://open.faceit.com/data/v4/rankings/games/{game_id}/regions/{region}"
    headers = {
        "Authorization": auth_key
    }
    
    
    # requesting API for 100 players' data from leaderboard
    response = requests.get(url_leaderboard, 
                            headers = headers, 
                            params = parameters)

    # Conditional to catch API request errors
    if response.status_code == 404:
        print("Error 404: Resource not found.")
        print(f"Requested URL: {response.url}")

    # Flattening nested json into dataframe
    elif response.status_code == 200:
        data = response.json()
        data_frame_rankings = pd.json_normalize(data['items'], 
                                                sep = '_')
        
    # Extracting player_id column
        return data_frame_rankings['player_id']
        
    else:
        print(f"Error {response.status_code}: {response.text}")


# In[11]:


# Uses player ID to pull 3 match_id from match histroy
def match_data_selection(player_id, auth_key):

    # parameters for API request
    parameters = {
        "limit": 3
    }
    url_match_history = f"https://open.faceit.com/data/v4/players/{player_id}/history"

    # requesting match history from API for player
    response = requests.get(url_match_history, 
                            headers = headers, 
                            params = parameters)

    # Conditional to check for request errors
    if response.status_code == 200:

        # Flattening JSON to dataframe
        data = response.json()
        df_match_id = pd.json_normalize(data['items'], 
                                        sep = '_')

        # returning match_id column
        return df_match_id['match_id']
        
    else:
        print(f"Error {response.status_code}: {response.text}")
    
    


# In[13]:


# Uses match_ID to calculate dataframe of match stats for each team
def calculate_match_stats(match_id, auth_key, count):

    # parameters for API request
    headers = {
        "Authorization": auth_key
        }
    url_match_id = f"https://open.faceit.com/data/v4/matches/{match_id}/stats"

    # API request for match statsitics
    response = requests.get(url_match_id, 
                            headers = headers)
        

    # Flattens nested json
    match_data = response.json()

    # attempts to flatten nested JSON
    try:
        rounds_flat = pd.json_normalize(match_data['rounds'], 
                                        sep = '_')
    # returns empty dataframe if rounds does not exist 
    except KeyError:
        stats = pd.DataFrame()
        return stats
    
    # Flatten teams, nested in match_data
    teams_flat = pd.json_normalize(
        match_data['rounds'],
        record_path = 'teams',
        meta = ['match_id'],
        sep = '_'
    )
    
    # Flatten players data
    players_flat = pd.json_normalize(
        match_data['rounds'],
        record_path = ['teams', 'players'],
        meta = ['match_id', ['teams', 'team_id']],
        sep = '_'
    )

    # flatten teams data
    teams_df = pd.json_normalize(match_data['rounds'], 
                                 record_path = 'teams', 
                                 meta = ['match_id'], 
                                 sep = '_')
    
    # creating columns for match data frame
    columns = ["win", "map", "Team_A_avg_win_percentage", "Team_A_avg_KR", "Team_A_avg_elo",
                  "Team_B_avg_win_percentage", "Team_B_avg_KR", "Team_B_avg_elo", "Match ID"]

    # creating match data frame
    
    data_df = pd.DataFrame(columns = columns)
    data_df.columns

    # checking if match data exists, or returns empty dataframe
    try:
        if teams_df.loc[0, 'team_stats_Team Win'] == "1":
            data_df.loc[0, "win"] = "team a"
        else:
            data_df.loc[0, "win"] = "team b"
        data_df.loc[0, "map"] = rounds_flat.round_stats_Map[0]
    
        data_df.loc[0, "Match ID"] = teams_df.match_id[0]
        
    except KeyError:
        stats = pd.DataFrame()
        return stats
    

    
    
    # Team A Stats
    team_a_df = pd.DataFrame(teams_df.players[0])
    
    team_a_nicknames = team_a_df.nickname
    team_a_id_elo_list = []

    # loops over nicknames column and appends list of player ids for team A
    for nickname in team_a_nicknames:
        id_elo = get_player_data(nickname, auth_key)
        
        # returns empty dataframe if player elo DNE
        if id_elo.empty:
            print(count)
            return id_elo
        else:
            team_a_id_elo_list.append(id_elo)

    # creates column of player IDs from list
    team_a_id_elo_df = pd.concat(team_a_id_elo_list)

    # adds mean of team elo to match data df
    data_df.loc[0 , "Team_A_avg_elo"] = team_a_id_elo_df["faceit_elo"].mean()
    
    # Uses player ID to calculate individual player stats (K/R and win percentage)
    team_a_stats_list = []
    for id in team_a_df.player_id:
        # uses get_player_stats to calculate individual stats
        stats_df = get_player_stats(id, auth_key)
        stats = player_stats_calc(stats_df, data_df["map"][0])
        # if returned df is empty, return empty match dataframe
        if stats.empty:
            # used to track missing/invalid data
            print(count)
            print("Unable to compute stats, may be error with map used")
            return stats

        # append individual stats to list
        else: 
            team_a_stats_list.append(stats)

    # creates win percentage and K/R ratio columns for team A 
    team_a_stats_df = pd.concat(team_a_stats_list)
    data_df.loc[0 , "Team_A_avg_win_percentage"] = team_a_stats_df["Win Percentage"].mean()
    data_df.loc[0 , "Team_A_avg_KR"] = team_a_stats_df["Average K/R Ratio"].mean()
        
    
    
    
    
    # Team B stats, repeats same process used for team A stats
    
    team_b_df = pd.DataFrame(teams_df.players[1])
    team_b_nicknames = team_b_df.nickname
    team_b_id_elo_list = []
    
    for nickname in team_b_nicknames:
        
        if id_elo.empty:
            print(count)
            return id_elo
            
        else:
            team_b_id_elo_list.append(id_elo)
    
    team_b_id_elo_df = pd.concat(team_b_id_elo_list)
    team_b_id_elo_df
    data_df.loc[0 , "Team_B_avg_elo"] = team_b_id_elo_df["faceit_elo"].mean()
    
    
    team_b_stats_list = []
    for id in team_b_df.player_id:
        
        stats_df = get_player_stats(id, auth_key)
        stats = player_stats_calc(stats_df, data_df["map"][0])
        
        if stats.empty:
            print(count)
            print("Unable to compute stats, may be error with map used")
            return stats
            
        else: 
            team_b_stats_list.append(stats)
            
    team_b_stats_df = pd.concat(team_b_stats_list)
    data_df.loc[0 , "Team_B_avg_win_percentage"] = team_b_stats_df["Win Percentage"].mean()
    data_df.loc[0 , "Team_B_avg_KR"] = team_b_stats_df["Average K/R Ratio"].mean()

    # Returns row of match data for match_id given
    return data_df


# In[ ]:





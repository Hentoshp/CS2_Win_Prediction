# CS2_Win_Prediction
Designed and implemented a Support Vector Machine (SVM) model to forecast team wins in Counter-Strike 2. Achieved a predictive accuracy of 77% ± 0.92, after testing multiple models including Logistic Regression, Random Forests, neural net, and XGBoosted Trees. Extracted and processed a robust dataset of 9,651 observations from Faceit, an esports matchmaking service, API.

## Features
- **Accurate Predictions:** Achieves 77% ± 0.92 predictive accuracy using support vector machine.
- **Data Pipeline:** Automated extraction and preprocessing of match data from Faceit’s API.
- **Clean Data Handling:** Employs advanced data cleaning and transformation techniques to ensure accurate results.
- **Actionable Insights:** Outputs clear predictions for team wins based on historical player statistics.

## Usage limitations
- Used for any FACEIT player wanting to estimate the probability of their team winning given a certain map. Player simply inputs FACEIT nicknames for each player on each team and will receive the likelihood of each team winning.
- Current limitations: new/smurf accounts are likly to cause an error in calculating data, uses last 100 games to calculate player stats. If a player has no games on a given map, model will return an error. Average ELO also plays a role in predicting which team will win, smurf accounts with very low elo can throw off model predictions.
- Model is currently only available for faceit players in NA, plan to expand to EU regions next.

## Dependencies
- Pandas
- Numpy
- requests
- time
- sckit-learn
- PyTorch

## Code files:
- **Win Prediction Data Mining and Processing**: Contains code used to mine player data from FACEIT API. Pulled 50,000 player_ids from faceit leaderboard then randomly selected 1,000 players from the player_id pool. Took 3 matches from each randomly selected player_id and calculated match statistics (avg team win percentage for map, avg K/R ratio for map, avg team ELO). After calculating match statistics, ended with 1500 observations per pull, the rest of the data was not usable either due to deleted accounts, old maps not longer in FACEIT pool, or matches played in CSGO.

- **Win Prediction Model Fitting and Tuning**: Contains code used for model fitting and tuning. Tried various  model types, lLogistic Regression, Random Forests, neural net, and XGBoosted Trees. Validated predictive accuracy and model tuning with cross validation.

- **Win Prediction Applied**: Contains code to use model applied to new data. Input player nicknames of each team and map, code will output array containing the win probability of each team. Looking into an easier input system rather than having to type all 10 player nicknames.

- **Win Predictions Functions**: Contains all functions defined in win prediction code files, see below for explanation of each function.

## Functions:

### get_player_data(nickname, auth_key): --> dataframe

**Description**:
This function takes a FACEIT players' nickname and an authentification key and then requests FACEIT API for player information. Then reformats API JSON to a dictionary, and pulls player_id and ELO using dictionary keys. Player_id and ELO dict is converted to a dataframe and returned. Will return an error for API request if any error code is raised. If dict KeyError, will return an empty dataframe.

**Parameters**:
- nickname, string of player nickname
- auth_key, string of API key used for request

**Returns**:
- Dataframe: 2 columns (player_id and ELO), 1 row


### get_player_stats(player_id, auth_key): --> dataframe

**Description**:
Function takes player_id and API auth key and then request FACEIT API for player match statistics for the last 100 games played (if at least 100 games have been played). The nested JSON information is normalized and converted to a dataframe then returned. 

**Parameters**:
- player_id, string of player id
- auth_key, string of API key used for request

**Returns**:
- Dataframe: 34 columns columns (player_id and ELO), up to 100 rows.

### player_stats_calc(df, map): --> dataframe

**Description**:
This function takes a player stats dataframe from get_player_data function and a map name in the current FACEIT map pool (string) and returns a dataframe containing the stats for win percentage and mean K/R ratio as a dataframe. Will catch errors in calculations, such as if a player has zero games played for the given map. For all errors, it will return an empty dataframe. 

**Parameters**:
- df, dataframe of player stats, from get_player_data
- map, string of map found in FACEIT map pool for CS2. Will return an empty map 

**Returns**:
- dataframe, 2 columns, 1 row

### get_ranking_player_ids(offset, auth_key) --> dict

**Description**:
This function takes offset number (int) and auth_key. It then requests FACEIT API for 100 player_ids from FACEIT leaderboard, offset is the starting position of where data is pulled from leaderboard. 100 player_ids are returned as a list in a dictionary with key "player_id". Will return error response code if API request is rejected.

**Parameters**:
- offset, int, determines starting point of where data is pulled on player leaderboard
- auth_key, string of API key used for request

**Returns**:
- Dict, list of 100 player ids with key "player_id"

### match_data_selection(player_id, auth_key) --> dict

**Description**:
Takes player_id and auth_key as arguements and returns a dictionary with a list of 3 match_ids from given player's match history. 

**Parameters**:
- player_id, string, unique id assigned to each player account on FACEIT
- auth_key, string of API key used for request

**Returns**:
- Dict, list of 3 match_ids, key "match_id"

### calculate_match_stats(match_id, auth_key, count): --> dataframe

**Description**:
This function takes a match_id, auth_key, and current iteration count as arguments and returns a dataframe containing calculated team statistics for each team. Requests match information from FACEIT API and normalizes nested list of dictionaries. Team statistics include team win_rate for map, avg K/R of team for map, avg elo of team. This function uses get_player_data, get_player_stats, and player_stats_calc within its code. If there is any issue/error in calculating the match data, an empty dataframe will be returned.

**Parameters**:
- match_id, string, match_id given to each unique match within FACEIT matchmaking.
- auth_key, string of API key used for request
- count, calculate_match_stats is used iteratively on many match_ids, helpful in error handeling. Finding what data is causing issues in data mining.

**Returns**:
- Dataframe, 9 columns, 1 row.


### new_player_data(team_a_nicknames, team_b_nicknames, map, auth_key): --> dataframe

**Description**:
Very similar to calculate_match_stats function, but is used for new player data. This function takes a list of FACEIT nicknames for team a and team b and the current map and returns a dataframe with calculated team stats, similar to calculate_match_stats function. Will also return an empty dataframe if any errors are encountered.

**Parameters**:
- team_a_nicknames, list of strings, 5 nicknames for players on team A
- team_b_nicknames, list of strings, 5 nicknames for players on team B
- map, string, map in the current FACEIT map pool
- auth_key, string of API key used for request

**Returns**:
- Dataframe, 6 columns, 1 row

### team_inputs() --> 2 lists and one string

**Description**:
Prompts user for input of 5 nicknames for team a and team b. Then prompts user for input of map name. 

**Parameters**:
- None

**Returns**:
- (list, list of strings, 5 player nicknames) * 2
- map, string, name of current map in FACEIT map pool

### win_probability_calc(model, auth_key): --> array

**Description**:
Uses a fitted model to calculate each team's probability of winning the match. team_inputs and new_player_data functions are used within.

**Parameters**:
- model, fitted model
- auth_key, string of API key used for request

**Returns**:
- array, with team a and team b win probabilities.

### get_auth_key(): --> string

**Description**:
defined on separate file, used to hide auth key for API calls

**Parameters**:
- None 

**Returns**:
- string, of authentification key used for API calls


  
## License
This project is licensed under the MIT License.

You are free to use, modify, and distribute this software, provided that appropriate credit is given to the original author. This software is provided "as-is," without any warranties or guarantees.

For detailed information, see the LICENSE file in this repository.


## Contact:

email: pierce@hentosh.com for inquiries





















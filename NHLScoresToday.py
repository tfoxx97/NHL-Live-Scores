from datetime import datetime
import requests, polling2
from nhl_teams import nhl_abbreviations

year = datetime.now().strftime("%Y")
month = datetime.now().strftime("%m")
day = datetime.now().strftime("%d")
URL = f"https://nhl-score-api.herokuapp.com/api/scores?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}"

class NHLClient():
    def __init__(self, timeout, polling=1.0):
        self.timeout = timeout
        self.polling = polling
        self.team = None
        self.ishome = False
        self.isaway = False
        self.goals = 0
        self.in_progress = {}
        self.preview = {}
        self.final = {}

    def get_response(self):
        response = requests.get(URL)
        return response

    def get_response_code(self):
        response = self.get_response()
        return response.status_code, response.json() if response.status_code == 200 else None
    
    def get_needed_data(self):
        # need to get the data from second arg of get_response_code and parse it to get the teams playing, the score, and the game status. Separate these into three dicts and return them:
        code, data = self.get_response_code()
        if data:
            data = self.get_response_code()[1]
            data = data[0] # data is now a dict type
            new_data = [
                {
                    "gameId": game["meta"]["gameId"], 
                    "teams": {"home": {"abbreviation": game["teams"]["home"]["abbreviation"]}, "away": {"abbreviation": game["teams"]["away"]["abbreviation"]}},
                    "scores": {"scores": game["scores"]},
                    "status": {"state": game["status"]["state"]}
                } for game in data['games']
            ]
            return new_data
        else:
            print(f"Failed to get request: HTTP {code}")
            return

    def get_team_score(self, team):
        #TODO: include period and time left in period. If intermission, polling paused for 10 minutes and then resumed. If intermission, print "Intermission: 10 minutes remaining until next update."
        data = self.get_needed_data()
        for game in data:
            # game: {'gameId': 2025021266, 'teams': {'home': {'abbreviation': 'CHI'}, 'away': {'abbreviation': 'STL'}}, 'scores': {'scores': {'STL': 1, 'CHI': 1}}, 'status': {'state': 'LIVE'}}
            if team in [game["teams"]["home"]["abbreviation"], game["teams"]["away"]["abbreviation"]]:
                team_score = game["scores"]["scores"][team]
                opponent_score = game["scores"]["scores"][game["teams"]["home"]["abbreviation"] if team == game["teams"]["away"]["abbreviation"] else game["teams"]["away"]["abbreviation"]]
                return team_score, opponent_score, game["status"]["state"]

    def get_daily_schedule(self, input_):
        parsed_data: list = self.get_needed_data()

        for game in parsed_data:
            if game["status"]["state"] == "PREVIEW":
                self.preview[game["gameId"]] = [game['teams']['home']['abbreviation'], game['teams']['away']['abbreviation']]
            elif game["status"]["state"] == "FINAL":
                self.final[game["gameId"]] = [game['teams']['home']['abbreviation'], game['teams']['away']['abbreviation']]
            else:
                self.in_progress[game["gameId"]] = [game['teams']['home']['abbreviation'], game['teams']['away']['abbreviation'], game['scores']]
        
        # print(in_progress) output: {2025021229: ['BUF', 'TBL', {'TBL': 2, 'BUF': 3}], 2025021230: ['WPG', 'SEA', {'SEA': 1, 'WPG': 3}]}
        # if all three dicts are empty, then there are no games scheduled for today
        if not self.preview and not self.in_progress and not self.final:
            print("No games scheduled for today.")
        else:
            # each value in the preview dict is a list of the home and away team abbreviations, so we can check if the user's team is in the list
            if input_:
                self.team = input_
                for teams in self.preview.values():
                    if input_ in teams:
                        other_team = teams[0] if teams[1] == input_ else teams[1]
                        print(f"The {nhl_abbreviations[input_]} have a game scheduled for today against the {nhl_abbreviations[other_team]}. Check back later for updates.")
                        break
                else:
                    for teams in self.in_progress.values():
                        if input_ in teams:
                            other_team = teams[0] if teams[1] == input_ else teams[1]
                            print(f"The {nhl_abbreviations[input_]} are currently playing against the {nhl_abbreviations[other_team]}")
                            print("Begin polling for updates.")
                            self.update_score_count()
                            self.begin_polling(input_)
                            break
                    else:
                        for teams in self.final.values():
                            if input_ in teams:
                                print(f"The {nhl_abbreviations[input_]} already played their game today. Check back later for updates.")
                                break
                        else:
                            print(f"No game scheduled for {nhl_abbreviations[input_]} today.")
            else:
                raise ValueError("Input cannot be empty. Please enter a valid NHL team abbreviation.")
    
    def update_score_count(self):
        for teams in self.in_progress.values():
            if self.team in teams:
                other_team = teams[0] if teams[1] == self.team else teams[1]
                print(f"Current score: {nhl_abbreviations[self.team]}: {teams[2]["scores"][self.team]} - {nhl_abbreviations[other_team]}: {teams[2]["scores"][other_team]}")
                self.goals = teams[2]["scores"][self.team]
                break

    def get_latest_scores(self, team):
        print("Getting latest score updates...")
        new_score, opponent_score, status = self.get_team_score(team)
        print(f"Latest score: {nhl_abbreviations[team]}: {new_score} - Bad Guys: {opponent_score} | Status: {status}")
        if status == "LIVE":
            if new_score > self.goals:
                self.goals = new_score
                print(f"Goal for {nhl_abbreviations[team]}!")
        elif status == "FINAL":
            print(f"The game has ended. No longer polling for updates.")
            return True # this will break the polling loop
        
    def begin_polling(self, team):
        polling2.poll(
            lambda: client.get_latest_scores(team), 
            step=self.polling, 
            timeout=self.timeout
        )
        
if __name__ == "__main__":
    your_team = input("Enter your favorite NHL team (abbreviation): ").upper()

    while your_team not in nhl_abbreviations:
        print("Invalid team abbreviation. Please try again.")
        your_team = input("Enter your favorite NHL team (abbreviation): ").upper()
    
    if your_team in nhl_abbreviations:
        client = NHLClient(timeout=7200, polling=1.0)
        client.get_daily_schedule(your_team)
        
import os
import shutil
import glob
import re
from choose_idol import Idol
import json

class History:
    folder_name = 'game files' # folder where all files are stored

    def __init__(self):
        self.history = [] # each element of the list is a line of the file, denoting one action during the game
        self.overview = [] # contains information for overview board to show at top of history file
        self.all_idols = [] # contains a list of every idol that appeared in the game

    def write(self, line: str): # function to add a line to history
        self.history.append(line)

    def remove_ansi(self, text): # remove ansi codes from any string
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def create_overview(self, game): # creates overview board to display on top of a history file
        self.overview.append(f'WINNER: {self.remove_ansi(game.winner.name)}') # display winner along with combat score/exodia
        if game.p1.combat_score > 0 or game.p2.combat_score > 0:
            self.overview.append(f'Score: {game.p1.combat_score} to {game.p2.combat_score}')
        else: 
            self.overview.append(f'Score: EXODIA ({game.exodia})')
        self.overview.append('-' * 30) # divider

        def eval_idols(player): # evaluates each idol in each player's roster for the overview
            self.overview.append(f'{self.remove_ansi(player.name)}: ${player.money}') # p1 info & roster
            self.overview.append(f'Ult: {self.remove_ansi(player.ult.to_string())}\n')
            for idol in player.roster:
                if idol.stats["price"] is not None: # set marker for idol in overview
                    marker = f'${idol.stats["price"]}'
                elif idol.stats["gr"]:
                    marker = '(GR)'
                elif idol.stats["dr"]:
                    marker = '(DR)'
                elif idol.stats["letter"]:
                    marker = '(Letter)'
                else:
                    marker = 'N/A'
                if idol.stats["ult"]:
                    marker += ' (ULT)'
                if idol.stats["switch"]:
                    marker += ' (SW)'
                if idol.stats["stolen"]:
                    marker += ' (STOLEN)'
                self.overview.append(f'{marker} - {self.remove_ansi(idol.to_string())}')
            self.overview.append('-' * 30) # divider
        
        eval_idols(game.p1)
        eval_idols(game.p2)
        # end of overview creation function

    def write_history_file(self, game): # writes the history file of the game
        existing_files = [f for f in os.listdir(self.folder_name) if f.startswith('game_') and f.endswith(".txt")]
        game_number = len(existing_files) + 1
        filename = f'game_{game_number}.txt'
        path = os.path.join(self.folder_name, filename)

        self.write_idol_stats()
        self.create_overview(game)

        with open(path, 'w') as f:
            f.writelines('\n'.join(self.overview))
            f.writelines('\n'.join(self.history))
        print(f'Wrote history of game #{game_number} to {filename}')

    def print_idol(self, idol: Idol):
        print(f'{idol.to_string()} | Price: {idol.stats["price"]} | Reroll: {idol.stats["reroll"]}')

    def write_idol_stats(self): # uploads idol stats to json database
        for idol in self.all_idols:
            # self.print_idol(idol)
            groups = idol.group.upper().split('/') # for IZONE edge cases
            for group in groups:
                file_path = f'./girl groups/{group}.json'
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    for member in data["members"]:
                        if idol.name == member["name"]:
                            stats = member["stats"]
                            stats["total_games"] += 1 # total games stat
                            if idol.stats["price"] is not None:
                                stats["times_bought"] += 1 # total games bought by bidding
                                stats["money_spent"] += idol.stats["price"] # total money spent on bidding
                            stats["times_rerolled"] += idol.stats["reroll"]
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
            
def reset_stats(): # resets all idol stats
    files = glob.glob(os.path.join('./game files', "*"))

    for file in files:
        if os.path.isfile(file):
            os.remove(file)

    files = os.listdir('./girl groups')
    for file in files:
        file_name = f'./girl groups/{file}'
        with open(file_name, 'r') as f:
            data = json.load(f)

            for member in data["members"]: # reset all stats
                stats = member["stats"]
                stats["total_games"] = 0
                stats["times_rerolled"] = 0
                stats["times_bought"] = 0
                stats["money_spent"] = 0

        with open(file_name, 'w') as f: # rewrite resetted stats to file
            json.dump(data, f, indent=4)

    print("All stats and game history erased!")

# reset_stats()
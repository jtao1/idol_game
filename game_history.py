import os
import re
from choose_idol import Idol
import json

class History:
    game_stats = "./info/game_stats.txt" # file where game stats are stored

    def __init__(self):
        self.all_idols = [] # contains a list of every idol that appeared in the game

    def remove_ansi(self, text): # remove ansi codes from any string
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def update_game_stats(self, game): # updates total game stats and writes idol statistics
        with open(self.game_stats, 'r') as f: 
            # read data of game statistic file
            lines = f.readlines()
            data = {
                "total games": int(lines[2].split(":")[1].strip()),
                "sejun wins": int(lines[3].split(":")[1].split("-")[0].strip()),
                "jason wins": int(lines[4].split(":")[1].split("-")[0].strip()),
                "exodias": int(lines[6].split(":")[1].split("-")[0].strip()),
                "exodia letters": {},
                "synergies": 0, # retrieve later since line can vary
                "letters": {}
            }
            exod = True
            for line in lines[7:]:
                if line.strip():
                    if line.startswith("Letter"):
                        data["synergies"] = int(line.split(":")[1].strip())
                        exod = False
                        continue
                    if exod: # read variable-length list under exodia
                        exodia_mark, count = line.strip().split(":")
                        data["exodia letters"][exodia_mark.strip()] = int(count.split("-")[0].strip())
                    else: # exodia reading finished, read variable length list under letter synergies
                        letter, count = line.strip().split(":")
                        data["letters"][letter.strip()] = int(count.split("-")[0].strip())

            # update data
            data["total games"] += 1
            if "Sejun" in game.winner.name:
                data["sejun wins"] += 1
            else:
                data["jason wins"] += 1
            if game.exodia:
                data["exodias"] += 1
                data["exodia letters"][game.exodia] = data["exodia letters"].get(game.exodia, 0) + 1 # add exodia type
            game.turn = game.p1
            for _ in range(2):
                for char in game.turn.synergies:
                    if len(char) == 1: # if synergy is a letter
                        data["synergies"] += 1
                        data["letters"][char] = data["letters"].get(char, 0) + 1 # add specific letters of all hit synergies
                game.switch_turns()

        # data to write
        new_data = []
        new_data.append("IDOLS 3.5 GAME STATISTICS OVERVIEW\n\n")
        new_data.append(f'Total Games: {data["total games"]}\n')
        new_data.append(f'Sejun: {data["sejun wins"]} - ({round(data["sejun wins"] / data["total games"] * 100, 2)}%)\n')
        new_data.append(f'Jason: {data["jason wins"]} - ({round(data["jason wins"] / data["total games"] * 100, 2)}%)\n\n')
        new_data.append(f'Exodias: {data["exodias"]} - ({round(data["exodias"] / data["total games"] * 100, 2)}%)\n')
        for key in data["exodia letters"]:
            new_data.append(f'\t{key}: {data["exodia letters"][key]} - ({round(data["exodia letters"][key] / data["exodias"] * 100, 2)}%)\n')
        new_data.append(f'\nLetter Synergies: {data["synergies"]}\n')
        for key in data["letters"]:
            new_data.append(f'\t{key}: {data["letters"][key]} - ({round(data["letters"][key] / data["synergies"] * 100, 2)}%)\n')

        with open(self.game_stats, 'w') as f:
            f.writelines(new_data) 
        
        self.write_idol_stats()
        print(f'Wrote game history and idol statistics')

    def print_idol(self, idol: Idol):
        print(f'{idol.to_string()} | Stats: {idol.stats}')

    def write_idol_stats(self): # uploads idol stats to json database
        for idol in self.all_idols:
            self.print_idol(idol)
        for idol in self.all_idols:
            groups = idol.group.upper().split('/') # for IZONE edge cases
            for group in groups:
                file_path = f'./girl groups/{group}.json'
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    for member in data["members"]:
                        if idol.name == member["name"]:
                            stats = member["stats"]
                            stats["games"] += 1 # total games stat
                            if idol.stats["win"]: # add to total wins
                                stats["wins"] += 1
                            stats["reroll"] += idol.stats["reroll"]
                            stats["opp reroll"] += idol.stats["opp reroll"]
                            stats["gr"] += idol.stats["gr"]
                            
                            if idol.stats["price"] is not None:
                                stats["times bought"] += 1 # total games bought by bidding
                                stats["money spent"] += idol.stats["price"] # total money spent on bidding
                            
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
            
    def reset_stats(self): # resets all idol stats
        files = os.listdir('./girl groups')
        for file in files:
            file_name = f'./girl groups/{file}'
            with open(file_name, 'r') as f:
                data = json.load(f)

                for member in data["members"]: # reset all stats
                    stats = member["stats"]
                    stats["games"] = 0
                    stats["wins"] = 0
                    stats["ults"] = 0
                    stats["reroll"] = 0
                    stats["opp reroll"] = 0
                    stats["opp chances"] = 0
                    stats["gr"] = 0
                    stats["times bought"] = 0
                    stats["money spent"] = 0

            with open(file_name, 'w') as f: # rewrite resetted stats to file
                json.dump(data, f, indent=4)
        
        reset_string = """
IDOLS 3.5 GAME STATISTICS OVERVIEW

Total Games: 0
Sejun: 0 - (0.0%)
Jason: 0 - (0.0%)

Exodias: 0 - (0.0%)

Letter Synergies: 0
    """.strip()
        
        with open(self.game_stats, 'w') as f:
            f.write(reset_string)

        print("All stats and game history erased!")
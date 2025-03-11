import os
import re
import choose_idol as choose
import card_collector as card
from choose_idol import Idol
import json

game_stats = "./info/game_statistics.txt" # file where game stats are stored
all_idol_file = "./info/all_idols.txt" # file where all idols are stored in a single list

def remove_ansi(text): # remove ansi codes from any string
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return ansi_escape.sub('', text)

# sort - True for sorting alphabetically, False for sorting by group
def write_all_idols(sort: bool): # Writes all idols to a single file
    search = './girl groups'
    files = os.listdir(search)
    with open(all_idol_file, 'w', encoding="utf-8") as output:
        idols = []
        for file in files:
            print(file)
            with open(f'{search}/{file}', 'r') as f:
                data = json.load(f)
                for i in range(len(data["members"])):
                    name = data["members"][i]["name"]
                    group = data["group"]["name"]
                    age = data["members"][i]["age"]
                    rating = data["members"][i]["rating"]
                    country = data["members"][i]["country"]
                    idol = Idol(name, group, age, rating, country)
                    choose.multigroup(idol)
                    if not any(idol.equals(compare) for compare in idols): # avoid double group duplicates
                        idols.append(idol)
        idol_strings = []
        for idol in idols:
            idol_strings.append(choose.remove_ansi(f'{idol.to_string()} | {idol.rating}\n'))
        if sort:
            idol_strings.sort()
        output.writelines(idol_strings)
    print(f'Wrote all idols from "{search}" to a single file')

def update_game_stats(game): # updates total game stats and writes idol statistics
    with open(game_stats, 'r') as f: 
        # read data of game statistic file
        lines = f.readlines()
        data = {
            "total games": int(lines[2].split(":")[1].strip()),
            "sejun wins": int(lines[3].split(":")[1].split("-")[0].strip()),
            "jason wins": int(lines[4].split(":")[1].split("-")[0].strip()),
            "exodias": int(lines[6].split(":")[1].split("-")[0].strip()),
            "exodia letters": {},
            "flushes": 0, # retrieve later since line can vary
            "flush ratings": {},
            "synergies": 0, # retrieve later since line can vary
            "letters": {}
        }
        eval = "exodia"
        for line in lines[7:]:
            if line.strip():
                if line.startswith("-"): # stop reading file once exodia/synergy stats are finished
                    break
                if line.startswith("Flushes:"):
                    data["flushes"] = int(line.split(":")[1].split("-")[0].strip())
                    eval = "flush"
                    continue
                if line.startswith("Letter"):
                    data["synergies"] = int(line.split(":")[1].strip())
                    eval = "letter"
                    continue
                if eval == "exodia": # read variable-length list under exodia
                    exodia_mark, count = line.strip().split(":")
                    data["exodia letters"][exodia_mark.strip()] = int(count.split("-")[0].strip())
                elif eval == "flush": # exodia reading finished, read variable length list under flushes
                    flush_rating, count = line.strip().split(":")
                    data["flush ratings"][flush_rating.strip()] = int(count.split("-")[0].strip())
                elif eval == "letter": # flush reading finished, read variable length list under letter synergies
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
        if game.flush:
            data["flushes"] += 1
            data["flush ratings"][Idol.RATINGS[game.flush.roster[0].rating][1]] = data["flush ratings"].get(Idol.RATINGS[game.flush.roster[0].rating][1], 0) + 1 # add flush rating
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
    for exodia_key in data["exodia letters"]:
        exodia_percentage = round(data["exodia letters"][exodia_key] / data["exodias"] * 100, 2) if data["exodias"] != 0 else 0.0
        new_data.append(f'\t{exodia_key}: {data["exodia letters"][exodia_key]} - ({exodia_percentage}%)\n')
    new_data.append(f'\nFlushes: {data["flushes"]} - ({round(data["flushes"] / data["total games"] * 100, 2)}%)\n')
    for flush_key in data["flush ratings"]:
        flush_percentage = round(data["flush ratings"][flush_key] / data["flushes"] * 100, 2) if data["flushes"] != 0 else 0.0
        new_data.append(f'\t{flush_key}: {data["flush ratings"][flush_key]} - ({flush_percentage}%)\n')
    new_data.append(f'\nLetter Synergies: {data["synergies"]}\n')
    for letter_key in data["letters"]:
        synergy_percentage = round(data["letters"][letter_key] / data["synergies"] * 100, 2) if data["synergies"] != 0 else 0.0
        new_data.append(f'\t{letter_key}: {data["letters"][letter_key]} - ({synergy_percentage}%)\n')

    with open(game_stats, 'w') as f:
        f.writelines(new_data)
        f.writelines(find_distribution()) 
    
    write_idol_stats(game)

def find_distribution() -> str: # finds distribution info of entire idol pool
    rating_counts, letter_counts = [0] * 8, [0] * 26
    with open(all_idol_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            rating_counts[int(line.strip()[-1]) - 1] += 1 # add to rating stats
            letter_counts[ord(line[0].lower()) - ord('a')] += 1 # add to letter stats
    idol_count = len(lines)
    
    rating_string, letter_string = '', ''
    grand_string = f'\n{"-" * 30}'
    grand_string += f'\nIDOL DISTRIBUTION INFORMATION\nTotal Idols: {idol_count}\n\nRATING DISTRIBUTION\n'
    for i in range(len(rating_counts)):
        rating_string += f'{Idol.RATINGS[i + 1][1]}: {rating_counts[i]} - ({round(rating_counts[i] / idol_count * 100, 2)}%)\n'
    grand_string += f'{rating_string}\nLETTER DISTRIBUTION\n'
    for i in range(len(letter_counts)):
        letter_string += f'{chr(i + ord("a")).upper()}: {letter_counts[i]} - ({round(letter_counts[i] / idol_count * 100, 2)}%)\n'
    grand_string += letter_string
    return grand_string

def print_idol(idol: Idol):
    print(f'{idol.to_string()} | Stats: {idol.stats}')

def write_idol_stats(game): # uploads idol stats to json database
    for idol in game.all_idols:
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
                        stats["opp chances"] += idol.stats["opp chances"]
                        stats["gr"] += idol.stats["gr"]
                        
                        if idol.stats["price"] is not None:
                            stats["times bought"] += 1 # total games bought by bidding
                            stats["money spent"] += idol.stats["price"] # total money spent on bidding
                        
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        
def reset_stats(): # resets all idol stats
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
    write_all_idols(True)
    reset_string = """IDOLS 3.5 GAME STATISTICS OVERVIEW

Total Games: 0
Sejun: 0 - (0.0%)
Jason: 0 - (0.0%)

Exodias: 0 - (0.0%)

Flushes: 0 - (0.0%)

Letter Synergies: 0
"""
    
    with open(game_stats, 'w') as f:
        f.write(reset_string)
        f.write(find_distribution())

    card.create_card_collection()
    print("All statistics reset!")
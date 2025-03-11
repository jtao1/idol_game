import os
import json
import shutil
import re
import random
from random import randint
from enum import Enum

def rainbow_text(text): # function to make text rainbow
    colors = [
        "\033[1;38;2;255;67;67m",  # Red
        "\033[1;38;2;255;127;0m",  # Orange
        "\033[1;38;2;255;250;0m",  # Yellow
        "\033[1;38;2;0;255;81m",  # Green
        "\033[1;96m",  # Cyan
        "\033[1;94m",  # Blue
        "\033[1;38;2;169;53;255m", # Purple
        "\033[1;38;2;255;0;222m" # Pink
    ]
    reset = "\033[0m"
    return "".join(colors[i % len(colors)] + char for i, char in enumerate(text)) + reset

class Variants(Enum): # represents all the variants that idols can spawn in
    AFIT = "\033[1;38;2;255;0;222m(AFIT)"
    IBONDS = "\033[1;38;2;255;190;0m(I-Bonds)"
    ELIGE = "\033[1;38;2;255;127;0m(Elige)"
    GAMBLER = "\033[1;38;2;133;187;101m(Gambler)"
    EVOLVING = "\033[1;38;2;0;255;81m(Evolving)"
    BULLY = "\033[1;38;2;165;100;0m(Bully)"
    WILDCARD = rainbow_text("(WILDCARD)")
    COLLECTIBLE = "\033[1;38;2;0;255;218m(TCG)"

class Idol: # class to represent an idol
    RATINGS = { # dictionary for all possible ratings of all idol [color, rating name]
        9: ["", "Hackclaw", 0], # secret rating
        8: ["\033[38;2;255;0;116m", "The Big 3", 0.01],
        7: ["\033[38;2;255;111;237m", "910", 0.05],
        6: ["\033[38;2;169;53;255m", "Luka Doncic", 0.10],
        5: ["\033[38;2;206;155;255m", "Jason Taytum", 0.2],
        4: ["\033[38;2;112;146;255m", "Passion UA", 0.35],
        3: ["\033[38;2;98;197;255m", "Anthony Davis", 0.5],
        2: ["\033[38;2;156;190;210m", "Lower AD", 0.60],
        1: ["\033[38;2;149;150;153m", "Dychas", 0.75],
        0: ["\033[0m", "Unrated"]
    }
    c_good = "\033[38;2;133;187;101m"
    c_bad = "\033[38;2;224;102;102m"
    c_info = "\033[38;2;245;255;0m"
    c_reset = "\033[0m"
    bully_chance = 0.25 # chance that a bully variant idol bullies someone

    def __init__(self, name, group, age, rating, country): # constructor
        self.name = name
        self.group = group
        self.age = age
        self.rating = rating
        self.country = country
        self.variant = None
        self.wildcard = None
        self.winrate = 0 # bonus winrate if idol has GAMBLER variant
        self.protected = False # group rerolls, ult biases, and synergies protect idols

        self.stats = { # contains information to determine idol statistics
            "win": False, # true if on winning team
            "price": None, # set to integer of price if idol is bought through bidding
            "reroll": 0, # +1 if rerolled, dr, replace, or upgrade
            "opp reroll": 0, # +1 if opponent rerolled
            "opp chances": 0, # number of chances for opponent to reroll
            "gr": 0, # +1 if group rerolled
        }

    def to_string(self): # string representation
        string = f'{self.name} | {self.group}'
        if self.rating == 9:
            string = rainbow_text(string)
        if self.protected:
            string = string[:string.index('|')] + '(PR) ' + string[string.index('|'):]
        if self.variant:
            string = string[:string.index('|')] + f'{self.variant.value}{Idol.c_reset}{Idol.RATINGS[self.rating][0]} ' + string[string.index('|'):]
            if self.wildcard:
                string = string[:string.index('|')] + f'({self.wildcard}) ' + string[string.index('|'):]
        return f'{Idol.RATINGS[self.rating][0]}{string}{Idol.c_reset}'
    
    def clean_name(self): # prints out clean name of idol without any tags
        if self.rating == 9:
            return rainbow_text(f'{self.name} | {self.group}')
        return f'{Idol.RATINGS[self.rating][0]}{self.name} | {self.group}{Idol.c_reset}'

    def equals(self, compare: "Idol") -> bool: # custom equals command
        return self.name == compare.name and self.group == compare.group
    
    def ult_value(self): # return value for when chosen as ultimate bias
        if self.rating <= 5:
            return self.rating - 5
        else:
            return self.rating - 4
        
    def idol_info(self): # command to print out information for an idol
        string = f"""
------------------------------------------
Info for {self.clean_name()}
Group: {Idol.c_info}{self.group}{Idol.c_reset}
Age: {Idol.c_info}{self.age}{Idol.c_reset}
Nationality: {Idol.c_info}{self.country}{Idol.c_reset}
Rating: {Idol.RATINGS[self.rating][0]}{Idol.RATINGS[self.rating][1]}{Idol.c_reset}
------------------------------------------
""".strip()
        print(string)
        
    def idol_stats(self): # command to print out statistics for an idol
        with open("./info/game_statistics.txt", 'r') as f:
            lines = f.readlines()
            game_count = int(lines[2].split(':')[1].strip()) # retrieve total amount of games

        groups = self.group.upper().split('/')
        file_path = f'./girl groups/{groups[0]}.json'
        with open(file_path, 'r') as f: 
            data = json.load(f)
            for member in data["members"]: # retrieve stats of specified idol
                if self.name == member["name"]:
                    stats = member["stats"]
        
        no_stat = f'{Idol.c_info}N/A'

        # percentage of total games that the idol appears in some form
        game_presence = stats["games"] / game_count * 100 if game_count else 0
        # winrate of idol
        winrate = stats["wins"] / stats["games"] * 100 if stats["games"] else no_stat
        # pickrate for ultimate bias
        avg_price = round(stats["money spent"] / stats["times bought"], 2) if stats["times bought"] else no_stat
        # reroll rate per game they appear in
        reroll_rate = stats["reroll"] / stats["games"] * 100 if stats["games"] else no_stat
        # opponent reroll rate per game they appear in
        opp_rate = stats["opp reroll"] / stats["opp chances"] * 100 if stats["opp chances"] else no_stat
        # group reroll rate per game they appear in
        gr_rate = stats["gr"] / stats["games"] * 100 if stats["games"] else no_stat

        # set color of number depending on whether stat is good or not
        if avg_price != no_stat:
            if avg_price >= 0:
                avg_price = f'{Idol.c_good}${avg_price:.2f}'
            else:
                avg_price = f'{Idol.c_bad}${avg_price:.2f}'
        if reroll_rate != no_stat:
            if reroll_rate >= 50:
                reroll_rate = f'{Idol.c_bad}{reroll_rate:.1f}%'
            else:
                reroll_rate = f'{Idol.c_good}{reroll_rate:.1f}%'
        if winrate != no_stat:
            if winrate >= 50:
                winrate = f'{Idol.c_good}{winrate:.1f}%'
            else:
                winrate = f'{Idol.c_bad}{winrate:.1f}%'
        if opp_rate != no_stat:
            if opp_rate >= 50:
                opp_rate = f'{Idol.c_good}{opp_rate:.1f}%'
            else:
                opp_rate = f'{Idol.c_bad}{opp_rate:.1f}%'
        if gr_rate != no_stat:
            gr_rate = f'{gr_rate:.1f}%'

        string = f"""
------------------------------------------
Stats for {self.clean_name()}
Game Presence: {Idol.c_info}{game_presence:.1f}%{Idol.c_reset}
Winrate: {winrate}{Idol.c_reset}
Average Price: {avg_price}{Idol.c_reset}
Reroll Rate: {reroll_rate}{Idol.c_reset}
Opponent Reroll Rate: {opp_rate}{Idol.c_reset}
Group Reroll Rate: {Idol.c_info}{gr_rate}{Idol.c_reset}
------------------------------------------
        """.strip()
        print(string)

def remove_ansi(text): # remove ansi codes from any string
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)
    
def determine_variant(idol: Idol, chance: float): # function to add variants to idols
    if random.random() < chance: # chance is a float less than 1, represents percentage chance to hit variant
        idol.variant = random.choice(list(Variants))
    if idol.variant == Variants.AFIT: # increase rating if variant is AFIT
        idol.rating += 1

def multigroup(idol: Idol): # function to handle idols with multiple groups (mainly IZONE)
        if any(sub in idol.to_string() for sub in ["Sakura", "Chaewon | LE SSERAFIM", "Chaewon | IZONE"]):
            idol.group = "LE SSERAFIM/IZONE"
        elif any(sub in idol.to_string() for sub in ["Wonyoung", "Yujin | IVE", "Yujin | IZONE"]):
            idol.group = "IVE/IZONE"
        elif idol.name == "Hyeonju":
            idol.group = "UNIS/CIGNATURE"

def find_idol(name: str, group: str) -> Idol: # find a specific idol and create an Idol object for it

    def find_member(file: str, name: str): # helper function to search for a member in a group file
        with open(file, 'r') as f:
            data = json.load(f)
            for i in range(len(data["members"])):
                for member in data["members"]:
                    if name.lower() == member["name"].lower():
                        return {
                            "name": member["name"],
                            "group": data["group"]["name"],
                            "age": member["age"],
                            "rating": member["rating"],
                            "country": member["country"]
                        }
        return None

    idol = None
    if group and group != "stat": # group was specified, find exact idol
        file = f'./girl groups/{group.upper()}.json'
        if os.path.exists(file):
            with open (file, 'r') as f:
                idol_data = find_member(file, name)
                idol = Idol(**idol_data)
                multigroup(idol)
                return idol
    else: # group not specified, search all group files for matching name
        groups = []
        files = os.listdir('./girl groups')
        for file in files:
            idol_data = find_member(os.path.join('./girl groups', file), name)
            if idol_data:
                idol = Idol(**idol_data)
                multigroup(idol)
                if group == "stat": # return first found idol for stat command to prevent extra inputs
                    break
                groups.append(idol_data["group"]) # otherwise ask for which group specifically for things like adding idols/ult biases
        if len(groups) > 1:
            print("Multiple idols detected, please specify which group:")
            for i in range(len(groups)):
                print(f'{i+1}. {groups[i]}')
            while True:
                ans = input("Enter group number: ")
                if 1 <= int(ans) <= (len(groups) + 1):
                    file = f'./girl groups/{groups[int(ans)-1].upper()}.json'
                    idol = Idol(**find_member(file, name))
                    multigroup(idol)
                    return idol
        else:
            return idol

# Rolls a random idol
# group - specifies a specific group to pick a random idol for, used for group rerolls
# times - specifies amount of idols to roll, used for deluxe rerolls
# duplicate - list of idols that rolled idols cannot be a duplicate of
# target_rating - specific rating to be rolled if desired
def random_idol(group: str, times: int, duplicate: list[Idol], target_rating: int) -> list[Idol]: 
    directory = './girl groups' # if type else './boy groups'
    files = os.listdir(directory)
    results = []
    while len(results) < times:
        while True:
            if group: 
                if '/' in group: # IZONE edge case
                    file = random.choice(group.split('/')) + '.json'
                else: # group reroll
                    file = group + '.json'
            else: # random idol
                file = random.choice(files)
            with open(f'./girl groups/{file}', 'r') as f:
                data = json.load(f)
                
                # store idol data from group file
                rand = randint(0, len(data["members"])-1)
                name = data["members"][rand]["name"]
                group_name = data["group"]["name"]
                age = data["members"][rand]["age"]
                rating = data["members"][rand]["rating"]
                country = data["members"][rand]["country"]
                idol = Idol(name, group_name, age, rating, country)
                
                if target_rating and idol.rating != target_rating: # make sure idol is of specified rating
                    continue
                multigroup(idol) # handle izone edge cases
                if not duplicate or not any(idol.equals(compare) for compare in duplicate): # check if in duplicate loop
                    if not any(idol.equals(comp) for comp in results):
                        results.append(idol)
                        break
    return results
 
def true_random(duplicate: list[Idol]) -> Idol: # rolls a truly random idol from the pool without picking group first
    file = './info/all_idols.txt'
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    while True:
        line = random.choice(lines).strip()
        if line:
            idol = find_idol(line.split('|')[0].strip(), line.split('|')[1].split('/')[0].strip())
            if not duplicate or not any(idol.equals(compare) for compare in duplicate):
                return idol

def move_files(old_dir: str, new_dir: str): # Moves all group files to a different directory
    files = os.listdir(old_dir)
    for file in files:
        path = os.path.join(old_dir, file)
        with open(path, 'r') as f:
            data = json.load(f)
        determinant = 'gg' # if type else 'bg'
        if data['group-type'] == determinant:
            shutil.move(path, os.path.join(new_dir, file))
    print("Moved all group files")
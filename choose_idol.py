import os
import random
from random import randint
import json
import shutil
import re
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

class Idol: # class to represent an idol
    RATINGS = { # dictionary for all possible ratings of all idol [color, rating name]
        9: ["", "m0e", 0], # secret rating
        8: ["\033[38;2;255;0;116m", "The Big 3", 0.01],
        7: ["\033[38;2;255;111;237m", "910", 0.05],
        6: ["\033[38;2;169;53;255m", "Luka Doncic", 0.1],
        5: ["\033[38;2;206;155;255m", "Jason Taytum", 0.15],
        4: ["\033[38;2;112;146;255m", "Passion UA", 0.2],
        3: ["\033[38;2;98;197;255m", "Anthony Davis", 0.3],
        2: ["\033[38;2;156;190;210m", "Lower AD", 0.4],
        1: ["\033[38;2;149;150;153m", "Dychas", 0.5],
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
        self.stats = {
            "price": None, # set to integer of price if idol is bought through bidding
            "reroll": 0, # +1 if rerolled, group rerolled, deluxe rerolled, or replaced
            "gr": False, # true if obtained through group reroll
            "dr": False, # true if obtained through deluxe reroll
            "switch": False, # true if used in a switch powerup
            "stolen": False, # true if stolen during the game
            "letter": False, # true if obtained through letter synergy
            "ult": False # true if chosen as ultimate bias
        }

    def to_string(self): # string representation
        string = f'{self.name} | {self.group}'
        # if self.age < 18:
        #     string = string[:string.index('|')] + '(M) ' + string[string.index('|'):]
        if self.protected:
            string = string[:string.index('|')] + '(PR) ' + string[string.index('|'):]
        if self.variant:
            string = string[:string.index('|')] + f'{self.variant.value}{Idol.c_reset}{Idol.RATINGS[self.rating][0]} ' + string[string.index('|'):]
            if self.wildcard:
                string = string[:string.index('|')] + f'({self.wildcard}) ' + string[string.index('|'):]
        return f'{Idol.RATINGS[self.rating][0]}{string}{Idol.c_reset}'
    
    def clean_name(self): # prints out clean name of idol without any tags
        return f'{Idol.RATINGS[self.rating][0]}{self.name} | {self.group}{Idol.c_reset}'

    def equals(self, compare: "Idol") -> bool: # custom equals command
        return self.name == compare.name and self.group == compare.group
    
    def ult_value(self): # return value for when chosen as ultimate bias
        if self.rating <= 5:
            return self.rating - 4
        else:
            return self.rating - 3
        
    def idol_stats(self): # comamnd to print out stats/information for an idol
        groups = self.group.upper().split('/')
        file_path = f'./girl groups/{groups[0]}.json'
        with open(file_path, 'r') as f:
            data = json.load(f)

            for member in data["members"]:
                if self.name == member["name"]:
                    stats = member["stats"]

        game_counter = [f for f in os.listdir('game files') if f.startswith('game_') and f.endswith(".txt")]
        game_count = len(game_counter) # retrieve total amount of games

        # average price of idol within games they are bought
        avg_price = round(stats["money_spent"] / stats["times_bought"], 2) if stats["times_bought"] else 'N/A'
        # reroll percentage per game they appear in
        reroll_rate = stats["times_rerolled"] / stats["total_games"] * 100 if stats["total_games"] else 'N/A'
        # percentage of total games that the idol appears in some form
        game_presence = stats["total_games"] / game_count * 100 if game_count else 0

        if avg_price != 'N/A':
            if avg_price >= 0:
                avg_price = f'{Idol.c_good}${avg_price:.2f}'
            else:
                avg_price = f'{Idol.c_bad}${avg_price:.2f}'

        if reroll_rate != 'N/A':
            if reroll_rate >= 50:
                reroll_rate = f'{Idol.c_bad}{reroll_rate:.1f}%'
            else:
                reroll_rate = f'{Idol.c_good}{reroll_rate:.1f}%'

        string = f"""
------------------------------------------
Info for {Idol.RATINGS[self.rating][0]}{self.name}{Idol.c_reset}
Group: {Idol.c_info}{self.group}{Idol.c_reset}
Age: {Idol.c_info}{self.age}{Idol.c_reset}
Nationality: {Idol.c_info}{self.country}{Idol.c_reset}
Rating: {Idol.RATINGS[self.rating][0]}{Idol.RATINGS[self.rating][1]}{Idol.c_reset}
------------------------------------------
Stats for {Idol.RATINGS[self.rating][0]}{self.name}{Idol.c_reset}
Average Price: {avg_price}{Idol.c_reset}
Reroll Rate: {reroll_rate}{Idol.c_reset}
Game Presence: {Idol.c_info}{game_presence:.1f}%{Idol.c_reset}
------------------------------------------
        """.strip()
        print(string)

def remove_ansi(text): # remove ansi codes from any string
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)
    
def determine_variant(idol: Idol, chance: float): # function to add variants to idols
    if random.random() < chance: # chance is a float less than 1, represents percentage chance to hit variant
        idol.variant = Variants.WILDCARD # random.choice(list(Variants))
    if idol.variant == Variants.AFIT: # increase rating if variant is AFIT
        idol.rating += 1

def multigroup(idol: Idol): # function to handle idols with multiple groups (mainly IZONE)
        if any(sub in idol.to_string() for sub in ["Sakura", "Chaewon | LE SSERAFIM", "Chaewon | IZONE"]):
            idol.group = "LE SSERAFIM/IZONE"
        elif any(sub in idol.to_string() for sub in ["Wonyoung", "Yujin | IVE", "Yujin | IZONE"]):
            idol.group = "IVE/IZONE"

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

                if target_rating is not None and idol.rating != target_rating: # make sure idol is of specified rating
                    continue
                multigroup(idol) # handle izone edge cases
                if not duplicate or not any(idol.equals(compare) for compare in duplicate): # check if in duplicate loop
                    if not any(idol.equals(comp) for comp in results):
                        results.append(idol)
                        break
    return results

# Rolls a random idol from the list of all idols. This gives every single idol an equal chance of
# being chosen, rather than choosing a random group first like random_idol() does.    
def true_random() -> str:
    file = './all female idols.txt'
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    line = random.choice(lines).strip()
    if int(line[line.rfind("{")+1:line.rfind("}")]) < 18:
        line = line[:line.rfind("|")] + "(M) " + line[line.rfind("|"):]
    return line[:line.rfind('{')-1].strip()

# # Main function to play the game and input game commands
# def manual_game():
#     os.system('cls')
#     res = None
#     while True:
#         command = input("--------->>>  ")
#         command = command.lower().strip()

#         if res and len(res) > 1: # last roll was a DR, no group set for GR
#                 res = None
#                 cur_idol = None
#         else:
#             cur_idol = next(iter(res)) if res is not None else None

#         commands = {
#             "r": lambda: random_idol(None, 1, 1, []),
#             "gr": lambda: random_idol(cur_idol.group if cur_idol else None, 1, 1, [cur_idol] if cur_idol else None),
#             "dr": lambda: random_idol(None, 3, 1, []),
#             "tr": lambda: true_random(),
#             "c": lambda: os.system('cls') or "Invalid",
#             "e": exit,
#             "h": lambda: print("""List of commands:
#             r: reroll
#             gr: group reroll last rolled group
#             dr: deluxe reroll
#             tr: true random reroll
#             c: clear console
#             e: quit game"""),
#         }

#         res = commands.get(command, lambda: res)()
#         if command in ["r", "gr", "dr", "tr"]:
#             print("\n".join([idol.to_string() for idol in res]))

# old - Old directory of all group files
# new - New directory of all group files         
def move_files(old: str, new: str): # Moves all group files to a different directory
    files = os.listdir(old)
    for file in files:
        path = os.path.join(old, file)
        with open(path, 'r') as f:
            data = json.load(f)
        determinant = 'gg' # if type else 'bg'
        if data['group-type'] == determinant:
            shutil.move(path, os.path.join(new, file))
    print("Moved all group files")

# sort - True for sorting alphabetically, False for sorting by group
# name - Name of file to write all idols to
def write_all_idols(sort: bool, name: str): # Writes all idols to a single file
    search = './girl groups' # if type else './boy groups'
    files = os.listdir(search)
    rating_counts, letter_counts = [0] * 8, [0] * 26
    with open(name, 'w', encoding="utf-8") as output:
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
                    rating_counts[idol.rating - 1] += 1 # add to rating stats
                    letter_counts[ord(idol.name[0].lower()) - ord('a')] += 1 # add to letter stats
                    idols.append(remove_ansi(f'{idol.to_string()} | {rating}\n'))
        if sort:
            idols.sort()

        rating_string, letter_string = '', ''
        for i in range(len(rating_counts)):
            rating_string += f'{Idol.RATINGS[i + 1][1]}: {rating_counts[i]}\n'
        for i in range(len(letter_counts)):
            letter_string += f'{chr(i + ord("a"))}: {letter_counts[i]}\n'
        idols.append(rating_string)
        idols.append(letter_string)
        output.writelines(idols)
    print(f'Wrote all idols from "{search}" to a single file')

# write_all_idols(True, "all female idols.txt")
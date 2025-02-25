import os
import random
from random import randint
import json
import shutil

class Idol: # class to represent an idol
    RATINGS = { # dictionary for all possible ratings of all idol [color, rating]
        8: ["\033[38;2;255;0;116m", "The Big 3"],
        7: ["\033[38;2;255;111;237m", "910"], 
        6: ["\033[38;2;169;53;255m", "Luka Doncic"],
        5: ["\033[38;2;206;155;255m", "Jason Taytum"],
        4: ["\033[38;2;112;146;255m", "Passion UA"], 
        3: ["\033[38;2;98;197;255m", "Anthony Davis"], 
        2: ["\033[38;2;156;190;210m", "Lower AD"],
        1: ["\033[38;2;149;150;153m", "Dychas"], 
        0: ["\033[0m", "Unrated"] 
    }
    c_good = "\033[38;2;133;187;101m"
    c_bad = "\033[38;2;224;102;102m"
    c_info = "\033[38;2;245;255;0m"
    c_reset = "\033[0m"

    def __init__(self, name, group, age, rating, country): # constructor
        self.name = name
        self.group = group
        self.age = age
        self.rating = rating
        self.country = country
        self.stats = {
            "price": None,
            "reroll": 0,
            "gr": False,
            "dr": False,
            "switch": False,
            "letter": False,
            "ult": False
        }
        self.protected = False # group rerolls protect idols

    def to_string(self): # string representation
        string = f'{self.name} | {self.group}'
        if self.age < 18:
            string = string[:string.index('|')] + '(M) ' + string[string.index('|'):]
        if self.protected:
            string = string[:string.index('|')] + '(PR) ' + string[string.index('|'):]
        return f'{Idol.RATINGS[self.rating][0]}{string}{Idol.c_reset}'
    
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

# Moves all group files to a different directory
# old - Old directory of all group files
# new - New directory of all group files
# type - True for girl groups only, False for boy groups only            
def move_files(old: str, new: str, type: bool):
    files = os.listdir(old)
    for file in files:
        path = os.path.join(old, file)
        with open(path, 'r') as f:
            data = json.load(f)
        determinant = 'gg' if type else 'bg'
        if data['group-type'] == determinant:
            shutil.move(path, os.path.join(new, file))
    print("Moved all group files")

# Writes all idols to a single file
# sort - True for sorting alphabetically, False for sorting by group
# type - True for girl groups, False for boy groups
# name - Name of file to write all idols to
def write_all_idols(sort: bool, type: bool, name: str):
    search = './girl groups' if type else './boy groups'
    files = os.listdir(search)
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
                    idols.append(f'{idol.to_string()} | {rating}\n')
        if sort:
            idols.sort()
        output.writelines(idols)
    print(f'Wrote all idols from "{search}" to a single file')

def multigroup(idol: Idol): # function to handle idols with multiple groups (mainly IZONE)
        if idol.name in ["Sakura", "Chaewon"]: # IZONE edge cases
            idol.group = "LE SSERAFIM/IZONE"
        elif any(sub in idol.to_string() for sub in ["Wonyoung", "Yujin | IVE", "Yujin | IZONE"]):
            idol.group = "IVE/IZONE"

def find_idol(name: str, group: str) -> Idol:
    file = f'./girl groups/{group.upper()}.json'
    idol = None
    if os.path.exists(file):
        with open (file, 'r') as f:
            data = json.load(f)
            for i in range(len(data["members"])):
                if name.lower() == data["members"][i]["name"].lower():
                    name = data["members"][i]["name"]
                    group = data["group"]["name"]
                    age = data["members"][i]["age"]
                    rating = data["members"][i]["rating"]
                    country = data["members"][i]["country"]
                    idol = Idol(name, group, age, rating, country)
                    multigroup(idol)
                    break
    return idol

# Rolls a random idol
# group - specifies a specific group to pick a random idol for, used for group rerolls
# times - specifies amount of idols to roll, used for deluxe rerolls
# type - (UNUSED) True for girl groups, False for boy groups
# duplicate - list of idols that rolled idols cannot be a duplicate of
def random_idol(group: str, times: int, duplicate: list[Idol]) -> list[Idol]: 
    directory = './girl groups' # if type else './boy groups'
    files = os.listdir(directory)
    results = []
    while len(results) < times:
        file = (group + ".json") if group else random.choice(files)
        with open(f'./girl groups/{file}', 'r') as f:
            data = json.load(f)
            rand = randint(0, len(data["members"])-1)
            name = data["members"][rand]["name"]
            group_name = data["group"]["name"]
            age = data["members"][rand]["age"]
            rating = data["members"][rand]["rating"]
            country = data["members"][rand]["country"]
            idol = Idol(name, group_name, age, rating, country)
            if not duplicate or not any(idol.equals(compare) for compare in duplicate):
                if not any(idol.equals(comp) for comp in results):
                    results.append(idol)
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

# Main function to play the game and input game commands
def manual_game():
    os.system('cls')
    res = None
    while True:
        command = input("--------->>>  ")
        command = command.lower().strip()

        if res and len(res) > 1: # last roll was a DR, no group set for GR
                res = None
                cur_idol = None
        else:
            cur_idol = next(iter(res)) if res is not None else None

        commands = {
            "r": lambda: random_idol(None, 1, 1, []),
            "gr": lambda: random_idol(cur_idol.group if cur_idol else None, 1, 1, [cur_idol] if cur_idol else None),
            "dr": lambda: random_idol(None, 3, 1, []),
            "tr": lambda: true_random(),
            "c": lambda: os.system('cls') or "Invalid",
            "e": exit,
            "h": lambda: print("""List of commands:
            r: reroll
            gr: group reroll last rolled group
            dr: deluxe reroll
            tr: true random reroll
            c: clear console
            e: quit game"""),
        }

        res = commands.get(command, lambda: res)()
        if command in ["r", "gr", "dr", "tr"]:
            print("\n".join([idol.to_string() for idol in res]))

# write_all_idols(False, 1, "all female idols.txt")
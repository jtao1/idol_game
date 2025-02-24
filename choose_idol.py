import os
import random
from random import randint
import json
import shutil

class Idol: # class to represent an idol
    reset = "\033[0m" # reset color (white)
    COLORS = {
        8: "\033[38;2;255;0;116m", # The Big 3
        7: "\033[38;2;255;111;237m", # 910
        6: "\033[38;2;169;53;255m", # Luka DOncic
        5: "\033[38;2;206;155;255m", # Jason Taytum
        4: "\033[38;2;112;146;255m", # Passion UA
        3: "\033[38;2;98;197;255m", # Anthony Davis
        2: "\033[38;2;156;190;210m", # Lower AD
        1: "\033[38;2;149;150;153m", # Dycha
        0: reset
    }

    def __init__(self, name, group, age, rating):
        self.name = name
        self.group = group
        self.age = age
        self.rating = rating
        self.protected = False # group rerolls protect idols

    def to_string(self):
        string = ''
        if self.age < 18:
            string = f'{self.name} (M) | {self.group}'
        else:
            string = f'{self.name} | {self.group}'
        if self.protected:
            string = "(PR) " + string
        return f'{Idol.COLORS[self.rating]}{string}{Idol.reset}'
    
    def equals(self, compare: "Idol") -> bool:
        return self.name == compare.name and self.group == compare.group
    
    def ult_value(self):
        if self.rating == 8:
            return 6
        else:
            return self.rating - 3

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
                    idol = Idol(name, group, age, rating)
                    idols.append(f'{idol.to_string()} | {rating}\n')
        if sort:
            idols.sort()
        output.writelines(idols)
    print(f'Wrote all idols from "{search}" to a single file')

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
                    idol = Idol(name, group, age, rating)
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
    results = set()
    while len(results) < times:
        file = (group + ".json") if group else random.choice(files)
        with open(f'./girl groups/{file}', 'r') as f:
            data = json.load(f)
            rand = randint(0, len(data["members"])-1)
            name = data["members"][rand]["name"]
            group_name = data["group"]["name"]
            age = data["members"][rand]["age"]
            rating = data["members"][rand]["rating"]
            idol = Idol(name, group_name, age, rating)

            if not duplicate or not any(idol.equals(compare) for compare in duplicate):
                results.add(idol)
    final = list(results)
    return final

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

# print(f'{Idol.COLORS[8]}Julie')
# print(f'{Idol.COLORS[7]}Nana')
# print(f'{Idol.COLORS[6]}Sakura')
# print(f'{Idol.COLORS[5]}Chaeyoung')
# print(f'{Idol.COLORS[4]}Kotoko')
# print(f'{Idol.COLORS[3]}Sieun')
# print(f'{Idol.COLORS[2]}Mimimeister')
# print(f'{Idol.COLORS[1]}Hwasa')
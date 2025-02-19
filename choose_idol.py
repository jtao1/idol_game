import os
import random
import json
import pandas as pd
import numpy as np
import shutil

class Idol: # class to represent an idol
    def __init__(self, name, group, age):
        self.name = name
        self.group = group
        self.age = age
        self.rating = None
        self.protected = False # group rerolls protect idols

    def to_string(self):
        string = self.name + " | " + self.group
        if self.age < 18:
            string = self.name + " (M) | " + self.group
        return string
    
    def equals(self, compare: "Idol") -> bool:
        return self.name == compare.name and self.group == compare.group and self.age == compare.age

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
                dict_data = next((value for key, value in data.items() if isinstance(value, dict)), None)
                df = pd.DataFrame(list(dict_data.items()), columns=['Name', 'Info'])
                for _, row in df.iterrows():
                    idols.append(row['Name'] + " | " + data['group name'] + " {" + str(row['Info']) + '}\n')
        if sort:
            idols.sort()
        output.writelines(idols)
    print(f'Wrote all idols from "{search}" to a single file')

# Rolls a random idol
# group - specifies a specific group to pick a random idol for, used for group rerolls
# times - specifies amount of idols to roll, used for deluxe rerolls
# type - True for girl groups, False for boy groups
# duplicate - list of idols that rolled idols cannot be a duplicate of
def random_idol(group: str, times: int, type: bool, duplicate: list[Idol]) -> list[Idol]: 
    directory = './girl groups' if type else './boy groups'
    files = os.listdir(directory)
    results = set()
    while len(results) < times:
        file = (group.upper() + ".json") if group else random.choice(files)
        with open(f'./girl groups/{file}', 'r') as f:
            data = json.load(f)
            dict_data = next((value for key, value in data.items() if isinstance(value, dict)), None)
            df = pd.DataFrame(list(dict_data.items()), columns=['Name', 'Info'])
            row = df.sample()
            idol = Idol(row['Name'].iloc[0], data['group name'], row['Info'].iloc[0])
            # string = f"{row['Name'].iloc[0]} {'(M) |' if row['Info'].iloc[0] < 18 else '|'} {data['group name']}"
            if not duplicate or not any(idol.equals(compare) for compare in duplicate):
                results.add(idol)
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
# manual_game()
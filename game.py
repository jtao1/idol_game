import os
import random
import json
import pandas as pd
import numpy as np
import shutil

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
                    idols.append(row['Name'] + " - " + data['group name'] + " {" + str(row['Info']) + '}\n')
        if sort:
            idols.sort()
        output.writelines(idols)
    print(f'Wrote all idols from "{search}" to a single file')

# Rolls a random idol
# group - specifies a specific group to pick a random idol for, used for group rerolls
# times - specifies amount of idols to roll, used for deluxe rerolls
# type - True for girl groups, False for boy groups
# duplicate - notes a specific idol to avoid a duplicate roll of, used for group rerolls
def random_idol(group: str, times: int, type: bool, duplicate: str) -> str: 
    directory = './girl groups' if type else './boy groups'
    files = os.listdir(directory)
    results = set()
    while len(results) < times:
        file = (group.upper() + ".json") if group else random.choice(files)
        try:
            with open(f'./girl groups/{file}', 'r') as f:
                data = json.load(f)
                dict_data = next((value for key, value in data.items() if isinstance(value, dict)), None)
                df = pd.DataFrame(list(dict_data.items()), columns=['Name', 'Info'])
                row = df.sample()
                string = f"{row['Name'].iloc[0]} {'(M) -' if row['Info'].iloc[0] < 18 else '-'} {data['group name']}"
                if string != duplicate:
                    results.add(string)
        except FileNotFoundError:
            return "Invalid group"
    return '\n'.join(results)

# Rolls a random idol from the list of all idols. This gives every single idol an equal chance of
# being chosen, rather than choosing a random group first like random_idol() does.    
def true_random() -> str:
    file = './all female idols.txt'
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    line = random.choice(lines).strip()
    if int(line[line.find("{")+1:line.find("}")]) < 18:
        line = line[:line.rfind("-")] + "(M) " + line[line.rfind("-"):]
    return line[:line.rfind('{')-1].strip()

# Main function to play the game and input game commands
def play_game():
    os.system('cls')
    idol = "Invalid"
    while True:
        command = input("--------->>>  ")
        command = command.lower().strip()

        if command == "r":
            idol = random_idol(None, 1, 1, None)
        elif command == "gr":
            idol = random_idol(idol[idol.rfind('-')+2:], 1, 1, idol)
        elif command == "dr":
            idol = random_idol(None, 3, 1, None)
        elif command == "tr":
            idol = true_random()
        elif command in ["n", "c"]:
            os.system('cls')
            idol = "Invalid"
        elif command in ["e", "exit"]:
            exit()
        elif command in ["h", "help"]:
            print("""List of commands:
            r: reroll
            gr: group reroll last rolled group
            dr: deluxe reroll
            tr: true random reroll
            n or c: clear console
            e or exit: quit game""")
        # elif command.startswith("r "):
        #     idol = random_idol(command[2:], 1, 1, None)

        if command in ["r", "gr", "dr", "tr"]:
            print(idol)

# write_all_idols(1, 1, "all female idols.txt")
play_game()
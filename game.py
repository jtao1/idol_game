import os
import random
import json
import pandas as pd
import numpy as np
import shutil

# def choose_rand_idol(type: str) -> list:
#     files = os.listdir('./groups')
#     while True:
#         random_file = random.choice(files)
#         with open(f'./groups/{random_file}', 'r') as f:
#             data = json.load(f)
#             if data['group-type'] == type:
#                 vote_data = pd.DataFrame(list(data['votes'].items()), columns=['Name', 'Votes'])
#                 vote_data.sort_values(by='Votes')
#                 #print(vote_data)
#                 row = vote_data.sample()
#                 idol = row['Name'].iloc[0]
#                 idol_votes = row['Votes'].iloc[0]
#                 total_votes = vote_data['Votes'].sum()
#                 share = idol_votes / total_votes
#                 adj_share = idol_votes / total_votes / np.log(vote_data.shape[0])
#                 return idol, idol_votes, data['name'], data['voters'], share, adj_share
            
def move_files():
    files = os.listdir('groups')
    for file in files:
        path = os.path.join('groups', file)
        with open(path, 'r') as f:
            data = json.load(f)
        if data['group-type'] == 'gg':
            shutil.copy(path, os.path.join('girl groups', file))
            os.remove(path)
    print("moved all group files")

def write_all_idols(sort: bool): # write all idols to a single file
    files = os.listdir('./girl groups')
    with open(f'./all female idols.txt', 'w', encoding="utf-8") as output:
        sorted = []
        for file in files:
            print(file)
            with open(f'./girl groups/{file}', 'r') as f:
                data = json.load(f)
                dict_data = next((value for key, value in data.items() if isinstance(value, dict)), None)
                df = pd.DataFrame(list(dict_data.items()), columns=['Name', 'Info'])
                for _, row in df.iterrows():
                    name = row['Name']
                    age = row['Info']
                    string = name + " - " + data['group name'] + " (" + str(age) + ')\n'
                    if sort:
                        sorted.append(string)
                    else:
                        output.write(string)
        if sort:
            sorted.sort()
            for a in sorted:
                output.write(a)
    print("wrote all idols to file")

def random_idol(group: str, times: int) -> str:
    files = os.listdir('./girl groups')
    results = set()
    while len(results) < times:
        if group != "":
            file = group.upper() + ".json"
        else:
            file = random.choice(files)
        try:
            with open(f'./girl groups/{file}', 'r') as f:
                data = json.load(f)
                dict_data = next((value for key, value in data.items() if isinstance(value, dict)), None)
                df = pd.DataFrame(list(dict_data.items()), columns=['Name', 'Info'])
                row = df.sample()
                idol = row['Name'].iloc[0]
                if row['Info'].iloc[0] < 18:
                    string = idol + " (M) - " + data['group name']
                else:
                    string = idol + " - " + data['group name']
                # if "(former member)" in string.lower() and group != "":
                #     continue
                results.add(string)
        except FileNotFoundError:
            return "Invalid group"
    return '\n'.join(results)
    
def true_random() -> str:
    file = './all female idols.txt'
    with open(file, 'r') as f:
        lines = f.readlines()
    return random.choice(lines).strip()

def play_game():
    os.system('cls')
    while True:
        command = input("--------->>>  ")
        command = command.lower()

        if command.strip() == "r":
            print(random_idol("", 1))
        elif command.startswith("r "):
            print(random_idol(command[2:], 1))
        elif command.strip() == "dr":
            print(random_idol("", 3))
        elif command.strip() == "tr":
            print(true_random())
        elif command.strip() in ["n", "c"]:
            os.system('cls')
        elif command.strip() in ["e", "exit"]:
            exit()
        elif command.strip() in ["h", "help"]:
            print("""List of commands:
            r: reroll
            r (group): group reroll
            dr: deluxe reroll
            tr: true random reroll
            n or c: clear console
            e or exit: quit game""")

# write_all_idols(False)
play_game()

# WRITING RANDOM IDOL SAMPLES TO FILE TO CHECK DISTRIBUTION
# for i in range(5):
#     with open('stats', 'a') as f:
#         var = choose_rand_idol('gg')
#         f.write(f"{var[0]} | {var[2]}\n")

# data = []
# group = []
# idols = set()
# num_voters = 0
# while len(data) < 25:
#     idol, idol_vote, group, voters, share, adj_share = choose_rand_idol('gg')
#     if idol not in idols:
#         data.append({
#             'idols': idol,
#             'idol_votes': idol_vote,
#             'groups': group,
#             'group_voters': voters,
#             'idol_share': share * 0.25,
#             'adj_share': adj_share
#         })
#         num_voters += voters
#         idols.add(idol)

# df = pd.DataFrame(data)

# rank = [[], [], [], [], []]
# adj = [[], [], [], [], []]

# df['group_share'] = df['group_voters'] / num_voters
# df['rank'] = (df['idol_share']) + df['group_share']
# df['adj_rank'] = df['adj_share'] * df['group_share']

# df.sort_values(by='rank', ascending=False, inplace=True)
# df = df.reset_index(drop=True)
# df['tier'] = (df.index // 5) + 1
# df = df.set_index('tier')

# for i in range(len(df['idols'].values)):
#     if i % 5 == 0 and i != 0:
#         print()
#     if i % 5 == 0:
#         print(f'tier {(i // 5) + 1}: ', end='')
#     print(df['idols'].values[i], end=', ')    

# df.sort_values(by='adj_rank', ascending=False, inplace=True)
# df = df.reset_index(drop=True)
# df['tier'] = (df.index // 5) + 1
# df = df.set_index('tier')

# print('\n')

# for i in range(len(df['idols'].values)):
#     if i % 5 == 0 and i != 0:
#         print()
#     if i % 5 == 0:
#         print(f'tier {(i // 5) + 1}: ', end='')
#     print(df['idols'].values[i], end=', ')

# print('\n')
# print(df)
import json
import os
import random
import time
from enum import Enum

import choose_idol as choose
from choose_idol import Idol
from choose_idol import Perks

class rarities(Enum):
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    LEGENDARY = "LEGENDARY"

class Card:
    reset = "\033[0m"
    stat = "\033[38;2;255;250;0m"
    colors = {
        rarities.COMMON: "\033[1;38;2;0;134;65m",
        rarities.UNCOMMON: "\033[1;38;2;0;109;168m",
        rarities.RARE: "\033[1;38;2;189;141;0m",
        rarities.LEGENDARY: "\033[1;38;2;194;40;40m"
    }

    def __init__(self, idol: Idol, rarity: rarities):
        self.idol = idol
        self.rarity = rarity
        self.color = self.colors[rarity]

    def to_string(self):
        return f'{self.idol.clean_name()} - {self.color}{self.rarity.value}{self.reset}'

class Booster:
    booster_filters = {
        "Standard": lambda idol: True, # can contain any idol
        "Minor": lambda idol: idol.age < 18,
        "Foreigner": lambda idol: idol.country != "Korean",
        "3rd Gen": lambda idol: any(group in idol.group.upper() for group in ["BLACKPINK", "TWICE", "RED VELVET", "GFRIEND", "MAMAMOO", "OH MY GIRL"]),
        "5th Gen": lambda idol: any(group in idol.group.upper() for group in ["BABYMONSTER", "ILLIT", "KISS OF LIFE", "TRIPLES", "UNIS", "QWER", "FIFTY FIFTY", "RESCENE"]),
        "HYBE": lambda idol: any(group in idol.group.upper() for group in ["ILLIT", "NJZ", "LE SSERAFIM", "GFRIEND", "FROMIS_9"]),
        "JYP": lambda idol: any(group in idol.group.upper() for group in ["TWICE", "ITZY", "NMIXX"]),
        "SM": lambda idol: any(group in idol.group.upper() for group in ["RED VELVET", "AESPA"]),
        "YG": lambda idol: any(group in idol.group.upper() for group in ["BLACKPINK", "BABYMONSTER"]),
        "Nugu": lambda idol: any(group in idol.group.upper() for group in ["ALICE", "CIGNATURE", "QWER", "WOOAH", "UNIS"]),
        "10 Million+": lambda idol: any(group in idol.group.upper() for group in ["AESPA", "LE SSERAFIM", "TWICE", "BLACKPINK", "NJZ"]),
        # "Passion UA": lambda idol: idol.rating == 4,
        "Jason Taytum": lambda idol: idol.rating == 5,
        "Luka Doncic": lambda idol: idol.rating == 6,
        "910": lambda idol: idol.rating == 7,
        "Big 3": lambda idol: idol.rating == 8
    }

    def __init__(self, type, rarity):
        self.type = type
        self.rarity = rarity
        self.idol = None
        self.color = Card.reset if type == "Standard" else Card.colors[rarity]

    def to_string(self):
        if not self.rarity:
            return f'\033[1m{self.type} Pack{Card.reset}'
        return f'\033[1m{self.color}{self.type} Pack ({self.rarity.value}){Card.reset}'
    
    def equals(self, compare): 
        return self.type == compare.type

def determine_rarity(COM: float, UNC: float, RARE: float) -> rarities: # function to determine rarity of card/pack
    probability = random.random()
    if probability < COM: # card is common
        return rarities.COMMON
    elif probability < UNC: # card is uncommon
        return rarities.UNCOMMON
    elif probability < RARE: # card is rare
        return rarities.RARE
    else: # card is legendary
        return rarities.LEGENDARY

def update_card(player: str, add_card: list[Card]): # function to add a specific card to a collection
    with open(f'./info/{player}_cards.json', 'r') as f:
        data = json.load(f)
        for card in add_card:
            for group in data:
                if group in card.idol.group.upper().split('/'):
                    for member in data[group]:
                        if member == card.idol.name:
                            data[group][member][card.rarity.value] += 1
    with open(f'./info/{player}_cards.json', 'w') as f:
        json.dump(data, f, indent=4)

def single_card(player: str, idol: Idol, testing: bool, chosen_rarity: rarities): # function to roll a single card for an idol and add it to player's collection
    if not chosen_rarity:
        print("Pulling card...")
        time.sleep(1)
        print("\033[F\033[K", end="")

    fresh_idol = choose.find_idol(idol.name, idol.group.split('/')[0]) # find fresh object of idol without any editions
    rarity = chosen_rarity if chosen_rarity is not None else determine_rarity(0.55, 0.85, 0.97)
    add_card = Card(fresh_idol, rarity)
    if not testing:
        update_card(choose.remove_ansi(player), [add_card])
    print(f'{player}{Card.reset} pulled {add_card.to_string()}')

def choose_boosters() -> list[Booster]: # function to retrieve booster pack selection for winner
    boosters = [Booster("Standard", None)] # every selection has a standard pack

    for _ in range(3):
        while True:
            rarity = determine_rarity(0.55, 0.85, 0.97)
            if rarity == rarities.COMMON:
                booster_type = random.choice(["Nugu", "Minor", "Foreigner", "3rd Gen", "5th Gen"])
            elif rarity == rarities.UNCOMMON:
                booster_type = random.choice(["HYBE", "SM", "JYP", "YG", "JT"])
            elif rarity == rarities.RARE:
                booster_type = random.choice(["10 Million+", "LD", "910", "Your Roster"])
            else:
                booster_type = random.choice(["Big 3", "Your Choice"])
            add_booster = Booster(booster_type, rarity)
            if not any(add_booster.equals(boost) for boost in boosters): # prevent duplicate booster packs
                boosters.append(add_booster)
                break
    return boosters

def open_pack(player, pack: Booster, testing: bool): # function to open a booster pack
    dupes = [] # list of dupes so same idol is not pulled multiple times in a pack
    cards = [] # list of cards objects to add
    amount = len(player.roster) if pack.type == "Your Roster" else 3 if pack.type == "Big 3" else 4 if pack.rarity == rarities.UNCOMMON or pack.rarity == rarities.RARE else 5
    if pack.type == "Your Roster":
        random.shuffle(player.roster)
    for i in range(amount):
        while True:
            if pack.type == "Your Roster":
                idol = player.roster[i]
            elif pack.type == "Your Choice":
                idol = pack.idol
            else:
                idol = choose.true_random(dupes)
                if not Booster.booster_filters[pack.type](idol):
                    continue # if idol doesn't fit booster pack criteria, reroll
            break
            
        if i == amount - 1: # if last card of pack, guarantee rare
            rarity = determine_rarity(0, 0, 0.9)
        else:
            rarity = determine_rarity(0.55, 0.85, 0.97)
        cards.append(Card(idol, rarity))
        if pack.type != "Your Choice":
            dupes.append(idol)

    for card in cards:
        print("Opening pack...")
        if card.rarity == rarities.RARE:
            time.sleep(2)
        elif card.rarity == rarities.LEGENDARY:
            time.sleep(3.5)
        else:
            time.sleep(1)
        print("\033[F\033[K", end="")
        print(card.to_string())

    if not testing:
        update_card(choose.remove_ansi(player.name), cards)

def collection_info(player, idol: Idol): # display card collection info of a specific idol
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    common_count = data[idol.group.upper().split('/')[0]][idol.name]["COMMON"]
    uncommon_count = data[idol.group.upper().split('/')[0]][idol.name]["UNCOMMON"]
    rare_count = data[idol.group.upper().split('/')[0]][idol.name]["RARE"]
    legendary_count = data[idol.group.upper().split('/')[0]][idol.name]["LEGENDARY"]
    completed = "\033[1;38;2;255;250;0m(COMPLETED)" if discount_check(choose.remove_ansi(player.name), idol) else ""
    string = f"""
------------------------------------------
{player.name}'s{Card.reset} collection info for {idol.clean_name()} {completed}{Card.reset}
{Card.colors[rarities.COMMON]}Common:{Card.reset} {Card.stat}{common_count}{Card.reset}
{Card.stat}{round(common_count * 0.1, 1)}%{Card.reset} increased roll rate
{Card.colors[rarities.UNCOMMON]}Uncommon:{Card.reset} {Card.stat}{uncommon_count}{Card.reset}
{Card.stat}{uncommon_count * 2}%{Card.reset} increased upgrade rate
{Card.colors[rarities.RARE]}Rare:{Card.reset} {Card.stat}{rare_count}{Card.reset}
{Card.stat}{rare_count * 3}%{Card.reset} increased combat rate
{Card.colors[rarities.LEGENDARY]}Legendary:{Card.reset} {Card.stat}{legendary_count}{Card.reset}
{Card.stat}{legendary_count * 10}%{Card.reset} chance to roll on first turn when chosen as ultimate bias
------------------------------------------
    """.strip()
    print(string)

def total_collection(player): # display overall collection info for a player
    common, uncommon, rare, legendary = [], [], [], []
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    for group in data:
        for member in data[group]:
            idol = choose.find_idol(member, group)
            if not any(idol.equals(comp[0]) for comp in common + uncommon + rare + legendary): # avoid multigroup duplicates
                if data[group][member]["COMMON"] > 0:
                    common.append([idol, data[group][member]["COMMON"]])
                if data[group][member]["UNCOMMON"] > 0:
                    uncommon.append([idol, data[group][member]["UNCOMMON"]])
                if data[group][member]["RARE"] > 0:
                    rare.append([idol, data[group][member]["RARE"]])
                if data[group][member]["LEGENDARY"] > 0:
                    legendary.append([idol, data[group][member]["LEGENDARY"]])
    common.sort(key=lambda x: (x[1], x[0].rating), reverse=True) # sort by card amount, then by rating
    uncommon.sort(key=lambda x: (x[1], x[0].rating), reverse=True)
    rare.sort(key=lambda x: (x[1], x[0].rating), reverse=True)
    legendary.sort(key=lambda x: (x[1], x[0].rating), reverse=True)

    common_info = '\n'.join(f'{idol.to_string()}: {Card.colors[rarities.COMMON]}{num}{Card.reset}' for idol, num in common[:4])
    uncommon_info = '\n'.join(f'{idol.to_string()}: {Card.colors[rarities.UNCOMMON]}{num}{Card.reset}' for idol, num in uncommon[:4])
    rare_info = '\n'.join(f'{idol.to_string()}: {Card.colors[rarities.RARE]}{num}{Card.reset}' for idol, num in rare[:4])
    legendary_info = '\n'.join(f'{idol.to_string()}: {Card.colors[rarities.LEGENDARY]}{num}{Card.reset}' for idol, num in legendary[:4])
    string = f"""
------------------------------------------
Overall top collection info for {player.name}{Card.reset}

{Card.colors[rarities.COMMON]}{rarities.COMMON.value}{Card.reset}
{common_info}

{Card.colors[rarities.UNCOMMON]}{rarities.UNCOMMON.value}{Card.reset}
{uncommon_info}

{Card.colors[rarities.RARE]}{rarities.RARE.value}{Card.reset}
{rare_info}

{Card.colors[rarities.LEGENDARY]}{rarities.LEGENDARY.value}{Card.reset}
{legendary_info}
------------------------------------------
    """.strip()

    print(string)
            

def common_check(player) -> Idol: # function to check entire common card info for a player
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    choices = []
    weight = []
    total_weight = 100
    for group in data:
        for member in data[group]:
            if data[group][member]["COMMON"] > 0:
                choices.append(choose.find_idol(member, group))
                bonus = 0.1 if player.perk == Perks.COLLECTOR else 0.2 # double bonus from card if collector perk
                chance = round(data[group][member]["COMMON"] * bonus, 1)
                weight.append(chance)
                total_weight -= chance
    choices.append(None)
    weight.append(round(total_weight, 1))
    return random.choices(choices, weights = weight, k = 1)[0]

def uncommon_check(player, idol: Idol) -> float: # function to check uncommon card info for certain idol for player
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    bonus = 0.04 if player.perk == Perks.COLLECTOR else 0.02 # double bonus from card if collector perk
    return min(bonus * data[idol.group.upper().split('/')[0]][idol.name]["UNCOMMON"], 1)

def rare_check(player, idol: Idol) -> int: # function to check rare card info for certain idol for player
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    bonus = 0.06 if player.perk == Perks.COLLECTOR else 0.03 # double bonus from card if collector perk
    return min(bonus * data[idol.group.upper().split('/')[0]][idol.name]["RARE"], 1)

def legendary_check(player) -> bool: # function to check legendary card info for certain idol for player
    with open(f'./info/{choose.remove_ansi(player.name)}_cards.json', 'r') as f:
        data = json.load(f)
    bonus = 0.2 if player.perk == Perks.COLLECTOR else 0.1 # double bonus from card if collector perk
    if random.random() < data[player.ult[0].group.upper().split('/')[0]][player.ult[0].name]["LEGENDARY"] * bonus: # amount of legendary cards times 10%
        return True
    else:
        return False

def discount_check(player: str, idol: Idol) -> bool: # function that checks if all 4 rarities of cards collected for an idol
    with open(f'./info/{player}_cards.json', 'r') as f:
        data = json.load(f)
    check = data[idol.group.upper().split('/')[0]][idol.name]
    for key in check:
        if check[key] == 0:
            return False
    return True

def group_check(player: str, group: str) -> bool: # function that checks if all members of a group are fully collected for group reroll discount
    with open(f'./info/{player}_cards.json', 'r') as f:
        data = json.load(f)
        check = data[group.upper()]
        for member in check:
            if not discount_check(player, choose.find_idol(member, group)):
                return False
    return True
        
def create_card_collection(): # function to create the json file that stores all card collection info (also functions as reset)
    names = ["sejun", "jason"]
    for i in range(2):
        json_text = {}
        groups = os.listdir('./girl groups')
        for file in groups:
            group = file.split('.')[0]
            json_text[group] = {}
            with open(f'./girl groups/{file}', 'r') as f:
                data = json.load(f)
                for member in data["members"]:
                    json_text[group][member["name"]] = {
                        "COMMON": 0,
                        "UNCOMMON": 0,
                        "RARE": 0,
                        "LEGENDARY": 0
                    }
        with open(f'./info/{names[i]}_cards.json', 'w') as f:
            json.dump(json_text, f, indent=4)
    print("Card collection reset!")
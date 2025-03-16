import choose_idol as choose
import game_stats as stats
import card_collector as card
from choose_idol import Idol
from choose_idol import Variants
from choose_idol import Perks
from media.audio import on_win
import media.video_player

import os
import sys
import re
import time
import random
import math
from collections import Counter

class Player: # class to reprsent a player
    def __init__(self, name, color):
        self.name = name
        self.roster = []
        self.money = 15
        self.extra_money = 0 # extra money from spending perk
        self.color = color # color for their text
        self.ult = None # ultimate bias
        self.perk = None # perk chosen at start of game
        self.synergizer = False
        self.combat_score = 0 # combat score of this game
        self.done = False # tracks whether they are finished with deluxe rerolls/upgrades
        self.synergies = set() # keeps track of used synergies

    def update_money(self, change: int): # updates money count of player
        if self.extra_money > 0: # if extra money remaining
            self.extra_money -= change
            if self.extra_money < 0:
                self.money -= abs(self.extra_money)
        else:
            self.money -= change

    def total_money(self): # returns total amount of money player has for display purposes
        return self.money + self.extra_money

class Game:
    CONST = {
        "r": 2, # reroll price
        "gr": 5, # group reroll price
        "dr": 6, # deluxe reroll price
        "up": 2, # upgrade price
        "size": 5, # max roster size
        "div": 110, # '-' divider width
        "variant": 0.35, # default chance for idol to spawn with variant
        "synergies": 3, # number of idols needed to hit a synergy
        "perks": True, # whether game should use perks or not
        "testing": False, # whether game is being played in a test state or not
        "media": False, # whether to add sound/video effects to game
        "crazy": False # whether to change game settings to crazy mode
    }

    c_reset = "\033[0m" # reset color (white)
    c_money = "\033[38;2;133;187;101m" # money color
    c_p1 = "\033[38;2;255;250;0m" # player 1 color
    c_p2 = "\033[38;2;255;67;67m" # player 2 color

    def __init__(self): # constructor for game object
        self.p1 = self.p2 = None # holds player objects
        self.turn = None # holds player object who is currently their turn
        self.turn_count = 0 # number of turns that have elapsed
        self.winner = None
        self.flush = None
        self.exodia = None # whether game was won by exodia or not (and what kind)
        self.all_idols = [] # stores every idol present in game for statistics

    @property
    def opponent(self): # holds player object who is currently not their turn
        return self.p2 if self.turn == self.p1 else self.p1
    
    def switch_turns(self):
        self.turn = self.opponent

    def game_start(self) -> str: # start and restart games
        print(f'{"-" * (Game.CONST["div"] + 2)}')

        def player_first(): # function that 50/50s to see which player goes first
            print("Flipping a coin to determine which player goes first...")
            if not Game.CONST["testing"]:
                time.sleep(1)
            return random.choice([True, False])

        os.system('cls')
        while True:
            # p1 = input("Enter player name: ").strip()
            # p2 = input("Enter player name: ").strip()
            p1 = "Sejun"
            p2 = "Jason"

            if p1 != p2 and p1 and p2:
                self.p1 = Player(f'{Game.c_p1}{p1}', Game.c_p1)
                self.p2 = Player(f'{Game.c_p2}{p2}', Game.c_p2)
                if player_first():
                    self.p1, self.p2 = self.p2, self.p1
                break
            print("Player names must be different.")

        if Game.CONST["crazy"]: # set game stats to crazy mode
            Game.CONST["r"] = 1
            Game.CONST["gr"] = 3
            Game.CONST["dr"] = 3
            Game.CONST["variant"] = 1
            Game.CONST["size"] = 9
            self.p1.money = 20
            self.p2.money = 20

        print(f'{self.p1.name}{Game.c_reset} goes first! {self.p2.name}{Game.c_reset} goes second!')
        print("-" * (Game.CONST["div"] + 2))
        self.turn = self.p1
        if Game.CONST["perks"]:
            perks = list(Perks)
            for _ in range(2):
                print("Pick your perk:")
                for i in range(len(perks)):
                    print(f'{i + 1}. {perks[i].value}')
                while True:
                    ans = self.input_command("number", self.turn)
                    if 1 <= ans <= len(perks):
                        self.turn.perk = perks[ans - 1]
                        if self.turn.perk == Perks.SPENDER:
                            self.turn.extra_money = 4
                        break
                    print("Invalid input!")
                self.switch_turns()
                print("-" * (Game.CONST["div"] + 2)) # divider
        print("Pick your ultimate bias:")
        for _ in range(2):
            while True:
                ans = self.input_command("idol", self.turn)
                self.turn.ult = ans
                if self.opponent.ult is None or (self.opponent.ult and not self.turn.ult.equals(self.opponent.ult)): # not duplicate of opponent's
                    break
                print("Invalid idol!")
            print(f'{self.turn.name}\'s{Game.c_reset} ultimate bias: {self.turn.ult.to_string()}')
            self.switch_turns()

    def strip_ansi(self, text): # remove ansi from strings (for text using center formatting)
        ansi_escape = re.compile(r'\033\[[0-9;]*m') 
        return ansi_escape.sub('', text) 

    def format_text(self, text: str, width: int) -> str: # formats text to show in center without ansi code interference
            return text.center(width + (len(text) - len(self.strip_ansi(text))))
    
    def uncenter_text(self, text: str, width: int, left: bool) -> str: # formats text to left or right without ansi code interference
            if left:
                return text.ljust(width + (len(text) - len(self.strip_ansi(text))))
            else:
                return text.rjust(width + (len(text) - len(self.strip_ansi(text))))
            
    def show_money(self):
        ltext = self.uncenter_text(f'{self.p1.name}: {Game.c_money}${self.p1.total_money()}{Game.c_reset}', Game.CONST["div"] // 2 - 1, False)
        rtext = self.uncenter_text(f'{self.p2.name}: {Game.c_money}${self.p2.total_money()}{Game.c_reset}', Game.CONST["div"] // 2 - 1, True)
        print(f'{ltext} || {rtext}')

    def show_game_info(self):
        # print(f'{"-" * (Game.CONST["div"] + 2)}')
        num_lines = max(len(self.turn.roster), len(self.opponent.roster))
        width = Game.CONST["div"] // 2
        half = width // 2

        def idol_string(player):
            try:
                return player.roster[i].to_string().split('|')
            except IndexError:
                return ['', '']

        left_name = f"{self.p1.name}{Game.c_reset} - {Game.c_money}${self.p1.total_money()}{Game.c_reset}"
        right_name = f"{self.p2.name}{Game.c_reset} - {Game.c_money}${self.p2.total_money()}{Game.c_reset}"

        left_name = self.format_text(left_name, width)
        right_name = self.format_text(right_name, width)
        print(f'{left_name}||{right_name}')
        print("-" * (width * 2 + 2))

        for i in range(num_lines):
            left_idol, left_group = idol_string(self.p1)
            right_idol, right_group = idol_string(self.p2)
            left_idol, left_group = self.format_text(left_idol, half), self.format_text(left_group, half)
            right_idol, right_group = self.format_text(right_idol, half), self.format_text(right_group, half)
            print(f'{left_idol}|{left_group}||{right_idol}|{right_group}')

    def help_command(self):
        string = f"""
------------------------------------------
All Commands:
{Game.c_p1}i{Game.c_reset} - show roster info
{Game.c_p1}m{Game.c_reset} - show money info
{Game.c_p1}u{Game.c_reset} - show ultimate biases
{Game.c_p1}h{Game.c_reset} - show all commands
{Game.c_p1}c{Game.c_reset} - clear console
{Game.c_p1}e{Game.c_reset} - exit game
\033[38;2;255;118;118mreset stats - resets all idol stats and game files{Game.c_reset}
------------------------------------------
""".strip()
        print(string)
    
    def input_command(self, input_type: str, cur_player: Player) -> str: # yon: True for yes or no question, False if not
        while True:
            ans = input(f'{cur_player.name}{Game.c_reset} | ----> ').strip().lower() # Inquires for input

            if "letter" in input_type: # for WILDCARD, overrides any one letter commands
                if len(ans) == 1 and ans.isalpha():
                    return ans
            # UTILITY COMMANDS - Available at any point in the game, do not affect game state
            if ans == 'exit': # command to exit the game
                sys.exit()
            elif ans == 'reset': # resets all idol stats and removes all game history files
                stats.reset_stats()
            elif ans == 'cl': # command to clear terminal
                os.system('cls')
            elif ans in ['h', 'help']: # TODO: create total command list
                self.help_command()
            elif ans in ['i', 'in']: # command to print out money and roster information
                self.show_game_info()
            elif ans == 'm': # command to print out only money information
                self.show_money()
            elif ans in ['u', 'ult']: # command to show ultimate biases
                if self.p1.ult and self.p2.ult:
                    print(f'{self.p1.name}\'s{Game.c_reset} ultimate bias: {self.p1.ult.to_string()}')
                    print(f'{self.p2.name}\'s{Game.c_reset} ultimate bias: {self.p2.ult.to_string()}')
                else:
                    print("Not all ultimate biases chosen yet!")
            elif ans in ['cs', 'cj']: # command to search up overall card collection info for a certain player
                sejun = self.p1 if "Sejun" in self.p1.name else self.p2
                jason = self.p1 if "Jason" in self.p1.name else self.p2
                if ans == 'cs':
                    card.total_collection(sejun)
                else:
                    card.total_collection(jason)
            elif ans.startswith(("i ", "in ", "s ", "st ", "c ", "cs ", "cj ")): # searching up info/statistics on an idol
                answer = ans.split(" ", 2)
                search = None
                if len(answer) >= 3: # group specified
                    search = choose.find_idol(answer[1], answer[2])
                elif len(answer) >= 2: # group not specified
                    search = choose.find_idol(answer[1], "stat")
                if search:
                    if ans.startswith(("in ", "info ")): # searching up idol info
                        search.idol_info()
                    elif ans.startswith(("c ", "cs ", "cj ")): # searching up collectiong info
                        sejun = self.p1 if "Sejun" in self.p1.name else self.p2
                        jason = self.p1 if "Jason" in self.p1.name else self.p2
                        if ans.startswith("cs "):
                            card.collection_info(sejun, search)
                        elif ans.startswith("cj "):
                            card.collection_info(jason, search)
                        else:
                            card.collection_info(cur_player, search)
                    else: # searching up idol stats
                        search.idol_stats()
                    continue
                print("Invalid idol!")
            else: ### need continue after all failures after this point
                if "idol" in input_type: # for typing in specific idol names
                    answer = ans.split(" ", 1)
                    search = None
                    if len(answer) >= 2: # group specified
                        search = choose.find_idol(answer[0], answer[1])
                    else: # group not specified
                        search = choose.find_idol(answer[0], None)
                    if search:
                            return search
                    print("Invalid idol!")
                    continue
                if "number" in input_type or "bid" in input_type: 
                    try: # see if command is an integer (for bids or selections)
                        num = int(ans)
                        if "bid" in input_type:
                            opp = self.p1 if cur_player == self.p2 else self.p2
                            if num < 0 and len(opp.roster) >= Game.CONST["size"]:
                                print(f'{opp.name}\'s{Game.c_reset} roster is full, cannot bid negative!')
                                continue
                            if abs(num) <= cur_player.money: # for bids (needs money check)
                                return num
                            else:
                                print("Not enough money!")
                                continue
                        else: # for selections
                            return num
                    except ValueError:
                        pass
                if input_type == "opp bid": # opponent is counter bidding, add option to group reroll or say no to bidding
                    if ans in ['gr', 'group reroll']:
                        return 'gr'
                    elif ans in ['n', 'no']:
                        return 'n'
                    print("Invalid response!")
                    continue
                if "yon" in input_type: # for yes or no questions
                    if ans in ['y', 'yes']:
                        return 'y'
                    elif ans in ['n', 'no']:
                        return 'n'
                    print("Answer must be yes or no. ")
                    continue
                elif "turn" in input_type: # for turn based actions (bid, reroll)
                    if ans in ['r', 'rr', 'reroll']: # reroll
                        if cur_player.perk == Perks.GAMBLER:
                            Game.CONST["r"] = 1
                        if cur_player.money >= Game.CONST["r"]:
                            return 'r'
                        print("You don't have enough money for a reroll! ")
                        Game.CONST["r"] = 2
                        continue
                    elif ans in ['gr', 'group reroll']: # group reroll
                        if cur_player.money >= Game.CONST["gr"]:
                            return 'gr'
                        print("You don't have enough money for a group reroll! ")
                        continue
                print("Invalid input!") # all commands checked, invalid command

    def add_idol(self, player: Player, add: Idol, index: int) -> int: # add idol to a roster, potentially check synergies (might make new func for that)
        if index is not None:
            player.roster.insert(index, add)
        else:
            player.roster.append(add)
        print(f'{add.to_string()} added to {player.name}\'s{Game.c_reset} roster!')

        if add.variant == Variants.IBONDS: # if idol is I-Bonds
            gain_money = Game.CONST["size"] - len(player.roster)
            player.money += gain_money
            if gain_money > 0: # only print message if at least $1
                print(f'{player.name}{Game.c_reset} gained {Game.c_money}${gain_money}{Game.c_reset} for {gain_money} empty slots in their roster!')
        elif add.variant == Variants.WILDCARD: # if idol is WILDCARD
            while add.wildcard is None:
                print("Enter a letter for Wildcard.")
                letter = self.input_command("letter", player)
                if letter.lower() == add.name[0].lower(): # letter must be different from letter idol already starts with
                    print(f'{add.clean_name()} already starts with {Game.c_money}{letter.upper()}{Game.c_reset}, choose a different letter!')
                else:
                    add.wildcard = letter.upper()
                    print(f'{Game.c_money}{letter.upper()}{Game.c_reset} added to {add.to_string()} synergies!')
        self.check_synergies(player) # check synergies after adding idol to roster

    def replace_idol(self, player: Player) -> Idol: # function for replacing an idol on a roster
        print(f'\nPick an idol on {player.name}\'s{Game.c_reset} roster to remove.')
        print("0. Cancel")
        for i in range(len(player.roster)):
            print(f'{i+1}. {player.roster[i].to_string()}')
        while True:
            ans = self.input_command("number", self.turn) # pick idol 1-5 to replace
            if ans == 0:
                return None
            elif 1 <= ans <= Game.CONST["size"]:
                idol = player.roster[ans - 1]
                if idol.variant == Variants.ELIGE: # idol is eliged, cannot replace
                    print(f'{idol.to_string()} is Eliged!')
                    continue
                if self.turn != player and idol.protected: # opponent idol is protected, cannot switch
                    print(f'{idol.to_string()} is protected!')
                    continue
                del player.roster[ans - 1]
                break
            print(f'Invalid selection. Please choose a number between 1 and {Game.CONST["size"]}.')
        return ans - 1, idol # returns index of idol that was removed, and the idol itself
            
    def check_synergies(self, player: Player): # function to check and handle synergies
        self.check_exodia(player) # checks for exodia synergies
        opp = self.p1 if player == self.p2 else self.p2

        old_syn = player.synergies.copy()
        counts = Counter()
        for idol in player.roster:
            counts[idol.name[0]] += 1
            if idol.variant == Variants.WILDCARD:
                counts[idol.wildcard] += 1
            if len(idol.group.split('/')) > 1: # IZONE exception
                counts[idol.group.split('/')[0].strip()] += 1
                counts[idol.group.split('/')[1].strip()] += 1
            else: # for all other regular groups
                counts[idol.group] += 1 
        player.synergies.update({syn for syn, count in counts.items() if count >= Game.CONST["synergies"]})
        new_syn = player.synergies - old_syn

        if new_syn: # give synergy effects
            for syn in new_syn:
                if len(syn) > 1: # group synergy (SWITCH))
                    print(f'{player.name}{Game.c_reset} hit a group synergy for {Game.c_money}{syn}{Game.c_reset}! They receive a switch powerup.')
                    if all(check.variant == Variants.ELIGE for check in player.roster):
                        print(f'{player.name}\'s{Game.c_reset} roster is completely Eliged, so you can\'t use the switch!')
                    if all(check.variant == Variants.ELIGE for check in opp.roster):
                        print(f'{opp.name}\'s{Game.c_reset} roster is completely Eliged, so you can\'t use the switch!')
                    elif len(opp.roster) != 0:
                        turn_ind = self.replace_idol(player)
                        if turn_ind is None: # cancelled switch
                            continue
                        opp_ind = self.replace_idol(opp)
                        if opp_ind is None:
                            player.roster.insert(turn_ind[0], turn_ind[1]) # add back removed idol from earlier
                            continue # cancelled switch

                        self.add_idol(player, opp_ind[1], turn_ind[0])
                        self.add_idol(opp, turn_ind[1], opp_ind[0])
                    else:
                        print(f'{opp.name}\'s{Game.c_reset} roster is empty, so you can\'t use the switch!')
                else: # letter synergy (ADD/REPLACE))
                    ind = None
                    print(f'{player.name}{Game.c_reset} hit a letter synergy for {Game.c_money}{syn}{Game.c_reset}! They get to add/replace an idol.')
                    if choose.letter_check(syn, self.p1.roster + self.p2.roster): # check if all idols for current letter are already in the roster
                        print(f'All idols that start with {Game.c_money}{syn}{Game.c_reset} are taken! Cannot use synergy.')
                        continue
                    if len(player.roster) >= Game.CONST["size"]: # player roster is full, must replace instead of adding
                        if all(check.variant == Variants.ELIGE for check in player.roster):
                            print("Your roster is completely Eliged, cannot use synergy!")
                            continue
                        removed = self.replace_idol(player)
                        if removed is None:
                            continue # cancelled replace
                        ind = removed[0]
                        self.edit_stats(removed[1], "reroll", None)
                    print(f'Choose an idol whose name starts with a {Game.c_money}{syn.upper()}{Game.c_reset}: (name) (group)')

                    while True:
                        ans = self.input_command("idol", player)
                        if isinstance(ans, Idol) and ans.name.lower().startswith(syn.lower()) and not any(ans.equals(compare) for compare in self.turn.roster + self.opponent.roster):
                            ans.protected = True
                            self.edit_stats(ans, None, None)
                            self.add_idol(player, ans, ind)
                            break
                        else:
                            print("Invalid idol!")

    def check_exodia(self, player: Player): # function to check exodia synergies
        if len(player.roster) >= Game.CONST["size"]:
            chars = [player.roster[0].name[0].upper()] # starting letter
            if player.roster[0].wildcard: # append second wildcard letter if exists for first idol
                chars.append(player.roster[0].wildcard)

            for idol in player.roster: # letter exodia check
                for char in chars:
                    if char == idol.name[0] or char == idol.wildcard:
                        matching_char = char
                        break
                else:
                    break # break loop, no exodia
            else:
                self.exodia = f'letter exodia! {Game.c_money}({matching_char.upper()}){Game.c_reset}'

            # check group synergies
            groups = player.roster[0].group.split('/') # group
            for group in groups:
                if all(group in idol.group for idol in player.roster): # full roster of same group
                    self.exodia = f'group exodia! {Game.c_money}({group}){Game.c_reset}'

            if self.exodia:
                win_text = f'{player.name}{Game.c_reset} won through {self.exodia}'
                if group in self.exodia: # group exodia
                    self.exodia = group
                else: # letter exodia
                    self.exodia = matching_char
                print(f'\n{self.format_text(win_text, Game.CONST["div"] + 2)}')
                self.winner = player
                if Game.CONST["media"]:
                    media.video_player.play_exodia()
                self.final_screen()
   
    # True if duplicate is protected and cannot be stolen
    # False if no duplicate, or duplicate exists and is stolen
    def duplicate_check(self, cur_idol: Idol) -> int: # check if rolled idol is already on a roster
        for idol in self.opponent.roster: 
            if cur_idol.equals(idol):
                print(self.format_text(cur_idol.to_string(), Game.CONST["div"] + 2)) # print the idol like you would on a normal turn, but without adding any editions
                if not idol.protected and not idol.variant == Variants.ELIGE: # only steal if idol is not protected or eliged
                    print(f'{self.turn.name}{Game.c_reset}, would you like to steal {idol.to_string()} from {self.opponent.name}{Game.c_reset}?')
                    ans = self.input_command("yon", self.turn)
                    if ans == 'y':
                        print(f'{self.turn.name}{Game.c_reset} steals {idol.to_string()} from {self.opponent.name}\'s{Game.c_reset} roster!')
                        self.opponent.roster.remove(idol)
                        self.add_idol(self.turn, idol, None)
                        return 1
                    else:
                        return 2
                else: # idol is protected, cannot be stolen
                    if idol.protected:
                        print(f'{self.turn.name}{Game.c_reset} tries to steal {cur_idol.to_string()} from {self.opponent.name}{Game.c_reset}, but they are protected!')
                    elif idol.variant == Variants.ELIGE:
                        print(f'{self.turn.name}{Game.c_reset} tries to steal {cur_idol.to_string()} from {self.opponent.name}{Game.c_reset}, but they are eliged!')
                    return 2
        return 0
    
    def ultimate_bias(self, idol: Idol) -> bool: # handle actions when ultimate bias is rolled
        ult_player = None
        ult_value = idol.ult_value()
        if idol.equals(self.p1.ult):
            ult_player = self.p1
        elif idol.equals(self.p2.ult):
            ult_player = self.p2
        if ult_player and ult_player.money >= ult_value and len(ult_player.roster) < Game.CONST["size"]:
            print(f'{idol.clean_name()} is {ult_player.name}\'s{Game.c_reset} ultimate bias! Would you like to instantly add them to your roster for {Game.c_money}${ult_value}{Game.c_reset}?')
            ans = self.input_command("yon", ult_player)
            if ans == 'y':
                if card.discount_check(choose.remove_ansi(ult_player.name), idol): # if player has all card types for idol
                    ult_value -= 1
                    print(f'{ult_player.name}{Game.c_reset} receives {Game.c_money}$1{Game.c_reset} cashback for {idol.to_string()} through cards!')
                ult_player.update_money(ult_value)
                idol.protected = True
                idol.winrate += 0.05
                self.edit_stats(idol, None, ult_value)
                self.add_idol(ult_player, idol, None)
                return True
        return False
    
    def bid_process(self, bid: int, cur_idol: Idol): # function that handles bidding process
        opponent_win = False
        if len(self.opponent.roster) < Game.CONST["size"]: # check if opponent roster is full
            if self.opponent.money > abs(bid): # check if opponent has enough money to counter bid
                while not opponent_win:
                    counter_bid = self.input_command("opp bid", self.opponent)
                    if counter_bid == 'n': # opponent doesn't bid
                        break
                    if counter_bid == 'gr': # opponent group rerolls
                        amount = Game.CONST["gr"]
                        if bid >= 0:
                            amount += bid + 1 # must have enough money to both buy and group reroll
                        if self.opponent.money >= amount:
                            self.opponent.update_money(amount)
                            if self.group_reroll(self.opponent, cur_idol):
                                self.edit_stats(cur_idol, "gr", None)
                                return
                            else:
                                self.opponent.money += amount
                            continue
                        else:
                            print("You do not have enough money to bid and group reroll!")
                            continue
                    elif bid >= 0: # opponent bids to buy
                        if counter_bid > bid:
                            self.add_idol(self.opponent, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent.")
                            continue
                    else: # opponent bids to give
                        if counter_bid < bid:
                            self.add_idol(self.turn, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent.")
                            continue
                    if card.discount_check(choose.remove_ansi(self.opponent.name), cur_idol): # if player has all cards, give $1 cashback
                        counter_bid -= 1
                        print(f'{self.opponent.name}{Game.c_reset} receives {Game.c_money}$1{Game.c_reset} cashback for {cur_idol.to_string()} through cards!')
                    self.opponent.update_money(counter_bid)
                    opponent_win = True
                    self.edit_stats(cur_idol, None, counter_bid)
        if not opponent_win: # turn player wins bid
            self.edit_stats(cur_idol, None, bid)
            if bid >= 0:
                self.add_idol(self.turn, cur_idol, None)
            else:
                self.add_idol(self.opponent, cur_idol, None)
            if card.discount_check(choose.remove_ansi(self.turn.name), cur_idol): # if player has all cards, give $1 cashback
                bid -= 1
                print(f'{self.turn.name}{Game.c_reset} receives {Game.c_money}$1{Game.c_reset} cashback for {cur_idol.to_string()} through cards!')
            self.turn.update_money(abs(bid))

    def group_reroll(self, player: Player, dup_idol: Idol) -> bool: # function for handling group reroll process
        cur_idol = dup_idol
        dupes = [dup_idol]

        groups = dup_idol.group.split('/')
        if len(groups) > 1: # idol is in multiple groups, prompt player to select one
            print("Select a group to reroll for:")
            for i in range(len(groups)):
                print(f'{i + 1}. {groups[i]}')
            while True:
                ans = self.input_command("number", player)
                if 1 <= ans <= len(groups):
                    group = groups[ans - 1]
                    break
                print("Invalid input!")
        else:
            group = dup_idol.group

        for idol in self.p1.roster + self.p2.roster: # add all existing idols from same group into duplicate list
            if group in idol.group.split('/'):
                dupes.append(idol)
        
        if choose.group_full_check(group, dupes): # if no more possible idols, refund and cancel group reroll
                print(f'No more possible idols left for {group}!')
                return False
        while True:
            if not Game.CONST["testing"]:
                print("Rolling idol...")
                time.sleep(1) # suspense
                print("\033[F\033[K", end="") # deletes previous line to replace with rolled idol
            cur_idol = choose.random_idol(group, 1, dupes, None)[0]
            cur_idol.variant = dup_idol.variant
            cur_idol.protected = True # idols from group rerolls are protected
            dupes.append(cur_idol)
            if card.group_check(choose.remove_ansi(player.name), group): # if player has all cards collected of group, give discount
                player.money += 1
                print(f'{player.name}{Game.c_reset} receives {Game.c_money}$1{Game.c_reset} cashback for collecting every card for {group}!')
            if player.money >= Game.CONST["gr"] and not choose.group_full_check(group, dupes): # group reroll again
                print(cur_idol.to_string())
                print("Would you like to group reroll again? ",)
                if self.input_command("yon", player) == 'y': # if answer is yes
                    player.update_money(Game.CONST["gr"])
                    self.edit_stats(cur_idol, "gr", None)
                    continue
            break
        self.edit_stats(cur_idol, None, None)
        self.add_idol(player, cur_idol, None)
        return True

    def deluxe_reroll(self): # function for deluxe reroll
        self.turn = self.p1
        while not self.p1.done or not self.p2.done:
            if self.turn.perk == Perks.GAMBLER: # gambler perk not allowed to deluxe reroll
                self.turn.done = True
            if self.turn.done: # if current player is done with deluxe rerolls, switch to next player
                self.switch_turns()
                continue
            if all(check.variant == Variants.ELIGE for check in self.turn.roster):
                print("-" * (Game.CONST["div"] + 2)) # divider
                print(f'{self.turn.name}\'s{Game.c_reset} roster is all Eliges and cannot be deluxe rerolled!')
                self.turn.done = True
            elif self.turn.money >= Game.CONST["dr"]: # if they have money for deluxe reroll
                print("-" * (Game.CONST["div"] + 2)) # divider
                print(f'{self.turn.name}{Game.c_reset}, would you like to deluxe reroll for {Game.c_money}${Game.CONST["dr"]}{Game.c_reset}?')
                if self.input_command("yon", self.turn) == 'y': # dr if yes, else break and move to next player
                    removed = self.replace_idol(self.turn) # index and object of removed idol
                    if removed is None:
                        self.turn.done = True
                        continue # deluxe reroll is cancelled
                    self.edit_stats(removed[1], "reroll", None) # add to reroll stat of deluxe rerolled idol
                    print(f'{removed[1].to_string()} removed from {self.turn.name}\'s{Game.c_reset} roster!')
                    
                    if not Game.CONST["testing"]:
                        print("Rolling idols...")
                        time.sleep(1) # suspense
                        print("\033[F\033[K", end="") # deletes previous line to replace with rolled idol
                    choices = choose.random_idol(None, 3, self.p1.roster + self.p2.roster + [removed[1]], None) # deluxe reroll cannot roll duplicates
                    print("\nPick an idol to add to your roster:")
                    for i, choice in enumerate(choices, start=1):
                        print(f'{i}. {choice.to_string()}')
                    while True:
                        ans = self.input_command("number", self.turn) # pick idol 1-3 to add
                        if 1 <= ans <= 3:
                            self.edit_stats(choices[ans-1], None, None)
                            self.add_idol(self.turn, choices[ans-1], removed[0])
                            break
                        print(f'Invalid selection!')

                    self.turn.update_money(Game.CONST["dr"])
                    self.gambler_check(Game.CONST["dr"]) # update gambler variant idols
                    self.show_game_info()
                    self.switch_turns()
                else: # player says no to deluxe reroll
                    self.turn.done = True
            else: # player does not have enough money for deluxe reroll
                self.turn.done = True
        self.p1.done, self.p2.done = False, False # reset variables to be reused for upgrades

    def upgrade_idol(self): # function for upgrade minigame
        self.turn = self.p1
        while not self.p1.done or not self.p2.done:
            if self.turn.done: # if current player is done with upgrading, switch to next player
                self.switch_turns()
            if all(check.variant == Variants.ELIGE for check in self.turn.roster):
                print("-" * (Game.CONST["div"] + 2)) # divider
                print(f'{self.turn.name}\'s{Game.c_reset} roster is all Eliges and cannot be upgraded!')
                self.turn.done = True
            elif self.turn.money >= Game.CONST["up"]: # if they have money for an upgrade
                print("-" * (Game.CONST["div"] + 2)) # divider
                print(f'{self.turn.name}{Game.c_reset}, would you like to upgrade for ${Game.CONST["up"]}?')
                if self.input_command("yon", self.turn) == 'y': # dr if yes, else break and move to next player
                    print(f'Pick an idol on {self.turn.name}\'s{Game.c_reset} roster to upgrade.')
                    print("0. Cancel")
                    for i in range(len(self.turn.roster)):
                        print(f'{i+1}. {self.turn.roster[i].to_string()}')
                    while True:
                        ind = self.input_command("number", self.turn) # pick idol 1-5 to upgrade
                        if ind == 0:
                            break # cancel upgrade
                        elif 1 <= ind <= Game.CONST["size"]:
                            upgrade_idol = self.turn.roster[ind - 1]
                            if upgrade_idol.variant == Variants.ELIGE: # idol is eliged, cannot upgrade
                                print(f'{upgrade_idol.to_string()} is Eliged!')
                                continue
                            if upgrade_idol.rating == 9: # idol is max rating, cannot be upgraded any further
                                print(f'{upgrade_idol.to_string()} cannot be upgraded any further!')
                                continue
                            else:
                                break # choice is valid
                        print(f'Invalid selection. Please choose a number between 1 and {Game.CONST["size"]}.')

                    if ind == 0: # upgrade cancelled
                        self.turn.done = True
                        continue

                    print("Please enter the number of tiers you would like to upgrade your idol.")
                    while True:
                        ans = self.input_command("number", self.turn) 
                        if 1 <= ans <= 8 and upgrade_idol.rating + ans <= 9:
                            chance = 0.5 ** ans
                            chance = min(chance + card.uncommon_check(self.turn, upgrade_idol), 1)
                            print(f'Upgrade chance: {Game.c_money}{round(chance * 100, 2)}%{Game.c_reset}')
                            print("Upgrading...")
                            time.sleep(1) # suspense
                            print("\033[F\033[K", end="") # deletes previous line to replace with upgrade result
                            if random.random() < chance: # if upgrade chance hits
                                print(f'{Game.c_money}SUCCESSFUL!{Game.c_reset}')
                                time.sleep(0.5)
                                if upgrade_idol.rating + ans == 9: # if idol is being upgraded into Hackclaw, do not roll new idol
                                    print(f'{upgrade_idol.to_string()} upgraded into their {Idol.RATINGS[9][1]} form, ', end="")
                                    upgrade_idol.rating += ans
                                    print(f'{upgrade_idol.to_string()}!')
                                    break
                                if upgrade_idol.rating == 7 and ans == 1 and self.big_three_check(): # when all big 3 already exist, simply upgrade rating of 910 idol
                                    print(f'{upgrade_idol.to_string()} upgraded their rating and is now ', end="")
                                    upgrade_idol.rating += ans
                                    print(f'{upgrade_idol.to_string()}!') 
                                    break
                                self.edit_stats(upgrade_idol, "reroll", None) # add to reroll stat of upgraded idol
                                self.turn.roster.remove(upgrade_idol)
                                new_idol = choose.random_idol(None, 1, self.turn.roster + self.opponent.roster, upgrade_idol.rating + ans)[0]
                                print(f'{upgrade_idol.to_string()} upgraded into {new_idol.to_string()}!')

                                self.edit_stats(new_idol, None, None)
                                self.turn.roster.insert(ind - 1, new_idol) # insert upgraded idol and check synergies
                                self.check_synergies(self.turn)
                            else:
                                print(f'\033[38;2;255;118;118mFAILED!{Game.c_reset}')
                                time.sleep(0.5)
                            break
                        print("Invalid amount entered!")
                    
                    self.turn.update_money(Game.CONST["up"])
                    self.gambler_check(Game.CONST["up"]) # update gambler variant idols
                    self.show_game_info()
                    self.switch_turns()
                else: # player says no to upgrade
                    self.turn.done = True
            else: # player does not have enough money for deluxe reroll
                self.turn.done = True
        self.p1.done, self.p2.done = False, False # reset variables

    def big_three_check(self) -> bool: # function to check if all of the big 3 are already in a roster
        big3 = []
        big3.append(choose.find_idol("yuna", "itzy"))
        big3.append(choose.find_idol("julie", "kiss of life"))
        big3.append(choose.find_idol("karina", "aespa"))
        for big in big3:
            if not any(big.equals(big_compare) for big_compare in self.p1.roster + self.p2.roster):
                return False # one of the big three is missing, return false
        return True # all big three exist in the game, return true

    def gambler_check(self, add_winrate: int): # updates bonus winrate of all gambler variant idols
        update = False
        for _ in range(2):
            for idol in self.turn.roster:
                if idol.variant == Variants.GAMBLER:
                    update = True
                    # added winrate is equal to dollar cost of reroll, plus additional scaling based off rating
                    real_add = (add_winrate / 100) + (idol.rating / 1000)
                    idol.winrate += round(real_add, 3)
                    print(f'{idol.to_string()}{Game.c_reset} gained {Game.c_money}{round(real_add * 100, 1)}%{Game.c_reset} bonus winrate! (Currently: {Game.c_money}{round(idol.winrate * 100, 1)}%{Game.c_reset})')
            self.switch_turns()
        if update:
            print() # print empty line
    
    def variant_check(self): # function to check all variants that take action at the end of a turn
        for _ in range(2):
            for idol in self.turn.roster:
                if idol.variant == Variants.EVOLVING: # handle evolving variant actions
                    if random.random() < Idol.RATINGS[idol.rating][2]: # if evolve chance hits
                        if idol.rating == 7 and self.big_three_check():
                            continue # idol is a 910 and all big 3 already exist, cancel evolve
                        elif idol.rating == 8:
                            idol.rating = 9
                            print(f'{idol.to_string()} evolved into their {Idol.RATINGS[9][1]} form, {new_idol.to_string()}!')
                            continue
                        new_idol = choose.random_idol(None, 1, self.turn.roster + self.opponent.roster, idol.rating + 1)[0] # create new idol one tier above
                        new_idol.variant = Variants.EVOLVING
                        new_idol.protected = True if idol.protected else False # copy protected stats

                        ind = self.turn.roster.index(idol) # get index of old idol and delete idol from roster
                        del self.turn.roster[ind]

                        self.edit_stats(new_idol, None, None)
                        self.turn.roster.insert(ind, new_idol) # add idol to roster
                        self.check_synergies(self.turn) # check synergies after adding new idol
                        print(f'{idol.to_string()} evolved into {new_idol.to_string()}!')
                elif idol.variant == Variants.BULLY: # handle bully variant actions
                    if random.random() < Idol.bully_chance: # if bully chance hits
                        players = [] # make sure to choose a player that has a non-empty roster
                        if len(self.p1.roster) > 0:
                            players.append(self.p1)
                        if len(self.p2.roster) > 0:
                            players.append(self.p2)
                        remove_player = random.choice(players)
                        remove_idol = random.choice(remove_player.roster)
                        if remove_idol.protected or remove_idol.variant == Variants.ELIGE: # if idol is protected, bullying fails
                            if remove_idol.variant == Variants.ELIGE:
                                print(f'{idol.to_string()} tried to bully {remove_idol.to_string()}, but they are Eliged!')
                            else:
                                print(f'{idol.to_string()} tried to bully {remove_idol.to_string()}, but they are protected!')
                        else: # remove bullied idol from their roster
                            if remove_idol.equals(idol): # removed themselves
                                print(f'{idol.to_string()} bullied too hard and got kicked from their roster!')
                            else: # removed another idol
                                print(f'{idol.to_string()} bullied {remove_idol.to_string()} out of their roster!')
                            remove_player.roster.remove(remove_idol)
            self.switch_turns()

    def combat(self): # simulates combat to determine a game winner
        print("-" * (Game.CONST["div"] + 2)) # divider

        self.turn = self.p1 
        for _ in range(2): # check for flushes
            compare_rating = self.turn.roster[0].rating
            for idol in self.turn.roster:
                if compare_rating != idol.rating:
                    break
            else:
                if self.flush:
                    self.flush = None
                    print("Both players hit a flush! Neither player gets a combat advantage.\n")
                else:
                    self.flush = self.turn
            self.switch_turns()

        if self.flush:
            print(f'{self.flush.name}{Game.c_reset} hit a flush! They receive a combat advantage.\n')

        sorted_p1 = sorted(self.p1.roster, key=lambda idol: idol.rating, reverse=True) # sort rosters to determine matchups
        sorted_p2 = sorted(self.p2.roster, key=lambda idol: idol.rating, reverse=True)

        for i in range(len(sorted_p1)):
            print(self.format_text(f'Matchup #{i+1}:', (Game.CONST["div"] + 2)))
            p1_prob, p2_prob = 0, 0

            if sorted_p1[i].rating == 9 and sorted_p2[i].rating != 9:
                p1_prob = 1
            elif sorted_p2[i].rating == 9 and sorted_p1[i].rating != 9:
                p2_prob = 1
            else:
                p1_prob = 0.5 ** (abs(sorted_p1[i].rating - sorted_p2[i].rating) + 1) # probability calculation
                p2_prob = 1 - p1_prob
                if sorted_p1[i].rating > sorted_p2[i].rating:
                    p1_prob, p2_prob = p2_prob, p1_prob

                if self.flush == self.p1: # add flush winrates
                    p1_prob = min(p1_prob + ((1 - p1_prob) ** 4) * 0.6 + 0.02, 1)
                    p2_prob = 1 - p1_prob
                elif self.flush == self.p2:
                    p2_prob = min(p2_prob + ((1 - p2_prob) ** 4) * 0.6 + 0.02, 1)
                    p1_prob = 1 - p2_prob

                # add bonus winrates from gambler variants and card bonuses
                p1_bonus = sorted_p1[i].winrate + card.rare_check(self.p1, sorted_p1[i])
                p2_bonus = sorted_p2[i].winrate + card.rare_check(self.p2, sorted_p2[i])

                # add bonus winrate from warlord perk
                if self.p1.perk == Perks.WARLORD and self.p2.perk != Perks.WARLORD:
                    p1_bonus += 0.1
                elif self.p2.perk == Perks.WARLORD and self.p1.perk != Perks.WARLORD:
                    p2_bonus += 0.1

                bonus = p1_bonus - p2_bonus
                if bonus > 0:
                    p1_prob = min(p1_prob + bonus, 1)
                    p2_prob = 1 - p1_prob
                elif bonus < 0:
                    p2_prob = min(p2_prob + abs(bonus), 1)
                    p1_prob = 1 - p2_prob
            
            p1_text = self.format_text(f'{sorted_p1[i].to_string()}', Game.CONST["div"] // 2 - 8)
            p2_text = self.format_text(f'{sorted_p2[i].to_string()}', Game.CONST["div"] // 2 - 8)
            p1_percent = self.uncenter_text(f'{Game.c_money}{round(p1_prob*100, 2)}%{Game.c_reset}', 6, False)
            p2_percent = self.uncenter_text(f'{Game.c_money}{round(p2_prob*100, 2)}%{Game.c_reset}', 6, True)
            print(f'{p1_text} {p1_percent} || {p2_percent} {p2_text}')

            # add suspense before each matchup, extra if game is tied at last matchup
            if Game.CONST["testing"]:
                wait = 0
            elif i == (len(sorted_p1) - 1) and self.p1.combat_score == self.p2.combat_score:
                wait = 5
            # speed up combat if one player is already guaranteed to win, or combat percentages of particular match up is 100-0
            elif self.p1.combat_score >= (math.ceil(len(sorted_p1) / 2)) or self.p2.combat_score >= (math.ceil(len(sorted_p1) / 2)) or p1_prob == 1 or p2_prob == 1:
                wait = 1
            else:
                wait = 3
            for j in range(wait):
                if wait == 1:
                    print(f'{" " * (Game.CONST["div"] // 2 - 5)}Fighting...')
                else:
                    print(f'{" " * (Game.CONST["div"] // 2 - 5)}Fighting{"." * (j + 1)}')
                time.sleep(1)
                print("\033[F\033[K", end="")

            winner = random.choices([self.p1, self.p2], weights=[p1_prob, p2_prob])
            if winner[0] == self.p1:
                win_string = f'{sorted_p1[i].clean_name()} wins!'
                self.p1.combat_score += 1
            else: 
                win_string = f'{sorted_p2[i].clean_name()} wins!'
                self.p2.combat_score += 1
            print(self.format_text(win_string, (Game.CONST["div"] + 2)))
            cur_score = f'{self.p1.name}: {self.p1.combat_score}{Game.c_reset} || {self.p2.name}: {self.p2.combat_score}{Game.c_reset}'
            print(f'{self.format_text(cur_score, (Game.CONST["div"] + 2))}\n')
            time.sleep(1) # add pause before next matchup revealed
        if self.p1.combat_score > self.p2.combat_score:
            self.winner = self.p1
        else:
            self.winner = self.p2
        final_score = f'{self.winner.name}{Game.c_reset} wins the game {self.p1.color}{self.p1.combat_score}{Game.c_reset} to {self.p2.color}{self.p2.combat_score}{Game.c_reset}!'

        print(f'{self.format_text(final_score, (Game.CONST["div"] + 2))}')
        print("-" * (Game.CONST["div"] + 2)) # divider

    def final_screen(self): # closes the game, uploads data
        if "Jason" in self.winner.name and Game.CONST["media"]: # video/sound effects for win
            on_win(False)

        for idol in self.winner.roster: # edit win stat of idols in winning roster
            self.edit_stats(idol, "win", None)
        self.show_game_info()
        
        if Game.CONST["testing"]: # if testing, don't write history/stats but print out idol stats for debugging
            for idol in self.all_idols:
                stats.print_idol(idol)
        else:
            stats.update_game_stats(self) # writes game history to a file and updates idol stats
        self.booster_packs()
        sys.exit() # end python instance

    def play_turn(self): # main game function to play out a turn
        if len(self.turn.roster) >= Game.CONST["size"]: # switch turn if one player's roster is full
            self.switch_turns()

        print(f'{"-" * (Game.CONST["div"] + 2)}')
        print(self.format_text(f'{self.turn.name}\'s{Game.c_reset} Turn ', Game.CONST["div"] + 2))

        dupes = []
        while True:
            if not Game.CONST["testing"]:
                print(self.format_text("Rolling idol...", Game.CONST["div"] + 2))
                time.sleep(1) # suspense
                print("\033[F\033[K", end="") # deletes previous line to replace with rolled idol
            if not any(self.turn.ult.equals(dupe) for dupe in dupes + self.turn.roster + self.opponent.roster) and card.legendary_check(self.turn, self.turn.ult):
                cur_idol = choose.find_idol(self.turn.ult.name, self.turn.ult.group) # turn player has legendary card for ultimate bias, guaranteed roll
                message = f'{cur_idol.to_string()} rolled from legendary card bonus!'
            else:
                cur_idol = card.common_check(self.turn) # evaluate boosted roll rates from common cards
                if cur_idol is None: # choose random idol if no idol rolled from common cards
                    cur_idol = choose.random_idol(None, 1, self.turn.roster + dupes, None)[0] # CHANGE TESTING HERE
                    message = None
                else:
                    message = f'{cur_idol.to_string()} rolled from common card bonus!'

            dup_check = self.duplicate_check(cur_idol) # check for duplicates
            if dup_check == 1: # duplicate was stolen
                break # end turn 
            elif dup_check == 2: # duplicate was denied/protected/eliged, reroll idol
                dupes.append(cur_idol)
                continue

            choose.determine_variant(cur_idol, Game.CONST["variant"]) # determine variant of rolled idol after stealing is checked
            print(self.format_text(cur_idol.to_string(), Game.CONST["div"] + 2)) # print rolled idol
            if message:
                print(self.format_text(message, Game.CONST["div"] + 2)) # print message for card bonuses
            
            if self.ultimate_bias(cur_idol): # check for ultimate bias
                break # end turn if ultimate bias was bought
            
            if self.opponent.perk == Perks.GAMBLER:
                Game.CONST["r"] = 1
            if len(self.opponent.roster) >= Game.CONST["size"] and self.opponent.money >= Game.CONST["r"]: # opponent reroll
                print(f'{self.opponent.name},{Game.c_reset} would you like to reroll {self.turn.name}\'s{Game.c_reset} idol for ${Game.CONST["r"]}? ')
                if self.input_command("yon", self.opponent) == 'y': # if answer is yes
                    self.opponent.update_money(Game.CONST["r"])
                    self.gambler_check(Game.CONST["r"]) # update gambler variant idols
                    self.edit_stats(cur_idol, "opp reroll", None) # add idol to history
                    self.show_money()
                    continue
                else:
                    self.edit_stats(cur_idol, "opp chances", None)
            Game.CONST["r"] = 2

            if self.turn.money <= 0: # turn player has no money
                if len(self.opponent.roster) >= Game.CONST["size"]: # opponent can't steal, automatically add to turn player roster
                    self.edit_stats(cur_idol, None, 0)
                    self.add_idol(self.turn, cur_idol, None)
                else: # opponent has choice to steal
                    print(f'{self.turn.name}{Game.c_reset} bids {Game.c_money}$0{Game.c_reset} for {cur_idol.to_string()}')
                    self.bid_process(0, cur_idol)
                break
            
            while True:
                ans = self.input_command("bid turn", self.turn) # turn player chooses action for rolled idol
                if isinstance(ans, int): # bid/give
                    self.bid_process(ans, cur_idol)
                    done = True
                elif ans == 'r': # reroll
                    self.turn.update_money(Game.CONST["r"]) # deduct money
                    dupes.append(cur_idol) # add idol to dupe list and reroll idol
                    self.edit_stats(cur_idol, "reroll", None) # add to reroll stat of rerolled idol
                    self.gambler_check(Game.CONST["r"]) # update gambler variant idols
                    Game.CONST["r"] = 2
                    self.show_money()
                    done = False
                elif ans == 'gr': # group reroll
                    self.turn.update_money(Game.CONST["gr"]) # deduct money
                    if not self.group_reroll(self.turn, cur_idol):
                        self.turn.money += Game.CONST["gr"]
                        done = False
                        continue
                    self.edit_stats(cur_idol, "gr", None) # add to gr stat of gr'd idol
                    self.gambler_check(Game.CONST["gr"]) # update gambler variant idols
                    done = True
                break
            if done:
                break
        
        self.variant_check() # try variant conditions
        print("-" * (Game.CONST["div"] + 2)) # divider

        self.turn_count += 1 # increment turn count
        if self.turn_count >= 2: # set extra money from spending perk to 0 after turn 2
            self.p1.extra_money = 0
            self.p2.extra_money = 0

        # show info and switch players for next turn
        self.show_game_info()
        self.switch_turns()

    def edit_stats(self, cur_idol: Idol, stat: str, price: int): # edits stats of idols
        edit_idol = cur_idol
        duplicate = False
        for idol in self.all_idols: # check if cur_idol already in list
            if cur_idol.equals(idol): # edit the info of the idol in the list instead of appending a new one
                edit_idol = idol
                duplicate = True
                break

        if price is not None: # set price of idol
            edit_idol.stats["price"] = price
        if stat in ["reroll", "opp reroll", "gr", "opp chances"]: # add to reroll stats
            edit_idol.stats[stat] += 1
            if stat == "opp reroll":
                edit_idol.stats["opp chances"] += 1
        elif stat: 
            edit_idol.stats[stat] = True

        if not duplicate: # append idol if not in history already
            self.all_idols.append(edit_idol)

    def play_game(self): # function that runs entire game
        # start game
        self.game_start()

        self.show_money()
        # playing out all turns until rosters are full
        while len(self.p1.roster) < Game.CONST["size"] or len(self.p2.roster) < Game.CONST["size"]:
            self.play_turn()

        # end game processes
        self.synergy_perk()
        self.deluxe_reroll()
        self.upgrade_idol()
        self.combat()
        self.final_screen()

    def synergy_perk(self): # function to apply synergy perk bonuses
        self.turn = self.p1
        for _ in range(2):
            if self.p1.perk == Perks.SYNERGY:
                print(f'\nPick an idol on {self.turn.name}\'s{Game.c_reset} roster to make Wildcard.')
                print("0. Cancel")
                for i in range(len(self.turn.roster)):
                    print(f'{i+1}. {self.turn.roster[i].to_string()}')
                while True:
                    ans = self.input_command("number", self.turn) # pick idol 1-5 to replace
                    if ans == 0:
                        return None
                    elif 1 <= ans <= Game.CONST["size"]:
                        idol = self.turn.roster[ans - 1]
                        del self.turn.roster[ans - 1]
                        idol.variant = Variants.WILDCARD
                        self.add_idol(self.turn, idol, ans - 1)
                        break
                    print(f'Invalid selection. Please choose a number between 1 and {Game.CONST["size"]}.')
            self.switch_turns()

    def booster_packs(self): # function to simulate booster pack process
        self.turn = self.p1
        for _ in range(2): # pulling individual cards
            if len(self.turn.roster) > 0: # if player has idols on their roster
                print("-" * (Game.CONST["div"] + 2)) # divider
                for idol in self.turn.roster:
                    if idol.variant == choose.Variants.COLLECTIBLE: # if idol is collectible, pull a card
                        print(f'Choose a card rarity to receive for {idol.to_string()}')
                        print("0. Cancel")
                        numbers = list(enumerate(card.rarities))
                        for i, rarity in numbers:
                            print(f'{i + 1}. {card.Card.colors[rarity]}{rarity.value}{Game.c_reset}')
                        while True:
                            ans = self.input_command("number", self.turn)
                            if 0 <= ans <= len(numbers):
                                if ans != 0: # player doesn't cancel
                                    _, chosen_rarity = numbers[ans - 1]
                                    card.single_card(self.turn.name, idol, Game.CONST["testing"], chosen_rarity)
                                    time.sleep(1)
                                break 
                            print("Invalid input!")
                print("Choose an idol to receive a card for:")
                print("0. Cancel")
                for i in range(len(self.turn.roster)):
                    print(f'{i + 1}. {self.turn.roster[i].to_string()}')
                while True:
                    ans = self.input_command("number", self.turn)
                    if 0 <= ans <= len(self.turn.roster):
                        if ans != 0: # player doesn't cancel
                            card.single_card(self.turn.name, self.turn.roster[ans - 1], Game.CONST["testing"], None)
                            time.sleep(1)
                        break
                    print("Invalid input!")
            self.switch_turns()

        # booster pack for winner
        print("-" * (Game.CONST["div"] + 2)) # divider
        print("Choose a booster pack to open:")
        packs = card.choose_boosters()
        print("0. Cancel")
        for i in range(len(packs)):
            print(f'{i + 1}. {packs[i].to_string()}')
        while True:
            ans = self.input_command("number", self.winner)
            if 0 <= ans <= 4:
                if ans != 0:
                    chosen = packs[ans - 1]
                    if chosen.type == "Your Choice":
                        print("Choose an idol for your booster pack:")
                        ans = self.input_command("idol", self.winner)
                        chosen.idol = ans
                    card.open_pack(self.winner, chosen, Game.CONST["testing"])
                break
            print("Invalid input!")

new_game = Game()
new_game.play_game()
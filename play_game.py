import choose_idol as choose
from choose_idol import Idol
import game_history
from game_history import History
from stupid import on_win

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
        self.color = color # color for their text
        self.ult = None # ultimate bias
        self.combat_score = 0 # combat score of this game
        self.dr = False # tracks whether they are finished with deluxe rerolls
        self.synergies = set() # keeps track of used synergies

class Game:
    CONST = {
        "r": 2, # reroll price
        "gr": 5, # group reroll price
        "dr": 6, # deluxe reroll price
        "size": 5, # max roster size
        "div": 90, # '-' divider width
        "synergies": 3, # number of idols needed to hit a synergy
        "testing": False # whether game is being played in a test state or not
    }

    c_reset = "\033[0m" # reset color (white)
    c_money = "\033[38;2;133;187;101m" # money color
    c_p1 = "\033[38;2;255;198;0m" # player 1 color
    c_p2 = "\033[38;2;255;67;67m" # player 2 color

    def __init__(self):
        self.p1 = self.p2 = None # holds player objects
        self.turn = None # holds player object who is currently their turn
        self.winner = None
        self.exodia = None
        self.flush = None
        self.history = History()

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

        print(f'{self.p1.name}{Game.c_reset} goes first! {self.p2.name}{Game.c_reset} goes second!')
        print("-" * (Game.CONST["div"] + 2))
        self.turn = self.p1
        print("Pick your ultimate biases:")
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
        ltext = self.uncenter_text(f'{self.p1.name}: {Game.c_money}${self.p1.money}{Game.c_reset}', Game.CONST["div"] // 2 - 1, False)
        rtext = self.uncenter_text(f'{self.p2.name}: {Game.c_money}${self.p2.money}{Game.c_reset}', Game.CONST["div"] // 2 - 1, True)
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

        left_name = f"{self.p1.name}{Game.c_reset} - {Game.c_money}${self.p1.money}{Game.c_reset}"
        right_name = f"{self.p2.name}{Game.c_reset} - {Game.c_money}${self.p2.money}{Game.c_reset}"

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
    
    def input_command(self, input_type: str, cur_player: Player) -> str: # yon: True for yes or no question, False if not
        while True:
            ans = input(f'{cur_player.name}{Game.c_reset} | ----> ').strip().lower() # Inquires for input

            # UTILITY COMMANDS - Available at any point in the game, do not affect game state
            if ans in ['e', 'exit']: # command to exit the game
                sys.exit()
            elif ans == 'reset stats': # resets all idol stats and removes all game history files
                game_history.reset_stats()
            elif ans in ['c', 'clear']: # command to clear terminal
                os.system('cls')
            elif ans in ['h', 'help']: # TODO: create total command list
                print ("") 
            elif ans in ['i', 'info']: # command to print out money and roster information
                self.show_game_info()
            elif ans in ['m', 'money']: # command to print out only money information
                self.show_money()
            elif ans in ['u', 'ult']: # command to show ultimate biases
                if self.p1.ult and self.p2.ult:
                    print(f'{self.p1.name}\'s{Game.c_reset} ultimate bias: {self.p1.ult.to_string()}')
                    print(f'{self.p2.name}\'s{Game.c_reset} ultimate bias: {self.p2.ult.to_string()}')
                else:
                    print("Not all ultimate biases chosen yet!")
            elif ans.startswith("st ") or ans.startswith("stats "): # command to search up stats for a specific idol
                answer = ans.split(" ", 2)
                search = None
                if len(answer) >= 3: # group specified
                    search = choose.find_idol(answer[1], answer[2])
                elif len(answer) >= 2: # group not specified
                    search = choose.find_idol(answer[1], "stat")
                if search:
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
                        if cur_player.money >= Game.CONST["r"]:
                            return 'r'
                        print("You don't have enough money for a reroll! ")
                        continue
                    elif ans in ['gr', 'group reroll']: # group reroll
                        if cur_player.money >= Game.CONST["gr"]:
                            return 'gr'
                        print("You don't have enough money for a group reroll! ")
                        continue
                print("Invalid command!") # all commands checked, invalid command

    def add_idol(self, player: Player, add: Idol, index: int) -> int: # add idol to a roster, potentially check synergies (might make new func for that)
        if index is not None:
            player.roster.insert(index, add)
        else:
            player.roster.append(add)

        print(f'{add.to_string()} added to {player.name}\'s{Game.c_reset} roster!')
        self.check_synergies(player)

    def replace_idol(self, player: Player) -> Idol: # function for replacing an idol on a roster
        print(f'Pick an idol on {player.name}\'s{Game.c_reset} roster to remove.')

        for i in range(len(player.roster)):
            print(f'{i+1}. {player.roster[i].to_string()}')
        while True:
            ans = self.input_command("number", self.turn) # pick idol 1-5 to replace
            if 1 <= ans <= Game.CONST["size"]:
                idol = player.roster[ans - 1]
                if self.turn != player and idol.protected:
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
            if len(idol.group.split('/')) > 1: # IZONE exception
                counts[idol.group.split('/')[0].strip()] += 1
                counts[idol.group.split('/')[1].strip()] += 1
            else: # for all other regular groups
                counts[idol.group] += 1 
        player.synergies.update({syn for syn, count in counts.items() if count >= Game.CONST["synergies"]})
        new_syn = player.synergies - old_syn

        # foreigners = 0 # give money according to amount of foreign idols
        # for idol in player.roster:
        #     if idol.country != "Korean":
        #         foreigners += 1
        # if foreigners > 1 and foreigners not in player.synergies:
        #     player.money += 1
        #     player.synergies.add(foreigners)
        #     print(f'{player.name}{Game.c_reset} has {foreigners} foreigners! They have gained {Game.c_money}${foreigners - 1}{Game.c_reset} in total!')

        if new_syn: # give synergy effects
            for syn in new_syn:
                if len(syn) > 1: # group synergy (SWITCH))
                    print(f'{player.name}{Game.c_reset} hit a group synergy for {Game.c_money}{syn}{Game.c_reset}! They receive a switch powerup.')
                    if len(opp.roster) != 0:
                        turn_ind = self.replace_idol(player)
                        opp_ind = self.replace_idol(opp)

                        opp_ind[1].stats["switch"] ^= True # invert current boolean values for SWITCH info
                        turn_ind[1].stats["switch"] ^= True

                        self.add_history(opp_ind[1], "switch", None)
                        self.add_history(turn_ind[1], "switch", None)

                        self.add_idol(player, opp_ind[1], turn_ind[0])
                        self.add_idol(opp, turn_ind[1], opp_ind[0])
                    else:
                        print(f'{opp.name}\'s{Game.c_reset} roster is empty, so you can\'t use the switch!')
                else: # letter synergy (ADD/REPLACE))
                    print(f'{player.name}{Game.c_reset} hit a letter synergy for {Game.c_money}{syn}{Game.c_reset}! They get to add/replace an idol.')
                    ind = None
                    if len(player.roster) >= Game.CONST["size"]: # player roster is full, must replace instead of adding
                        removed = self.replace_idol(player)
                        removed[1].stats["reroll"] += 1 # add to reroll stat of removed idol
                        ind = removed[0]
                    print(f'Choose an idol whose name starts with a {Game.c_money}{syn.upper()}{Game.c_reset}: (name) (group)')

                    while True:
                        ans = self.input_command("idol", player)
                        if isinstance(ans, Idol) and ans.name.lower().startswith(syn.lower()) and not any(ans.equals(compare) for compare in player.roster):
                            ans.protected = True
                            self.add_history(ans, "letter", None)
                            self.add_idol(player, ans, ind)
                            break
                        else:
                            print("Invalid idol!")

    def check_exodia(self, player: Player): # function to check exodia synergies
        if len(player.roster) >= Game.CONST["size"]:
            char = player.roster[0].name[0] # starting letter
            groups = player.roster[0].group.split('/') # group
            if all(idol.name[0] == char for idol in player.roster): # full roster of letter synergy
                self.exodia = f'letter exodia! {Game.c_money}({char.upper()}){Game.c_reset}'
            elif all(idol.age < 18 for idol in player.roster): # full roster of minors
                self.exodia = "minor exodia!"
            for group in groups:
                if all(group in idol.group for idol in player.roster): # full roster of same group
                    self.exodia = f'group exodia! {Game.c_money}({group}){Game.c_reset}'

            if self.exodia:
                win_text = f'{player.name}{Game.c_reset} won through {self.exodia}'
                if group in self.exodia:
                    self.exodia = group
                elif 'minor' in self.exodia:
                    self.exodia = "Minors"
                else:
                    self.exodia = char
                print(f'\n{self.format_text(win_text, Game.CONST["div"] + 2)}')
                self.winner = player
                self.final_screen()

    # True if duplicate is protected and cannot be stolen
    # False if no duplicate, or duplicate exists and is stolen
    def duplicate_check(self, cur_idol: Idol) -> int: # check if rolled idol is already on a roster
        for idol in self.opponent.roster: 
            if cur_idol.equals(idol):
                if not idol.protected: # only steal if idol is not protected
                    print(f'{self.turn.name} steals {cur_idol.to_string()} from {self.opponent.name}\'s{Game.c_reset} roster!')
                    self.add_history(idol, "stolen", None)
                    self.add_idol(self.turn, idol, None)
                    self.opponent.roster.remove(idol)
                    return 1
                else: # idol is protected, cannot be stolen
                    print(f'{self.turn.name}{Game.c_reset} tries to steal {cur_idol.to_string()} from {self.opponent.name}{Game.c_reset}, but they are protected!')
                    return 2
        return 0
    
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
                            self.opponent.money -= amount
                            self.switch_turns() # switch turns so idol is added to proper player
                            self.group_reroll(cur_idol)
                            self.switch_turns() # switch back to preserve turn order
                            return
                        else:
                            print("You do not have enough money to bid and group reroll!")
                            continue
                    elif bid >= 0: # opponent bids to buy
                        if counter_bid > bid:
                            self.add_history(cur_idol, None, counter_bid)
                            self.add_idol(self.opponent, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent.")
                            continue
                    else: # opponent bids to give
                        if counter_bid < bid:
                            self.add_history(cur_idol, None, counter_bid)
                            self.add_idol(self.turn, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent.")
                            continue
                    self.opponent.money -= abs(counter_bid)
                    opponent_win = True
        if not opponent_win: # turn player wins bid
            cur_idol.stats["price"] = bid
            if bid >= 0:
                self.add_idol(self.turn, cur_idol, None)
            else:
                self.add_idol(self.opponent, cur_idol, None)
            self.add_history(cur_idol, None, bid)
            self.turn.money -= abs(bid)

    # TODO: Add group rerolling for opponent after they outbid for the idol
    def group_reroll(self, dup_idol: Idol): # function for handling group reroll process
        cur_idol = dup_idol
        dupes = [dup_idol]
        for _ in range(2):
            for idol in self.turn.roster:
                dup_groups = dup_idol.group.split('/')
                for dup_group in dup_groups:
                    if dup_group in idol.group.split('/'):
                        dupes.append(idol)
            self.switch_turns()
        while True:
            if not Game.CONST["testing"]:
                print("Rolling idol...")
                time.sleep(1) # suspense
                print("\033[F\033[K", end="") # deletes previous line to replace with rolled idol
            cur_idol = choose.random_idol(cur_idol.group, 1, dupes)[0]
            cur_idol.protected = True # idols from group rerolls are protected
            if self.turn.money >= Game.CONST["gr"]: # group reroll again
                print(cur_idol.to_string())
                print("Would you like to group reroll again? ",)
                if self.input_command("yon", self.turn) == 'y': # if answer is yes
                    self.turn.money -= Game.CONST["gr"]
                    self.add_history(cur_idol, "reroll", None)
                    dupes.append(cur_idol)
                    continue
            break
        self.add_history(cur_idol, "gr", None)
        self.add_idol(self.turn, cur_idol, None)

    def deluxe_reroll(self): # function for deluxe reroll
        self.turn = self.p1
        while not self.p1.dr or not self.p2.dr:
            if self.turn.dr: # if current player is done with deluxe rerolls, switch to next player
                self.switch_turns()
            if self.turn.money >= Game.CONST["dr"]: # if they have money for deluxe reroll
                print(f'{self.turn.name}{Game.c_reset}, would you like to deluxe reroll for ${Game.CONST["dr"]}?')
                if self.input_command("yon", self.turn) == 'y': # dr if yes, else break and move to next player
                    self.turn.money -= Game.CONST["dr"]
                    removed = self.replace_idol(self.turn) # index and object of removed idol
                    removed[1].stats["reroll"] += 1 # add 1 to reroll stat
                    if not Game.CONST["testing"]:
                        print("Rolling idol...")
                        time.sleep(1) # suspense
                        print("\033[F\033[K", end="") # deletes previous line to replace with rolled idol
                    choices = choose.random_idol(None, 3, self.p1.roster + self.p2.roster) # deluxe reroll cannot roll duplicates
                    print("Pick an idol to add to your roster:")
                    for i, choice in enumerate(choices, start=1):
                        print(f'{i}. {choice.to_string()}')
                    while True:
                        ans = self.input_command("number", self.turn) # pick idol 1-3 to add
                        if 1 <= ans <= 3:
                            self.add_history(choices[ans-1], "dr", None)
                            self.add_idol(self.turn, choices[ans-1], removed[0])
                            break
                        print(f'Invalid selection!')
                    self.switch_turns()
                    continue
                self.turn.dr = True # player says no to deluxe reroll
            else: # player does not have enough money for deluxe reroll
                self.turn.dr = True

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

            p2_prob = 0.5 ** (abs(sorted_p1[i].rating - sorted_p2[i].rating) + 1) # probability calculation
            p1_prob = 1 - p2_prob
            if sorted_p1[i].rating < sorted_p2[i].rating:
                p1_prob, p2_prob = p2_prob, p1_prob

            if self.flush == self.p1:
                p1_prob = min(p1_prob + ((1 - p1_prob) ** 4) * 0.6 + 0.02, 1)
                p2_prob = 1 - p1_prob
            elif self.flush == self.p2:
                p2_prob = min(p2_prob + ((1 - p2_prob) ** 4) * 0.6 + 0.02, 1)
                p1_prob = 1 - p2_prob
            
            p1_text = self.format_text(f'{sorted_p1[i].to_string()}', Game.CONST["div"] // 2 - 8)
            p2_text = self.format_text(f'{sorted_p2[i].to_string()}', Game.CONST["div"] // 2 - 8)
            p1_percent = self.uncenter_text(f'{Game.c_money}{round(p1_prob*100, 2)}%{Game.c_reset}', 6, False)
            p2_percent = self.uncenter_text(f'{Game.c_money}{round(p2_prob*100, 2)}%{Game.c_reset}', 6, True)
            print(f'{p1_text} {p1_percent} || {p2_percent} {p2_text}')

            # add suspense before each matchup, extra if game is tied at 5th matchup
            if i == (len(sorted_p1) - 1) and self.p1.combat_score == self.p2.combat_score:
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
                win_string = f'{sorted_p1[i].to_string()} wins!'
                self.p1.combat_score += 1
            else: 
                win_string = f'{sorted_p2[i].to_string()} wins!'
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

    def final_screen(self): # closes the game, uploads data
        if "Jason" in self.winner.name :
            on_win(False)
        self.show_game_info()
        if not Game.CONST["testing"]:
            self.history.write_history(self) # writes game history to a file and updates idol stats
        sys.exit()

    def ultimate_bias(self, idol: Idol) -> bool: # handle actions when ultimate bias is rolled
        ult_player = None
        ult_value = idol.ult_value()
        if idol.equals(self.p1.ult):
            ult_player = self.p1
        elif idol.equals(self.p2.ult):
            ult_player = self.p2
        if ult_player and ult_player.money >= ult_value and len(ult_player.roster) < Game.CONST["size"]:
            print(f'{idol.to_string()} is {ult_player.name}\'s{Game.c_reset} ultimate bias! Would you like to instantly add them to your roster for {Game.c_money}${ult_value}{Game.c_reset}?')
            ans = self.input_command("yon", ult_player)
            if ans == 'y':
                ult_player.money -= ult_value
                idol.protected = True
                self.add_history(idol, "ult", ult_value)
                self.add_idol(ult_player, idol, None)
                return True
        return False

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
            cur_idol = choose.random_idol(None, 1, self.turn.roster + dupes)[0] # roll idol
            print(self.format_text(cur_idol.to_string(), Game.CONST["div"] + 2))

            dup_check = self.duplicate_check(cur_idol) # check for duplicates
            if dup_check == 1: # duplicate was stolen
                break # end turn 
            elif dup_check == 2: # duplicate was protected, reroll idol
                dupes.append(cur_idol)
                continue
            if self.ultimate_bias(cur_idol): # check for ultimate bias
                break # end turn if ultimate bias was bought
            
            if len(self.opponent.roster) >= Game.CONST["size"] and self.opponent.money >= Game.CONST["r"]: # opponent reroll
                print(f'{self.opponent.name},{Game.c_reset} would you like to reroll {self.turn.name}\'s{Game.c_reset} idol for ${Game.CONST["r"]}? ')
                if self.input_command("yon", self.opponent) == 'y': # if answer is yes
                    self.opponent.money -= Game.CONST["r"]
                    self.add_history(cur_idol, "reroll", None) # add idol to history
                    self.show_money()
                    continue

            if len(self.opponent.roster) >= Game.CONST["size"] and self.turn.money <= 0: # opponent roster is full and turn player has no options, automatically add idol
                self.add_idol(self.turn, cur_idol, None)
                self.add_history(cur_idol, None, 0)
                break
            
            ans = self.input_command("bid turn", self.turn) # turn player chooses action for rolled idol
            if isinstance(ans, int): # bid/give
                self.bid_process(ans, cur_idol)
                break
            elif ans == 'r': # reroll
                self.turn.money -= Game.CONST["r"] # deduct money
                dupes.append(cur_idol) # add idol to dupe list and reroll idol
                self.add_history(cur_idol, "reroll", None) # add idol to history
                self.show_money()
                continue 
            elif ans == 'gr': # group reroll
                self.turn.money -= Game.CONST["gr"] # deduct money
                self.add_history(cur_idol, "reroll", None) # add idol to history
                self.group_reroll(cur_idol)
                break
        print('\n')
        self.show_game_info()
        self.switch_turns()

    def add_history(self, cur_idol: Idol, stat: str, price: int): # adds an idol to the history list in History object
        duplicate = False
        for idol in self.history.all_idols: # check if cur_idol already in list
            if cur_idol.equals(idol): # edit the info of the idol in the list instead of appending a new one
                duplicate = True
                if price is not None:
                    idol.stats["price"] = price
                if stat == "reroll":
                    idol.stats[stat] += 1
                elif stat:
                    idol.stats[stat] = True
                break
        
        if price is not None: # always edit the new idol object passed in for accurate data when creating overview
            cur_idol.stats["price"] = price
        if stat == "reroll":
            cur_idol.stats[stat] += 1
        elif stat:
            cur_idol.stats[stat] = True

        if not duplicate: # if idol was not already in idol history list
            self.history.all_idols.append(cur_idol) # add idol to list

    def play_game(self): # function that runs entire game
        # start game
        self.game_start()

        # playing out all turns until rosters are full
        while len(self.p1.roster) < Game.CONST["size"] or len(self.p2.roster) < Game.CONST["size"]:
            self.play_turn()
        
        # end game processes
        self.deluxe_reroll()
        self.combat()
        self.final_screen()

new_game = Game()
new_game.play_game()
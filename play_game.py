import choose_idol as choose
from choose_idol import Idol
import os
import sys
from collections import Counter
import re
import time
import random

class Col:
    reset = "\033[0m" # reset color (white)
    money = "\033[38;2;133;187;101m" # money color
    p1 = "\033[38;2;255;198;0m" # player 1 color
    p2 = "\033[38;2;255;67;67m" # player 2 color

class Player:
    def __init__(self, name, color):
        self.name = name
        self.roster = []
        self.money = 15
        self.color = color
        self.ult = None
        self.synergies = set() # keeps track of used synergies

class Game:
    CONST = {
        "r": 2, # reroll price
        "gr": 5, # group reroll price
        "dr": 6, # deluxe reroll price
        "size": 5, # max roster size
        "div": 41 # '-' divider width
    }

    def __init__(self):
        self.p1 = self.p2 = None # holds player objects
        self.turn = None # holds player object who is currently their turn
        self.winner = None

    @property
    def opponent(self): # holds player object who is currently not their turn
        return self.p2 if self.turn == self.p1 else self.p1
    
    def switch_turns(self):
        self.turn = self.opponent

    def game_start(self) -> str: # start and restart games

        def player_first(): # function that 50/50s to see which player goes first
            print("Flipping a coin to determine which player goes first...")
            time.sleep(1)
            return random.choice([True, False])

        os.system('cls')
        while True:
            # p1 = input("Enter player name: ").strip()
            # p2 = input("Enter player name: ").strip()
            p1 = "Sejun"
            p2 = "Jason"

            if p1 != p2 and p1 and p2:
                self.p1 = Player(f'{Col.p1}{p1}', Col.p1)
                self.p2 = Player(f'{Col.p2}{p2}', Col.p2)
                if player_first():
                    self.p1, self.p2 = self.p2, self.p1
                break
            print("Player names must be different.")

        print(f'{self.p1.name}{Col.reset} goes first! {self.p2.name}{Col.reset} goes second!')
        print("-" * (Game.CONST["div"] * 2 + 2))
        self.turn = self.p1
        for _ in range(2):
            print("Pick your ultimate bias:")
            while True:
                ans = self.input_command("idol", self.turn)
                answer = ans.split(" ", 1)
                if len(answer) == 2:
                    self.turn.ult = choose.find_idol(answer[0], answer[1])
                    if self.turn.ult: # check if inputted idol is valid
                        if self.opponent.ult and not self.turn.ult.equals(self.opponent.ult):
                            break
                        elif not self.opponent.ult:
                            break
                print("Invalid idol!")
            print(f'{self.turn.name}\'s{Col.reset} ultimate bias: {self.turn.ult.to_string()}')
            self.switch_turns()


    def strip_ansi(self, text): # remove ansi from strings (for text using center formatting)
        ansi_escape = re.compile(r'\033\[[0-9;]*m') 
        return ansi_escape.sub('', text) 

    def format_text(self, text, width):
            return text.center(width + (len(text) - len(self.strip_ansi(text))))

    def show_game_info(self):
        num_lines = max(len(self.turn.roster), len(self.opponent.roster))
        width = Game.CONST["div"]
        half = width // 2

        def idol_string(player):
            try:
                return player.roster[i].to_string().split('|')
            except IndexError:
                return ['', '']

        left_name = f"{self.p1.name}{Col.reset} - {Col.money}${self.p1.money}{Col.reset}"
        right_name = f"{self.p2.name}{Col.reset} - {Col.money}${self.p2.money}{Col.reset}"

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
    
    # Return codes:
    # 0 - No/Reroll
    # 1 - Yes/Group Reroll
    # "number" - return int, returned integer is bid amount/idol selection
    # "com" - non-bid command, returned integer is an action code
    # type - 
    def input_command(self, input_type: str, cur_player: Player) -> str: # yon: True for yes or no question, False if not
        while True:
            ans = input(f'{cur_player.name}{Col.reset} | ----> ').strip().lower() # Inquires for input

            # UTILITY COMMANDS - Available at any point in the game, do not affect game state
            if ans in ['e', 'exit']: # command to exit the game
                sys.exit()
            elif ans in ['c', 'clear']: # command to clear terminal
                os.system('cls')
            elif ans in ['h', 'help']: # TODO: create total command list
                print ("") 
            elif ans in ['i', 'info']: # command to print out money and roster information
                self.show_game_info()
            elif ans in ['m', 'money']: # command to print out only money information
                print(f'{self.p1.name}: {Col.money}${self.p1.money}{Col.reset} | {self.p2.name}: {Col.money}${self.p2.money}{Col.reset}')
            elif ans.startswith("u ") and len(ans.split()) == 2: # command to print a player's ultimate bias
                player_int = int(ans.split()[1])
                if 1 <= player_int <= 2:
                    if player_int == 1:
                        print(f'{self.p1.name}\'s{Col.reset} ultimate bias: {self.p1.ult.to_string()}')
                    else:
                        print(f'{self.p2.name}\'s{Col.reset} ultimate bias: {self.p2.ult.to_string()}')
                else:
                    ("Invalid command!")
                    continue
            else:
                if "idol" in input_type: # for typing in specific idol names
                    return ans
                if "number" in input_type or "bid" in input_type: 
                    try: # see if command is an integer (for bids or selections)
                        num = int(ans)
                        if "bid" in input_type:
                            if abs(num) <= cur_player.money: # for bids (needs money check)
                                return num
                            else:
                                print("Not enough money!")
                                continue
                        else: # for selections
                            return num
                    except ValueError:
                        pass
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
                            cur_player.money -= Game.CONST["r"]
                            return 'r'
                        print("You don't have enough money for a reroll! ")
                        continue
                    elif ans in ['gr', 'group reroll']: # group reroll
                        if cur_player.money >= Game.CONST["gr"]:
                            cur_player.money -= Game.CONST["gr"]
                            return 'gr'
                        print("You don't have enough money for a group reroll! ")
                        continue
                print("Invalid command!") # all commands checked, invalid command

    def add_idol(self, player: Player, add: Idol, index: int) -> int: # add idol to a roster, potentially check synergies (might make new func for that)
        if index is not None:
            player.roster.insert(index, add)
        else:
            player.roster.append(add)

        print(f'{add.to_string()} added to {player.name}\'s{Col.reset} roster!')
        self.check_synergies(player)

    def replace_idol(self, player: Player) -> Idol:
        idol = None # idol to be removed
        print(f'Pick an idol on {player.name}\'s{Col.reset} roster to remove.')

        for i in range(len(player.roster)):
            print(f'{i+1}. {player.roster[i].to_string()}')
        while True:
            ans = self.input_command("number", self.turn) # pick idol 1-5 to replace
            if 1 <= ans <= Game.CONST["size"]:
                idol = player.roster[ans - 1]
                if self.turn != player and idol.protected:
                    print(f'{idol.to_string()} is protected and cannot be replaced!')
                    continue
                del player.roster[ans - 1]
                break
            print(f'Invalid selection. Please choose a number between 1 and {Game.CONST["size"]}.')
        return ans - 1, idol
            
    def check_synergies(self, player: Player): # function to check and handle synergies
        self.check_exodia(player) # checks for exodia synergies
        opponent = self.p1 if player == self.p2 else self.p2

        old_syn = player.synergies.copy()
        counts = Counter()
        for idol in player.roster:
            counts[idol.name[0]] += 1
            counts[idol.group] += 1 
        player.synergies.update({syn for syn, count in counts.items() if count >= 3})
        new_syn = player.synergies - old_syn

        if new_syn: # give synergy effects
            for syn in new_syn:
                if len(syn) > 1: # group synergy (SWITCH))
                    print(f'{player.name}{Col.reset} hit a group synergy for {Col.money}{syn}{Col.reset}! They receive a switch powerup.')
                    if len(self.opponent.roster) != 0:
                        turn_ind = self.replace_idol(self.turn)
                        opp_ind = self.replace_idol(self.opponent)

                        self.add_idol(self.turn, opp_ind[1], turn_ind[0])
                        self.add_idol(self.opponent, turn_ind[1], opp_ind[0])
                    else:
                        print(f'{opponent.name}\'s{Col.reset} roster is full, so you can\'t use the switch!')
                else: # letter synergy (ADD/REPLACE))
                    print(f'{player.name}{Col.reset} hit a letter synergy for {Col.money}{syn}{Col.reset}! They get to add/replace an idol.')
                    ind = None
                    if len(player.roster) >= Game.CONST["size"]: # player roster is full, must replace instead of adding
                        ind = self.replace_idol(player)
                    print(f'Choose an idol whose name starts with a {Col.money}{syn.upper()}{Col.reset}: (name) (group)')

                    while True:
                        ans = self.input_command("idol", player)
                        answer = ans.split(" ", 1)
                        if ans.startswith(syn.lower()) and len(answer) == 2:
                            idol_add = choose.find_idol(answer[0], answer[1])
                            if idol_add:
                                self.add_idol(player, idol_add, ind[0])
                                break
                            print("Invalid idol!")
                        else:
                            print("Invalid idol!")

    def check_exodia(self, player: Player): # function to check exodia synergies
        if len(player.roster) >= Game.CONST["size"]:
            char = player.roster[0].name[0] # starting letter
            group = player.roster[0].group # group
            exodia = True
            if all(idol.name[0] == char for idol in player.roster): # full roster of letter synergy
                message = f'letter exodia! {Col.money}({char}){Col.reset}'
            elif all(idol.group == group for idol in player.roster): # full roster of same group
                message = f'group exodia! {Col.money}({group}){Col.reset}'
            elif all(idol.age < 18 for idol in player.roster): # full roster of minors
                message = "minor exodia!"
            else:
                exodia = False

            if exodia:
                print("-" * (Game.CONST["div"] * 2 + 2))
                print(f'{player.name}{Col.reset} won through {message}')
                self.winner = player
                self.final_screen()

    # True if duplicate is protected and cannot be stolen
    # False if no duplicate, or duplicate exists and is stolen
    def duplicate_check(self, cur_idol: Idol) -> int: # check if rolled idol is already on a roster
        for idol in self.opponent.roster: 
            if cur_idol.equals(idol):
                if not idol.protected: # only steal if idol is not protected
                    print(f'{cur_idol.to_string()} is already in {self.opponent.name}\'s{Col.reset} roster, so you steal them to your own roster!')
                    self.opponent.roster.remove(idol)
                    self.add_idol(self.turn, cur_idol, None)
                    return 1
                else: # idol is protected, cannot be stolen
                    return 2
        return 0
    
    def bid_process(self, bid: int, cur_idol: Idol): # function that handles bidding process
        opponent_win = False
        if len(self.opponent.roster) < Game.CONST["size"]: # check if opponent roster is full
            if self.opponent.money > abs(bid): # check if opponent has enough money to counter bid
                while not opponent_win:
                    counter_bid = self.input_command("number yon", self.opponent)
                    if counter_bid == 'n': # opponent doesn't bid
                        break
                    if bid >= 0: # opponent bids to buy
                        if counter_bid > bid:
                            self.add_idol(self.opponent, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent ",)
                            continue
                    else: # opponent bids to give
                        if counter_bid < bid:
                            self.add_idol(self.turn, cur_idol, None)
                        else: 
                            print("Bid must be more than your opponent ",)
                            continue
                    self.opponent.money -= abs(counter_bid)
                    opponent_win = True
        if not opponent_win: # turn player wins bid
            if bid >= 0:
                self.add_idol(self.turn, cur_idol, None)
            else:
                self.add_idol(self.opponent, cur_idol, None)
            self.turn.money -= abs(bid)

    # TODO: Add group rerolling for opponent after they outbid for the idol
    def group_reroll(self, dup_idol: Idol): # function for handling group reroll process
        dupes = [dup_idol]
        for idol in self.turn.roster:
            if idol.group == dup_idol.group:
                dupes.append(idol)
        while True:
            cur_idol = choose.random_idol(dup_idol.group, 1, dupes)[0]
            if self.turn.money >= Game.CONST["gr"]: # group reroll again
                print(cur_idol.to_string())
                print("Would you like to group reroll again? ",)
                if self.input_command("yon", self.turn) == 'y': # if answer is yes
                    self.turn.money -= Game.CONST["gr"]
                    dupes.append(cur_idol)
                else: 
                    break
            else:
                break

        idol.protected = True # idols from group rerolls are protected
        self.add_idol(self.turn, cur_idol, None)

    def deluxe_reroll(self): # function for deluxe reroll
        self.turn = self.p1
        for _ in range(2):
            while self.turn.money >= Game.CONST["dr"]: # if they have money for deluxe reroll
                print(f'{self.turn.name}{Col.reset}, would you like to deluxe reroll for ${Game.CONST["dr"]}?')
                if self.input_command("yon", self.turn) == 'y': # dr if yes, else break and move to next player
                    self.turn.money -= Game.CONST["dr"]
                    ind = self.replace_idol(self.turn)[0] # index of idol that was removed
                    choices = choose.random_idol(None, 3, self.p1.roster + self.p2.roster) # deluxe reroll cannot roll duplicates
                    print("Pick an idol to add to your roster:")
                    for i, choice in enumerate(choices, start=1):
                        print(f'{i}. {choice.to_string()}')
                    while True:
                        ans = self.input_command("number", self.turn) # pick idol 1-3 to add
                        if 1 <= ans <= 3:
                            self.add_idol(self.turn, choices[ans-1], ind)
                            break
                        print(f'Invalid selection!')
                else:
                    break
            self.switch_turns()

    def combat(self): # simulates combat to determine a game winner
        print("-" * (Game.CONST["div"] * 2 + 2))
        p1_wins = 0
        p2_wins = 0
        sorted_p1 = sorted(self.p1.roster, key=lambda idol: idol.rating, reverse=True)
        sorted_p2 = sorted(self.p2.roster, key=lambda idol: idol.rating, reverse=True)

        for i in range(len(sorted_p1)):
            print(self.format_text(f'Matchup #{i+1}:', (Game.CONST["div"]*2+2)))
            p2_prob = 0.5 ** (abs(sorted_p1[i].rating - sorted_p2[i].rating) + 1)
            p1_prob = 1 - p2_prob
            if sorted_p1[i].rating < sorted_p2[i].rating:
                p1_prob, p2_prob = p2_prob, p1_prob
            p1_text = f'{sorted_p1[i].to_string()} {Col.money}{round(p1_prob*100, 2)}{Col.reset}%'
            p2_text = f'{sorted_p2[i].to_string()} {Col.money}{round(p2_prob*100, 2)}{Col.reset}%'
            p1_text, p2_text = self.format_text(p1_text, Game.CONST["div"]), self.format_text(p2_text, Game.CONST["div"]), 
            print(f'{p1_text}||{p2_text}')

            time.sleep(3)
            winner = random.choices([self.p1, self.p2], weights=[p1_prob, p2_prob])
            if winner[0] == self.p1:
                win_string = f'{sorted_p1[i].to_string()} wins!'
                p1_wins += 1
            else: 
                win_string = f'{sorted_p2[i].to_string()} wins!'
                p2_wins += 1
            print(self.format_text(win_string, (Game.CONST["div"]*2+2)))
            cur_score = f'{self.p1.name}:{Col.reset} {p1_wins} || {self.p2.name}:{Col.reset} {p2_wins}'
            print(self.format_text(cur_score, (Game.CONST["div"]*2+2)))
        if p1_wins > p2_wins:
            self.winner = self.p1
        else:
            self.winner = self.p2
        final_score = f'{self.winner.name}{Col.reset} wins the game {self.p1.color}{p1_wins}{Col.reset} to {self.p2.color}{p2_wins}{Col.reset}!'
        print(self.format_text(final_score, (Game.CONST["div"]*2+2)))
    
    def end_game(self): # performs all end game processes
        self.deluxe_reroll()
        self.combat()
        self.final_screen()

    def final_screen(self): # closes the game, uploads data
        self.show_game_info()
        # TODO: Upload game history and idol stats to files
        input('Press any key to exit.')
        sys.exit()

    def ultimate_bias(self, idol: Idol) -> bool: # handle actions when ultimate bias is rolled
        ult_player = None
        ult_value = idol.ult_value()
        if idol.equals(self.p1.ult):
            ult_player = self.p1
        elif idol.equals(self.p2.ult):
            ult_player = self.p2
        if ult_player and ult_player.money >= ult_value:
            print(f'{idol.to_string()} is {ult_player.name}\'s{Col.reset} ultimate bias! Would you like to instantly buy them for {ult_value}?')
            ans = self.input_command("yon", ult_player)
            if ans == 'y':
                ult_player.money -= ult_value
                self.add_idol(ult_player, idol, None)

    def play_turn(self): # main game function to play out a turn
        if len(self.turn.roster) >= Game.CONST["size"]: # switch turn if one player's roster is full
            self.switch_turns()

        print(f'{"-" * (Game.CONST["div"] * 2 + 2)}\n{self.turn.name}\'s{Col.reset} Turn ')

        while True:
            cur_idol = choose.random_idol(None, 1, self.turn.roster)[0] # roll idol
            print(cur_idol.to_string())

            dup_res = self.duplicate_check(cur_idol) # check for duplicates
            if dup_res == 2:
                print(f'{cur_idol.to_string()} is a duplicate, but is protected and cannot be stolen!')
                continue
            elif dup_res == 1:
                break

            self.ultimate_bias(cur_idol)
            
            if len(self.opponent.roster) >= Game.CONST["size"] and self.opponent.money >= Game.CONST["r"]: # opponent reroll
                print(f'{self.opponent.name}{Col.reset}, would you like to reroll your opponent\'s idol for ${Game.CONST["r"]}? ',)
                if self.input_command("yon", self.opponent) == 'y': # if answer is yes
                    self.opponent.money -= Game.CONST["r"]
                    continue
            ans = self.input_command("number turn", self.turn)
            
            if isinstance(ans, int): # bid/give
                self.bid_process(ans, cur_idol)
                break
            elif ans == 'r': # reroll
                continue
            elif ans == 'gr': # group reroll
                self.group_reroll(cur_idol)
                break

        self.switch_turns()

    def play_game(self): # function that runs entire game
        self.game_start()
        while len(self.p1.roster) < Game.CONST["size"] or len(self.p2.roster) < Game.CONST["size"]:
            self.play_turn()
        self.end_game()

new_game = Game()
new_game.play_game()
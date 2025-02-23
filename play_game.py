import choose_idol as choose
from choose_idol import Idol
import os
import math
import sys
from collections import Counter

class Col:
    reset = "\033[0m" # reset color (white)
    money = "\033[38;2;133;187;101m" # money color
    p1 = "\033[38;2;255;198;0m" # player 1 color
    p2 = "\033[38;2;255;67;67m" # player 2 color

class Player:
    def __init__(self, name):
        self.name = name
        self.roster = []
        self.money = 15
        self.synergies = set() # keeps track of used synergies

class Game:
    CONST = {
        "r": 2, # reroll price
        "gr": 5, # group reroll price
        "dr": 6, # deluxe reroll price
        "size": 5 # max roster size
    }

    def __init__(self):
        self.p1 = self.p2 = None # holds player objects
        self.turn = None # holds player object who is currently their turn
        self.game_over = False
        self.winner = None

    @property
    def opponent(self): # holds player object who is currently not their turn
        return self.p2 if self.turn == self.p1 else self.p1
    
    def switch_turns(self):
        self.turn = self.opponent

    def game_start(self) -> str: # start and restart games
        os.system('cls')
        while True:
            # p1 = input("Enter player one name: ").strip()
            # p2 = input("Enter player two name: ").strip()
            p1 = "Sejun"
            p2 = "Jason"

            if p1 != p2 and p1 and p2:
                p1 = f'{Col.p1}{p1}{Col.reset}'
                p2 = f'{Col.p2}{p2}{Col.reset}'
                self.p1 = Player(p1)
                self.p2 = Player(p2)
                break
            print("Player names must be different.")
        self.turn = self.p1
        self.game_over = False

    def show_game_info(self):
        PADDING = 30
        num_lines = max(len(self.turn.roster), len(self.opponent.roster))

        def get_player_from_roster(player):
            try:
                return player.roster[i].to_string()
            except IndexError:
                return ''

        p1_name_padding = (PADDING - len(self.p1.name) - len(str(self.p1.money)) - 4) / 2
        p1_name = f'{" " * int(math.ceil(p1_name_padding))}{self.p1.name} - ${self.p1.money}{" " * int(math.floor(p1_name_padding))}'
        p2_name_padding = (PADDING - len(self.p2.name) - len(str(self.p1.money)) - 5) / 2
        p2_name = f'{" " * int(math.ceil(p2_name_padding))}{self.p2.name} - ${self.p2.money}'
        print(f'{p1_name}||{p2_name}')
        print("-" * 62)

        for i in range(num_lines):
            left_player = get_player_from_roster(self.p1)
            left_padding = (PADDING - len(left_player)) / 2
            left_player_string = f'{" " * int(math.ceil(left_padding))}{left_player}{" " * int(math.floor(left_padding))}'
            right_player = get_player_from_roster(self.p2)
            right_player_string = f'{" " * int(math.ceil((PADDING - 1 - len(right_player)) / 2))}{right_player}'

            print(f'{left_player_string}||{right_player_string}')
    
    # Return codes:
    # 0 - No/Reroll
    # 1 - Yes/Group Reroll
    # "number" - return int, returned integer is bid amount/idol selection
    # "com" - non-bid command, returned integer is an action code
    # type - 
    def input_command(self, input_type: str, cur_player: Player) -> int: # yon: True for yes or no question, False if not
        while True:
            ans = input(f'{cur_player.name} | ----> ').strip().lower() # Inquires for input

            # UTILITY COMMANDS - Available at any point in the game, do not affect game state
            if ans in ['new', 'reset']: # reset game
                sys.exit()
            elif ans in ['i', 'info']:
                self.show_game_info()
            elif ans in ['h', 'help']:
                print ("") # todo: Create command list
            elif ans in ['c', 'clear']:
                os.system('cls')
            elif ans in ['m', 'money']:
                print(f'{self.turn.name}: {Col.money}${self.turn.money}{Col.reset} | {self.opponent.name}: {Col.money}${self.opponent.money}{Col.reset}')
            else:
                if "idol" in input_type: # for typing in specific idol names
                    idol = ans.split()
                    if len(idol) == 2:
                        return (idol, 0)
                    print("Invalid format!")
                    continue
                if "number" in input_type or "bid" in input_type: 
                    try: # see if command is an integer (for bids or selections)
                        num = int(ans)
                        if "bid" in input_type:
                            if abs(num) <= cur_player.money: # for bids (needs money check)
                                return ("number", num)
                            else:
                                print("Not enough money!")
                                continue
                        else: # for selections
                            return ("number", num)
                    except ValueError:
                        pass
                if "yon" in input_type: # for yes or no questions
                    if ans in ['y', 'yes']:
                        return ("com", 1)
                    elif ans in ['n', 'no']:
                        return ("com", 0)
                    print("Answer must be yes or no. ")
                    continue
                elif "turn" in input_type: # for turn based actions (bid, reroll)
                    if ans in ['r', 'rr', 'reroll']: # reroll
                        if cur_player.money >= Game.CONST["r"]:
                            cur_player.money -= Game.CONST["r"]
                            return ("com", 0)
                        print("You don't have enough money for a reroll! ")
                        continue
                    elif ans in ['gr', 'group reroll']: # group reroll
                        if cur_player.money >= Game.CONST["gr"]:
                            cur_player.money -= Game.CONST["gr"]
                            return ("com", 1)
                        print("You don't have enough money for a group reroll! ")
                        continue
                print("Invalid command/ammount! ") # all commands checked, invalid command

    def add_idol(self, player: Player, add: Idol, index: int) -> int: # add idol to a roster, potentially check synergies (might make new func for that)
        if index is not None:
            player.roster.insert(index, add)
        else:
            player.roster.append(add)
        print(f'{add.to_string()} added to {player.name}\'s roster!')
        self.check_synergies(player)

    def replace_idol(self, player: Player) -> int:
        ind = 0 # index of idol that was removed
        print("Pick an idol to replace on your roster (enter number)")
        for i in range(Game.CONST["size"]):
            print(f'{i+1}. {player.roster[i].to_string()}')
        while True:
            ans = self.input_command("number", player) # pick idol 1-5 to replace
            if 1 <= ans[1] <= Game.CONST["size"]:
                ind = ans[1]-1
                del player.roster[ind]
                break
            print(f'Invalid selection. Please choose a number between 1 and {Game.CONST["size"]}.')
        return ind
            
    def check_synergies(self, player: Player): # function to check and handle synergies
        old_syn = player.synergies.copy()
        counts = Counter()
        for idol in player.roster:
            counts[idol.name[0]] += 1
            counts[idol.group] += 1 
        player.synergies.update({syn for syn, count in counts.items() if count >= 3})
        new_syn = player.synergies - old_syn
        if new_syn: # give synergy effects
            for syn in new_syn:
                if len(syn) > 1: # group synergy
                    return
                else: # letter synergy
                    ind = None
                    if len(player.roster) >= Game.CONST["size"]: # player roster is full, must replace instead of adding
                        ind = self.replace_idol(player)
                    print(f'Type the name of an idol whose name starts with a {syn.upper()}: (group) (idol name)')
                    while True:
                        ans = self.input_command("idol", player)
                        add = choose.find_idol(ans)
                        if add:
                            self.add_idol(player, add, ind)
                        else:
                            print("Invalid idol!")

    def duplicate_check(self, cur_idol: Idol) -> bool: # check if rolled idol is already on a roster
        for idol in self.opponent.roster: 
            if cur_idol.equals(idol):
                print(f'{cur_idol.to_string()} is already in {self.opponent.name}\'s roster, so you steal them to your own roster!')
                self.opponent.roster.remove(idol)
                self.add_idol(self.turn, cur_idol)
                return True
        return False
    
    def bid_process(self, bid: int, cur_idol: Idol): # function that handles bidding process
        opponent_win = False
        if len(self.opponent.roster) < Game.CONST["size"]: # check if opponent roster is full
            if self.opponent.money > abs(bid): # check if opponent has enough money to counter bid
                while not opponent_win:
                    counter_bid = self.input_command("number yon", self.opponent)
                    if counter_bid[0] == "com" and counter_bid[1] == 0: # opponent doesn't bid
                        break
                    elif counter_bid[0] == "bid": # opponent bids
                        if bid >= 0: # opponent bids to buy
                            if counter_bid[1] > bid:
                                self.add_idol(self.opponent, cur_idol, None)
                            else: 
                                print("Bid must be more than your opponent ",)
                                continue
                        else: # opponent bids to give
                            if counter_bid[1] < bid:
                                self.add_idol(self.turn, cur_idol, None)
                            else: 
                                print("Bid must be more than your opponent ",)
                                continue
                    else: # opponent bid is invalid
                        print("Bid must be more than opponent's.")
                        continue
                    self.opponent.money -= abs(counter_bid[1])
                    opponent_win = True
        if not opponent_win: # turn player wins bid
            if bid >= 0:
                self.add_idol(self.turn, cur_idol, None)
            else:
                self.add_idol(self.opponent, cur_idol, None)
            self.turn.money -= abs(bid)

    # todo: Add option for opponent to group reroll after outbidding an idol
    def group_reroll(self, cur_idol: Idol): # function for handling group reroll process
        while True:
            cur_idol = choose.random_idol(cur_idol.group, 1, True, [cur_idol])[0]
            if self.turn.money >= Game.CONST["gr"]: # group reroll again
                print(cur_idol.to_string())
                print("Would you like to group reroll again? ",)
                if self.input_command("yon", self.turn)[1] == 1: # if answer is yes
                    self.turn.money -= Game.CONST["gr"]
                else: 
                    break
            else:
                break
        cur_idol.protected = True # idols from group rerolls are protected
        self.add_idol(self.turn, cur_idol, None)

    def deluxe_reroll(self): # function for deluxe reroll
        self.turn = self.p1
        for _ in range(2):
            while self.turn.money >= Game.CONST["dr"]: # if they have money for deluxe reroll
                print(f'{self.turn.name}, would you like to deluxe reroll for ${Game.CONST["dr"]}?')
                if self.input_command("yon", self.turn)[1] == 1: # dr if yes, else break and move to next player
                    ind = self.replace_idol() # index of idol that was removed
                    choices = choose.random_idol(None, 3, True, self.p1.roster + self.p2.roster) # deluxe reroll cannot roll duplicates
                    print("Pick an idol to add to your roster:")
                    for i, choice in enumerate(choices, start=1):
                        print(f'{i}. {choice.to_string()}')
                    while True:
                        ans = self.input_command("number", self.turn) # pick idol 1-3 to add
                        if 1 <= ans[1] <= 3:
                            self.add_idol(self.turn, choices[ans[1]-1], ind)
                            break
                        print(f'Invalid selection!')
                else:
                    break
            self.switch_turns()
    
    def end_game(self): # performs all end game processes
        if not self.game_over:
            self.deluxe_reroll()
            # function to evaluate combat, sets self.winner to the winner
        self.finalize()

    def finalize(self): # closes the game, uploads data
        self.game_over = True
        if len(self.p1.roster) < Game.CONST["size"] and len(self.p2.roster) < Game.CONST["size"]: # game prematurely ended
            print("Game ended early!")
        else: # game was played out
            print(f'Winner: {self.winner}')
            self.show_game_info()
            # upload game history to file and idol stats

    def play_turn(self): # main game function to play out a turn
        if len(self.turn.roster) >= Game.CONST["size"]: # switch turn if one player's roster is full
            self.switch_turns()

        print(f'{"-" * 100}\n{self.turn.name}\'s Turn ')

        while True:
            cur_idol = choose.random_idol(None, 1, True, self.turn.roster)[0] # roll idol
            print(cur_idol.to_string())

            if self.duplicate_check(cur_idol): # check for duplicates
                break
            
            if len(self.opponent.roster) >= Game.CONST["size"] and self.opponent.money >= Game.CONST["r"]: # opponent reroll
                print(f'{self.opponent.name}, would you like to reroll your opponent\'s idol for ${Game.CONST["r"]}? ',)
                if self.input_command("yon", self.opponent)[1] == 1: # if answer is yes
                    self.opponent.money -= Game.CONST["r"]
                    continue
            # print(f'Actions: (r - reroll, gr - group reroll, (number) - bid/give)')
            ans = self.input_command("number turn", self.turn)
            if ans[0] == "number": # bid/give
                self.bid_process(ans[1], cur_idol)
                break
            elif ans[1] == 0: # reroll
                continue
            elif ans[1] == 1: # group reroll
                self.group_reroll(cur_idol)
                break

        # todo: function to check end of turn effects
        self.switch_turns()

    def play_game(self): # function that runs the game
        self.game_start()
        while len(self.p1.roster) < Game.CONST["size"] or len(self.p2.roster) < Game.CONST["size"]:
            self.play_turn()
        self.end_game()

new_game = Game()
new_game.play_game()
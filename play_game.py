import choose_idol as choose
from choose_idol import Idol
import os

class Player:
    def __init__(self, name):
        self.name = name
        self.roster = []
        self.money = 15

    def info(self): # displays money and roster, todo
        string = ""
        return string

class Game:
    PRICES = {
        "r": 2,
        "gr": 5,
        "dr": 6
    }

    def __init__(self):
        self.p1 = self.p2 = None # holds player objects
        self.turn = None # holds player object who is currently their turn
        self.game_over = False

    @property
    def opponent(self): # holds player object who is currently not their turn
        return self.p2 if self.turn == self.p1 else self.p1
    
    def switch_turns(self):
        self.turn = self.opponent

    def game_start(self) -> str: # start and restart games
        os.system('cls')
        while True:
            p1 = input("Enter player one name: ").strip()
            p2 = input("Enter player two name: ").strip()

            if p1 != p2 and p1 and p2:
                self.p1 = Player(p1)
                self.p2 = Player(p2)
                break
            print("Player names must be different.")
        self.turn = self.p1
        self.game_over = False
    
    # Return codes:
    # 0 - No/Reroll
    # 1 - Yes/Group Reroll
    # "bid" - bid/give action, returned integer is bid amount
    def input_command(self, yon: bool) -> int: # yon: True for yes or no question, False if not
        while True:
            ans = input("----> ").strip().lower() # Inquires for input

            try: # see if command is a bid
                bid = int(ans)
                return ("bid", bid)
            except ValueError:
                pass

            if ans in ['new', 'reset']: # reset game
                self.game_start() # reset game functionality todo
            elif ans in ['i', 'info']: # util commands, don't affect game state
                print(self.p1.money, self.p2.money)
            elif ans in ['h', 'help']:
                print ("COMMAND LIST")
            elif ans in ['c', 'clear']:
                os.system('cls')
            elif yon: # for yes or no questions
                if ans in ['y', 'yes']:
                    return ("com", 1)
                elif ans in ['n', 'no']:
                    return ("com", 0)
                print("Answer must be yes or no. ")
            elif ans in ['r', 'rr', 'reroll']: # reroll
                if self.turn.money >= Game.PRICES["r"]:
                    self.turn.money -= Game.PRICES["r"]
                    return ("com", 0)
                print("You don't have enough money for a reroll! ")
            elif ans in ['gr', 'group reroll']: # group reroll
                if self.turn.money >= Game.PRICES["gr"]:
                    self.turn.money -= Game.PRICES["gr"]
                    return ("com", 1)
                print("You don't have enough money for a group reroll! ")
            else: # all commands checked, invalid command
                print("Invalid command! ")

    def duplicate_check(self, cur: str) -> int: # check if rolled idol is already on a roster
        for idol in self.turn.roster:
            if idol == cur:
                self.turn.money += 2 # Gain reroll instead of money, todo
                print("You rolled an idol already on your roster, you gain 2 dollars! ", end="")
                return 1
        for idol in self.opponent.roster: 
            if idol == cur:
                print("You rolled an idol already on your opponent's roster, you steal them onto your roster! ", end="")
                self.opponent.roster.remove(idol)
                self.turn.roster.append(idol) # stealing idols, todo
                return 2
        return 0

    def add_idol(self, player: Player, add: Idol) -> int: # add idol to a roster, potentially check synergies (might make new func for that)
        player.roster.append(add)
        print(f'{add.to_string()} added to {player.name}\'s roster!')
        # todo, check synergies
        return 0
    
    def bid_process(self, bid: int, cur_idol: Idol): # function that handles bidding process
        opponent_win = False
        if len(self.opponent.roster) < 5: # check if opponent roster is full
            if self.opponent.money > abs(bid): # check if opponent has enough money to counter bid
                print("Enter counter-bid, or n if you do not want to bid. ", end="")
                while not opponent_win:
                    counter_bid = self.input_command(True)
                    if counter_bid[0] == "com" and counter_bid[1] == -1: # opponent doesn't bid
                        break
                    elif counter_bid[1] <= abs(bid): # opponent bid amount is invalid
                        print("Bid must be more than your opponent ", end="")
                        continue
                    elif bid >= 0: # opponent bids to buy
                        self.add_idol(self.opponent, cur_idol)
                    else: # opponent bids to give
                        self.add_idol(self.turn, cur_idol)
                    self.opponent.money -= abs(counter_bid[1])
                    opponent_win = True
        if not opponent_win: # turn player wins bid
            if bid >= 0:
                self.add_idol(self.turn, cur_idol)
            else:
                self.add_idol(self.opponent, cur_idol)
            self.turn.money -= abs(bid)

    def group_reroll(self, cur_idol: Idol): # function for handling group reroll process
        while True:
            cur_idol = next(iter(choose.random_idol(cur_idol.group, 1, 1, cur_idol)))
            if self.turn.money >= Game.PRICES["gr"]: # group reroll again
                print(cur_idol.to_string())
                print("Would you like to group reroll again? ", end="")
                if self.input_command(True)[1] == 1: # if answer is yes
                    self.turn.money -= Game.PRICES["gr"]
                else: 
                    break
            else:
                break
        cur_idol.protected = True # idols from group rerolls are protected
        self.add_idol(self.turn, cur_idol)

    def play_turn(self):
        if len(self.turn.roster) >= 5: # switch turn if one player's roster is full
            self.switch_turns()

        print(f'{self.turn.name}\'s turn')

        while True:
            cur_idol = next(iter(choose.random_idol(None, 1, 1, None))) # rol idol
            print(cur_idol.to_string())

            if self.duplicate_check(cur_idol) != 0: # check for duplicates
                break
            
            if len(self.opponent.roster) >= 5 and self.opponent.money >= Game.PRICES["r"]: # opponent reroll
                print(f'{self.opponent.name}, would you like to reroll your opponent\'s idol for ${Game.PRICES("r")}? ', end="")
                if self.input_command(True)[1] == 1: # if answer is yes
                    self.opponent.money -= Game.PRICES["r"]
                    continue
            print(f'{self.turn.name}, Enter action: (r - reroll, gr - group reroll, (number) - bid/give ', end="")
            ans = self.input_command(False)
            if ans[0] == "bid": # bid/give
                self.bid_process(ans[1], cur_idol)
            elif ans[1] == 0: # reroll
                continue
            elif ans[1] == 1: # group reroll
                self.group_reroll(cur_idol)
        self.switch_turns()
        # todo: function to check game state after each turn (could be combined with synergy check)

    def play_game(self):
        while True:
            self.game_start()
            while not self.game_over:
                self.play_turn()

new_game = Game()
new_game.play_game()
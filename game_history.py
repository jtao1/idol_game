import os
import re
from choose_idol import Idol

class History:
    folder_name = 'game files' # folder where all files are stored

    def __init__(self):
        self.history = [] # each element of the list is a line of the file, denoting one action during the game
        self.board = [] # contains information for overview board to show at top of history file

    def write(self, line: str): # function to add a line to history
        self.history.append(line)

    def remove_ansi(self, text): # remove ansi codes from any string
        ansi_escape = re.compile(r'\033\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def create_board(self, game): # creates overview board to display on top of a history file
        self.board.append(f'{self.remove_ansi(game.p1.name)}: ${game.p1.money}')
        self.board.append('')
        for idol in game.p1.roster:
            self.board.append(f'{self.remove_ansi(idol.to_string())} ${0 if not idol.price else idol.price}')
        self.board.append('-' * 30)
        self.board.append(f'{self.remove_ansi(game.p2.name)}: ${game.p2.money}')
        self.board.append('')
        for idol in game.p2.roster:
            self.board.append(f'{self.remove_ansi(idol.to_string())} ${0 if not idol.price else idol.price}')

    def write_file(self, game):
        existing_files = [f for f in os.listdir(self.folder_name) if f.startswith('game_') and f.endswith(".txt")]
        game_number = len(existing_files) + 1
        filename = f'game_{game_number}.txt'
        path = os.path.join(self.folder_name, filename)

        self.create_board(game)

        with open(path, 'w') as f:
            f.writelines('\n'.join(self.board))
            f.writelines(self.history)
        print(f'Wrote history of game #{game_number} to {filename}')

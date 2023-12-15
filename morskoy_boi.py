# Define a custom exception for board-related errors
class BoardOutException(IndexError):
    def __init__(self, message="Attempted to shoot outside the board boundaries"):
        self.message = message
        super().__init__(self.message)

# Represent a point on the board
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.x == other.x and self.y == other.y
        return False

# Represent a ship on the board
class Ship:
    def __init__(self, length, start_dot, direction, lives_left):
        self.length = length
        self.start_dot = start_dot
        self.direction = direction
        self.lives_left = lives_left
    
    def dots(self):
        ship_dots = []
        x, y = self.start_dot.x, self.start_dot.y

        for i in range(self.length):
            if self.direction == 'h':
                ship_dots.append(Dot(x, y + i))
            elif self.direction == 'v':
                ship_dots.append(Dot(x + i, y))
        return ship_dots

# Represent the game board
class Board:
    def __init__(self, board_state, ship_list, hid, alive_ships):
        self.board_state = board_state
        self.ship_list = ship_list
        self.hid = hid
        self.alive_ships = alive_ships

    def add_ship(self, ship, x, y, direction):
        try:
            ship_cells = []  # To store ship cells before adding to the board

            # Check if any dot of the ship is out of bounds
            if self.out(ship):
                raise BoardOutException("Ship placement is out of bounds.")

            # Check for collisions and place the ship on the board
            if direction == 'h':
                # Check for collisions with other ships or out-of-bounds
                for i in range(ship.length):
                    if (
                        self.board_state[x][y + i] == 1
                        or self.board_state[x][y+i] == -1
                        or (x > 0 and self.board_state[x-1][y+i] == -1)
                        or (x > 0 and self.board_state[x - 1][y + i] == 1)
                        or (x < len(self.board_state) - 1 and self.board_state[x + 1][y + i] == 1)
                        or (x < len(self.board_state)-1 and self.board_state[x+1][y+i] == -1)
                    ):
                        raise BoardOutException()
                    ship_cells.append(Dot(x, y + i))
                for cell in ship_cells:
                    self.board_state[cell.x][cell.y] = 1
            elif direction == 'v':
                for i in range(ship.length):
                     # Check for collisions with other ships or out-of-bounds
                    if (
                        self.board_state[x + i][y] == 1
                        or self.board_state[x+i][y] == -1
                        or (y > 0 and self.board_state[x+i][y-1] == -1)
                        or (y > 0 and self.board_state[x + i][y - 1] == 1)
                        or (y < len(self.board_state[0]) - 1 and self.board_state[x + i][y + 1] == 1)
                        or (y < len(self.board_state[0]) - 1 and self.board_state[x + i][y + 1] == -1)
                    ):
                        raise BoardOutException()
                    ship_cells.append(Dot(x + i, y))
                for cell in ship_cells:
                    self.board_state[cell.x][cell.y] = 1
            else:
                raise ValueError("Invalid orientation. Use 'h' for horizontal or 'v' for vertical.")
            
            # Update ship list and alive ship count
            self.ship_list.append(ship)
            self.alive_ships += ship.length
            
            print("Ship added successfully:")
            print("Ship cells:", [cell.__dict__ for cell in ship_cells])
            print("Current board:")
            self.print_board()

            print('Added contouring')
            self.contour(ship)
            self.print_board()
        except IndexError:
            raise BoardOutException("Ship placement is out of bounds.")

    def contour(self, ship):
        for dot in ship.dots():
            x, y = dot.x, dot.y

            # Mark the surrounding cells of the ship as ship contours (-1)
            for i in range(-1, 2):
                for j in range(-1, 2):
                    new_x, new_y = x + i, y + j
                    new_dot = Dot(new_x, new_y)
            
                    if (
                        0 <= new_x < len(self.board_state)
                        and 0 <= new_y < len(self.board_state[0])
                        and new_dot not in ship.dots()  # Skip the ship's own cells
                    ):
                        self.board_state[new_x][new_y] = -1
    
    def print_board(self):
        for row in self.board_state:
            if not self.hid:
                print(row)
            else:
                for cell in row:
                    if cell == 1:
                        print('1', end=' ')
                    else:
                        print(cell, end=' ')
                print()   # Move to the next line after printing each row
    
    def out(self, ship):
        for dot in ship.dots():
            x, y = dot.x, dot.y

            if not(0 <= x < len(self.board_state) and 0 <= y < len(self.board_state[0])):
                return True
        
        return False

    def shot(self, x, y):
        if not (0 <= x < len(self.board_state) and 0 <= y < len(self.board_state[0])):
            raise BoardOutException('Attempted to shoot outside the board boundaries.')
        
        if self.board_state[x][y] == 1:
            print("Hit a ship!")        
            self.alive_ships -= 1
            self.board_state[x][y] = 'X'
        elif self.board_state[x][y] == 0:
            print("Missed the target.")
            self.board_state[x][y] = 'T'
        elif self.board_state[x][y] == -1:
            print("Hit the contour.")
            self.board_state[x][y] = 'T'

# Represent a player in the game
class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board
    
    def ask(self):
        pass

    def move(self):
        try:
            dot = self.ask()
            x, y = dot.x, dot.y

            # Check if the cell is already marked or shot
            if self.enemy_board.board_state[x][y] == 'X' or self.enemy_board.board_state[x][y] == 'T':
                raise BoardOutException('You attempted to shoot in an already shot or marked cell.')
            
            self.enemy_board.shot(x, y)
            print('This is an enemy_board after shot')
            enemy_board.print_board()

            # Check if the shot hit a ship and return True if the player gets another turn
            if self.enemy_board.board_state[x][y] == 'X':
                print("You hit a ship! Take another turn.")
                return True
            return False
            
        except BoardOutException as e:
            print(e)

# Represent an AI player
class AI(Player):
    def move(self):
        try:
            dot = self.ask()
            x, y = dot.x, dot.y

            # Check if the cell is already marked or shot
            if self.player_board.board_state[x][y] == 'X' or self.player_board.board_state[x][y] == 'T':
                raise BoardOutException('AI attempted to shoot in an already shot or marked cell.')
            
            self.player_board.shot(x, y)  
            print('This is a player_board after shot')
            player_board.print_board() 

            # Check if the shot hit a ship and return True if the player gets another turn
            if self.player_board.board_state[x][y] == 'X':
                print("AI hit your ship! AI takes another turn.")
                return True
            return False
        except BoardOutException as e:
            print(e)
        

    def ask(self):
        random_x = random.randint(0, len(self.enemy_board.board_state) - 1)
        random_y = random.randint(0, len(self.enemy_board.board_state[0]) - 1)

        if not (0 <= random_x < len(self.enemy_board.board_state) and 0 <= random_y < len(self.enemy_board.board_state[0])):
            raise BoardOutException('Entered coordinates are out of bounds.')

        return Dot(random_x, random_y)

# Represent a user player
class User(Player):
    def ask(self):
        try:
            x = int(input('Please enter row number: '))
            y = int(input('Please enter col number: '))

            # Check if the entered coordinates are within the board boundaries
            if not (0 <= x < len(self.enemy_board.board_state) and 0 <= y < len(self.enemy_board.board_state[0])):
                raise BoardOutException('Entered coordinates are out of bounds.')
            
            return Dot(x, y)
        except ValueError:
            print('Invalid input. Please enter valid integers for row and column.')

# Represent the game and handle game logic
class Game:
    def __init__(self, player, player_board, enemy, enemy_board):
        self.player = player
        self.player_board = player_board
        self.enemy = enemy
        self.enemy_board = enemy_board

    # Randomly place ships on the board
    def random_board(self, board):
        ships_to_place = [(3, 1), (2, 2), (1, 4)]  # Ship lengths and their counts
        max_failed_attempts = 2000  # Maximum number of failed attempts before generating a new board

        for ship_length, ship_count in sorted(ships_to_place, reverse=True):
            placed_ships_count = 0
            failed_attempts = 0

            while placed_ships_count < ship_count and failed_attempts < max_failed_attempts:
                try:
                    for _ in range(ship_count):
                        x = random.randint(0, len(board.board_state) - 1)
                        y = random.randint(0, len(board.board_state[0]) - 1)
                        direction = random.choice(['h', 'v'])

                        # Check if the ship can be placed
                        can_place = True
                        ship_dots = []

                        if direction == 'h' and y + ship_length <= len(board.board_state[0]):
                            ship_dots = [Dot(x, y + i) for i in range(ship_length)]
                        elif direction == 'v' and x + ship_length <= len(board.board_state):
                            ship_dots = [Dot(x + i, y) for i in range(ship_length)]
                        else:
                            can_place = False

                        if can_place and all(dot not in board.ship_list for dot in ship_dots):
                            board.add_ship(Ship(ship_length, Dot(x, y), direction, ship_length), x, y, direction)
                            placed_ships_count += 1
                        else:
                            failed_attempts += 1

                except BoardOutException:
                    failed_attempts += 1
                    continue

            if failed_attempts >= max_failed_attempts:
                print(f"Failed to place {ship_count} ships of length {ship_length} on the board. Generating a new board.")
                board.board_state = [[0] * len(board.board_state[0]) for _ in range(len(board.board_state))]
                board.alive_ships = 0
                self.random_board(board)  
                return  # Exit the method after generating a new board

            print("Ships placed successfully:")
            print("Current board:")
            board.print_board()

    # Main game loop
    def loop(self):
        current_player = self.player

        while self.player_board.alive_ships > 0 and self.enemy_board.alive_ships > 0:
            # Check if the current player gets another turn
            while current_player.move():
                pass  # Keep prompting the current player for another turn

            # Switch to the other player
            current_player = self.enemy if current_player == self.player else self.player

            # Add print statements to check alive_ships values
            print("Player Board alive_ships:", self.player_board.alive_ships)
            print("Enemy Board alive_ships:", self.enemy_board.alive_ships)

        # After the loop ends, determine the winner
        if self.player_board.alive_ships == 0:
            print("You lost! Better luck next time.")
        elif self.enemy_board.alive_ships == 0:
            print("Congratulations! You won!")
        else:
            # This case will occur if both players still have alive ships, which shouldn't happen in a valid game.
            print("The game ended in a draw.")
        
    # Display a welcome message
    def greet(self):
        print('Welcome to the battleship game!')

    # Start the game
    def start(self):
        self.greet()
        self.random_board(self.player_board)
        self.random_board(self.enemy_board)

        # Print board states
        print("\nPlayer Board after placing ships:")
        self.player_board.print_board()
        print("\nEnemy Board after placing ships:")
        self.enemy_board.print_board()
        self.loop() 

import copy
import random

# Instantiation for the Board class with a 6x6 board
board_size = 6
initial_board_state = [[0] * board_size for _ in range(board_size)]
initial_ship_list = []  # Assuming an empty list initially
hid = True  # Change to True if you want to hide ships during printing
alive_ships = 0  # Initially, no ships are alive

# Creating instances of the Board class
player_board = Board(copy.deepcopy(initial_board_state), initial_ship_list.copy(), hid, alive_ships)
enemy_board = Board(copy.deepcopy(initial_board_state), initial_ship_list.copy(), hid, alive_ships)

# Instantiate User and AI players
user_player = User(player_board, enemy_board)
ai_player = AI(player_board, enemy_board)

# Instantiate the Game with User and AI players
game1 = Game(user_player, player_board, ai_player, enemy_board)
game1.start()

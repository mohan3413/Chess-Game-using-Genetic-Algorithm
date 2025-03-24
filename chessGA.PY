import pygame
import sys
import random
import copy

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
SQUARE_SIZE = WIDTH // 12
BOARD_WIDTH = 2 * WIDTH // 3
SCOREBOARD_WIDTH = WIDTH - BOARD_WIDTH
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCOREBOARD_COLOR = (44, 12, 32)



# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Define the chessboard
chessboard = [[None for _ in range(8)] for _ in range(8)]

# Define piece classes
class Piece:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col

class King(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)

    def is_valid_move(self, new_row, new_col):
        return abs(new_row - self.row) <= 1 and abs(new_col - self.col) <= 1

class Boat(Piece):
    def __init__(self, color, row, col):
        super().__init__(color, row, col)

    def is_valid_move(self, new_row, new_col):
        row_diff = new_row - self.row
        col_diff = new_col - self.col
        return (
            (row_diff == 0 and abs(col_diff) >= 1 and abs(col_diff) <= 7) or
            (col_diff == 0 and abs(row_diff) >= 1 and abs(row_diff) <= 7)
        )

# Initialize the chessboard with pieces
user_king = King("user", 7, 4)
system_king = King("system", 0, 0)
chessboard[7][4] = user_king
chessboard[0][0] = system_king
chessboard[6][2] = Boat("user", 6, 2)

# Initialize points for the user
user_points = 1000
user_points_text = pygame.Surface((250, 50))

# Function to deduct points and move a piece
def move_piece(piece, new_row, new_col, cost):
    global user_points
    if user_points >= cost:
        user_points -= cost
        chessboard[piece.row][piece.col] = None
        piece.row = new_row
        piece.col = new_col
        chessboard[new_row][new_col] = piece

# Function to capture the system king
def capture_system_king():
    global user_points
    user_points += 100

# Genetic Algorithm parameters
POPULATION_SIZE = 10
MUTATION_RATE = 0.01
GENERATIONS = 5

# Function to calculate fitness for a given system king's position
def calculate_fitness(system_king_row, system_king_col, user_king_row, user_king_col):
    # Define a fitness function, e.g., minimize the distance to the user king
    user_king = (user_king_row, user_king_col)
    distance = abs(system_king_row - user_king[0]) + abs(system_king_col - user_king[1])
    return 1 / (distance + 1)  # Inverse of the distance

# Genetic Algorithm
def genetic_algorithm(user_king_row, user_king_col,valid_moves):
    global system_king
    best_move=None
    best_fitness = 0

    for generation in range(GENERATIONS):
        population = valid_moves  # Use the provided valid_moves as the initial population

        for i in range(POPULATION_SIZE):
            # Select two individuals from the population
            parent1 = random.choice(population)
            parent2 = random.choice(population)

            # Crossover to produce a new individual
            crossover_point = random.randint(0, 1)
            child = (
                parent1[0] if random.random() < crossover_point else parent2[0],
                parent1[1] if random.random() < crossover_point else parent2[1],
            )

            # Mutate the child with a certain probability
            if random.random() < MUTATION_RATE:
                child = (
                    random.randint(0, 7),
                    random.randint(0, 7),
                )

            # Calculate fitness for the new individual
            fitness = calculate_fitness(child[0], child[1], user_king_row, user_king_col)

            # Update the best system king if a better position is found
            if fitness > best_fitness:
                best_fitness = fitness
                best_move = child

        # Update the population with the new individuals
        population = [best_move] + population[1:]

    return best_move
# Main game loop
running = True
selected_piece = None
user_turn = True
user_won = False
system_won = False
font = pygame.font.Font(None, 36)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if user_turn:
            if event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // SQUARE_SIZE
                row = event.pos[1] // SQUARE_SIZE
                selected_piece = chessboard[row][col]

            if event.type == pygame.MOUSEBUTTONUP and selected_piece:
                col = event.pos[0] // SQUARE_SIZE
                row = event.pos[1] // SQUARE_SIZE

                if selected_piece.color == "user":
                    if isinstance(selected_piece, King):
                        cost = 10
                        if selected_piece.is_valid_move(row, col):
                            if not chessboard[row][col] or chessboard[row][col].color != "user":
                                move_piece(selected_piece, row, col, cost)
                                user_turn = False
                    elif isinstance(selected_piece, Boat):
                        cost = 20
                        if selected_piece.is_valid_move(row, col):
                            if not chessboard[row][col] or chessboard[row][col].color != "user":
                                move_piece(selected_piece, row, col, cost)
                                user_turn = False
                        if row == system_king.row and col == system_king.col:
                            capture_system_king()
                selected_piece = None

                user_points_text = font.render(f"User Points: {user_points}", True, (255, 255, 255))
        else:
            user_king_row = user_king.row
            user_king_col = user_king.col

            # Calculate valid moves for the system king
            valid_moves = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    new_row = system_king.row + dr
                    new_col = system_king.col + dc

                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        if (
                            (dr != 0 or dc != 0)  # Not the current position
                            and (chessboard[new_row][new_col] is None or chessboard[new_row][new_col].color == "user")
                        ):
                            valid_moves.append((new_row, new_col))

            if valid_moves:
                new_row, new_col = random.choice(valid_moves)
                move_piece(system_king, new_row, new_col, 0)  # Move the system king
                user_turn = True  # Switch to user's turn

                user_points_text = font.render(f"User Points: {user_points}", True, (255, 255, 255))
            else:
                # Call the genetic_algorithm function to determine the best move for the system king
                best_move = genetic_algorithm(user_king_row, user_king_col)
                move_piece(system_king, best_move[0], best_move[1], 0)  # Move the system king
                user_turn = True  # Switch to user's turn

                user_points_text = font.render(f"User Points: {user_points}", True, (255, 255, 255))

    system_king_exists = any(isinstance(piece, King) and piece.color == "system" for row in chessboard for piece in row)

    if not system_king_exists:
        user_won = True
        system_king = False
        
    
    user_king_exists = any(isinstance(piece, King) and piece.color == "user" for row in chessboard for piece in row)

    if not user_king_exists:
        system_won = True
        
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    user_king_image = pygame.image.load("user king.png")
    system_king_image = pygame.image.load("system king.jpeg")
    user_boat_image = pygame.image.load("user_.jpeg")
    user_king_image = pygame.transform.scale(user_king_image, (SQUARE_SIZE - 20, SQUARE_SIZE - 20))
    system_king_image = pygame.transform.scale(system_king_image, (SQUARE_SIZE - 20, SQUARE_SIZE - 20))
    user_boat_image = pygame.transform.scale(user_boat_image, (SQUARE_SIZE - 20, SQUARE_SIZE - 20))

    for row in range(8):
        for col in range(8):
            piece = chessboard[row][col]
            if piece:
                if isinstance(piece, King):
                    if piece.color == "user":
                        screen.blit(user_king_image, (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))
                    elif piece.color == "system":
                        screen.blit(system_king_image, (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))
                elif isinstance(piece, Boat) and piece.color == "user":
                    screen.blit(user_boat_image, (col * SQUARE_SIZE + 10, row * SQUARE_SIZE + 10))

    pygame.draw.line(screen, (0, 0, 0), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 2)
    pygame.draw.rect(screen, SCOREBOARD_COLOR, (BOARD_WIDTH, 0, SCOREBOARD_WIDTH, HEIGHT))
    user_points_text_rect = user_points_text.get_rect()
    user_points_text_rect.topleft = (BOARD_WIDTH + 10, 50)
    screen.blit(user_points_text, user_points_text_rect)

    turn_text = font.render("User's Turn" if user_turn else "System's Turn", True, (255, 255, 255))
    turn_text_rect = turn_text.get_rect()
    turn_text_rect.center = (BOARD_WIDTH + SCOREBOARD_WIDTH // 2, 30)
    screen.blit(turn_text,turn_text_rect)

    if user_won:
        win_text = font.render("User won!", True, (255, 255, 255))
        win_text_rect = win_text.get_rect()
        win_text_rect.center = (BOARD_WIDTH + SCOREBOARD_WIDTH // 2, HEIGHT // 2)
        screen.blit(win_text, win_text_rect)

    if system_won:
        win_text = font.render("System won!", True, (255, 255, 255))
        win_text_rect = win_text.get_rect()
        win_text_rect.center = (BOARD_WIDTH + SCOREBOARD_WIDTH // 2, HEIGHT // 2)
        screen.blit(win_text, win_text_rect)
        # running = False 
    

    pygame.display.update()
    pygame.time.delay(3000)
    

pygame.quit()
sys.exit()

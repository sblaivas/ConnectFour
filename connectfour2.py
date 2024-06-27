import numpy as np
import pygame
import sys
import math
import random
import turtle

from pygame.font import FontType

ROW_COUNT = 6
COLUMN_COUNT = 7

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4


def createBoard():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    return board


def dropPiece(board, row, col, piece):
    board[row][col] = piece


def isValidLocation(board, col):
    return board[ROW_COUNT - 1][col] == 0  #checks if the top row is empty


def getNexOpenRow(board, col):
    for r in range(ROW_COUNT):  #checks the rows
        if board[r][col] == 0:  #checks if the row is empty
            return r  #returns the row


def printBoard(board):
    print(np.flip(board, 0))  #prints the board


def winningMove(board, piece):
    #Check horizontal locations for win
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][
                    c + 2] == piece and board[r][
                        c + 3] == piece:  #checks if the pieces are in a row
                return True
    #Check vertical locations for win
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[
                    r + 2][c] == piece and board[r + 3][c] == piece:
                return True
    #Check positively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[
                    r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True
    #Check negatively sloped diaganols
    for c in range(COLUMN_COUNT - 3):
        for r in range(
                3, ROW_COUNT
        ):  #starts at 3 because the first 3 rows are already checked
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[
                    r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True


def evaluateWindow(window, piece):
    score = 0
    opponentPiece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opponentPiece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    elif window.count(opponentPiece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score


def scorePosition(board, piece):
    score = 0
    #score center
    centerArray = [int(i) for i in list(board[:, COLUMN_COUNT // 2])
                   ]  #creates an array of the center column
    centerCount = centerArray.count(piece)
    score += centerCount * 3  #adds the score to the score variable

    #Check horizontal locations for win

    for r in range(ROW_COUNT):
        row_array = [int(i)
                     for i in list(board[r, :])]  #converts the board to a list
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c +
                               WINDOW_LENGTH]  #gets the 4 pieces in a row
            score += evaluateWindow(window, piece)
    #Check vertical locations for win
    for c in range(COLUMN_COUNT):
        col_array = [int(i)
                     for i in list(board[:, c])]  #converts the board to a list
        for r in range(ROW_COUNT - 3):  #checks the rows
            window = col_array[r:r +
                               WINDOW_LENGTH]  #gets the 4 pieces in a row
            score += evaluateWindow(window, piece)

    #Check postive diagnol locations for win
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluateWindow(window, piece)

    #Check negative diagnol locations for win
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [
                board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)
            ]  #checks the rows and we do 3-i because we are checking the negative diagnol
            score += evaluateWindow(window, piece)

    return score


def is_terminal_node(board):
    return winningMove(board, PLAYER_PIECE) or winningMove(
        board, AI_PIECE) or len(get_valid_location(board)) == 0


def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_location(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winningMove(board, AI_PIECE):
                return (None, 100000000000000)
            elif winningMove(board, PLAYER_PIECE):
                return (None, -100000000000000)
            else:
                return (None, 0)

                #if the depth is 0 or the game is over then it will return 0
        else:
            return (None, scorePosition(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = getNexOpenRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = getNexOpenRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value


def get_valid_location(board):
    valid_location = []  #creates a list
    for col in range(COLUMN_COUNT):  #checks the columns
        if isValidLocation(board, col):  #checks if the column is empty
            valid_location.append(col)  #adds the column to the list
    return valid_location


def pickBestMove(board, piece):
    validLocations = get_valid_location(board)
    best_score = -10000
    best_col = random.choice(validLocations)
    for col in validLocations:
        row = getNexOpenRow(board, col)
        temp_board = board.copy()  #copies the board
        dropPiece(temp_board, row, col, piece)  #drops the piece
        score = scorePosition(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col  #We return best column because we want to drop the piece in that column


def confetti(screen, num_confetti):
    colors = [RED, YELLOW, BLUE, GREEN, ORANGE, PURPLE]  # Confetti colors
    for _ in range(num_confetti):
        color = random.choice(colors)
        size = random.randint(5, 10)
        position = (random.randint(0, width), random.randint(0, height))
        pygame.draw.circle(screen, color, position, size)

        pygame.display.update()


def drawBoard(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE,
                             (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE,
                              SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(
                screen, BLACK,
                (int(c * SQUARESIZE + SQUARESIZE / 2),
                 int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(
                    screen, RED,
                    (int(c * SQUARESIZE + SQUARESIZE / 2),
                     height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(
                    screen, YELLOW,
                    (int(c * SQUARESIZE + SQUARESIZE / 2),
                     height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()


board = createBoard()
printBoard(board)
#print(board)
gamesOver = False
# turn = 0

pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE  #width of the board
height = (ROW_COUNT + 1) * SQUARESIZE  #height of the board

size = (width, height)

RADIUS = int(SQUARESIZE / 2 - 5)  #radius of the circles
screen = pygame.display.set_mode(size)
drawBoard(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)


#Restart button function
def restartButton(screen, width, height):
    button_width, button_height = 350, 70
    button_x, button_y = (width // 2 - button_width // 2,
                          height // 2 - button_height // 2)

    restart_button = pygame.Rect(button_x, button_y, button_width,
                                 button_height)
    pygame.draw.rect(screen, GREEN, restart_button)

    restart_text = myfont.render("Restart", True, WHITE)
    text_rect = restart_text.get_rect(center=restart_button.center)
    screen.blit(restart_text, text_rect)

    pygame.display.update(
    ) 
    return restart_button


while not gamesOver:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)),
                                   RADIUS)
            # else:
            #     pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            #print(event.pos)

            # #Ask for player 1 input
            if turn == PLAYER:
                posx = event.pos[0]  #x coordinate of the mouse
                col = int(math.floor(posx /
                                     SQUARESIZE))  #column that the mouse is in

                if isValidLocation(board, col):
                    row = getNexOpenRow(board, col)
                    dropPiece(board, row, col, PLAYER_PIECE)

                    if winningMove(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        gamesOver = True
                        confetti(screen, 100)
                    turn += 1  #Makes sure that the turn is alternating
                    turn = turn % 2  #Makes sure that the turn is either 0 or 1

                    printBoard(board)
                    drawBoard(board)
            #     #print(col)
            #Ask for player 2 input
    if turn == AI and not gamesOver:
        #col = random.randint(0,COLUMN_COUNT-1)#random column
        #col = pickBestMove(board, AI_PIECE)  #column that the AI is in

        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
        if isValidLocation(board, col):
            pygame.time.wait(500)
            row = getNexOpenRow(board, col)
            dropPiece(board, row, col, AI_PIECE)

            if winningMove(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (40, 10))
                gamesOver = True
                confetti(screen, 100)
            printBoard(board)
            drawBoard(board)
            turn += 1  #Makes sure that the turn is alternating
            turn = turn % 2  #Makes sure that the turn is either 0 or 1

        if gamesOver:
            pygame.time.wait(1000)
            restart_button = restartButton(screen, width, height)
            pygame.event.clear(
            )  
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_button.collidepoint(event.pos):
                            board = createBoard()
                            printBoard(board)
                            drawBoard(board)
                            turn = random.randint(PLAYER, AI)
                            gamesOver = False
                            waiting_for_input = False  
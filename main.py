import sys
import pygame
import numpy as np
import time
import math
import copy
import random
import pickle
import zlib
import io

# Turns on and off print statements
debug_mode = False


# Define Board dimensions
row_count = 6
column_count = 7

try:
    # CACHE MANAGEMENT BLOCK
    with open('cache/cache.pkl', 'rb') as f:
        c = f.read()

    bytes = zlib.decompress(c)  # Decompress  cache
    table = pickle.loads(bytes)  # Load cache into memory
except:
    table = {}
# CACHE MANAGEMENT BLOCK


# Dimensions of the board
bdArea = row_count * column_count

# Initialize Board
board = np.zeros((row_count, column_count))
# Dimensions of window of the game
size = width, height = 640, 600


# Some predefined colors for elements of pygame
red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)
purple = (147, 112, 219)


# Start Pygame
pygame.init()
# Set Window Name
pygame.display.set_caption('Connect Four')
# Start clock for refresh rate purposes
clock = pygame.time.Clock()


# Create window of previously defined size
window = pygame.display.set_mode(size, 0, 24)
# Start game at turn 0
turn = 0

# MUSIC BLOCK
pygame.mixer.init()
pygame.mixer.music.load(
    "./Child's Nightmare.ogg")
pygame.mixer.music.set_volume(0.0)
# MUSIC BLOCK

# Load image of board
boardimage = pygame.image.load("board.png")


def compressBoard(board):
    """Compresses board in order to make it take less space in the cache.

    Removes rows of only 0 and turns remaining rows into strings with the values
    streamed into a single line

    Input: Numpy Board

    Example input:
    [[0,1,2,3,4]
    [5,6,7,8,9]
    [10,11,12,13]

    Example Output:
    "012345678910111213"

    """
    base = ""
    for i in range(row_count):
        if np.count_nonzero(board[i]) != 0:
            for j in range(column_count):
                base += str(int(board[i][j]))
    return base


def decompressBoard(compressed):
    """Decompresses board that was previously compressed in compressBoard

    Adds 0s back to board if board not large enough. Turns string into numpy array

    Input: String

    Example input:
    "012345678910111213"


    Example Output:
    [[0,1,2,3,4]
    [5,6,7,8,9]
    [10,11,12,13]
"""
    boardHeight = int(len(compressed)/column_count)
    acc = []
    for i in range(0, len(compressed), column_count):
        strlist = list(compressed[i:i+column_count])
        intlist = list(map(int, strlist))
        acc += [intlist]
    if boardHeight != row_count:
        extra = np.zeros((row_count-boardHeight, column_count))
        acc = np.append(acc, extra, axis=0)
    return acc


def validplay(bd, col):
    """Simply checks whether or not a column is full or not

    Inputs: Board, column number

    Returns true if column is not yet full, false otherwise
    """
    return bd[row_count-1][col] == 0
    # return bd[0][col] == 0


def drop_piece(bd, r, c, piece):
    """Drops a piece in the specificed column.

     Inputs: Board, row number, column number, piece

     Returns: N/A

    """
    if bd[r][c] == 0:
        bd[r][c] = piece
    else:
        if r+1 >= row_count:
            print("Bad placement")
        else:
            drop_piece(bd, r+1, c, piece)


def horizontal_check(bd, r, c, piece, depth=0):
    """Checks if the given piece won via horizontal matching.

    Can change depth of check to place variations of the game where you only need to match less than 4 pieces

    Returns true if player won, false otherwise"""
    if depth == 0:
        return bd[r][c] == piece and bd[r][c+1] == piece and bd[r][c+2] == piece and bd[r][c+3] == piece
    if depth == 1:
        return bd[r][c] == piece and bd[r][c+1] == piece and bd[r][c+2] == piece
    if depth == 2:
        return bd[r][c] == piece and bd[r][c+1] == piece


def vertical_check(bd, r, c, piece, depth=0):
    """Checks if the given piece won via verticak matching.

    Can change depth of check to place variations of the game where you only need to match less than 4 pieces

    Returns true if player won, false otherwise"""
    if depth == 0:
        return bd[r][c] == piece and bd[r+1][c] == piece and bd[r+2][c] == piece and bd[r+3][c] == piece
    if depth == 1:
        return bd[r][c] == piece and bd[r+1][c] == piece and bd[r+2][c] == piece
    if depth == 2:
        return bd[r][c] == piece and bd[r+1][c] == piece


def diagonal_check_1(bd, r, c, piece, depth=0):
    """Checks if the given piece won via forward diagonal matching.

    Can change depth of check to place variations of the game where you only need to match less than 4 pieces

    Returns true if player won, false otherwise"""
    if depth == 0:
        return bd[r][c] == piece and bd[r+1][c+1] == piece and bd[r+2][c+2] == piece and bd[r+3][c+3] == piece
    if depth == 1:
        return bd[r][c] == piece and bd[r+1][c+1] == piece and bd[r+2][c+2] == piece
    if depth == 2:
        return bd[r][c] == piece and bd[r+1][c+1] == piece


def diagonal_check_2(bd, r, c, piece, depth=0):
    """Checks if the given piece won via backwards diagonal matching.

    Can change depth of check to place variations of the game where you only need to match less than 4 pieces

    Returns true if player won, false otherwise"""
    if depth == 0:
        return bd[r][c] == piece and bd[r-1][c+1] == piece and bd[r-2][c+2] == piece and bd[r-3][c+3] == piece
    if depth == 1:
        return bd[r][c] == piece and bd[r-1][c+1] == piece and bd[r-2][c+2] == piece
    if depth == 2:
        return bd[r][c] == piece and bd[r-1][c+1] == piece


def win_check(bd, piece, depth=0):
    """Checks if the given piece won in any fashion

    Can change depth of check to place variations of the game where you only need to match less than 4 pieces

    Returns true if player won, false otherwise"""
    for r in range(row_count):
        for c in range(column_count-3 - depth):
            if horizontal_check(bd, r, c, piece, depth):
                return True
    for r in range(row_count-3 - depth):
        for c in range(column_count):
            if vertical_check(bd, r, c, piece, depth):
                return True
    for r in range(row_count-3 - depth):
        for c in range(column_count-3 - depth):
            if diagonal_check_1(bd, r, c, piece, depth):
                return True
    for r in range(3, row_count):
        for c in range(column_count-3 - depth):
            if diagonal_check_2(bd, r, c, piece, depth):
                return True
    return False


def place_pieces():
    """Draws the pieces onto the board by checking whether or not the 
    board array has any non-zero values then placing pieces whose color depends
    on what piece is in a given coordinate"""
    for r in range(row_count):
        for c in range(column_count):
            if board[r][c] == 1:
                pygame.draw.circle(window, red, (int(
                    50 + (c * 2) * 45), height-int(39 + (r * 2) * 40)), 36)
            elif board[r][c] == 2:
                pygame.draw.circle(window, black, (int(
                    50 + (c * 2) * 45), height-int(39 + (r * 2) * 40)), 36)
    window.blit(boardimage, (0, 120))
    pygame.display.update()


def intro_screen():
    """Introduction screen. Prompts user if they want to continue."""
    intro = True
    global debug_mode
    smallfont = pygame.font.SysFont(None, 30)
    smallerfont = pygame.font.SysFont(None, 18)
    debug_button = pygame.Rect(5, height - 150, 80, 30)

    def colorButton():
        if debug_mode:
            return (0, 128, 0)
        return red

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                intro = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if debug_button.collidepoint(event.pos):
                        debug_mode = not debug_mode
        window.fill((255, 255, 255))
        text = smallfont.render("Continue", True, (0, 0, 0))
        window.blit(text, [int(width/2)-50, int(height/2)-20])

        pygame.draw.rect(window, colorButton(), debug_button)

        msg = smallerfont.render(
            "Note:The Game might hang on the AI's turn, this is normal. In worst case, could take up to 300 seconds", True, (0, 0, 0))
        window.blit(msg, [int(width/2)-300, int(height)-40])

        msg2 = smallerfont.render(
            "As you play the cache will build and load times will decrease", True, (0, 0, 0))
        window.blit(msg2, [int(width/2)-260, int(height)-27])

        debug_text = smallerfont.render(
            "debug_mode", True, (0, 0, 0))
        window.blit(debug_text, [10, height-140])

        pygame.display.update()
        clock.tick(15)


def colorReturn(col):
    """Gives back a color based on what number is given. If 1, gives red, else black"""
    if col == 1:
        return red
    return black


def flip(num):
    """Turns 1 into 2 and 2 into 1 for turn purposes"""
    if num == 1:
        return 2
    return 1


turn = 0


############


# Debug tool
x = 0


def would_win(bd, i, player):
    """Check if the player would win if they placed a piece in column i from the current board state."""
    basebd = np.copy(bd)
    drop_piece(basebd, 0, i, player)
    return win_check(basebd, player), basebd


def alphabeta(bd, player, alpha, beta, trn, col=0, first=False):
    """This function uses alpha-beta pruning to find the optimal move for the given player to take.

    The score is equal to the total number of possible moves minus the number of turns divided by 2.
    This is because each player can only take half the number of slots. Maximizing this number would mean
    you won in the least number of turns.

    For time complexity optimzations the function implements the cache in the form of a dictionary that maps compress versions of the board
    to their relative scores. These key-value pairs are added to the dictionary every time they're created. It increases the efficiency of the
    function by magnitudes.

    The alpha-beta pruning allows for bad paths to be prematurely cut off such that there'd be no need to explore them thus saving time.
    """
    # print("test")
    global x
    x += 1
    flipped = np.flip(board, axis=1)
    cmpbrd = compressBoard(bd)
    if cmpbrd in table:
        if debug_mode:
            print(f"cached")
            print(x)
        return table[cmpbrd]
    revbrd = compressBoard(flipped)
    if revbrd in table:
        if debug_mode:
            print(f"cached")
            print(x)
        return table[revbrd]

    if trn+1 == bdArea:
        if debug_mode:
            print("Full board")
        return 0
    # wincheck

    for i in range(column_count):
        if validplay(bd, i):
            truth, basebd = would_win(bd, i, player)
            if truth:
                # number of moves needed until winning
                final = (((row_count+1) * column_count) - trn)/2

                comp = compressBoard(basebd)
                table[comp] = final
                return final

    maxS = ((row_count-1) * column_count - trn)/2

    # print(f"Before beta: {1}")
    if(beta > maxS):
        beta = maxS
        if(alpha >= beta):
            return beta

    newbd = np.copy(bd)

    # print("before main loop")
    if first:
        # print("Here once")
        drop_piece(newbd, 0, col, player)
        # print(newbd)
        score = -alphabeta(newbd, flip(player), -beta, -
                           alpha, trn+1, first=False)

        if(score >= beta):
            table[cmpbrd] = score
            return score
        if(score > alpha):
            alpha = score
    else:
        # print(f"Turn: {trn}")
        for i in range(column_count):
            if validplay(newbd, i):
                # print("Pre valid")
                drop_piece(newbd, 0, i, player)
                score = -alphabeta(newbd, flip(player), -
                                   beta, -alpha, trn+1, first=False)
                # print("Post valid")
                if(score >= beta):
                    table[cmpbrd] = score
                    return score
                if(score > alpha):
                    alpha = score

    return alpha

####### #############

####################


def findAns(bd, player, alpha, beta, trn):
    """This function runs the alpha-beta function on all possible columns. It then returns the column with the highest score, 
    thus maximizing your chance of winning. If a column is unplayable it retunrs -50.0"""
    ans = []
    reverseAns = []
    start_time = time.time()
    for i in range(column_count):
        if validplay(bd, i):
            check, _ = would_win(bd, i, player)
            if check:
                return i

            out = alphabeta(bd, player, alpha, beta, trn, col=i, first=True)
            ans.append(out)
        else:
            ans.append(-50.0)
        # rout = alphabeta(bd, flip(player), alpha, beta,
        #                  trn, col=i, first=True)
        # reverseAns.append(rout)

    m = max(ans)
    if debug_mode:
        print("--- %s seconds ---" % (time.time() - start_time))
        print(f"Answer list: {ans}")
    result = [i for i, j in enumerate(ans) if j == m]
    # return ans.index(max(ans))

    # print(f"Reverse list: {reverseAns}")

    return random.choice(result)

################


def Game():
    """Main Game Function:

    Manages key-detection. Move player piece with the left and right arrow keys. Place a key by using the down arrow key.

    This function updates the board and runs the AI functions. It also keeps track of the turns and starts the End() function
    once a player wins.


    """
    pos = 0
    pygame.mixer.music.play(-1)
    global turn
    check = 0
    end = True
    smallfont = pygame.font.SysFont(None, 20)
    while end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bytes = io.BytesIO()
                pickle.dump(table, bytes)
                c = zlib.compress(bytes.getbuffer())
                with open('cache/cache.pkl', 'wb') as f:
                    f.write(c)
                pygame.quit()
                sys.exit()
            if turn % 2 + 1 == 2:
                time.sleep(0.5)
                newbd = np.copy(board)
                ans = findAns(newbd, turn %
                              2 + 1, -bdArea/2, bdArea/2, turn)

                drop_piece(board, 0, ans, turn % 2 + 1)
                if debug_mode:
                    print(f"Answer: {ans}")
                    print(f"Turn: {turn}")
                turn += 1

            if turn % 2 + 1 == 1:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        # print(pos)
                        if pos > 0:
                            window.fill((255, 255, 255), (0, 0, 640, 120))
                            pos -= 1
                    elif event.key == pygame.K_RIGHT:
                        if pos < column_count-1:
                            if debug_mode:
                                print(pos)
                            window.fill((255, 255, 255), (0, 0, 640, 120))
                            pos += 1
                    elif event.key == pygame.K_UP and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        newbd = np.copy(board)
                        out = alphabeta(newbd, 1, -bdArea/2,
                                        bdArea/2, turn, pos, first=True)

                        print(f"Output: {out}")

                    elif event.key == pygame.K_DOWN:
                        if validplay(board, pos):
                            drop_piece(board, 0, pos, turn % 2 + 1)
                            turn += 1

            if check == 0:
                window.fill((255, 255, 255))
                check += 1

            # text = smallfont.render(
            #     "Game will hang on AI's turn", True, (0, 0, 0))
            # window.blit(text, [width-200, 20])

            # print("test")

            place_pieces()

            pygame.draw.circle(window, colorReturn(turn % 2 + 1), (int(
                50 + (pos * 2) * 45), 40), 36)

            window.blit(boardimage, (0, 120))
            truth = win_check(board, flip(turn % 2 + 1))
            if truth:
                end = False
                End()

            # print(truth)

            pygame.display.update()
            # init_board()

            clock.tick(60)


def numToColor(col):
    """Converts a player's integer representation to a string of their color name"""
    if col == 1:
        return "Red"
    return "Black"


def End():
    """Represents the win screen.

    Saves the table into the cache.
    Screenshots the end game into a folder for debugging purposes.

    Prompts the player if they'd like to play again.If yes resets the baord and runs Game()

    """
    global board, turn
    end = True
    pos = 0
    smallfont = pygame.font.SysFont(None, 30)
    team = numToColor(flip(turn % 2 + 1))
    if debug_mode:
        print(team)
    rect = pygame.Rect((int(width/2-150), int(height/2-100), 300, 200))
    bytes = io.BytesIO()
    pickle.dump(table, bytes)
    c = zlib.compress(bytes.getbuffer())

    end_time = time.time()
    pygame.image.save(window, "screenshots/ " + str(end_time) + ".jpg")
    if debug_mode:
        print(board)
    with open('cache/cache.pkl', 'wb') as f:
        f.write(c)
        # pickle.dump(table, f, pickle.HIGHEST_PROTOCOL)
    while end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    window.fill((255, 255, 255), (0, 0, 640, 120))
                    pos = 0
                elif event.key == pygame.K_RIGHT:
                    window.fill((255, 255, 255), (0, 0, 640, 120))
                    pos = 1
                elif event.key == pygame.K_RETURN:
                    if (pos == 0):
                        board = np.zeros((row_count, column_count))
                        turn = 0
                        Game()
                    else:
                        pygame.quit()
                        sys.exit()

            window.fill((255, 255, 255))
            pygame.draw.rect(window, (0, 0, 0),
                             rect, 2)
            textw = smallfont.render(f"{team} wins", True, (0, 0, 0))
            window.blit(textw, [int(width/2) - 50, int(height/2) - 40])

            textp = smallfont.render("Play again?", True, (0, 0, 0))
            window.blit(textp, [int(width/2) - 50, int(height/2)])

            texty = smallfont.render("yes", True, (0, 0, 0))
            window.blit(texty, [int(width/2) - 60, int(height/2) + 50])

            textn = smallfont.render("no", True, (0, 0, 0))
            window.blit(textn, [int(width/2) + 40, int(height/2) + 50])

            pygame.draw.rect(window, purple, (
                int(width/2) - 65 + (pos * 100), int(height/2) + 50, 50-(15*pos), 25), 2)

            pygame.display.update()
            clock.tick(60)


# Start the functions needed to play
intro_screen()
Game()

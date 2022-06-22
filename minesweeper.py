import random # default python library
import time # default python library
# Rich, a terminal styling library is created by Will McGugan at https://github.com/willmcgugan/rich
from rich import print # pip install rich
from rich.console import Console

startTime = 0

class Board:
    def __init__(self): # define starting parameters
        pass
    
    def createBoard(self, width, height, mines): # creates an empty board and hidden board
        self.width = width
        self.height = height
        self.mines = mines
        self.mineCount = mines
        self.numSpaces = width * height # will be used to determine when all spaces have been dug
        # hidden board is what is shown to the player
        board = []
        hboard = []
        for h in range(self.height): # fill board with empty spaces
            board.append([])
            hboard.append([]) # hboard is what is shown to the player
            for w in range(self.width):
                board[h].append("[ ]")
                hboard[h].append("[?]")
        self.board = board
        self.boardHidden = hboard
    
    def layMines(self, reservedSpaces): # lays mines randomly throughout the board, avoiding already mined spots and spaces in the 'reservedSpaces' array
        mineCount = 0
        while mineCount < self.mines: 
            spaceIsReserved = False
            column = random.randint(0,self.width-1)
            row = random.randint(0,self.height-1)
            if self.board[row][column] == "[X]": # prevents relaying the same space
                continue
            for i in reservedSpaces:
                if column == i[1] and row == i[0]: # prevents laying mines in 'reserved' areas (the shape around the first click)
                    spaceIsReserved = True # variable must be used because continue would just apply to the for loop insstead of the while
            if spaceIsReserved:
                continue
            self.board[row][column] = "[X]" 
            mineCount += 1
            self.numSpaces -= 1
    
    def findNumbers(self): # gets the number of adjacent mines for every space and stores it in the board array
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] == "[X]":
                    continue # don't check mines
                adjacent = self.getAdjacent(r, c) # gets the spaces adjacent to the current item
                mineCount = 0 
                for i in adjacent: 
                    if self.board[i[0]][i[1]] == "[X]": # if the space is a mine
                        mineCount += 1
                if mineCount > 0: # if it is =0, it will remain a space like [ ]
                    self.board[r][c] = f"[{mineCount}]" # otherwise it will display the count
    
    def digSpace(self,r, c, userInput): # userInput is a boolean value, whether or not the input is being made by the user or not
        try:
            r = int(r)
            c = int(c)
        except:
            print("Invalid space to dig.")
            return
        if userInput:
            c -= 1 # the numbers have 1 subtracted so the user can type column 1 (instead of 0) to access the first column, etc.
            r -= 1
        # if the c or r is out of range, exit
        if c>self.width+1 or c<0:
            print(f"Write a number from 1 to {self.height}.")
            return
        if r>self.height+1 or c<0:
            print(f"Write a number from 1 to {self.width}.")
            return
        if self.boardHidden[r][c] == "[[bold red]F[/bold red]]": # tags are because of styling
            print("You [bold red]cannot[/bold red] dig a space you have a [bold red]flag[/bold red] on!")
            return
        if self.board[r][c] == "[X]": # if the user tries to dig a mine
            endGame(False) # call endGame function as a loss
            return
        if self.board[r][c] == "[ ]": # if the user clicks on an open space, recursively dig
            self.boardHidden[r][c] = self.board[r][c]
            self.numSpaces -= 1
            adjacents = self.getAdjacent(r, c)
            for i in adjacents:
                y = i[0]
                x = i[1]
                if self.board[y][x] == "[ ]" and self.boardHidden[y][x] == "[dim][[/dim]?[dim]][/dim]":
                    self.digSpace(y, x, False) # recurse on the function with the new coordinates
                    continue
                if self.boardHidden[y][x] == "[dim][[/dim]?[dim]][/dim]": 
                    self.boardHidden[y][x] = self.board[y][x] # open up all of the adjacent spaces that arent also empty
                    self.numSpaces -= 1
            return
        self.boardHidden[r][c] = self.board[r][c]
        self.numSpaces -= 1
    
    def getAdjacent(self, y, x): # function to find all of the adjacent spaces, while accounting for edge cases
        adjacentSpaces = []
        if x != 0: # tedious code to account for edges and corners
            adjacentSpaces.append([y, x-1])
            if y != 0:
                adjacentSpaces.append([y-1, x-1])
            if y != self.height-1:
                adjacentSpaces.append([y+1, x-1])
        if x != self.width-1:
            adjacentSpaces.append([y, x+1])
            if y != 0:
                adjacentSpaces.append([y-1, x+1])
            if y != self.height-1:
                adjacentSpaces.append([y+1, x+1])
        if y != 0:
            adjacentSpaces.append([y-1, x])
        if y != self.height-1:
            adjacentSpaces.append([y+1, x])
        return adjacentSpaces
    
    def generateShape(self, origin_x, origin_y, size): # generate a random shape around the initial click
        # this shape will have no mines in it, resulting in a good and fair starting area for the player
        origin_x -= 1 
        origin_y -= 1
        currentShape = [[origin_y, origin_x]] # a 2d list of the x and y of all the points of the shape
        for i in self.getAdjacent(origin_y, origin_x): # the 3x3 area around your click is safe from mines
            currentShape.append(i)
        adjacent = []
        while len(currentShape) < size:
            for i in currentShape:
                adjacent = self.getAdjacent(i[0],i[1])
            toBeAdded = adjacent[random.randint(0, len(adjacent)-1)]
            if toBeAdded not in currentShape: # prevent same space in shape twice
                currentShape.append([toBeAdded[0], toBeAdded[1]])
        return currentShape # return a list of the points in the final shape
    
    # allows a user to flag a space, marking it as a mine and preventing it from being dug on.
    def flagSpace(self, y, x):
        try:
            y = int(y)
            x = int(x)
        except:
            print("Invalid space to flag.")
            return
        y -= 1 # for ease of use for the user
        x -= 1
        if y<0 or y>self.height-1 or x<0 or x>self.width-1:
            return
        # apply styles to shapes
        if self.boardHidden[y][x] == "[dim][[/dim]?[dim]][/dim]": # add a flag
            self.boardHidden[y][x] = "[[bold red]F[/bold red]]"
            self.mineCount -= 1
        elif self.boardHidden[y][x] == "[[bold red]F[/bold red]]": # remove a flag
            self.boardHidden[y][x] = "[?]"
            self.mineCount += 1
        else:
            print("You can't flag a space you already dug!")
    
    # adds colors and text styling to the board, to make it more visually appealing to the user.
    def styleBoard(self):
        for r in range(len(self.boardHidden)):
            for c in range(len(self.boardHidden[0])):
                if self.boardHidden[r][c] == "[?]":
                    self.boardHidden[r][c] = "[dim][[/dim]?[dim]][/dim]"
                elif self.boardHidden[r][c] == "[ ]":
                    self.boardHidden[r][c] = "[dim][ ][/dim]"
board = Board()

# ends the game for the user, giving a congratulations or better luck next time screen depending on if you
# won or lost. Also allows for retrying.
def endGame(win): # win param (bool) is whether you won or lost
    global playing
    if win:
        timeTaken = time.time() - startTime
        print("[bold green]Congratulations, you win![/bold green]") 
        print(f"[bold green]You took {timeTaken} seconds.[/bold green] \n")
    else:
        print("[bold red]Game Over![/bold red]\n")
    
    if input("Play again? ").lower() == "yes": 
        setupParameters()
    else:
        print("Thanks for playing!")
        playing = False

# sets up or resets the board for the player. Creates and styles a board, lays mines, finds numbers, and generates a
# starting shape. Also, allows for difficulty selection.
def setupParameters(): 
    print("\n"*150) # clear console
    print("[bold magenta] Welcome to Minesweeper! [/bold magenta]" ) # introductory messages
    print("[bold][blue]Difficulty Options: [/blue][green]Easy[/green][yellow] Medium[/yellow] [red]Hard[/red]")
    difficulty = input("What difficulty? ") # difficulty select management 
    if difficulty.lower() == "easy" or difficulty.lower() =="e":
        difficulty = 1
    elif difficulty.lower() == "medium" or difficulty.lower() == "med" or difficulty.lower() == "m":
        difficulty = 1.5
    elif difficulty.lower() == "hard" or difficulty.lower() == "h":
        difficulty = 2
    else:
        print("Sorry, I don't know that difficulty. Please select easy, medium, or hard.")
        setupParameters()
        return

    global board
    global startTime
    # determine dimensions of board, # of mines, and shape size
    w = int(10 * difficulty) 
    h = int(10 * difficulty)
    shapeSize = int(16 * difficulty)
    mines = w * h // 6

    #create and style a board, then show it to the user
    board.createBoard(w, h, mines)
    board.styleBoard()
    print("   01", end="")
    for i in range(len(board.boardHidden[0])-1):
        print(f"  {i+2:02d}", end="")
    print()
    for i in range(len(board.boardHidden)):
       print(f"[bold green]{i+1:02d}[/bold green]", end=" ") # formats the board to look appealing
       print(*board.boardHidden[i], sep=' ')

    # get starting position, and use it to create a shape around itself
    startTime = time.time() # time for determining high score later
    start_row = input("What row? ")
    start_col = input("What column? ")
    try:
        start_col = int(start_col)
        start_row = int(start_row)
    except:
        print("Invalid Starting Position")
        setupParameters()
        return
    if start_row <= 0 or start_row >= h - 1 or start_col <= 0 or start_col >= w - 1:
        print("Invalid Starting Position.")
        setupParameters()
    shape = board.generateShape(start_row, start_col, shapeSize)
    #lay mines on the board, while disallowing mines being placed on the starting shape
    board.layMines(shape)
    board.findNumbers()
    for i in shape:
        board.digSpace(i[0], i[1], False)

setupParameters() 
playing = True
# loops through showing the user the board, getting input, styling the board, and allowing for digging and flagging
while playing: 
    board.styleBoard()
    print(f"   [bold red]Mines:[/bold red] {board.mineCount}")
    print("   01", end="")
    for i in range(len(board.boardHidden[0])-1):
        print(f"[bold cyan]  {i+2:02d}[/bold cyan]", end="")
    print()
    for i in range(len(board.boardHidden)):
       print(f"[bold green]{i+1:02d}[/bold green]", end=" ")
       print(*board.boardHidden[i], sep=' ')
    mode = input("What mode (flag/dig)? ")
    row = input("What row? ")
    column = input("What column? ") 
    if mode == "dig" or mode == "d":
        board.digSpace(row, column, True)
    elif mode == "flag" or mode == "f":
        board.flagSpace(row, column)
    # elif mode == "debug.show_board:
    #     print(board.board)
    #     continue
    else: 
        print("Invalid mode.")
        continue
        

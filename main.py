import pygame
import numpy as np
import sys
import time

pygame.init()

WIDTH = 600
HEIGHT = 600
BOARD_WIDTH = 450
BOARD_HEIGHT = 450
PADDING = 10
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
BLACK = (0, 0, 0)
FPS = 60
FONT = pygame.font.SysFont("arial", 30)

class SudokuBoard:
    def __init__(self):
        self.grid = np.zeros((9,9))
        self.small_grids = np.zeros((9, 3, 3))
        self.root_indexs = []
        self.potential_indexs = []
        self.time = None

    '''def get_small_grids(self):
        x = 0
        count = 0
        for i in range(3):
            y = 0
            for j in range(3):
                self.small_grids[count] = self.grid[x:(x+3), y:(y+3)]
                y += 3
                count += 1
            x += 3'''

    def update_small_grid(self, selected, number):
        tmp = selected[1] // 3
        tmp2 = selected[0] // 3
        grid_index = tmp*3 + tmp2
        row = selected[1] % 3
        col = selected[0] % 3
        self.small_grids[grid_index][row][col] = number

    
    def is_valid(self, index, number):
        col, row = index
        tmp = row // 3
        tmp2 = col // 3
        grid_index = tmp * 3 + tmp2
        if number in self.grid[row]:
            return False
        elif number in self.grid[:, col]:
            return False
        elif number in self.small_grids[grid_index]:
            return False
        else:
            self.root_indexs.append(index)
            return True

    def get_next_index(self, index):
        if index[1] == 8:
            return (index[0] + 1, 0)
        else:
            return (index[0], index[1] + 1)


    def solve_bt(self):
        try:
            index = np.argwhere(self.grid == 0)[0]
        except IndexError:
            return True
        
        for k in range(9):
            number = k + 1
            '''for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()'''
            #root.draw_window()
            if self.is_valid((index[1],index[0]), number):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                self.grid[index[0]][index[1]] = number
                self.update_small_grid((index[1], index[0]), number)
                root.draw_window()
                if self.solve_bt() == True:
                    return True
                self.grid[index[0]][index[1]] = 0
                self.update_small_grid((index[1], index[0]), 0)
        #root.draw_window()
        return False

        

class SudokuGUI:
    def __init__(self):
        self.board = SudokuBoard()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.width = BOARD_WIDTH + PADDING
        self.height = BOARD_HEIGHT + PADDING
        self.distance = BOARD_WIDTH / 9
        self.selected = None
        self.solveButton = None
        self.solveTime = None
        pygame.display.set_caption('SUDOKU SOLVER')

    def draw_grid(self):
        for line in range(10):
            if line % 3 == 0:
                edge_width = 3
            else:
                edge_width = 1

            pygame.draw.line(self.screen, BLACK, (PADDING, PADDING + (self.distance * line)), (self.width, PADDING + (self.distance * line)), edge_width)
            pygame.draw.line(self.screen, BLACK, (PADDING + (self.distance * line), PADDING), (PADDING + (self.distance * line), self.height), edge_width)

    def display_numbers(self):
        for index, number in np.ndenumerate(self.board.grid):
            if number != 0:
                text = FONT.render(str(int(number)), True, BLACK)
                textRect = text.get_rect()
                textRect.center = ((index[1]) * (self.distance) + (self.distance / 2) + PADDING, (index[0]) * (self.distance) + (self.distance / 2) + PADDING)
                self.screen.blit(text, textRect)
    
    def highlight_cell(self):
        rect = ((self.selected[0] * self.distance + PADDING), (self.selected[1] * self.distance + PADDING))
        rect = pygame.Rect(rect[0], rect[1], self.distance + 1, self.distance + 1)
        pygame.draw.rect(self.screen, GRAY, rect, 5)
    
    def display_buttons(self):
        mouse = pygame.mouse.get_pos()
        solveText = FONT.render(' Solve ', True, BLACK, GRAY)
        solveRect = solveText.get_rect()
        solveRect.center = (47, 500)
        solveBounds = [solveRect.left, solveRect.right, solveRect.top, solveRect.bottom]
        self.solveButton = solveBounds
        if mouse[0] >= solveBounds[0] and mouse[0] <= solveBounds[1] and mouse[1] >= solveBounds[2] and mouse[1] <= solveBounds[3]:
            solveText = FONT.render(' Solve ', True, BLACK, LIGHT_GRAY)
        
        self.screen.blit(solveText, solveRect)
        
        
    def draw_window(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.display_numbers()
        if self.selected != None:
            self.highlight_cell()
        self.display_buttons()
        pygame.display.update()


    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if (x >= PADDING and x <= self.width) and (y >= PADDING and y <= self.height):
                        row = int((x - PADDING) // self.distance)
                        col = int((y - PADDING) // self.distance)
                        self.selected = (row, col)
                    else:
                        self.selected = None
                        if x >= self.solveButton[0] and x <= self.solveButton[1] and y >= self.solveButton[2] and y <= self.solveButton[3]:
                            start_time = time.perf_counter()
                            self.board.time = time.time()
                            self.board.solve_bt()
                            end_time = time.perf_counter()
                            self.solveTime = end_time - start_time
                            print(self.solveTime)

                elif event.type == pygame.KEYDOWN and self.selected != None:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.selected[0] == 0:
                            self.selected = None
                        else:
                            self.selected = (self.selected[0] - 1, self.selected[1])
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.selected[0] == 8:
                            self.selected = None
                        else:
                            self.selected = (self.selected[0] + 1, self.selected[1])
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.selected[1] == 0:
                            self.selected = None
                        else:
                            self.selected = (self.selected[0], self.selected[1] - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.selected[1] == 8:
                            self.selected = None
                        else:
                            self.selected = (self.selected[0], self.selected[1] + 1)
                    elif event.key == pygame.K_0 or event.key == pygame.K_BACKSPACE:
                        self.board.grid[self.selected[1]][self.selected[0]] = 0
                        self.board.update_small_grid(self.selected, 0)
                    elif event.key == pygame.K_1:
                        if self.board.is_valid(self.selected, 1):
                            self.board.grid[self.selected[1]][self.selected[0]] = 1
                            self.board.update_small_grid(self.selected, 1)
                    elif event.key == pygame.K_2:
                        if self.board.is_valid(self.selected, 2):
                            self.board.grid[self.selected[1]][self.selected[0]] = 2
                            self.board.update_small_grid(self.selected, 2)
                    elif event.key == pygame.K_3:
                        if self.board.is_valid(self.selected, 3):
                            self.board.grid[self.selected[1]][self.selected[0]] = 3
                            self.board.update_small_grid(self.selected, 3)
                    elif event.key == pygame.K_4:
                        if self.board.is_valid(self.selected, 4):
                            self.board.grid[self.selected[1]][self.selected[0]] = 4
                            self.board.update_small_grid(self.selected, 4)
                    elif event.key == pygame.K_5:
                        if self.board.is_valid(self.selected, 5):
                            self.board.grid[self.selected[1]][self.selected[0]] = 5
                            self.board.update_small_grid(self.selected, 5)
                    elif event.key == pygame.K_6:
                        if self.board.is_valid(self.selected, 6):
                            self.board.grid[self.selected[1]][self.selected[0]] = 6
                            self.board.update_small_grid(self.selected, 6)
                    elif event.key == pygame.K_7:
                        if self.board.is_valid(self.selected, 7):
                            self.board.grid[self.selected[1]][self.selected[0]] = 7
                            self.board.update_small_grid(self.selected, 7)
                    elif event.key == pygame.K_8:
                        if self.board.is_valid(self.selected, 8):
                            self.board.grid[self.selected[1]][self.selected[0]] = 8
                            self.board.update_small_grid(self.selected, 8)
                    elif event.key == pygame.K_9:
                        if self.board.is_valid(self.selected, 9):
                            self.board.grid[self.selected[1]][self.selected[0]] = 9
                            self.board.update_small_grid(self.selected, 9)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.selected = None
                        self.board.grid = np.zeros((9,9))
                        self.board.small_grids = np.zeros((9, 3, 3))

            self.draw_window()

        pygame.quit()

if __name__ == '__main__':
    root = SudokuGUI()
    root.run()
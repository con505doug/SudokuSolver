import pygame
import numpy as np
import sys
import time
import copy

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
        self.potential_indexs = [[], [], [], [], [], [], [], [], []]
        self.small_potentials = [[], [], [], [], [], [], [], [], []]
        self.hidden_singles = []
        self.possible_values = []
        self.time = None
        self.show_visual = False
        self.is_solveable = True
        self.counts = []

    def check_counts(self):
        j = 0
        for small_grid in self.small_potentials:
            counts = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            indexs = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(9):
                potentials = small_grid[i]
                for number in potentials:
                    counts[number-1] += 1
                    if counts[number-1] == 1:
                        col = (j % 3) * 3 + (i % 3)
                        row = (j // 3) * 3 + (i // 3)
                        indexs[number-1] = (col, row)
                    else:
                        indexs[number-1] = 0
            self.hidden_singles.append(indexs)
            j += 1
                                

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
        
    def get_possible_values(self):
        self.possible_values = []
        self.potential_indexs = [[], [], [], [], [], [], [], [], []]
        self.small_potentials = [[], [], [], [], [], [], [], [], []]
        self.hidden_singles = []
        for row in range(9):
            for col in range(9):
                possible_values = []
                tmp = row // 3
                tmp2 = col // 3
                grid_index = tmp * 3 + tmp2
                if self.grid[row][col] != 0:
                    self.possible_values.append(possible_values)
                    self.small_potentials[grid_index].append(possible_values)
                    continue
                for number in range(1, 10):
                    if self.is_valid((col, row), number):
                        possible_values.append(number)
                if possible_values:
                    size = len(possible_values) - 1
                    self.potential_indexs[size].append((col, row))
                    self.possible_values.append(possible_values)
                    self.small_potentials[grid_index].append(possible_values)
                    
                else:
                    self.possible_values.append(possible_values)
                    self.small_potentials[grid_index].append(possible_values)
                    self.is_solveable = False
                    return False
        return True
                    

    def solve_bt(self):
        try:
            index = np.argwhere(self.grid == 0)[0]
        except IndexError:
            return True
        
        for number in range(1, 10):
            if self.is_valid((index[1],index[0]), number):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                self.grid[index[0]][index[1]] = number
                self.update_small_grid((index[1], index[0]), number)
                if self.show_visual == True:
                    root.draw_window()
                if self.solve_bt() == True:
                    return True
                self.grid[index[0]][index[1]] = 0
                self.update_small_grid((index[1], index[0]), 0)
        return False
    
    def solve_logic_bt(self):
        #print(self.potential_indexs, "\n")
        #print(self.possible_values, "\n")
        #print(self.small_potentials, "\n")
        try:
            np.argwhere(self.grid == 0)[0]
        except IndexError:
            return True

        if not self.get_possible_values():
            return False
        # naked singles
        if self.potential_indexs[0]:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            index = self.potential_indexs.pop(0)
            col, row = index[0]
            pIndex = row*9 + col
            tmp_pv = self.possible_values[pIndex]
            self.grid[row][col] = tmp_pv[0]
            self.update_small_grid((col, row), tmp_pv[0])
            #self.possible_values[pIndex] = []
            if self.show_visual == True:
                root.draw_window()
            if self.solve_logic_bt() == True:
                return True
            self.grid[row][col] = 0
            self.update_small_grid((col, row), 0)
            self.potential_indexs.insert(0, index)
            self.possible_values.insert(pIndex, tmp_pv)
            self.get_possible_values()
            return False
        
        #hidden singles
        self.check_counts()
        for val in self.hidden_singles:
            num = 1
            for possible_index in val:
                if possible_index != 0:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                    col, row = possible_index
                    self.grid[row][col] = num
                    self.update_small_grid((col, row), num)
                    if self.show_visual == True:
                        root.draw_window()
                    if self.solve_logic_bt() == True:
                        return True
                    self.grid[row][col] = 0
                    self.update_small_grid((col, row), 0)
                    self.get_possible_values()
                    return False
                num += 1


        #back tracking if that fails
        for potentials in self.potential_indexs:
            if potentials:
                index = potentials[0]
                for number in range(1, 10):
                    if self.is_valid((index[0], index[1]), number):
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit()
                        self.grid[index[1]][index[0]] = number
                        self.update_small_grid((index[0], index[1]), number)
                        if self.show_visual == True:
                            root.draw_window()
                        if self.solve_logic_bt() == True:
                            return True
                        self.grid[index[1]][index[0]] = 0
                        self.update_small_grid((index[0], index[1]), 0)
                return False
            else:
                continue

        return True


        

class SudokuGUI:
    def __init__(self):
        self.board = SudokuBoard()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.width = BOARD_WIDTH + PADDING
        self.height = BOARD_HEIGHT + PADDING
        self.distance = BOARD_WIDTH / 9
        self.selected = None
        self.solveButton = None
        self.solve2Button = None
        self.startTime = None
        self.solveTime = None
        self.revert = SudokuBoard()
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
        solveText = FONT.render(' Solve-BT ', True, BLACK, GRAY)
        solveRect = solveText.get_rect()
        solveRect.center = (67, 500)
        solveBounds = [solveRect.left, solveRect.right, solveRect.top, solveRect.bottom]
        self.solveButton = solveBounds
        if mouse[0] >= solveBounds[0] and mouse[0] <= solveBounds[1] and mouse[1] >= solveBounds[2] and mouse[1] <= solveBounds[3]:
            solveText = FONT.render(' Solve-BT ', True, BLACK, LIGHT_GRAY)

        solve2Text = FONT.render(' Solve-Logic+BT ', True, BLACK, GRAY)
        solve2Rect = solve2Text.get_rect()
        solve2Rect.center = (240, 500)
        solve2Bounds = [solve2Rect.left, solve2Rect.right, solve2Rect.top, solve2Rect.bottom]
        self.solve2Button = solve2Bounds
        if mouse[0] >= solve2Bounds[0] and mouse[0] <= solve2Bounds[1] and mouse[1] >= solve2Bounds[2] and mouse[1] <= solve2Bounds[3]:
            solve2Text = FONT.render(' Solve-Logic+BT ', True, BLACK, LIGHT_GRAY)

        
        self.screen.blit(solveText, solveRect)
        self.screen.blit(solve2Text, solve2Rect)
    
    def display_text(self):
        text = FONT.render('Press R to Reset   Press T to Toggle Visual', True, BLACK)
        textRect = text.get_rect()
        textRect.center = (250, 550)
        self.screen.blit(text, textRect)
    
    def display_time(self):
        text = FONT.render('Time Taken', True, BLACK)
        textRect = text.get_rect()
        textRect.center = (530, 25)
        self.screen.blit(text, textRect)
        if self.startTime == None:
            currentTime = 0.0
        elif self.solveTime != None:
            currentTime = self.solveTime
        else: 
            currentTime = time.time() - self.startTime
        currentTime = round(currentTime, 2)
        cur_time = FONT.render(str(currentTime), True, BLACK)
        timeRect = cur_time.get_rect()
        timeRect.center = (530, 50)
        self.screen.blit(cur_time, timeRect)
        
        
    def draw_window(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.display_numbers()
        if self.selected != None:
            self.highlight_cell()
        self.display_buttons()
        self.display_text()
        self.display_time()
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
                            self.solveTime = None
                            '''board_copy = copy.deepcopy(self.board.grid)
                            small_grid_copy = copy.deepcopy(self.board.small_grids)
                            self.revert.grid = board_copy
                            self.revert.small_grids = small_grid_copy'''
                            self.revert = copy.deepcopy(self.board)
                            start_time = time.perf_counter()
                            self.startTime = time.time()
                            self.board.solve_bt()
                            end_time = time.perf_counter()
                            self.solveTime = end_time - start_time

                        elif x >= self.solve2Button[0] and x <= self.solve2Button[1] and y >= self.solve2Button[2] and y <= self.solve2Button[3]:
                            self.solveTime = None
                            self.revert = copy.deepcopy(self.board)
                            start_time = time.perf_counter()
                            self.startTime = time.time()
                            #self.board.get_possible_values()
                            self.board.solve_logic_bt()
                            end_time = time.perf_counter()
                            self.solveTime = end_time - start_time
                

                elif event.type == pygame.KEYDOWN and self.selected != None:
                    if event.key == pygame.K_r:
                        self.solveTime = None
                        self.startTime = None
                        self.selected = None
                        self.board.grid = np.zeros((9,9))
                        self.board.small_grids = np.zeros((9, 3, 3))
                    elif event.key == pygame.K_e:
                        self.solveTime = None
                        self.startTime = None
                        self.selected = None
                        self.board = self.revert
                    elif event.key == pygame.K_t:
                        if self.board.show_visual == False:
                            self.board.show_visual = True
                        else:
                            self.board.show_visual = False
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
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
                        self.solveTime = None
                        self.startTime = None
                        self.selected = None
                        self.board.grid = np.zeros((9,9))
                        self.board.small_grids = np.zeros((9, 3, 3))
                    elif event.key == pygame.K_t:
                        if self.board.show_visual == False:
                            self.board.show_visual = True
                        else:
                            self.board.show_visual = False
                    elif event.key == pygame.K_e:
                        self.solveTime = None
                        self.startTime = None
                        self.selected = None
                        self.board = self.revert

            self.draw_window()

        pygame.quit()

if __name__ == '__main__':
    root = SudokuGUI()
    root.run()
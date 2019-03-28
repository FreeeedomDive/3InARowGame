import random

import pygame

import Block
import BlockTypes


class Game:
    def __init__(self, crystals):
        self.display = (1100, 800)
        self.screen = pygame.display.set_mode(self.display)
        self.bg = pygame.Surface(self.display)
        self.background_color = "#322228"
        self.mouse_down_coord = (0, 0)
        self.mouse_up_coord = (0, 0)
        self.desk = []
        for i in range(0, 8):
            self.desk.append([])
        self.crystals_number = crystals
        self.create_start_blocks()
        self.selected_block = None

    def run(self):
        mainloop = True
        pygame.init()
        pygame.display.set_caption("I Don't Know Hot To Name It")
        self.bg.fill(pygame.Color(self.background_color))
        while mainloop:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    mainloop = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] <= 800:
                        self.mouse_down_coord = pos
                        self.selected_block = self.desk[pos[1] // 100][
                            pos[0] // 100]
                    else:
                        self.mouse_down_coord = (-1, -1)
                if e.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if pos[0] <= 800 and self.mouse_down_coord[0] != -1:
                        self.mouse_up_coord = pos
                        self.handle_mouse()
                        print("==========")
                    else:
                        self.mouse_up_coord = (-1, -1)
                    self.selected_block = None
            self.draw()

    def handle_mouse(self):
        delta_x = self.mouse_up_coord[0] - self.mouse_down_coord[0]
        delta_y = self.mouse_up_coord[1] - self.mouse_down_coord[1]
        if abs(delta_x) > abs(delta_y):
            if delta_x > 0:
                print("RIGHT")
                self.make_step(self.desk, self.selected_block, 1, 0)
            elif delta_x < 0:
                print("LEFT")
                self.make_step(self.desk, self.selected_block, -1, 0)
        elif abs(delta_x) < abs(delta_y):
            if delta_y > 0:
                self.make_step(self.desk, self.selected_block, 0, 1)
                print("DOWN")
            elif delta_y < 0:
                print("UP")
                self.make_step(self.desk, self.selected_block, 0, -1)

    def make_step(self, desk, block, delta_x, delta_y):
        # делается свап, если ход корректен, изменения остаются
        # иначе все возвращается назад
        if delta_x == -1:
            if block.x == 0:
                return False, desk
        if delta_x == 1:
            if block.x == 7:
                return False, desk
        if delta_y == -1:
            if block.y == 0:
                return False, desk
        if delta_y == 1:
            if block.y == 7:
                return False, desk
        desk[block.y][block.x], desk[block.y + delta_y][block.x + delta_x] = \
            desk[block.y + delta_y][block.x + delta_x], desk[block.y][block.x]
        destroy = self.check_triple_stacks(desk)
        if len(destroy) == 0:
            desk[block.y][block.x], desk[block.y + delta_y][block.x + delta_x] = desk[block.y + delta_y][block.x + delta_x], desk[block.y][block.x]
            self.desk = desk
            return
        for line in range(8):
            for column in range(8):
                desk[line][column].x = column
                desk[line][column].y = line
        destroy_in_column = [0, 0, 0, 0, 0, 0, 0, 0]
        for d in destroy:
            destroy_in_column[d.x] += 1
        columns = []
        for i in range(8):
            columns.append([])
        for line in range(8):
            for col in range(8):
                columns[col].append(desk[line][col])
        for d in destroy:
            print(d.x, d.y)
            columns[d.x].remove(d)
        new_columns = []
        for c in range(8):
            print("Need {} new blocks".format(destroy_in_column[c]))
            new_column = columns[c][::-1]
            if destroy_in_column[c] == 0:
                new_columns.append(new_column[::-1])
                continue
            for i in range(8 - destroy_in_column[c]):
                new_column[i].y = 7 - i
            for i in range(8 - destroy_in_column[c], 8):
                color = BlockTypes.types[
                        random.randint(0, len(BlockTypes.types) - 1)]
                new_block = Block.Block(c, 7 - i, color)
                new_column.append(new_block)
            new_columns.append(new_column[::-1])
        new_desk = []
        for i in range(8):
            new_desk.append([])
        for line in range(8):
            for column in range(8):
                print(column, line)
                new_desk[line].append(new_columns[column][line])
        self.desk = new_desk
        for line in range(8):
            print("{} {} {} {} {} {} {} {}".format(self.desk[line][0], self.desk[line][1], self.desk[line][2], self.desk[line][3],
                                                   self.desk[line][4], self.desk[line][5], self.desk[line][6], self.desk[line][7]))


    @staticmethod
    def check_triple_stacks(desk):
        destroy = []
        for line in range(8):
            for start in range(6):
                block1 = desk[line][start]
                block2 = desk[line][start + 1]
                block3 = desk[line][start + 2]
                current = (block1, block2, block3)
                if block1.color == block2.color == block3.color:
                    destroy.extend(current)
        for column in range(8):
            for start in range(6):
                block1 = desk[start][column]
                block2 = desk[start + 1][column]
                block3 = desk[start + 2][column]
                current = (block1, block2, block3)
                if block1.color == block2.color == block3.color:
                    destroy.extend(current)
        for b in set(destroy):
            print("\t" + str(b))
        return set(destroy)

    def create_start_blocks(self):
        for line in range(0, 8):
            for column in range(0, 8):
                self.desk[line].append(None)

        for line in range(0, 8):
            for column in range(0, 8):
                color = None
                while not self.is_correct_color(color, line, column):
                    color = BlockTypes.types[
                        random.randint(0, len(BlockTypes.types) - 1)]
                    self.desk[line][column] = Block.Block(column, line, color)

    def is_correct_color(self, color, line, column):
        if color is None:
            return False
        if column > 1:
            prev = self.desk[line][column - 1]
            if prev.color == color:
                prev2 = self.desk[line][column - 2]
                if prev2.color == color:
                    return False
        if line > 1:
            prev = self.desk[line - 1][column]
            if prev.color == color:
                prev2 = self.desk[line - 2][column]
                if prev2.color == color:
                    return False
        return True

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        pygame.draw.line(self.screen, (255, 255, 255),
                         (801, 0), (801, 800), 1)
        for line in range(0, 8):
            y = 50 + 100 * line
            for column in range(0, 8):
                x = 50 + 100 * column
                block = self.desk[line][column]
                pygame.draw.circle(self.screen, block.draw_color,
                                   (50 + block.x * 100, 50 + block.y * 100),
                                   45)
        pygame.display.update()


if __name__ == '__main__':
    window = Game(5)
    window.run()

import random
import threading
import time

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
        self.crystals_collected = 0
        self.max_crystals_on_screen = min(int(self.crystals_number * 0.4), 10)
        self.current_crystals_on_screen = 0
        self.create_start_blocks()
        self.selected_block = None
        self.mainloop = True

    def run(self):
        pygame.init()
        pygame.display.set_caption("I Don't Know Hot To Name It")
        self.bg.fill(pygame.Color(self.background_color))
        while self.mainloop:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.mainloop = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] <= 800:
                        self.mouse_down_coord = pos
                        self.selected_block = self.desk[pos[1] // 100][
                            pos[0] // 100]
                    else:
                        self.selected_block = None
                if e.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if self.selected_block is not None:
                        self.mouse_up_coord = pos
                        self.handle_mouse()
                    else:
                        self.mouse_up_coord = (-1, -1)
                    self.selected_block = None
            self.draw()

    def handle_mouse(self):
        delta_x = self.mouse_up_coord[0] - self.mouse_down_coord[0]
        delta_y = self.mouse_up_coord[1] - self.mouse_down_coord[1]
        if abs(delta_x) > abs(delta_y):
            if delta_x > 0:
                self.make_step(self.desk, self.selected_block, 1, 0)
            elif delta_x < 0:
                self.make_step(self.desk, self.selected_block, -1, 0)
        elif abs(delta_x) < abs(delta_y):
            if delta_y > 0:
                self.make_step(self.desk, self.selected_block, 0, 1)
            elif delta_y < 0:
                self.make_step(self.desk, self.selected_block, 0, -1)

    def make_step(self, desk, block, delta_x, delta_y):
        # делается свап, если ход корректен, изменения остаются
        # иначе все возвращается назад
        if not self.check_bounds(block, delta_x, delta_y):
            return
        x = block.x
        y = block.y
        moving_block = desk[block.y + delta_y][block.x + delta_x]
        desk[block.y][block.x], desk[block.y + delta_y][block.x + delta_x] = \
            desk[block.y + delta_y][block.x + delta_x], desk[block.y][block.x]
        destroy = self.check_triple_stacks(desk)
        if len(destroy) == 0:
            desk[block.y][block.x], desk[block.y + delta_y][
                block.x + delta_x] = desk[block.y + delta_y][
                                         block.x + delta_x], desk[block.y][
                                         block.x]
            return
        block.x = x + delta_x
        block.y = y + delta_y
        block.recount_coordination()
        moving_block.x = x
        moving_block.y = y
        moving_block.recount_coordination()

        while len(destroy) != 0:
            for line in range(8):
                for column in range(8):
                    desk[line][column].move_speed[0] = \
                        (column - desk[line][column].x)
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
                columns[d.x].remove(d)
            new_columns = []
            for c in range(8):
                new_column = columns[c][::-1]
                if destroy_in_column[c] == 0:
                    new_columns.append(new_column[::-1])
                    continue
                for i in range(8 - destroy_in_column[c]):
                    new_column[i].move_speed = [0, (7 - i - new_column[i].y)]
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
                    new_desk[line].append(new_columns[column][line])
            self.desk = new_desk
            destroy = []
            # time.sleep(0.1)
            # destroy = self.check_triple_stacks(self.desk)

    @staticmethod
    def is_desk_ready(desk):
        for line in range(8):
            for column in range(8):
                if desk[line][column].is_moving:
                    return False
        return True

    @staticmethod
    def check_bounds(block, delta_x, delta_y):
        if delta_x == -1:
            if block.x == 0:
                return False
        if delta_x == 1:
            if block.x == 7:
                return False
        if delta_y == -1:
            if block.y == 0:
                return False
        if delta_y == 1:
            if block.y == 7:
                return False
        return True

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
                    r = random.randint(0, 20)
                    has_crystal = False
                    if r == 10 and self.current_crystals_on_screen < self.max_crystals_on_screen:
                        self.current_crystals_on_screen += 1
                        has_crystal = True
                    self.desk[line][column] = Block.Block(column, line, color,
                                                          has_crystal)

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
            for column in range(0, 8):
                block = self.desk[line][column]
                if block.move_speed[0] != 0:
                    block.is_moving = True
                    block.centre_position[0] += block.move_speed[0]
                    if abs(block.centre_position[0] - (
                            50 + block.x * 100)) < 50:
                        block.is_moving = False
                        block.move_speed[0] = 0
                        block.centre_position[0] = 50 + block.x * 100
                if block.move_speed[1] != 0:
                    block.is_moving = True
                    block.centre_position[1] += block.move_speed[1]
                    if abs(block.centre_position[1] - (
                            50 + block.y * 100)) < 50:
                        block.move_speed[1] = 0
                        block.centre_position[1] = 50 + block.y * 100
                if block.has_crystal:
                    pygame.draw.circle(self.screen, block.draw_color,
                                       (block.centre_position[0],
                                        block.centre_position[1]),
                                       45, 10)
                else:
                    pygame.draw.circle(self.screen, block.draw_color,
                                       (block.centre_position[0],
                                        block.centre_position[1]),
                                       45)

        pygame.display.update()


if __name__ == '__main__':
    window = Game(5)
    window.run()

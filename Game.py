import random
import threading
import time
import datetime
import sys
import os
import pygame
import itertools

import Block
import BlockTypes
from CrystalParticle import Particle


class Game:
    def __init__(self, crystals, score):
        self.start_score = score
        self.score = score
        self.display = (1100, 875)
        self.screen = pygame.display.set_mode(self.display)
        self.bg = pygame.Surface(self.display)
        self.background_color = "#322228"
        self.mouse_down_coord = (0, 0)
        self.mouse_up_coord = (0, 0)
        self.desk = []
        for i in range(0, 8):
            self.desk.append([])
        self.player_can_touch = True
        self.level_passed = False
        self.crystals_number = crystals
        self.crystals_collected = 0
        self.max_crystals_on_screen = min(int(self.crystals_number * 0.4), 10)
        self.current_crystals_on_screen = 0
        self.create_start_blocks()
        self.selected_block = None
        self.mainloop = True
        self.next_level_thread = threading.Thread(target=self.start_countdown)
        self.go_to_next_level = False
        self.resets = 0
        self.crystal_particles = []
        self.separator_length = 750 / self.crystals_number
        self.current_crystal_pos = 25
        self.time_for_pass = self.crystals_number * 20
        self.time_for_pass = max(self.time_for_pass, 3 * 60)
        self.time_for_pass = min(self.time_for_pass, 6 * 60)
        self.level_start_time = int(round(time.time()))
        self.level_finish_time = self.level_start_time + self.time_for_pass
        self.enough_time = True
        self.time_thread = threading.Thread(target=self.timer)
        self.time_remaining = self.level_finish_time - self.level_start_time
        self.last_moves_history = []
        self.no_justice = False

    def run(self):
        pygame.init()
        pygame.display.set_caption("I Don't Know How To Name It")
        self.bg.fill(pygame.Color(self.background_color))
        self.time_thread.start()
        while self.mainloop:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    with open("save.txt", "w") as file:
                        file.write("{} {}".format(self.crystals_number,
                                                  self.start_score))
                    self.mainloop = False
                    sys.exit(0)
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if self.player_can_touch:
                        pos = pygame.mouse.get_pos()
                        if pos[0] <= 800 and pos[1] <= 800:
                            self.mouse_down_coord = pos
                            self.selected_block = self.desk[pos[1] // 100][
                                pos[0] // 100]
                        elif 830 <= pos[0] <= 930 and 400 <= pos[1] < 430:
                            self.resets += 1
                            cost = 1500 * self.resets
                            if self.score < cost:
                                self.resets -= 1
                            else:
                                self.score -= cost
                                self.create_start_blocks()
                                self.current_crystals_on_screen = 0
                        else:
                            self.selected_block = None
                if e.type == pygame.MOUSEBUTTONUP:
                    if self.player_can_touch:
                        pos = pygame.mouse.get_pos()
                        if self.selected_block is not None:
                            self.mouse_up_coord = pos
                            self.handle_mouse()
                        else:
                            self.mouse_up_coord = (-1, -1)
                        self.selected_block = None
            self.draw()
            if self.go_to_next_level:
                if self.enough_time:
                    window = Game(self.crystals_number + 5, self.score)
                    window.run()
                else:
                    window = Game(self.crystals_number, self.start_score)
                    window.run()
        print("end")

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
        self.last_moves_history.append(block.color)
        if len(self.last_moves_history) > 2:
            self.last_moves_history.pop(0)
        self.player_can_touch = False
        block.x = x + delta_x
        block.y = y + delta_y
        block.recount_coordination()
        moving_block.x = x
        moving_block.y = y
        moving_block.recount_coordination()
        for line in range(8):
            for column in range(8):
                desk[line][column].move_speed[0] = \
                    (column - desk[line][column].x)
                desk[line][column].x = column
                desk[line][column].y = line

        combo = 1
        step = True
        while len(destroy) != 0:
            if step:
                temp = list(destroy)
                temp.extend(self.check_and_execute_totem(desk, block.x,
                                                         block.y))
                destroy = set(temp)
            destroy_in_column = [0, 0, 0, 0, 0, 0, 0, 0]
            for d in destroy:
                destroy_in_column[d.x] += 1
            columns = []
            for i in range(8):
                columns.append([])
            for line in range(8):
                for col in range(8):
                    columns[col].append(desk[line][col])
            count = self.check_justice_in_the_world(desk)
            if count == 0:
                self.score = self.score // 5 * 4
                self.no_justice = True
            ratio = 1
            if not self.no_justice:
                ratio = 1 + (0.05 * count)
            for d in destroy:
                if d.has_crystal:
                    self.crystals_collected += 1
                    self.current_crystals_on_screen -= 1
                    self.score += int(50 * combo * ratio)
                    start_x = d.centre_position[0]
                    start_y = d.centre_position[1]
                    finish_x = self.current_crystal_pos
                    finish_y = 840
                    p = Particle(d.color, start_x, start_y,
                                 finish_x, finish_y,
                                 (finish_x -
                                  d.centre_position[0]) / 100,
                                 (finish_y - d.centre_position[1]) / 100)
                    self.crystal_particles.append(p)
                    self.current_crystal_pos += self.separator_length
                columns[d.x].remove(d)
                self.score += int(100 * combo * ratio)
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
                    crystal = False
                    if self.crystals_collected + self.current_crystals_on_screen < self.crystals_number and self.current_crystals_on_screen < self.max_crystals_on_screen:
                        crystal = random.randint(1, 10) == 5
                        if crystal:
                            self.current_crystals_on_screen += 1
                    new_block = Block.Block(c, 7 - i, color, crystal)
                    new_column.append(new_block)
                new_columns.append(new_column[::-1])
            new_desk = []
            for i in range(8):
                new_desk.append([])
            for line in range(8):
                for column in range(8):
                    new_desk[line].append(new_columns[column][line])
            desk = new_desk
            self.desk = desk
            for line in range(8):
                for column in range(8):
                    self.desk[line][column].x = column
                    self.desk[line][column].y = line
                    if self.desk[line][column].move_speed[0] != 0 or \
                            self.desk[line][column].move_speed[1] != 0:
                        self.desk[line][column].is_moving = True
            while not self.is_desk_ready(desk) and self.enough_time:
                self.draw()
            destroy = self.check_triple_stacks(desk)
            combo += 1
            step = False
        if self.check_win():
            self.level_passed = True
            for line in range(8):
                for column in range(8):
                    self.desk[line][column].move_speed = [0, 3]
            self.next_level_thread.start()
        else:
            self.player_can_touch = True

    @staticmethod
    def check_justice_in_the_world(desk):
        count = 0
        for x in range(8):
            for y in range(8):
                if desk[y][x].color == BlockTypes.Types.Grey:
                    count += 1
        return count

    def check_and_execute_totem(self, desk, x, y):
        destroy = []
        if len(self.last_moves_history) == 1:
            return destroy
        last = self.last_moves_history[-1]
        pre_last = self.last_moves_history[-2]
        if last == pre_last:
            if last == BlockTypes.Types.Blue:
                s_x = random.randint(0, 5)
                s_y = random.randint(0, 5)
                for x, y in itertools.product(range(s_x, s_x + 3),
                                              range(s_y, s_y + 3)):
                    destroy.append(desk[y][x])
                s_x = random.randint(0, 6)
                s_y = random.randint(0, 6)
                for x, y in itertools.product(range(s_x, s_x + 2),
                                              range(s_y, s_y + 2)):
                    destroy.append(desk[y][x])
            elif last == BlockTypes.Types.Red:
                for x, y in itertools.product(range(8), range(8)):
                    if desk[y][x].color == BlockTypes.Types.Red:
                        destroy.append(desk[y][x])
            elif last == BlockTypes.Types.Green:
                for x, y in itertools.product(range(8), range(8)):
                    if desk[y][x].has_crystal:
                        destroy.append(desk[y][x])
            elif last == BlockTypes.Types.Grey:
                for i in range(8):
                    destroy.append(desk[y][i])
                    destroy.append(desk[i][x])
            elif last == BlockTypes.Types.Yellow:
                self.score = int(self.score * 1.05)
            elif last == BlockTypes.Types.Purple:
                new_color = BlockTypes.types[random.randint(0, len(BlockTypes.types) - 1)]
                number = random.randint(5, 25)
                for i in range(number):
                    x = random.randint(0, 7)
                    y = random.randint(0, 7)
                    block = desk[y][x]
                    block.color = new_color
                    block.image_name = block.get_pic(new_color)
                    block.image = pygame.image.load(block.image_name)
            elif last == BlockTypes.Types.Orange:
                self.level_finish_time += 40
            self.last_moves_history.clear()
        return set(destroy)

    def check_win(self):
        if self.crystals_collected == self.crystals_number:
            return True

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
                    has_crystal = False
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
                         (801, 0), (801, 875), 5)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (0, 801), (801, 801), 5)
        for i in range(1, 8):
            pygame.draw.line(self.screen, (255, 255, 255),
                             (1 + i * 100, 0), (1 + i * 100, 800), 1)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (0, 1 + i * 100), (800, 1 + i * 100), 1)

        font = pygame.font.Font(None, 40)
        t = "Score: {0}".format(self.score)
        color = (255, 255, 255)
        if self.no_justice:
            color = (255, 0, 0)
        text = font.render(t, True, color)
        self.screen.blit(text, [820, 50])

        font = pygame.font.Font(None, 30)
        t = "Crystals".format(self.crystals_collected,
                              self.crystals_number)
        red = 255 - (self.crystals_collected / self.crystals_number) * 255
        green = (self.crystals_collected / self.crystals_number) * 255
        text = font.render(t, True, (red, green, 0))
        self.screen.blit(text, [10, 810])
        t = "{}/{}".format(self.crystals_collected,
                           self.crystals_number)
        text = font.render(t, True, (red, green, 0))
        self.screen.blit(text, [700, 810])

        pygame.draw.line(self.screen, (red, green, 0),
                         (24, 839), (776, 839), 2)
        pygame.draw.line(self.screen, (red, green, 0),
                         (24, 839), (24, 866), 2)
        pygame.draw.line(self.screen, (red, green, 0),
                         (776, 839), (776, 866), 2)
        pygame.draw.line(self.screen, (red, green, 0),
                         (24, 866), (776, 866), 2)

        if not self.enough_time:
            font = pygame.font.Font(None, 100)
            t = "Time has up!"
            color = (255, 0, 0)
            text = font.render(t, True, color)
            self.screen.blit(text, [220, 350])

        pygame.draw.rect(self.screen, (150, 0, 0), pygame.Rect(830, 400, 100, 30))
        font = pygame.font.Font(None, 25)
        t = "Reset desk"
        text = font.render(t, True, (255, 255, 255))
        self.screen.blit(text, [835, 405])

        for line in range(0, 8):
            for column in range(0, 8):
                block = self.desk[line][column]
                if self.level_passed or not self.enough_time:
                    block.centre_position[1] += block.move_speed[1]
                else:
                    if block.move_speed[0] != 0:
                        block.is_moving = True
                        block.centre_position[0] += block.move_speed[0]
                        if abs(block.centre_position[0] - (
                                50 + block.x * 100)) < 20:
                            block.is_moving = False
                            block.move_speed[0] = 0
                            block.centre_position[0] = 50 + block.x * 100
                    if block.move_speed[1] != 0:
                        block.is_moving = True
                        block.centre_position[1] += block.move_speed[1]
                        if abs(block.centre_position[1] - (
                                50 + block.y * 100)) < 10:
                            block.is_moving = False
                            block.move_speed[1] = 0
                            block.centre_position[1] = 50 + block.y * 100
                if block.has_crystal:
                    pygame.draw.circle(self.screen, (230, 170, 50),
                                       (block.centre_position[0],
                                        block.centre_position[1]),
                                       45)
                    block.draw(self.screen)
                else:
                    block.draw(self.screen)
        for p in self.crystal_particles:
            p.coordinations[0] += p.move_speed[0]
            p.coordinations[1] += p.move_speed[1]
            p.draw(self.screen)
            if abs(p.finish[0] - p.coordinations[0]) < 20 and abs(
                    p.finish[1] - p.coordinations[1]) < 20:
                p.coordinations[0] = p.finish[0]
                p.coordinations[1] = p.finish[1]
                p.move_speed = [0, 0]

        pygame.display.update()

    def timer(self):
        while self.enough_time and self.mainloop:
            current = int(round(time.time()))

            self.time_remaining = max(0, self.level_finish_time - current)

            font = pygame.font.Font(None, 35)
            t = "Time remaining: {}".format(
                self.create_correct_time(self.time_remaining))
            color = (255, 255, 255)
            text = font.render(t, True, color)
            self.screen.blit(text, [820, 350])

            if self.time_remaining == 0:
                self.enough_time = False
                for line in range(8):
                    for column in range(8):
                        self.desk[line][column].move_speed = [0, 3]
        if not self.level_passed:
            self.start_countdown()

    @staticmethod
    def create_correct_time(time):
        mins = time // 60
        secs = time % 60
        if secs < 10:
            return "{}:0{}".format(mins, secs)
        else:
            return "{}:{}".format(mins, secs)

    def start_countdown(self):
        time.sleep(3)
        self.mainloop = False
        self.go_to_next_level = True


if __name__ == '__main__':
    data = None
    try:
        with open("save.txt") as file:
            data = file.read().split()
        window = Game(int(data[0]), int(data[1]))
    except FileNotFoundError:
        with open("save.txt", "w") as file:
            file.write("5 0")
        window = Game(5, 0)
    window.run()

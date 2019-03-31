import pygame

import BlockTypes


class Block:
    def __init__(self, x, y, color, has_crystal=False):
        self.x = x
        self.y = y
        self.centre_position = [50 + x * 100, -100]
        self.has_crystal = has_crystal
        self.color = color
        self.image_name = self.get_pic(color)
        self.image = pygame.image.load(self.image_name)
        self.draw_color = self.get_color(color)
        self.move_speed = [5, 5]
        self.is_moving = False

    def recount_coordination(self):
        self.centre_position = [50 + self.x * 100, 50 + self.y * 100]

    def draw(self, screen):
        screen.blit(self.image,
                    (self.centre_position[0] - 40,
                     self.centre_position[1] - 40))

    @staticmethod
    def get_color(color):
        return BlockTypes.type_to_color[color]

    @staticmethod
    def get_pic(color):
        return BlockTypes.type_to_image[color]

    def __str__(self):
        # return "({}, {}) Crystal: {} Color: {}".format(self.x, self.y,
        #                                                self.has_crystal,
        #                                                self.color)
        return str(self.color) + str(self.move_speed)

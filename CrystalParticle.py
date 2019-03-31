import BlockTypes
import pygame


class Particle:

    def __init__(self, color, s_x, s_y, f_x, f_y, d_x, d_y):
        self.color = color
        self.coordinations = [s_x, s_y]
        self.finish = [f_x, f_y]
        self.move_speed = [d_x, d_y]
        self.image_name = BlockTypes.type_to_image[color][:-4] + "_m.png"
        self.image = pygame.image.load(self.image_name)

    def draw(self, screen):
        screen.blit(self.image,
                    (self.coordinations[0],
                     self.coordinations[1]))

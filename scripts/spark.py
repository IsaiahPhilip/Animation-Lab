# remember cartesian coords vs polar coords
# cartesian = (x, y)  polar = (r, a)
import math

import pygame.draw


class Spark:
    def __init__(self, pos, angle, speed):
        # position represents cartesian tuple
        self.pos = list(pos)
        # angle and speed represent components of polar coords
        self.angle = angle
        self.speed = speed

    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed
        # slows sparks down to 0
        self.speed = max(0, self.speed - 0.1)

        return not self.speed

    def render(self, surf, offset=(0, 0)):
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * .5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * .5) * self.speed * 0.5 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle - math.pi * .5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * .5) * self.speed * 0.5 - offset[1]),
        ]

        pygame.draw.polygon(surf, (255, 255, 255), render_points)

import math
import random

import pygame

from scripts.particle import Particle
from scripts.spark import Spark


# 4:10

# Class used for sprite characters
class PhysicsEntity:
    # acts as a constructor
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)  # every entity needs their own position list
        # (l, w) tuple
        self.size = size
        # [x, y]
        self.velocity = [0, 0]
        # dict of all collisions currently triggered
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''

        self.anim_offset = (-3, -3)
        self.flip = False  # enables to player to flip right or left
        self.set_action('idle')

        self.last_movement = [0, 0]
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    # used to define entity actions for the purpose of animation
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    # Handles general collisions and movement of entities
    def update(self, tilemap, movement=(0, 0)):
        # collisions are initially set to false in each frame
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        # 0 = -x, 1 = + ( currently self.velocity is always 0
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # x movement and collision handling
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:  # collision right
                    self.collisions['right'] = True
                    entity_rect.right = rect.left
                if frame_movement[0] < 0:  # collision left
                    self.collisions['left'] = True
                    entity_rect.left = rect.right
                self.pos[0] = entity_rect.x

        # y movement and collision handling
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:  # collision down
                    self.collisions['down'] = True
                    entity_rect.bottom = rect.top
                if frame_movement[1] < 0:  # collision up
                    self.collisions['up'] = True
                    entity_rect.top = rect.bottom
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:  # if entity moves to the left
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            # checks if there is a solid tile ahead + below the enemy
            if (not self.collisions['right'] and not self.collisions['left']
                    and tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23))):
                # subtract 0.5 if enemy is facing left and add 0.5 if enemy is facing right
                movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                # turns enemy around
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            # triggers on the first frame that the enemy stops in
            if not self.walking:
                # difference between player and enemy position
                # if player is to the left of enemy distance[0] < 0
                distance = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if abs(distance[1]) < 16:
                    if self.flip and distance[0] < 0:  # if the enemy is facing left, at the player
                        self.game.sfx['shoot'].play(0)
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark((self.game.projectiles[-1][0]), random.random() - 0.5 + math.pi, 2 + random.random()))
                    if not self.flip and distance[0] > 0:  # if the enemy is facing right, at the player
                        self.game.sfx['shoot'].play(0)
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark((self.game.projectiles[-1][0]), random.random() - 0.5, 2 + random.random()))

        # 1 in 100 chance of occuring, every frame
        elif random.random() < 0.01:
            # sets number of frames the enemy will continue to walk for
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # if player is currently dashing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screen_shake = max(16, self.game.screen_shake)
                self.game.sfx['hit'].play(0)
                for i in range(30):
                    angle = random.random() * math.pi * 2  # random angle (0 -> 2pi)
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True


    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset)

        if self.flip:
            gun_pos = (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1])
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), gun_pos)
        else:
            gun_pos = (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1])
            surf.blit(self.game.assets['gun'], gun_pos)

class Player(PhysicsEntity):
    def __init__(self, assets, game, pos, size):
        super().__init__(game, 'player', pos, size)  # call to parent constructor
        # weird variable with multiple uses
        self.dashing = 0
        self.air_time = 0
        # keeps track of the amount of jumps the player has left
        self.jumps = 1
        self.wall_slide = False

    def update(self, tilemap, movement=(0, 0)):

        super().update(tilemap, movement=movement)  # call to parent function

        if not self.wall_slide:
            self.air_time += 1

        if self.air_time > 120:
            self.game.dead += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False
        # if we hit the wall on either side and we are in the air
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            # sets a 0.5 cap on downward velocity when character is on the wall
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                # dash particle handling
                angle = random.random() * math.pi * 2  # random angle
                speed = random.random() * 0.5 + 0.5  # random value from 0.5 to 1
                p_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]  # memorize this formula
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                    velocity=p_velocity, frame=random.randint(0, 7)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        # if we are in the first 10 frames of the dash
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
                # stream particle handling
            p_velocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                velocity=p_velocity, frame=random.randint(0, 7)))

        # brings velocity towards zero if it does not equal zero
        if self.velocity[0] > 0:
            # to the right
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            # to the left
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        # if dash on cooldown
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:  # if self.jumps is greater than zero
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True

    def dash(self):
        # if self.dashing = 0
        if not self.dashing:
            self.game.sfx['dash'].play(0)
            if self.flip:  # if facing left
                self.dashing = -60
            else:
                self.dashing = 60



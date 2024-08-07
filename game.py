import math
import os
import random
import sys
import pygame

from scripts.buttons import Button
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Clouds


# 5:05:17

class Game:
    def __init__(self):
        # pygame.mixer.pre_init(buffer=20000, frequency=22050)
        pygame.init()

        pygame.display.set_caption('ANIMATION TESTER GAME')
        self.screen = pygame.display.set_mode((640, 480))

        # concept: render onto display then scale up to screen?
        # everything rendered in display gets an outline
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), 6),
            'enemy/run': Animation(load_images('entities/enemy/run'), 4),
            'player/idle': Animation(load_images('entities/player/idle'), 6),
            'player/run': Animation(load_images('entities/player/run'), 4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            # added buttons for main menu
            'exit': load_image('buttons/exit_btn.png'),
            'start': load_image('buttons/start_btn.png'),
            'continue': load_image('buttons/continue_btn.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        # instantiates player
        # size indicates the actual pixel width and length of the character

        self.player = Player(self.assets['player'], self, (50, 50), (8, 15))

        # again size indicates pixel length and height, in this case one value
        # is given since the pixel height and width are the same
        self.tilemap = Tilemap(self, 16)

        self.level = 0
        self.load_level(self.level)

        self.screen_shake = 16

        self.start_button = Button(self, 180, 100, self.assets['start'], .5)
        self.continue_button = Button(self, 180, 100, self.assets['continue'], .5)
        self.exit_button = Button(self, 200, 250, self.assets['exit'], .5)

        self.game_state = 'init'

    # Initiates the game with a given level
    def load_level(self, map_id):
        # self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.tilemap.load('map.json')

        # filled with rects
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        # 0 means that player is alive, once the player dies a counter begins to increment
        self.dead = 0
        # -30 should make a completely black screen while zero is just how the game normally looks
        self.transition = -30

    def run(self):
        # wav files are easier to deal with
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        # .play function takes the number of loops, 0 means no loop and -1 means infinite loop
        pygame.mixer.music.play(-1)
        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))

            while self.game_state == 'init' or self.game_state == 'paused':
                self.display.fill((0, 0, 0, 0))
                self.screen.blit(pygame.transform.scale(self.assets['background'], self.screen.get_size()), (0, 0))

                if self.game_state == 'init':  # game hasnt begun or new game is beginning
                    if self.start_button.draw(self.screen):
                        self.game_state = 'play'
                else:
                    if self.continue_button.draw(self.screen):
                        self.game_state = 'play'

                if self.exit_button.draw(self.screen):
                    pygame.quit()
                    sys.exit()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                pygame.display.update()
                self.clock.tick(60)

            self.screen_shake = max(0, self.screen_shake - 1)

            print(self.level)

            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(self.transition + 1, 30)
                if self.dead > 40:
                    self.load_level(self.level)

            # self.scroll[0] += 1  # moves entities and tilemap to the left by n pixels every frame
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # populates particles list
            for rect in self.leaf_spawners:
                # allows leafs to spawn at random
                if random.random() * 49999 < rect.width * rect.height:
                    # sets spawn position to random point between the bounds of the rect
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    # spawns particles
                    self.particles.append(
                        Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            # CLOUD HANDLING
            self.clouds.update()
            self.clouds.render(self.display_2, render_scroll)

            # TILEMAP HANDLING
            self.tilemap.render(self.display, offset=render_scroll)

            # Enemy handling

            # PLAYER HANDLING
            if not self.dead:  # if self.dead is zero
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # projectile consists of: [[x, y], direction, timer]

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

            # handles animation for each particle
            for particle in self.particles.copy():
                # if animation is finished kill becomes true
                kill = particle.update()
                # particle is rendered on screen
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # if key has been pressed down
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play(0)
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = 'paused'
                    # cheat used for bug testing
                    if event.key == pygame.K_p:
                        self.enemies.clear()
                # if key is not currently being pressed down
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # won't run while transition is at zero
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screen_shake_offset = (random.random() * self.screen_shake - self.screen_shake / 2,
                                   random.random() * self.screen_shake - self.screen_shake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screen_shake_offset)
            pygame.display.update()
            self.clock.tick(60)


Game().run()
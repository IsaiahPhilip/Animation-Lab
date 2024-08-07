import os

import pygame

BASE_IMAG_PATH = 'data/images/'

# function to return image objects and make black background transparent
def load_image(path):
    img = pygame.image.load(BASE_IMAG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

# function to load a list of images within a given directory
# to load multiple tiles at once
def load_images(path):
    images = []
    # os.listdir = all of the files in a given path
    for img_name in sorted(os.listdir(BASE_IMAG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0  # frame of the game

    def copy(self):  # returns a reference of the initial animation
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            # I actually understand ts fuck yea
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            # replays the final frame infinitely ig
            self.frame = min((self.frame + 1) % (self.img_duration * len(self.images)), self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    """
        returns current image of animation
    """
    def img(self):
        return self.images[int(self.frame / self.img_duration)]

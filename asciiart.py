import urllib.request
from bs4 import BeautifulSoup
import urllib.parse
import pygame as pg
import cv2 as cv
import numpy as np
from numba import njit
import os
@njit(fastmath=True)
def accelerate_conversion(image, width, height, ascii_coeff, step):
    array_of_values = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            char_index = image[y, x] // ascii_coeff
            if char_index:
                array_of_values.append((char_index, (x, y)))
    return array_of_values

class ArtConverter:
    def __init__(self, search='랄로', font_size=12):
        pg.init()
        self.search = search
        self.image = self.get_image(self.search)
        self.RES = self.WIDTH, self.HEIGHT = self.image.shape[1], self.image.shape[0]
        self.surface = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()

        self.ASCII_CHARS = ' .",:;!~+-xmo*#W&8@'
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS) - 1)

        self.font = pg.font.SysFont('Courier', font_size, bold=True)
        self.CHAR_STEP = int(font_size * 0.6)
        self.RENDERED_ASCII_CHARS = [self.font.render(char, False, 'white') for char in self.ASCII_CHARS]

    def get_image(self, search):
        encoded_search = urllib.parse.quote(search)
        url = f"https://www.youtube.com/results?search_query={encoded_search}"
        req = urllib.request.Request(url)
        fp = urllib.request.urlopen(req)
        source = fp.read()
        fp.close()

        soup = BeautifulSoup(source, 'html.parser')
        ssoup = str(soup)

        video_div = ssoup.find("videoRenderer")
        id = ssoup[video_div:video_div + 50].split('"')[4]

        url = f"https://img.youtube.com/vi/{id}/maxresdefault.jpg"
        img = urllib.request.urlopen(url).read()

        img = np.asarray(bytearray(img), dtype=np.uint8)
        img = cv.imdecode(img, cv.IMREAD_GRAYSCALE)
        img = cv.resize(img, (1800, 900), interpolation=cv.INTER_LINEAR)
        return img

    def draw_converted_image(self):
        array_of_values = accelerate_conversion(self.image, self.WIDTH, self.HEIGHT, self.ASCII_COEFF, self.CHAR_STEP)
        for char_index, pos in array_of_values:
            self.surface.blit(self.RENDERED_ASCII_CHARS[char_index], pos)

    def draw(self):
        self.surface.fill('black')
        self.draw_converted_image()

    def save_image(self):
        pygame_image = pg.surfarray.array3d(self.surface)
        pygame_image = np.transpose(pygame_image, (1, 0, 2))  # Transpose to match OpenCV's format
        cv.imwrite('result.jpg', pygame_image)
        os.rename('result.jpg',f"{self.search}.jpg")

    def run(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            self.draw()
            pg.display.flip()
        self.save_image()
        pg.quit()

if __name__ == '__main__':
    search = input("찾을거 : ")
    app = ArtConverter(search)
    app.run()

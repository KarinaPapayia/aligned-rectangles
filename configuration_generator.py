import random
from PIL import Image
import numpy as np


randsign = lambda: -1 if random.random() <= 0.5 else 1

def is_valid_rectangle(x0, y0, x1, y1, padding, canvas_size):
    return (x0 < canvas_size - padding) and \
    (x1 < canvas_size - padding) and \
    (y0 < canvas_size - padding) and \
    (y1 < canvas_size - padding) and x0 > 0 and y0 > 0

class RectangleConfigurationGenerator(object):
    def __init__(self, canvas_size = 28, padding = 5):
        self.canvas_size = canvas_size
        self.padding = padding
        
    def generate_rectangle(self, min_w = 2, max_w = 5, min_h = 2, max_h = 5, min_x0 = 0, min_y0 = 0):
        width = random.randint(min_w, max_w)
        height = random.randint(min_h, max_h)
        max_len = self.canvas_size - self.padding
        
        x0, y0, x1, y1 = [self.canvas_size] * 4
        while(not is_valid_rectangle(x0, y0, x1, y1, self.padding, self.canvas_size)):
            x0, y0 = random.randint(min_x0, max_len), random.randint(min_y0, max_len), 
            x1 = x0 + width
            y1 = y0 + height
        return x0, y0, x1, y1        
    
    def generate_sister(self, anchor, min_gap_x = 2, max_gap_x = 5, min_gap_y = 2, max_gap_y = 5):
        x0, y0, x1, y1 = anchor
        width = x1 - x0
        height = y1 - y0
        gap_x, gap_y = random.randint(min_gap_x, max_gap_x), random.randint(min_gap_y, max_gap_y)

        sx0, sy0, sx1, sy1 = [self.canvas_size] * 4
        while(not is_valid_rectangle(sx0, sy0, sx1, sy1, self.padding, self.canvas_size)):
            if randsign() > 0:
                sx0 = x0 + randsign() * (width + gap_x)
                sy0 = y0
            else:
                sy0 = y0 + randsign() * (height + gap_y)
                sx0 = x0    

            sx1 = sx0 + width
            sy1 = sy0 + height

        return (sx0, sy0, sx1, sy1)
    
    def generate_rectangles(self, count = 2, configs={}):
        
        sisters_count = count - 1
        rects = []
        current_anchor = self.generate_rectangle(**configs)
        print('Generated anchor:', current_anchor)
        rects.append(current_anchor)

        while (sisters_count):
            sister = self.generate_sister(current_anchor, **configs)
            rects.append(sister)
            sisters_count -= 1
            current_anchor = sister
            
        return rects
        
    def generate_configuration(self, count = 2, configs = {}):
        rects = self.generate_rectangles(count = count, configs=configs)
        canvas = Image.new('1', (self.canvas_size, self.canvas_size))
        for rect in rects:
            canvas.paste(1, rect)
        return canvas, rects
    
    def distort(self, rects):
        distorted_rects = []
        while(True):
            try:
                r1, r2, *rest = rects
                distorted_rects += self._distort_pair(r1, r2)
                rects = rest
            except Exception as e:
                break 
        return distorted_rects
    
    def _distort_pair(self, r1, r2, min_distortion_magnitude = 1, max_distortion_magnitude = 3):
        x10, y10, x11, y11 = r1
        x20, y20, x21, y21 = r2
        
        shift = random.randint(min_distortion_magnitude, max_distortion_magnitude)
    
        if x10 == x20:
            # vertical pair
            # todo: make sure they are valid rectangles:
            shift = (1 if y20 > y10 else -1) * shift
            return r1, (x20 + shift, y20, x21 + shift, y21)
        elif y10 == y20:
            # horizontal pair
            shift = (1 if x20 > x10 else -1) * shift
            return r1, (x20, y20 + shift, x21, y21 + shift)
        else:
            print(r1)
            print(r2)
            raise Exception("invalid pairs")
    
    def create_canvas(self, rects):
        canvas = Image.new('1', (self.canvas_size, self.canvas_size))
        for rect in rects:
            canvas.paste(1, rect)
        return canvas, rects

    def generate_training_pairs(self):
        beautified_rects = self.generate_rectangles(count=2)
        distorted_rects = self.distort(beautified_rects)
        return self.create_canvas(beautified_rects), self.create_canvas(distorted_rects)
    
    def generate_training_data(self, pair_count):
        data = []
        for i in range(pair_count):
            b, d = self.generate_training_pairs()
            data.append((b[0], d[0], b[1], d[1], i))
        return data
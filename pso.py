#    Copyright (C) 2004, Maxime Biais <maxime@biais.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: pso.py,v 1.2 2004/10/07 12:30:42 max Exp $

from random import uniform
import main as socon

class PSO:
    def __init__(self, pop_size, min, max, phi, phi2, lr, max_iter, func):
        self.func = func
        self.pop = []
        # 0: position, 1: velocity, 2: fitness
        self.min = min
        self.max = max
        for i in xrange(pop_size):
            self.pop.append([uniform(self.min, self.max), uniform(-1, 1), 0])
        self.evaluate()
        self.gdest = self.pop[0]
        self.pdest = self.pop[0]
        self.phi = phi
        self.phi2 = phi2
        self.lr = lr
        self.max_iter = max_iter
    
    def update_velocity(self):
        for i in self.pop:
            i[1] = self.lr * i[1] + uniform(0, self.phi) * (self.pdest[0] \
                    - i[0]) + uniform(0, self.phi2) * (self.gdest[0] - i[0])

    def evaluate(self):
        for i in self.pop:
            i[2] = self.func(i[0])

    def move(self):
        for i in self.pop:
            i[0] += i[1]
            if i[0] > self.max or i[1] < self.min:
                i[0], i[1], i[2] = uniform(self.min, self.max), uniform(-1, 1), 0
            
    def __cmp_by_fitness(self, a, b):
        return cmp(a[2], b[2])
    
    def run(self, update_func=False):
        for i in xrange(self.max_iter):
            if update_func:
                update_func()
            self.update_velocity()
            self.move()
            self.evaluate()
            self.pop.sort(self.__cmp_by_fitness, reverse=0)
            self.pdest = self.pop[0]
            print self.pdest[2], self.gdest[2]
            if self.pdest[2] < self.gdest[2]:
                self.gdest = self.pdest
            

    def __str__(self):
        ret = ""
        for i in self.pop:
            ret += str(i) + "\n"
        return ret

import pygame
import time

class PygamePrinter:
    def __init__(self, pso, w=400, h=300):
        self.calls = 0
        self.w = w
        self.h = h
        self._init_pygame()
        self.pso = pso
    
    def _init_pygame(self):
        self.screen = pygame.display.set_mode((self.w, self.h), 0, 8)
        self.backcolor  = (0, 0, 0)
        self.funccolor  = (255, 255, 255)
        self.partcolor  = (255, 0, 0)
        self.elitecolor  = (0, 0, 255)

    def draw_point(self, color, x, y, size=3):
        pygame.draw.rect(self.screen, color, (x - size, y - size, \
                                              size*2, size*2))

    def p2p(self, x, y):
        return (x + 1) * 200, y * 300

    def draw_func(self):
        for i in range(self.w):
            x = i / (self.w / float((self.pso.max - self.pso.min))) + self.pso.min
            y = self.pso.func(x)
            rh = y * (self.h / 2.) + (self.h / 2.)
            self.draw_point(self.funccolor, i, rh, 1)

    def _draw_xy(self, color, x, y):
        self.draw_point(color, (x + self.pso.max) * self.w / float((self.pso.max - self.pso.min)), \
                        (y + 1)*self.h/2)

    def draw_pop(self):
        for i in self.pso.pop:
            self._draw_xy(self.partcolor, i[0], i[2])
        i = self.pso.gdest
        self._draw_xy(self.elitecolor, i[0], i[2])

    def __call__(self):
        #time.sleep(0.5)
        self.screen.fill(self.backcolor)
        self.screen.lock()
        self.draw_func()
        self.draw_pop()
        self.screen.unlock()
        pygame.display.flip()
        if self.calls % 2 == 0:
           pygame.image.save(self.screen, "pso-%d.bmp" % self.calls) 
        self.calls += 1
                                 
def test():
    import math
    # func = lambda x:math.cos(x*math.sin(x*0.3)-x) / 1.5
    func = lambda x:math.cos(x) * math.exp(math.sin(x)) * math.sin(x)  / 1.5
    p = PSO(15, 0.0, 3.0, phi=1, phi2=1, lr=0.5, max_iter=20, func=func)
    #printer = PygamePrinter(p)
    #p.run(update_func=printer)
    print p
    
if __name__ == "__main__":
    test()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# orakel debakel - the revenge

import sys
import random
import cPickle as pickle


DEBUG = 1

class Main:
    def __init__(self):
        # read data
        pass

    def predict(self, teams):
        pass

   # add new scores and recalculate the stats
    def add_and_do_magic(self, team, gameday):
       pass


    def main(self):
      # sys args
      if len(sys.argv) != 3:
         print 'arguments wrong. major fuck up detected! stop(), hammertime!'
         print 'Usage: ' + sys.argv[0] + ' --predict <gameday> <input'
         print 'Usage: ' + sys.argv[0] + ' --verify <gameday> <input'
         sys.exit(1)
      else:
         mode = sys.argv[1]
         gameday = int(sys.argv[2])

      # read input
      input = sys.stdin.readlines()

      if mode == '--predict':
         # calculate every match
         for i in input:
            match = i.replace('\n', '').split(' ')

            # classic plus bonus method
            self.predict(match)

      # verify last gameday and enter scores to database
      elif mode == '--verify':
         for i in input:
            match = i.replace('\n', '').split(' ')

            # add live scores to the database and recalculate
            self.add_and_do_magic(match, gameday)

      else:
         print 'ERROR: arguments not recognized.\ndefault method called: solving the answer to the life, the universe and everything. come back in 7.5 million years. and thanks for all the fish!'


class Parser:
    def __init__(self):
        self.files = [2004, 2005, 2006, 2007, 2008, 2009]
        self.maps = {2004: {},
                2005: {},
                2006: {},
                2007: {},
                2008: {},
                2009: {}}
        self.score_timeline = {2004: {},
                2005: {},
                2006: {},
                2007: {},
                2008: {},
                2009: {}}

    def add_score(self, line, year):
        self.maps[year].setdefault(line[0], dict({line[1]: list()}))
        self.maps[year].setdefault(line[1], dict({line[0]: list()}))

        if line[1] in self.maps[year][line[0]]:
            self.maps[year][line[0]][line[1]].append((line[2], line[3]))
        else:
            self.maps[year][line[0]][line[1]] = list((line[2], line[3]))

        if line[0] in self.maps[year][line[1]]:
            self.maps[year][line[1]][line[0]].append((line[3], line[2]))
        else:
            self.maps[year][line[1]][line[0]] = list((line[3], line[2]))

    def add_score_timeline(self, line, year):
        self.score_timeline[year].setdefault(line[0], list())
        self.score_timeline[year].setdefault(line[1], list())

        self.score_timeline[year][line[0]].append((line[2], line[3]))
        self.score_timeline[year][line[1]].append((line[3], line[2]))

    def parse(self):        
        for year in self.files:
            fd = open('data/matches'+str(year)+'.dat')
            fd.seek(0)
            for line in fd.readlines():
                line_split = line.split(' ')
                self.add_score([int(i) for i in line_split], year)
                self.add_score_timeline([int(i) for i in line_split], year)

        maps_f = open('data/matches.pkl', 'wb')
        pickle.dump(self.maps, maps_f)
        maps_f.close()
        score_timeline_f = open('data/score_timeline.pkl', 'wb')
        pickle.dump(self.score_timeline, score_timeline_f)
        score_timeline_f.close()
                
                
                

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# orakel debakel - the revenge

import sys
import random
import cPickle as pickle
import db
import random

DEBUG = 0

class Main:
    def __init__(self):
        # nur zum testen
        self.parser = db.Parser()
        self.parser.parse()

        self.pred = Predictor()
        self.data = db.Data()

    def main(self):
      # sys args
      if len(sys.argv) != 3:
         print 'Usage: ' + sys.argv[0] + ' --predict <gameday> < input'
         print 'Usage: ' + sys.argv[0] + ' --verify <gameday> < input'
         sys.exit(1)
      else:
         mode = sys.argv[1]
         gameday = int(sys.argv[2])
         #val = float(sys.argv[3])

      input = sys.stdin.readlines()

      if mode == '--predict':
         # calculate every match
         for i in input:
            match = i.strip('\n').split(' ')
            self.generate_prediction(match)

      # verify last gameday and enter scores to database
      elif mode == '--verify':
         for i in input:
             match = i.strip('\n')
             self.new_scores(match, gameday)

      else:
         print >> sys.stderr, '\033[1;31mError:\033[1;m Arguments not recognized.'


    def generate_prediction(self, teams):
        pair = [int(t) for t in teams]
        self.pred.predict2(pair)

    # add new scores and recalculate the stats
    def new_scores(self, line, gameday):
        if self.data.insert_data(line, gameday):
            self.data.pickle()
        else:
            print >> sys.stderr, '\033[1;31mError:\033[1;m This match is already inserted.'

class Predictor:
    def __init__(self):
        self.d = db.Data()
        self.meta = db.Meta()
        self.current_year = self.meta.current_year

        self.pres = [[0,0], [1,0], [0,1], [1,1], [2,0], [2,1], [1,2], [0,2], [2,2], [3,0], [0,3], [3,1], [1,3], [3,2], [2,3]]
        self.pres_home = [[0,0], [1,0],[1,0], [1,1], [2,0], [2,1],[2,1], [2,2]]#[3,0], [3,1], [3,2]]
        self.pres_away = [[0,0], [0,1],[0,1], [1,1], [0,2], [1,2],[1,2], [2,2]]# [0,3], [1,3], [2,3]]
        self.pres_win = [[1,0], [2,0], [2,1], [3,0], [3,1], [3,2]]
        self.pres_loss = [[0,1], [0,2], [1,2], [0,3], [1,3], [2,3]]


    # bisher der beste, aber zuviel random
    def predict(self, teams):
        t1, t2 = teams[0], teams[1]

        # ratio geht ab!
        cmpr = self.d.compare_teams(t1, t2, 3, 0.4)
        if cmpr == 1:
            res = random.sample(self.pres_home, 1)[0]
        elif cmpr == -1:
            res = random.sample(self.pres_away, 1)[0]
        else:
            res = random.sample([[0,0], [1,1]], 1)[0]

        self.print_scores(t1, t2, res)

    # wie predict, aber mit mehr history (eternal_diff?)
    def predict2(self, teams, th1=0.3, th2=1.5, th3=0.5):
        t1, t2 = teams[0], teams[1]

        #optimize
        # th1: ab welchen torabstand wieviel tore abziehen (1 oder 2)
        # th2: ab wieviel toren für offensiv starke teams +0.5
        # th3: common scores grenze bei cmpr -0

        cmpr = self.d.compare_teams(t1, t2, 4, 0.4)
        if cmpr == 1:
            g1_self = self.d.get_homegoals_avg(t1) # macht g1 bei sieg
            g1_other = self.d.get_awaygoals_avg(t2) # bekommt g2 bei niederlage
            g1 = g1_self + g1_other / 2.0
            if g1_self >= th2:
                g1 = g1 + 0.5

            # tordifferenz 1 oder 2? oder doch unentschieden?
            avg1 = self.d.get_homegoals_avg(t1)
            avg2 = self.d.get_homegoals_avg(t2)
            diff = abs(avg1 - avg2)

            if diff > th1:
                g2 = g1-2
            else:
                g2 = g1-1
            if g2 < 0: g2 = 0

            g1 = round(g1,3)
            g2 = round(g2,3)
        elif cmpr == -1:
            g2_self = self.d.get_homegoals_avg(t2) # macht g1 bei sieg
            g2_other = self.d.get_awaygoals_avg(t1) # bekommt g2 bei niederlage
            g2 = g2_self + g2_other / 2.0
            if g2_self >= th2:
                g2 = g2 + 0.5

            # tordifferenz 1 oder 2? oder doch unentschieden?
            avg1 = self.d.get_homegoals_avg(t1)
            avg2 = self.d.get_homegoals_avg(t2)
            diff = abs(avg1 - avg2)

            if diff > th1:
                g1 = g2 - 2.0
            else:
                g1 = g2 - 1.0
            if g1 < 0: g1 = 0

            g1 = round(g1,3)
            g2 = round(g2,3)
        else:
            # common scores vergleichen
            av = self.d.pairaverage(t1,t2)
            diff = abs(av[0] - av[1])            
            if diff > th3:                
                res = list(self.d.median(self.d.pairscores(t1,t2))[0])
                g1 = res[0]
                g2 = res[1]
            else:
                res = random.sample([[0,0], [1,1]], 1)[0]
                g1 = res[0]
                g2 = res[1]
                
            g1 = round(g1,3)
            g2 = round(g2,3)

        if DEBUG: print cmpr
        self.print_scores(t1, t2, [g1,g2])


    # TODO: code vom letzten jahr auch submitten?

    def print_scores(self, t1, t2, score):
        if DEBUG:
            print t1, t2, int(score[0]), int(score[1]), '('+str(score[0]),str(score[1])+')'
            print '-------------------'
        else:
            print t1, t2, int(score[0]), int(score[1])

if __name__ == '__main__':
   m = Main()
   m.main()

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
        if len(sys.argv) != 3:
            print 'Usage: ' + sys.argv[0] + ' --predict <gameday> < input'
            print 'Usage: ' + sys.argv[0] + ' --verify <gameday> < input'
            sys.exit(1)
        else:
            try:
                mode = sys.argv[1]
                gameday = int(sys.argv[2])
            except:
                mode = '--predict'
                gameday = 1
            
        input = sys.stdin.readlines()

        if mode == '--predict':
            for i in input:
                match = i.strip('\n').split(' ')
                pair = [int(t) for t in match]
                self.pred.predict(pair)

        elif mode == '--predict2':
            for i in input:
                match = i.strip('\n').split(' ')
                pair = [int(t) for t in match]
                self.pred.predict2(pair)

        elif mode == '--predict3':
            for i in input:
                match = i.strip('\n').split(' ')
                pair = [int(t) for t in match]
                self.pred.predict3(pair)

        # verify last gameday and enter scores to database
        elif mode == '--verify':
            for i in input:
                match = i.strip('\n')
                self.new_scores(match, gameday)

        else:
            print >> sys.stderr, '\033[1;31mError:\033[1;m Arguments not recognized.'

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


    # too much random, but not bad (and simple)
    def predict2(self, teams):
        t1, t2 = teams[0], teams[1]

        cmpr = self.d.compare_teams(t1, t2, 3, 0.4)
        if cmpr == 1:
            res = random.sample(self.pres_home, 1)[0]
        elif cmpr == -1:
            res = random.sample(self.pres_away, 1)[0]
        else:
            res = random.sample([[0,0], [1,1]], 1)[0]

        self.print_scores(t1, t2, res)

    # wie predict, aber mit mehr history (eternal_diff?)
    # 0.3 1.4 0.5
    def predict(self, teams, th1=1.0, th3=0.0):
        t1, t2 = teams[0], teams[1]

        #optimize
        # th1: ab welchen torabstand wieviel tore abziehen (1 oder 2)
        # th2: ab wieviel toren für offensiv starke teams +0.5
        # th3: common scores grenze bei cmpr 0

        cmpr = self.d.compare_teams(t1, t2, 4, 0.4)
        if cmpr == 1:
            g1_self = self.d.get_homegoals_avg(t1)
            g1_other = self.d.get_awaygoals_avg(t2)
            g1 = g1_self + g1_other / 2.0

            # score diff 1 or 2?
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
            g2_self = self.d.get_homegoals_avg(t2)
            g2_other = self.d.get_awaygoals_avg(t1)
            g2 = g2_self + g2_other / 2.0

            # score diff 1 or 2?
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
            # compare common scores
            av = self.d.pairaverage(t1,t2)
            diff = abs(av[0] - av[1])
            if diff >= th3:
                median = self.d.median(self.d.pairscores(t1,t2))
                if median:
                    res = list(median[0])
                    if DEBUG: print '\033[1;31m'+str(res)+'\033[1;m'
                else:
                    # todo: ergebnis überlegen
                    res = [1,0]
                g1 = res[0]
                g2 = res[1]                    
            else:
                #res = random.sample([[0,0], [1,1]], 1)[0]
                #res = self.d.pairaverage(t1, t2)
                results = self.d.medianlist_all(self.d.pairscores(t1, t2))
                res = [1,1]
                for r in results:
                    if r[0][0] == r[0][1]:
                        res[0], res[1] = r[0][0], r[0][1]
                        break

                if DEBUG: print '\033[1;31m'+str(res)+'\033[1;m'
                g1 = res[0]
                g2 = res[1]

            g1 = round(g1,3)
            g2 = round(g2,3)

        if DEBUG: print cmpr
        self.print_scores(t1, t2, [g1,g2])

    # complete random
    def predict3(self, teams):
        t1, t2 = teams[0], teams[1]
        res = random.sample(self.pres, 1)[0]
        self.print_scores(t1, t2, res)

    def print_scores(self, t1, t2, score):
        if DEBUG:
            print t1, t2, int(score[0]), int(score[1]), '('+str(score[0]),str(score[1])+')'
            print '-------------------'
        else:
            print t1, t2, int(score[0]), int(score[1])

if __name__ == '__main__':
   m = Main()
   m.main()

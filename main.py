#!/usr/bin/env python
# -*- coding: utf-8 -*-
# orakel debakel - the revenge

import sys
import random
import cPickle as pickle
import db

DEBUG = 1

class Main:
    def __init__(self):
        self.pred = Predictor()
        self.data = db.Data()

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
        # call predictor here
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
        self.pres_home = [[0,0], [1,0], [1,1], [2,0], [2,1], [2,2], [3,0], [3,1], [3,2]]
        self.pres_away = [[0,0], [0,1], [1,1], [0,2], [1,2], [2,2], [0,3], [1,3], [2,3]]
        self.pres_win = [[1,0], [2,0], [2,1], [3,0], [3,1], [3,2]]

    # tendenz und allg. stärke
    # this is officialy declared as BULLSHIT!
    def predict(self, teams):
        t1, t2 = teams[0], teams[1]

        # compare
        cmpr = self.d.compare_teams(t1, t2)

        # eternal ladder
        t1_score, t2_score = self.d.eternal_ladder[t1], self.d.eternal_ladder[t2]
        ratio = t1_score / float(t2_score)
        if ratio > 1.0:
            et_cmp = 1
        else:
            et_cmp = -1
            
        # offense/defense
        t1_off, t1_def = self.d.get_homegoals_sum(t1), self.d.get_awaygoals_sum(t1)
        if t1_def:
            t1_gr = t1_off / float(t1_def)
        else:
            t1_gr = 0
        t2_off, t2_def = self.d.get_homegoals_sum(t2), self.d.get_awaygoals_sum(t2)
        if t2_def:
            t2_gr = t2_off / float(t2_def)
        else:
            t2_gr = 0
        gr_diff = t1_gr - t2_gr

        threshold = 0.4
        if  gr_diff > threshold:
            off_def_cmp = 1
        elif gr_diff <= threshold and gr_diff > (-1*threshold):
            off_def_cmp = 0
        else:
            off_def_cmp = -1

        # avg goals
        g1_avg = (round(self.d.get_homegoals_avg(t1), 3), round(self.d.get_awaygoals_avg(t1),3))
        g2_avg = (round(self.d.get_homegoals_avg(t2), 3), round(self.d.get_awaygoals_avg(t2), 3))

        print self.d.names[t1], self.d.names[t2]
        print 'cmpr', cmpr, 'off_def_cmp', off_def_cmp, 'et_cmp', et_cmp, 'goals', g1_avg, ':', g2_avg

        # falls cmpr 0, und noch ein weitres 0 -> unentschieden
        # falls cmpr 1, und ein weiteres 1, -> sieg heim
        # falls cmpr -1 und ein weitres -1 -> sieg gast


    # median als basis
    def predict2(self, teams):
        t1, t2 = teams[0], teams[1]

        # 1. basis
        t1_median = self.d.get_median(t1)
        t2_median = self.d.get_median(t2)
        t1_mres = []
        for res in t1_median:
            t1_mres.append(res[0])
        t2_mres = []
        for res in t2_median:
            t2_mres.append(res[0])

        # 2. aktuelle leistung
        t1_recent = self.d.get_timeline(t1, self.current_year)[-3:]
        t2_recent = self.d.get_timeline(t2, self.current_year)[-3:]        
        
        # häufigstes gemeinsames ergebnis
        match = 0
        for res in t1_mres:
            if res in t2_mres:
                match = res
                break
            else:
                continue
        if not match:
            match = t1_mres[0]
        match = list(match) # zur liste casten

        # trend
        t1_trend = self.d.get_trend(t1)
        t2_trend = self.d.get_trend(t2)
        trend = t1_trend -t2_trend
        if trend == 0:
            pass # keine änderung
        elif trend == 1:
            match[0]+=1
        elif trend == 2 :
            match[0]+= 1
            match[1]-= 1
        elif trend == -1:
            match[1]+= 1
        elif trend == -2:
            match[0]-= 1
            match[1]+= 1

        
        # und ab damit
        self.print_scores(t1, t2, match)    

    def print_scores(self, t1, t2, score):
        print t1, t2, score[0], score[1]
            
            
if __name__ == '__main__':
   m = Main()
   m.main()

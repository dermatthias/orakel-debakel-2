#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import cPickle as pickle
from suds.client import Client

class Meta:
    '''
    set years and other vars for a new season here
    raw year data must be done manually (for now)
    '''
    def __init__(self):
        self.matches_file = 'data/matches.pkl'
        self.timelime_file = 'data/score_timeline.pkl'
        self.years = [2004, 2005, 2006, 2007, 2008, 2009]
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


class Data:
    def __init__(self):
        # unpickle data
        meta = Meta()
        self.years = meta.years
        self.maps = meta.maps
        self.matches_file = meta.matches_file
        self.timeline_file = meta.timelime_file
        self.cross_table = 0
        self.score_timeline = 0


    def unpickle(self):
        matches_f = open(self.matches_file, 'rb')
        self.cross_table = pickle.load(matches_f)
        matches_f.close()

        timelime_f = open(self.timeline_file, 'rb')
        self.score_timeline = pickle.load(timelime_f)
        timelime_f.close()

    def get_all_goals(self, team):
        pass

    def get_timelime(self, team):
        pass

    # entweder reines ergebnis oder 1, 0, -1 (aus sicht des heimteams)
    def compare_teams(self, team1, team2):
        pass

    


class Parser:
    def __init__(self):
        meta = Meta()
        self.years = meta.years
        self.maps = meta.maps
        self.score_timeline = meta.score_timeline
        self.matches_file = meta.matches_file
        self.timeline_file = meta.timelime_file

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
        for year in self.years:
            fd = open('data/matches'+str(year)+'.dat')
            fd.seek(0)
            for line in fd.readlines():
                line_split = line.split(' ')
                self.add_score([int(i) for i in line_split], year)
                self.add_score_timeline([int(i) for i in line_split], year)

        maps_f = open(self.matches_file, 'wb')
        pickle.dump(self.maps, maps_f)
        maps_f.close()
        score_timeline_f = open(self.timelime_file, 'wb')
        pickle.dump(self.score_timeline, score_timeline_f)
        score_timeline_f.close()


class LigaDB:
    def __init__(self):
        self.url = 'http://www.openligadb.de/Webservices/Sportsdata.asmx?WSDL'
        self.client = Client(self.url)
        self.league = 'bl1'

        ## sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        ## fd = sys.stdout
        
        meta = Meta()
        self.years = meta.years

    def getScores(self, year, min=1, max=34):
        for st in range(min, max+1):
            result = self.client.service.GetMatchdataByGroupLeagueSaison(st, self.league, year)
            for spiel in result[0][:]:
                id1 = spiel.idTeam1
                pt1 = spiel.pointsTeam1
                id2 = spiel.idTeam2
                pt2 = spiel.pointsTeam2
                if pt1 == -1:
                    print str(id1) + ' ' + str(id2)
                else:
                    print str(id1) + ' ' + str(id2)  + ' ' + str(pt1) + ' ' + str(pt2)

    def getAllScores(self):
        for y in self.years:
            self.getScores(y)


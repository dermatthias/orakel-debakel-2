#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import codecs
import random
import cPickle as pickle
from suds.client import Client
from operator import itemgetter


'''
TODO:
 - create ladder for current season
 - use eternal ladder?
 - daten der aufsteiger aus 2. liga!!!
'''

class Meta:
    '''
    set years and other vars for a new season here
    raw year data must be done manually (for now)
    '''
    def __init__(self):
        self.matches_file = 'data/matches.pkl'
        self.timeline_file = 'data/score_timeline.pkl'
        self.current_year = 2010
        self.years = [2004, 2005, 2006, 2007, 2008, 2009]
        self.maps = {2004: {},
                     2005: {},
                     2006: {},
                     2007: {},
                     2008: {},
                     2009: {},
                     2010: {}}
        self.score_timeline = {2004: {},
                               2005: {},
                               2006: {},
                               2007: {},
                               2008: {},
                               2009: {},
                               2010: {}}


class Data:
    def __init__(self):
        meta = Meta()
        self.current_year = meta.current_year
        self.years = meta.years
        self.matches_file = meta.matches_file
        self.timeline_file = meta.timeline_file
        self.cross_table = 0
        self.score_timeline = 0

        self.names = {65: '1. FC Köln',123: '1899 Hoffenheim',83: 'Arminia Bielefeld',6: 'Bayer Leverkusen',87: 'Bor. Mönchengladbach',7: 'Bor. Dortmund',91: 'Eintracht Frankfurt',93: 'Energie Cottbus',40: 'FC Bayern München',9: 'FC Schalke 04',100: 'Hamburger SV',55: 'Hannover 96',54: 'Hertha BSC',105: 'Karlsruher SC',16: 'VfB Stuttgart',129: 'VfL Bochum',131: 'VfL Wolfsburg',134: 'Werder Bremen',79: '1. FC Nürnberg',102: 'Hansa Rostock',107: 'MSV Duisburg',81: '1. FSV Mainz 05',23: 'Alemannia Aachen',76: '1. FC Kaiserslautern',112: 'SC Freiburg', 98: 'FC St. Pauli'}

        self.eternal_ladder = {65: 159, 123: 175, 83: 181, 6: 260, 87: 165, 7: 244, 91: 185, 93: 167, 40: 355, 9: 306 ,100: 279, 55: 216, 54: 257, 105: 162, 16: 287, 129: 183, 131: 242, 134: 306, 79: 191, 102: 150, 107: 146, 81: 175, 23: 154, 76: 165, 112: 138, 98: 145}

        self.unpickle()


    def unpickle(self):
        matches_f = open(self.matches_file, 'rb')
        self.cross_table = pickle.load(matches_f)
        matches_f.close()

        timeline_f = open(self.timeline_file, 'rb')
        self.score_timeline = pickle.load(timeline_f)
        timeline_f.close()

    def pickle(self):
        matches_f = open(self.matches_file, 'wb')
        pickle.dump(self.cross_table, matches_f)
        matches_f.close()
        score_timeline_f = open(self.timeline_file, 'wb')
        pickle.dump(self.score_timeline, score_timeline_f)
        score_timeline_f.close()

    def insert_data(self, line, gameday):
        match = [int(i) for i in line.split(' ')]

        # timeline
        self.score_timeline[self.current_year].setdefault(match[0], list())
        self.score_timeline[self.current_year].setdefault(match[1], list())

        # check if gameday already in db (after .setdefault!)
        if len(self.score_timeline[self.current_year][match[0]]) >= gameday:
            # error, gameday already inserted
            return False

        self.score_timeline[self.current_year][match[0]].append((match[2], match[3]))
        self.score_timeline[self.current_year][match[1]].append((match[3], match[2]))

        # cross table
        self.cross_table[self.current_year].setdefault(match[0], dict({match[1]: list()}))
        self.cross_table[self.current_year].setdefault(match[1], dict({match[0]: list()}))


        if match[1] in self.cross_table[self.current_year][match[0]]:
            self.cross_table[self.current_year][match[0]][match[1]].append([match[2], match[3]])
        else:
            self.cross_table[self.current_year][match[0]][match[1]] = [[match[2], match[3]]]

        if match[0] in self.cross_table[self.current_year][match[1]]:
            self.cross_table[self.current_year][match[1]][match[0]].append([match[3], match[2]])
        else:
            self.cross_table[self.current_year][match[1]][match[0]] = [[match[3], match[2]]]


        return True

    # returns a list of all scores by given team
    def get_all_goals(self, team):
        all_goals = []
        for year, matches in self.cross_table.iteritems():
            try:
                for enemy, scores in matches[team].iteritems():
                    all_goals.append(scores[0])
                    all_goals.append(scores[1])
            except:
                continue # if no goals are found
        return all_goals

    def get_median(self, team, count=4):
        goals = self.get_all_goals(team)
        d = {}
        for match in goals:
            d.setdefault(tuple(match), 0)
            d[tuple(match)] +=1

        sorted_by_goals = sorted(d.items(), key=itemgetter(1), reverse=True)
        return sorted_by_goals[:count]

    def get_homegoals_sum(self, team):
        home_sum = sum([g[0] for g in self.get_all_goals(team)])
        return home_sum

    def get_homegoals_avg(self, team):
        home_sum = sum([g[0] for g in self.get_all_goals(team)])
        if len(self.get_all_goals(team)):
            return home_sum / float(len(self.get_all_goals(team)))
        else:
            return 0

    def get_awaygoals_sum(self, team):
        away_sum = sum([g[1] for g in self.get_all_goals(team)])
        return away_sum

    def get_awaygoals_avg(self, team):
        away_sum = sum([g[1] for g in self.get_all_goals(team)])
        if len(self.get_all_goals(team)):
            return away_sum / float(len(self.get_all_goals(team)))
        else:
            return 0

    # returns a score timeline for each year
    def get_timeline(self, team, year):
        try:
            tl = self.score_timeline[year][team]
        except:
            tl = []
        return tl

    def get_trend_ratio(self, team, timespan=3, year=2010):
        games = self.get_timeline(team, year)[-timespan:]
        if not games:
            games = self.get_timeline(team, year-1)[-timespan:]
        points = 0
        for game in games:
            if game[0]>game[1]:
                points+=3
            elif game[0]==game[1]:
                points+=1

        return points / float(timespan)

    def get_trend(self, team, timespan=3, year=2010, threshold=0.5):
        ratio = self.get_trend_ratio(team, timespan, year)

        # TODO ratio threshold could be optimized
        if ratio >= (1.0+threshold):
            return (1, ratio)
        elif ratio < (1.0+threshold) and ratio >= (0.4+threshold):
            return (0, ratio)
        else:
            return (-1, ratio)


    # entweder reines ergebnis oder 1, 0, -1 (aus sicht des heimteams)
    def compare_teams(self, team1, team2, timespan=3, threshold=0.5):
        r1 = self.get_trend(team1, timespan, self.current_year, threshold)[0]
        r2 = self.get_trend(team2, timespan, self.current_year, threshold)[0]
        if r1 > r2:
            return 1
        elif r1 == r2:
            return 0
        else:
            return -1

    def eternal_diff(self, team1, team2, diff_thresh=50):
        #sorted(d.eternal_ladder.items(), key=operator.itemgetter(1), reverse=True)
        diff = self.eternal_ladder[team1] - self.eternal_ladder[team2]
        if diff > diff_thresh:
            return 1
        elif diff < (-1*diff_thresh):
            return -1
        else:
            return 0

    # common results of both teams
    def pairscores(self, team1, team2):
        all_games = []
        for year, matches in self.cross_table.iteritems():
            try:
                res = matches[team1][team2]
                for r in res:
                    all_games.append(r)
            except:
                pass
        return all_games

    def pairaverage(self, team1, team2):
        s1, s2 = 0, 0
        scores = self.pairscores(team1, team2)
        for match in scores:
            s1 += match[0]
            s2 += match[1]
        if len(scores):
            s1 = s1 / float(len(scores))
            s2 = s2 / float(len(scores))
        else:
            s1 = 0.0
            s2 = 0.0

        return [s1, s2]

    def medianlist(self, scorelist):
        d = {}
        for i in scorelist:
            d.setdefault(tuple(i), 0)
            d[tuple(i)] +=1

        sorted_by_goals = sorted(d.items(), key=itemgetter(1), reverse=True)
        if sorted_by_goals:
            best_count = sorted_by_goals[0][1]
            candidates = []
            for e in sorted_by_goals:
                if e[1] == best_count:
                    candidates.append(e)
        else:
            best_count = 0
            candidates = []
        return candidates

    def medianlist_all(self, scorelist):
        d = {}
        for i in scorelist:
            d.setdefault(tuple(i), 0)
            d[tuple(i)] +=1

        return sorted(d.items(), key=itemgetter(1), reverse=True)

    def median(self, scorelist):
        candidates =  self.medianlist(scorelist)
        # take the smallest one
        if candidates:
            res = sorted(candidates)
            return res[0]
        else:
            return []

class Parser:
    def __init__(self):
        meta = Meta()
        self.years = meta.years
        self.maps = meta.maps
        self.score_timeline = meta.score_timeline
        self.matches_file = meta.matches_file
        self.timeline_file = meta.timeline_file

    def add_score(self, line, year):
        self.maps[year].setdefault(line[0], dict({line[1]: list()}))
        self.maps[year].setdefault(line[1], dict({line[0]: list()}))

        if line[1] in self.maps[year][line[0]]:
            self.maps[year][line[0]][line[1]].append([line[2], line[3]])
        else:
            self.maps[year][line[0]][line[1]] = [[line[2], line[3]]]

        if line[0] in self.maps[year][line[1]]:
            self.maps[year][line[1]][line[0]].append([line[3], line[2]])
        else:
            self.maps[year][line[1]][line[0]] = [[line[3], line[2]]]

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
        score_timeline_f = open(self.timeline_file, 'wb')
        pickle.dump(self.score_timeline, score_timeline_f)
        score_timeline_f.close()


class LigaDB:
    def __init__(self):
        self.url = 'http://www.openligadb.de/Webservices/Sportsdata.asmx?WSDL'
        self.client = Client(self.url)
        self.league = 'bl1'

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


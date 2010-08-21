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

        # fertig machen!
        # die ersten drei werte nehmen und wie unten verwenden, über durchschnttstore dann das ergebnis aus sicht des gewinners berechnen. (das erste bestimmt den sieger, das zweite doie tore)
        
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
        #t1_recent = self.d.get_timeline(t1, self.current_year)[-3:]
        #t2_recent = self.d.get_timeline(t2, self.current_year)[-3:]

        # häufigstes gemeinsames ergebnis
        def most_common():
            match = 0
            for res in t1_mres:
                if res in t2_mres:
                    match = res
                    break
                else:
                    continue
            if not match:
                match = t1_mres[0]
            return list(match) # zur liste casten

        # ein zufälliges der häufigsten 4
        def rand_common():
            if t1_mres and t2_mres:
                res1 = random.sample(t1_mres, 1)[0]
                res2 = random.sample(t2_mres, 1)[0]
            else:
                res1 = random.sample(self.pres, 1)[0]
                res2 = random.sample(self.pres, 1)[0]

            # vereinigen
            hgoals = int(round(res1[0]+res2[0] / 2.0))
            agoals = int(round(res1[1]+res2[1] / 2.0))

            # falls unentschieden
            if hgoals == agoals:
                cmpr = self.d.compare_teams(t1, t2)
                if cmpr == 1:
                    hgoals+= 1
                elif cmpr == -1:
                    agoals+= 1

            return [hgoals, agoals]

        match = rand_common()
        #match = most_common()


        # trend
        t1_trend = self.d.get_trend(t1)
        t2_trend = self.d.get_trend(t2)
        trend = t1_trend -t2_trend
        if trend == 0:
            # if random.randint(0,1) and match[0] > 0:
            #     match[0]-=1
            # if random.randint(0,1) and match[1] > 0:
            #     match[1]-=1
            pass
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

        # allgemeines ranking
        diff = self.d.eternal_diff(t1, t2)
        if diff == 1 and match[0] < match[1]:
            match[0]+= 1
        elif diff == -1 and match[0] > match[1]:
            match[1]+= 1

        # und ab damit
        self.print_scores(t1, t2, match)


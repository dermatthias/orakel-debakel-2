#!/usr/bin/env python
# -*- coding: utf-8 -*-
from suds.client import Client
import sys, codecs

def main():
    # stdout oder fileoutput
    if len(sys.argv) == 4:
        fd = codecs.open(sys.argv[3], mode='w', encoding='latin-1')
    elif len(sys.argv) == 3:
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)
        fd = sys.stdout
    
    # soap kram
    url = 'http://www.openligadb.de/Webservices/Sportsdata.asmx?WSDL'
    client = Client(url)

    # vars
    spieltage = int(sys.argv[1])
    jahr = int(sys.argv[2])
    liga = 'bl1'

    # daten lesen
    for st in range(1, 35):
        result = client.service.GetMatchdataByGroupLeagueSaison(st, liga, jahr)
        #fd.write(str(st) + '\n')
        for spiel in result[0][:]:
            id1 = spiel.idTeam1
            pt1 = spiel.pointsTeam1
            id2 = spiel.idTeam2
            pt2 = spiel.pointsTeam2
            if pt1 == -1:
                fd.write(str(id1) + ' ' + str(id2) + '\n')
            else:
                fd.write(str(id1) + ' ' + str(id2)  + ' ' + str(pt1) + ' ' + str(pt2) + '\n')
        #fd.write('\n')
# main call und argumente prüfen
if __name__ == "__main__":
    if len(sys.argv) not in (3,4):
        sys.exit("Usage: " +sys.argv[0]+ " <spieltage> <jahr> [<outfile>]")
    else:
        if int(sys.argv[1]) not in range(1,35):
            sys.exit("Wert für <spieltage> ist quatsch.")
        elif int(sys.argv[2]) not in range(2002, 2011):
            sys.exit("Wert für <jahr> ist quatsch.")
        else:
            main()

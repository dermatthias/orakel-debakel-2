#include<stdlib.h>
#include<time.h>
#include<cassert>
#include<sstream>
#include<cstdlib>
#include<iostream>
#include<fstream>
#include<map>
#include<string>
#include<cstring>

using namespace std;

typedef pair<int,int> Opponents;
typedef pair<int,int> Result;
typedef map<Opponents,Result> Matches;


void errusage() {
		cerr << "usage: judge <prediction> <results> [ --points OR --correct OR --difference OR --winner ]" << endl; exit(0);
}


	void readresults(Matches& matches, istream& file) {
//		cerr << "reading " << filename << " ... " << endl;
//		ifstream file;
//  	file.open(filename.c_str());
		matches.clear();
		int team1,team2,goals1,goals2;
		while (!file.eof()) {
			file >> team1 >> team2 >> goals1 >> goals2 >> ws;
			matches[Opponents(team1,team2)]=Result(goals1,goals2);
		}
		// file.close();
		// cerr << matches.size() << " Matches imported" << endl;
	}

	void judge(char* pred, char* res, int& points, int& correct, int& diff, int& winner) {
		Matches predictions,results;
		ifstream file; file.open(pred);
		readresults(predictions,file);
		file.close();
		file.open(res);
		readresults(results,file);
		file.close();
		points=correct=diff=winner=0;
		for (Matches::iterator it=predictions.begin(); it!=predictions.end(); it++) {
			if (it->second == results[it->first]) { correct++; points+=10; continue; }	
			if (it->second.first - it->second.second == results[it->first].first - results[it->first].second) { 
				diff++; 
				points+=6+max(0,3-abs(it->second.first-results[it->first].first));
				continue;
			}
			if ((it->second.first > it->second.second) && (results[it->first].first > results[it->first].second))
			{ winner++; points+=5; continue; }
			if ((it->second.first < it->second.second) && (results[it->first].first < results[it->first].second)) 
			{ winner++; points+=5; continue; }
		}
	}

int main(int argc, char* argv[]) {
	if (argc!=4) errusage();
	int points, diff, correct, winner;
	judge(argv[1],argv[2],points,correct,diff,winner);
	if (!strcmp(argv[3],"--points")) cout << points << endl;
	else if (!strcmp(argv[3],"--correct")) cout << correct << endl;
	else if (!strcmp(argv[3],"--difference")) cout << diff << endl;
	else if (!strcmp(argv[3],"--winner")) cout << winner << endl;
	else errusage();
}

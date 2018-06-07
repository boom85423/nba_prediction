import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import math
import warnings
import sys

def predict(team):
    '''Get predicted total score about 1st score.
       Input must be a string about team'''
    lm = LinearRegression()
    x = nba['1st']
    y = nba['total']
    lm.fit(np.reshape(x, (len(x),1)), np.reshape(y, (len(y),1)))
    y1 = int(lm.predict(int(nba_dict[team]))[0][0])
    return y1

def get_scatter(team):
    nba = pd.read_csv("/Users/kevin102575/Desktop/recent.csv")    
    x = nba['1st']
    y = nba['total']
    lm = LinearRegression()    
    lm.fit(np.reshape(x, (len(x),1)), np.reshape(y, (len(y),1)))
    plt.figtext(0.5, 1, team)       
    plt.scatter(x, y, color='black')
    plt.plot(x, lm.predict(np.reshape(x, (len(x), 1))), color='blue', linewidth=3)
    plt.plot(int(nba_dict[team]), predict(team), color = 'red', marker = '^', markersize = 10)
    plt.show()

def get_performance():
    '''Get the MSE and r squared about the regression model'''
    nba = pd.read_csv("/Users/kevin102575/Desktop/recent.csv")    
    x = np.reshape(nba['1st'], (len(nba['1st']),1))
    y = np.reshape(nba['total'], (len(nba['total']),1))
    lm = LinearRegression()
    lm.fit(np.reshape(x, (len(x),1)), np.reshape(y, (len(y),1)))    
    rmse = math.sqrt(np.mean((lm.predict(x) - y) ** 2))
    r_squared = lm.score(x, y)
    print("rmse :", rmse)
    print("r_squared :", r_squared)

def get_1st(year_month_day):
    '''Get information about score in dictionary format'''
    date = str(year_month_day)
    url = "http://www.espn.com/nba/scoreboard/_/date/" + date
    driver = webdriver.PhantomJS(executable_path="/Users/kevin102575/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs")
    driver.get(url)
    PageSource = driver.page_source
    soup = BeautifulSoup(PageSource, 'html5lib')
    nba_away_1st = []
    nba_home_1st = []
    nba_away_total = []
    nba_home_total = []
    nba_away_name = []
    nba_home_name = []
    
    #nba_away_1st
    away = soup.find_all("tr", {"class":"away"})
    try:
        #correct date or coming soon
        assert len(away) > 0
        away_score = []
        #out if index
        for i in range(len(away)):
            away_score.append(away[i].find_all("td",{"class":"score"}))
            nba_away_name.append(away[i].find("span", {"class":"sb-team-abbrev"}).text)
        away_1st = []
        for i in range(len(away_score)):
            away_1st.append(away_score[i][0].text)
        for i in away_1st:
            nba_away_1st.append(i)

        #nba_home_1st
        home = soup.find_all("tr", {"class":"home"})
        home_score = []
        for i in range(len(home)):
            home_score.append(home[i].find_all("td",{"class":"score"}))
            nba_home_name.append(home[i].find("span", {"class":"sb-team-abbrev"}).text)
        home_1st = []
        for i in range(len(home_score)):
            home_1st.append(home_score[i][0].text)
        for i in home_1st:
            nba_home_1st.append(i)

        #nba_away_total
        away_total = []
        for i in range(len(away)):
            away_total.append(away[i].find("td",{"class":"total"}).text)
        for i in away_total:
            nba_away_total.append(i)

        #nba_home_total
        home_total = []
        for i in range(len(home)):
            home_total.append(home[i].find("td",{"class":"total"}).text)
        for i in home_total:
            nba_home_total.append(i)

        name = nba_away_name + nba_home_name
        score = nba_away_1st + nba_home_1st
        nba_dict = {}
        for i, j in zip(name, score):
            nba_dict[i] = j
        return nba_dict, nba_away_1st, nba_home_1st, nba_away_total, nba_home_total, nba_away_name, nba_home_name
    except AssertionError:
        print("No game on this date")
    except IndexError:
        print("Coming soon")

def update_csv(nba_away_1st, nba_home_1st, nba_away_total, nba_home_total, nba_away_name, nba_home_name):
    nba = pd.read_csv("/Users/kevin102575/Desktop/recent.csv")
    x_csv = list(nba["1st"])
    y_csv = list(nba["total"])
    name_csv = list(nba["name"])
    x = x_csv + nba_away_1st + nba_home_1st
    y = y_csv + nba_away_total + nba_home_total
    name = name_csv + nba_away_name + nba_home_name
    data = {"1st":x, "total":y, "name":name}
    nba = pd.DataFrame(data)
    nba.to_csv("/Users/kevin102575/Desktop/recent.csv")

def get_today():
    '''USA CT time zone'''
    today = str(datetime.now().date())
    today = today.split("-")
    today = today[0]+today[1]+today[2]
    return str(int(today)-1)

def get_winner(team1, team2):
    if predict(team1) > predict(team2):
        print("Winner goes to", team1)
    else:
        print("Winner goes to", team2)

def get_vs():
    for i, j in zip(nba_away_name, nba_home_name):
        print(i, "vs", j)

if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    year_month_day = get_today()
    res = get_1st(year_month_day)
    try:
        assert res != None
        nba_dict = res[0]
        nba_away_1st = res[1]
        nba_home_1st = res[2]
        nba_away_total = res[3]
        nba_home_total = res[4]
        nba_away_name = res[5]
        nba_home_name = res[6]
        get_vs()
        nba = pd.read_csv("/Users/kevin102575/Desktop/recent.csv") 
        print("1st", nba_dict)
        print("------predict------")
        for i in range(len(nba_away_name)):
            print("{0}_total {1}".format(nba_away_name[i], predict(nba_away_name[i])))
        for i in range(len(nba_home_name)):
            print("{0}_total {1}".format(nba_home_name[i], predict(nba_home_name[i])))
        for i in range(len(nba_away_name)):
            get_winner(nba_away_name[i], nba_home_name[i])    
        #get_performance()        
        #get_scatter("CLE")    
    except:
        pass
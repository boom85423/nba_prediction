from bs4 import BeautifulSoup
from selenium import webdriver 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage import data, color, exposure
from skimage.feature import hog
import warnings

def get_score():
    res = soup.find_all("li", {"class":"score"})
    vs = []
    for i in res:
        vs.append(i.text)
    for i in range(len(vs)):
        if "3OT" in vs[i]:
            vs[i] = vs[i].replace("3OT","")
        elif "2OT" in vs[i]:
            vs[i] = vs[i].replace("2OT","")
        elif "OT" in vs[i]:
            vs[i] = vs[i].replace("OT","")
        else:
            continue
    res = soup.find_all("ul", {"class":"game-schedule"})
    result = []
    for i in range(1,len(res),2):
        result.append(res[i].find("li").text)
    score = []
    for i,j in zip(result,vs):
        if i == "W":
            score.append(j.split("-")[0])
        else:
            score.append(j.split("-")[1])
    return score

def get_image(name):
    for i in range(len(score)):
        score[i] = int(score[i])
    game = range(0,len(score))
    data = {"game":game, "score":score}
    df = pd.DataFrame(data)
    df = df.set_index(df["game"])
    del df["game"]
    df.plot(x=df.index, kind="line")
    plt.savefig("/Users/kevin102575/Desktop/"+name+".jpg")

def get_fd(resized_train):
    fds = []
    for i in range(len(resized_train)):
        image = color.rgb2grey(resized_train[i])
        fds.append(hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(2, 2), visualise=True)[0])
    return fds

def mse(fd1, fd2):
    err = np.sum((fd1 - fd2)**2)
    err = err / len(fds[0])
    return err

def get_winner(fds):
    winner = []
    for i in range(1,len(fds)):
        winner.append(mse(fds[0],fds[i]))
    for i,j in zip(teams,winner):
        if j == min(winner):
            return "Winner goes to {}".format(i)

if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    '''
    #2017 GS Postseason
    url = "http://www.espn.com/nba/team/schedule/_/name/gs/year/2017"
    driver = webdriver.PhantomJS(executable_path="/Users/kevin102575/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs")
    driver.get(url)
    PageSource = driver.page_source
    soup = BeautifulSoup(PageSource, 'html5lib')
    score = get_score()
    get_image("gs_2017")
    '''
    gs_2017 = cv2.imread("/Users/kevin102575/Desktop/gs_2017.jpg")
    #Final
    teams = ["cle", "gs"]
    for i in teams:
        url = "http://www.espn.com/nba/team/schedule/_/name/"
        dom = url + i
        driver = webdriver.PhantomJS(executable_path="/Users/kevin102575/Downloads/phantomjs-2.1.1-macosx/bin/phantomjs")
        driver.get(dom)
        PageSource = driver.page_source
        soup = BeautifulSoup(PageSource, 'html5lib')
        score = get_score()
        get_image(i)
    desktop = "/Users/kevin102575/Desktop/"
    file = []
    for i in teams:
        file.append(desktop+i+".jpg")
    photo = [gs_2017]
    for i in file:
        photo.append(cv2.imread(i))
    
    fds = get_fd(photo)
    print("------Minimum the MSE------")
    print("CLE :", mse(fds[0],fds[1]))    
    print("GS :", mse(fds[0],fds[2]))        
    print(get_winner(fds))

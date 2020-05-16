import requests
import numpy
import matplotlib
import time, sys

import matplotlib.pyplot as plt
from matplotlib import dates

TWITCH_API_URL = 'https://api.twitch.tv/v5'
TWITCH_CLIENT_ID = '' # Make sure to add your ClientID from your Twitch Dev Console see : https://dev.twitch.tv/console/apps

timeFrmtr = matplotlib.ticker.FuncFormatter(lambda s, x: time.strftime('%H:%M:%S', time.gmtime(s)))

def analyze(videoId, startTime, endTime, graphType, accuracy):
    """
    Main function, let you choose which kind f graphic you like

    :param int videoId: The videoID from Twitch
    :param int startTime: The start of the part you want to analyze (in seconds)
    :param int endTime: The start of the part you want to analyse (in seconds)
    :param str graphTime: The type of matplotlib you want. Available values : 'hist', 'line'.
    :param int accuracy: The time range (in seconds) in which the part analysed will be divided
    """
    comments, ratings = getComments(videoId, startTime, endTime)

    if graphType == 'hist':
        plotHist(comments, accuracy)
    if graphType == 'line':
        plotLineGraph(ratings, comments)

def getComments(videoId, startTime, endTime):
    path = 'videos/' + str(videoId)
    tag = 'comments?content_offset_seconds=' + str(startTime)
    url = TWITCH_API_URL + '/' + path + '/' + tag
    headers = {'Client-ID': TWITCH_CLIENT_ID}

    lastTime = startTime

    res = []
    ratings = []

    while(lastTime < endTime):
        r = requests.get(url, headers=headers)
        content = r.json()
        comments = content['comments']
        res += comments
        
        lastTime = comments[len(comments) - 1]['content_offset_seconds']
        firstTime = comments[0]['content_offset_seconds']

        ratings.append({
            "rating": len(comments) / (lastTime - firstTime),
            "offset": firstTime + (lastTime - firstTime) / 2
        })

        url = TWITCH_API_URL + '/' + path + '/comments?cursor=' + content['_next']
        
        progressBar((lastTime - startTime) / (endTime - startTime))
    
    return res, ratings

def plotLineGraph(ratings, comments):
    x = []
    y = []
    start = comments[0]['content_offset_seconds']
    end = comments[len(comments) - 1]['content_offset_seconds']

    for rating in ratings:
        x.append(rating['offset'])
        y.append(rating['rating'])
    
    plt.axis([start, end, 0, max(y)])
    plt.plot(x, y)

    ax = plt.gca()
    ax.xaxis.set_major_formatter(timeFrmtr)

    plt.ylabel('amount of comments')
    plt.xlabel('stream time')
    plt.show()

def plotHist(comments, accuracy):
    val = [com['content_offset_seconds'] for com in comments]
    start = float(comments[0]['content_offset_seconds'])
    end = float(comments[len(comments) - 1]['content_offset_seconds'])
    bins = round((end - start) / accuracy)
    plt.hist(val, range = (start, end), bins = bins, color = 'yellow', edgecolor = 'red')

    ax = plt.gca()
    ax.xaxis.set_major_formatter(timeFrmtr)

    plt.ylabel('amount of comments')
    plt.xlabel('stream time')
    plt.title('Comments per time ranges of ' + str(accuracy) + ' seconds')
    plt.show()

def progressBar(progress, barLen = 20):
    if (progress >= 1):
        sys.stdout.write("\n")
        print('Done !')
    else:
        sys.stdout.write("\r")
        bar = int(barLen * progress)
        sys.stdout.write("Progress : [{0}] {1}%".format("=" * bar + " " * (barLen - bar), int(progress * 100)))

    sys.stdout.flush()


analyze(618460248, 0, 500, 'line', 20)
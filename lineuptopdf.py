import statsapi
import sys
import random
from PIL import Image, ImageDraw, ImageFont
#this is a script which scrapes data from an MLB Api and places it on a .png using a font made from my hand writing
#it isn't the most optimal, but hey, it does its job
#to do: make bench/bullpen/SP names smaller in font size if they exceed the box

#the program has to know which game to search for - you have to pass the MLB game id to run it properly
#the ID can be found in the urls of MLB.tv [https://www.mlb.com/tv/g715719 <- the last 6 digits]
if len(sys.argv)!= 2:
    print("You have to pass an argument - the ID of a game found on MLB.tv or MLB.com")

dic = statsapi.boxscore_data(int(sys.argv[1])) #gets a dictionary with the lineup data from the MLB api
#getting the player IDs
awayDict = dic["away"] #dictionary with the away team data
awayStartingPitcher = awayDict["pitchers"][0] #the id of the first pitcher used during the game
awayBullpen = awayDict["bullpen"]+awayDict["pitchers"][1:] #the combination of pitchers not used and used in the game, excluding the SP

def getBattingOrder(teamDict):
    battingOrder = [0,0,0,0,0,0,0,0,0]
    for batter in teamDict["batters"]:
        try:
            #batting order data is formatted in the following way: xyy where x is between 1 and 9 and represents the order,
            #while yy is between 00 and probably 99, where 00 means the player was the first in a given (x) batting spot, 01 means he was the first substitute etc.
            if str(teamDict["players"]['ID'+str(batter)]['battingOrder'])[1:]=='00': 
                battingOrder[int(teamDict["players"]['ID'+str(batter)]['battingOrder'][0])-1] = batter 
        except:
            continue
    return battingOrder

awayBattingOrder = getBattingOrder(awayDict)

#if a player isn't the SP, in the bullpen, or in the batting order I conclude he has to be on the bench
def getBench(teamDict, SP, bullpen, battingOrder):
    bench = []
    for id in teamDict['players']:
        if int(id[2:]) == SP or int(id[2:]) in bullpen or int(id[2:]) in battingOrder:
            continue
        else:
            bench.append(id[2:])
    return bench

awayBench = getBench(awayDict, awayStartingPitcher, awayBullpen, awayBattingOrder)
#shuffling the lists to not make it obvious which player got into the game (they'd be last on the lists)
random.shuffle(awayBench) 
random.shuffle(awayBullpen)
#same process for the home team
homeDict = dic["home"]
homeStartingPitcher = homeDict["pitchers"][0]
homeBullpen = homeDict["bullpen"]+homeDict["pitchers"][1:]
homeBattingOrder = getBattingOrder(homeDict)
homeBench = getBench(homeDict, homeStartingPitcher, homeBullpen, homeBattingOrder)
random.shuffle(homeBench)
random.shuffle(homeBullpen)

#function to define formatting for names, i like them in a Name SURNAME format, hence the upper function
def formatNames(nameStr):
    retstr = ""
    arr = nameStr.split(' ')
    for i in range(len(arr)):
        if i!=0:
            retstr=retstr+arr[i].upper()+" "
        else:
            retstr=retstr+arr[i]+" "
    return retstr

#function which returns the teams name in, again, a City NAME format (can't be straightforward since for NYY normal procedure returns 'NY Yankees YANKEES')
def getTeamHeadline(teamInfoDict):
    badlyDoneTeams = ['NYY', 'NYM', 'CHC', 'CWS', 'LAD', 'LAA', 'AZ']
    fixedTeams = ['New York YANKEES', 'New York METS', 'Chicago CUBS', 'Chicago WHITE SOX', 'Los Angeles DODGERS', 'Los Angeles ANGELS', 'Arizona DIAMONDBACKS']
    for i in range(len(badlyDoneTeams)):
        if badlyDoneTeams[i]==teamInfoDict["abbreviation"]:
            return fixedTeams[i]
    return teamInfoDict['shortName'] + " " + teamInfoDict["teamName"].upper()
#function to make names fit in boxes
def textShrinker(initialN, text, width, coordX, coordY):
    textsize = myFont(initialN).getlength(text)
    while textsize>width:
        initialN = initialN-1
        textsize = myFont(initialN).getlength(text)
    d.text((coordX, coordY), text, fill=(0,0,0), font = myFont(initialN))

#dealing with page 1
img = Image.open('carp2023_1.png') #opening the blank scorecard
d = ImageDraw.Draw(img) #overlay with the text
def myFont(n):
    return ImageFont.truetype("tramsscript.ttf",n)


#getting the SP's name in a #. Name SURNAME FORMAT...
homesptext = homeDict['players']['ID'+str(homeStartingPitcher)]['jerseyNumber']+". "+formatNames(homeDict['players']['ID'+str(homeStartingPitcher)]['person']['fullName'])
textShrinker(40,homesptext,389,795,2775)


#getting bullpen names and putting them in their place, same for the batting order and bench
i=0 
for id in homeBullpen:
    try:
        namestr = homeDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        finalstr = homeDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr
    except:
        print(formatNames(namestr), "missing from home bullpen") #if the data isn't complete (f.e. no jersey number), the script outputs the details of the missing player, run with 661672 to test out (as of 03.01.2023) 
        finalstr=""
    textShrinker(40,finalstr,632,158,2557+i)
    i=i+50
i=0
for id in awayBattingOrder:
    try:
        namestr = awayDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        pos = awayDict['players']['ID'+str(id)]['allPositions'][0]['abbreviation']
        finalstr = awayDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr +" "+pos       
    except:
        print(formatNames(namestr), "missing from away batting order")
        finalstr=""
    textShrinker(42,finalstr,632,160,1224+i)
    i=i+142
i=0
for id in awayBench:
    try:
        namestr = awayDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        finalstr = awayDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr +" "
    except:
        print(formatNames(namestr), "missing from away bench")
        finalstr=""
    textShrinker(40,finalstr,404,1931,2775+i)
    i=i+50 
#getting surnames on the fielding chart
for id in homeBattingOrder:    
    try:
        pos = homeDict['players']['ID'+str(id)]['allPositions'][0]['abbreviation']
        namestr = homeDict['players']['ID'+str(id)]['person']['fullName']
        text = namestr[namestr.find(' ')+1:]            
        textsize = myFont(40).getlength(text) 
        if pos == "C":
            d.text((1758-(textsize/2),1010), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "3B": 
            d.text((1347-(textsize/2),914), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "LF":
            d.text((1347-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "RF":
            d.text((2182-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0)) 
        elif pos == "1B":
            d.text((2182-(textsize/2),914), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "CF":
            d.text((1758-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "2B":
            d.text((1997-(textsize/2),738), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "SS":
            d.text((1517-(textsize/2),738), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))   
    except:
        continue
#info box
#the two shortened names in the top left corner
d.text((190,500),dic["teamInfo"]["away"]["teamName"].upper(),fill=(0,0,0),font=myFont(40)) 
d.text((190,560),dic["teamInfo"]["home"]["teamName"].upper(),fill=(0,0,0),font=myFont(40))
d.text((163,1135),getTeamHeadline(dic['teamInfo']['away']),fill=(0,0,0),font=myFont(50)) #the "title" on top of the batting order
#getting misc data, and placing the ones needed in the first page on the page
weatherstring = ""
umps = []
venuestring = ""
for x in dic["gameBoxInfo"]:
    if x["label"] == 'First pitch': #time of the first pitch
        d.text((270,884),x["value"][:-1],fill=(0,0,0),font=ImageFont.truetype("tramsscript.ttf",35))
    elif x["label"] == "Att":
        d.text((734,953),x["value"],fill=(0,0,0),font=ImageFont.truetype("tramsscript.ttf",35))
    elif x["label"] == "Weather":
        weatherstring = weatherstring+x["value"]+" "
    elif x["label"] == "Wind":
        weatherstring = weatherstring+x["value"].split(",")[0]
    elif x["label"] == "Umpires":
        for y in x["value"].split('.'):
            if y!=' ':
                z = y.split(':')
                umps.append(z)
    elif x["label"] == "Venue":
        venuestring=x["value"]
        
textShrinker(32,weatherstring,405,769,1020)
datestr = dic["gameBoxInfo"][len(dic['gameBoxInfo'])-1]["label"]
d.text((611,884),datestr, fill=(0,0,0),font=myFont(35))
d.text((300,2508),dic["teamInfo"]["home"]["abbreviation"],fill=(0,0,0),font=myFont(40)) #abbreviations on the headlines (near the BENCH and BULLPEN etc)
d.text((845,2717),dic["teamInfo"]["home"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((1980,2719),dic["teamInfo"]["away"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((1650,445),dic["teamInfo"]["home"]["abbreviation"],fill=(0,0,0),font=myFont(45))
img.save('carptest.png') #saved, we're done with the first one

#page 2
img = Image.open('carp2023_2.png')
d = ImageDraw.Draw(img)
#pretty much same thing like above
awaysptext = awayDict['players']['ID'+str(awayStartingPitcher)]['jerseyNumber']+". "+formatNames(awayDict['players']['ID'+str(awayStartingPitcher)]['person']['fullName'])
textShrinker(40,awaysptext,389,795,2775)
i=0
for id in awayBullpen:
    try:
        namestr = awayDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        finalstr = awayDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr
    except:
        print(formatNames(namestr), "missing from away bullpen")
        finalstr=""
    textShrinker(40,finalstr,632,158,2557+i)
    i=i+50
i=0
for id in homeBattingOrder:
    try:
        namestr = homeDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        pos = homeDict['players']['ID'+str(id)]['allPositions'][0]['abbreviation']
        finalstr = homeDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr +" "+pos       
    except:
        print(formatNames(namestr), "missing from home batting order")
        finalstr=""
    textShrinker(42,finalstr,632,160,1224+i)
    i=i+142
i=0
for id in homeBench:
    try:
        namestr = homeDict['players']['ID'+str(id)]['person']['fullName']
        formattedstr = formatNames(namestr)
        finalstr = homeDict['players']['ID'+str(id)]['jerseyNumber']+". "+formattedstr +" "
    except:
        print(formatNames(namestr), "missing from home bench")
        finalstr=""
    textShrinker(40,finalstr,404,1931,2775+i)
    i=i+50 
for id in awayBattingOrder:    
    try:
        pos = awayDict['players']['ID'+str(id)]['allPositions'][0]['abbreviation']
        namestr = awayDict['players']['ID'+str(id)]['person']['fullName']
        text = namestr[namestr.find(' ')+1:]            
        textsize = myFont(40).getlength(text) 
        if pos == "C":
            d.text((714-(textsize/2),1010), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "3B": 
            d.text((297-(textsize/2),914), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "LF":
            d.text((297-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "RF":
            d.text((1132-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0)) 
        elif pos == "1B":
            d.text((1132-(textsize/2),914), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "CF":
            d.text((714-(textsize/2),538), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "2B":
            d.text((953-(textsize/2),738), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))
        elif pos == "SS":
            d.text((472-(textsize/2),738), namestr[namestr.find(' ')+1:],align='center',font=myFont(40), fill=(0,0,0))   
    except:
        continue
#misc: 
d.text((160,260),dic["teamInfo"]["away"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((160,330),dic["teamInfo"]["home"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((300,2508),dic["teamInfo"]["away"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((845,2717),dic["teamInfo"]["away"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((1980,2719),dic["teamInfo"]["home"]["abbreviation"],fill=(0,0,0),font=myFont(40))
d.text((588,445),dic["teamInfo"]["away"]["abbreviation"],fill=(0,0,0),font=myFont(45))
d.text((163,1135),getTeamHeadline(dic['teamInfo']['home']),fill=(0,0,0),font=myFont(50))
#umps in top right
for ump in umps:
    namestr = formatNames(ump[1].lstrip())
    textsize = myFont(40).getlength(namestr) 
    if ump[0].lstrip() == "HP":
        d.text((1977-(textsize/2),375), namestr ,align='center',font=myFont(40), fill=(0,0,0))
    if ump[0].lstrip() == "2B":
        d.text((1977-(textsize/2),213), namestr,align='center',font=myFont(40), fill=(0,0,0))
    if ump[0].lstrip() == "3B":
        textShrinker(40,namestr,303,1600,300)
    if ump[0].lstrip() == "1B":
        textShrinker(40,namestr,282,2042,300)
#stadium
d.text((1737,124),venuestring,font=myFont(40), fill=(0,0,0))
img.save('carptest2.png')
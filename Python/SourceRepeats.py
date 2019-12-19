import networkx as nx
import csv
import math

dir = r'C:\Users\axw161530\Dropbox\Documents\BLOG\Posted_Python\SourceNearRepeats'

BMV_tup = []
with open(dir + r'\TheftFromMV.csv') as f:
    z = csv.reader(f)
    for row in z:
        BMV_tup.append(tuple(row))

colnames = BMV_tup.pop(0)
print colnames
print BMV_tup[0:10]

xInd = colnames.index('xcoordinat')
yInd = colnames.index('ycoordinat')
dInd = colnames.index('DateInt')
IdInd = colnames.index('incidentnu')

def NearStrings(CrimeData,idCol,xCol,yCol,tCol,DistThresh,TimeThresh):
    G = nx.Graph()
    n = len(CrimeData)
    for i in range(n):
        for j in range(i+1,n):
            if (float(CrimeData[j][tCol]) - float(CrimeData[i][tCol])) > TimeThresh:
                break
            else:
                xD = math.pow(float(CrimeData[j][xCol]) - float(CrimeData[i][xCol]),2)
                yD = math.pow(float(CrimeData[j][yCol]) - float(CrimeData[i][yCol]),2)
                d = math.sqrt(xD + yD)
                if d < DistThresh:
                    G.add_edge(CrimeData[j][idCol],CrimeData[i][idCol])
    comp = nx.connected_components(G)
    finList = []
    compId = 0
    for i in comp:
        compId += 1
        for j in i:
            finList.append((j,compId))
    return finList

def NearStringCount(CrimeData,idCol,xCol,yCol,tCol,DistThresh,TimeThresh,p):
    G = nx.Graph()
    n = len(CrimeData)
    for i in range(n):
        for j in range(i+1,n):
            if (float(CrimeData[j][tCol]) - float(CrimeData[i][tCol])) > TimeThresh:
                break
            else:
                xD = math.pow(float(CrimeData[j][xCol]) - float(CrimeData[i][xCol]),2)
                yD = math.pow(float(CrimeData[j][yCol]) - float(CrimeData[i][yCol]),2)
                d = math.sqrt(xD + yD)
                if d < DistThresh:
                    G.add_edge(CrimeData[j][idCol],CrimeData[i][idCol])
    comp = nx.connected_components(G)
    ln = [len(i) for i in comp]
    res = []
    for i in set(ln):
        res.append((p,i,ln.count(i)))
    return res

#now making function to do permutations
#BMV_li = [list(i) for i in BMV_tup]
import random

def SortTime(item):
    return item[3]

def PermNear(CrimeData,idCol,xCol,yCol,tCol,DistThresh,TimeThresh,nperms):
    pN = 0
    perm_li = []
    orig = NearStringCount(CrimeData,idCol,xCol,yCol,tCol,DistThresh,TimeThresh,pN)
    for i in orig:
        perm_li.append(i)
    #now to do permutations
    times = [i[tCol] for i in CrimeData]
    for i in range(nperms):
        pN += 1
        PermData = []
        random.shuffle(times)
        for a,b in zip(CrimeData,times):
            PermData.append([a[idCol],a[xCol],a[yCol],b])
        SortData = sorted(PermData, key=SortTime)
        temp_li = NearStringCount(SortData,0,1,2,3,DistThresh,TimeThresh,pN)
        for j in temp_li:
            perm_li.append(j)
    return perm_li
    

 
#cc = NearStringCount(CrimeData=BMV_tup[0:10],idCol=IdInd,xCol=xInd,yCol=yInd,tCol=dInd,DistThresh=30000,TimeThresh=3,p=0)
cc = PermNear(CrimeData=BMV_tup[100:200],idCol=IdInd,xCol=xInd,yCol=yInd,tCol=dInd,DistThresh=3000,TimeThresh=1,nperms=9)

#This takes under a minute
BigResults = PermNear(CrimeData=BMV_tup,idCol=IdInd,xCol=xInd,yCol=yInd,tCol=dInd,DistThresh=1000,TimeThresh=7,nperms=2)

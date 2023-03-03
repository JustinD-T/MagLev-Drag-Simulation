import numpy as np
import matplotlib.pyplot as plt
import json
import os
import wx 
from tabulate import tabulate

def testingStuff():
    global varuibleDict
    global parentFolder
    global dV
    parentFolder = 'C:\Coding Projects1\Drag Sim'
    path = os.path.join(parentFolder, 'Payload-Varuibles')
    with open(path, 'r') as j:  #get list
        varuibleDict = json.loads(j.read())
    varInitialize(varuibleDict)
    dV = 0.7832

def getPath(): #Opens file explorer and returns path
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open', style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
    else:
        path = None
    dialog.Destroy()
    return path

def varInitialize(varuibleDict):
    global nVal
    global C
    global P
    global A
    global m
    global sigFig
    global upperVLim
    global dy
    global tracklen
    global g
    global theta
    global mTrain
    g = 9.8
    mTrain = float(varuibleDict['mTrain'])
    tracklen = float(varuibleDict['tracklen'])
    dy = float(varuibleDict['dy'])
    theta = float(varuibleDict['theta'])
    nVal = float(varuibleDict['nVal'])
    C = float(varuibleDict['C'])
    P = float(varuibleDict['P'])
    A = float(varuibleDict['A'])
    m = float(varuibleDict['m'])
    upperVLim = int(varuibleDict['upperVLim'])
    digList = []
    for i in varuibleDict.values():
        digList.append(len(i))
    sigFig = min(digList)

def vArrayCreation(V0, t):
    vArray = []
    tArray = []
    timeExperienced = t/nVal
    for x in range(1, int(nVal)+1):
        if x == 1:
            acceleration = -(V0 ** 2 * C * P * (A/2) / m)
            velocityFinal = (acceleration * timeExperienced + V0)
        else:
            initialVelocity = vArray[x-2]
            acceleration = -(((initialVelocity ** 2) * C * P * (A / 2)) / m)
            velocityFinal = (acceleration * timeExperienced + initialVelocity)
        xVal = x*timeExperienced
        tArray.append(xVal)
        vArray.append(velocityFinal)
    tArray.append(t)
    vArray.append(0)
    return tArray, vArray

def mplPlot(x, y, x2, y2):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    xPlot = np.array(x)
    yPlot = np.array(y)
    xPlot2 = np.array(x2)
    yPlot2 = np.array(y2)
    ax1.plot(xPlot, yPlot)
    ax1.set_title('Velocity(Time)')
    ax2.plot(xPlot2, yPlot2)
    ax2.set_title('Displacement(Initial Velocity)')
    xL = 0
        
def riemannSum(yValues, t):
    integrand = t/nVal
    area = 0
    for y in yValues:
        area = integrand * y + area
    return area

def displacementRecursion(t):
    t = float(t)
    accVar = 0.01
    displacementY = []
    v0X = []
    for i in np.arange(0, upperVLim, accVar):
        x, y = vArrayCreation(i, t)
        d = riemannSum(y, t)
        displacementY.append(d)
        v0X.append(i)
    return v0X, displacementY

def closest(disY, dV, inVArrayX):
    closestVal = disY[min(range(len(disY)), key = lambda i: abs(disY[i]-float(dV)))]
    v0True = inVArrayX[disY.index(closestVal)]
    # print('Closest Derivative to '+str(dV)+': '+str(closestVal))
    # print('Corresponding Initial Velocity:', v0True)
    return v0True

def testResults(path):
    global testVals
    with open(path, 'r') as j:  #get list
        testVals = json.loads(j.read())
    
def testRecursion():
    recType = 0
    t = np.sqrt( dy / 0.5 * g )
    for resultsDict in testVals.values():
        if recType == 0:
            testType = 'Magnetized'
            Results[testType] = {}
        if recType == 1:
            testType = 'nonMagnetized'
            Results[testType] = {}
        resList = list(resultsDict.values())
        times = list(resList[0].values())
        dxVals = list(resList[1].values())
        if recType == 0:
            testType = 'Magnetized'
        if recType == 1:
            testType = 'nonMagnetized'
        for i in range(0, len(times)):
            disY, inVArrayX = displacementRecursion(t)          
            v0Val = closest(disY, dxVals[i], inVArrayX)
            if recType == 0:
                testType = 'Magnetized'
                Results[testType]['Test #'+str(i+1)] = v0Val
            if recType == 1:
                testType = 'nonMagnetized'
                Results[testType]['Test #'+str(i+1)] = v0Val
        recType = 1
    return Results

def forceDifferential(Results):
    indexList = []
    magRes = Results["Magnetized"]
    nonmagRes = Results["nonMagnetized"]
    forceList = []    
    for i in range(0, len(magRes)):
        magV0 = float(magRes['Test #'+str(i+1)])
        nonmagV0 = float(nonmagRes['Test #'+str(i+1)])
        theoV0 = np.sqrt((2 * ( g * np.sin(theta) ) * tracklen))
        magFk = mTrain * ((( magV0 - np.sqrt(2 * ( g * np.sin(theta) ) * tracklen))**2) / (2 * tracklen) )
        nonmagFk = mTrain * ((( nonmagV0 - np.sqrt(2 * ( g * np.sin(theta) ) * tracklen))**2) / (2 * tracklen) )
        percV0dif = (abs(magV0 - nonmagV0) / ((magV0+nonmagV0) / 2)) *100
        percFkdif = (abs(magFk - nonmagFk) / ((magFk+nonmagFk) / 2)) * 100
        forceList.append([theoV0, magV0, magFk, nonmagV0, nonmagFk, percV0dif, percFkdif])
    forceList.append
    for x in Results["Magnetized"].keys():
        indexList.append(x)
    indexList.append('Averages')
    forceList.append(np.mean(np.array(forceList), axis=0))
    roundfList = []
    for x in forceList:
        temprList = []
        for i in range(0, len(x)):
            if i == 0 or i == 1 or i == 3:
                r = str(round(x[i], 3))+'m/s'
            elif i == 5 or i == 6:
                r = str(round(x[i], 3))+'%'
            else:
                r = str(round(x[i], 3))+'N'
            temprList.append(r)
        roundfList.append(temprList)
    roundfList.insert(0, ['Theo V0', 'Mag V0', 'Mag Fk', 'nonMag V0', 'nonMag Fk', 'V0 % diff', 'Fk % diff'])

    return roundfList, indexList




testingStuff()
Results = {}
parentFolder = 'C:\Coding Projects1\Drag Sim'
testPath = os.path.join(parentFolder, 'TestResults')
testResults(testPath)
Results = testRecursion()
forceList, indexList = forceDifferential(Results)
table = tabulate(forceList, tablefmt='fancy_grid', headers='firstrow', showindex=indexList)
print(table)


import yfinance as yf
import pandas as pd
import numpy as np
from cmu_112_graphics import *
from datetime import date
import random
from tkinter import *


def currentDate():
    return date.today()


def convertDaysAgoToDate(daysAgo, currentDay):
    monthSet = {
    1: 31, 
    2: 28, 
    3: 31, 
    4: 30, 
    5: 31, 
    6: 30, 
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
    }

    L = currentDay.split('-')
    Y = int(L[0])
    M = int(L[1])
    D = int(L[2])
    while daysAgo > 0:
        if D > 1:
            D -= 1
        else:
            if M > 1:
                M -= 1
                D = monthSet[M]
            else: 
                Y -= 1
                M = 12
                D = monthSet[M]
        daysAgo -= 1
    if D < 10:
        D = "0" + str(D)
    if M < 10:
        M = "0" + str(M)
    return str(Y) + '-' + str(M) + '-' + str(D)


def calculateLeastSquaresRegression(app, valueList):
    sumX = 0
    sumY = 0
    sumXSquared = 0
    sumXY = 0
    for i in range(app.day):
        sumX += i
        sumXSquared += i ** 2
        sumXY += (valueList[i] - 100000) * i
    sumX += app.day
    sumXSquared += app.day ** 2
    for i in range(app.day):
        sumY += (valueList[i] - 100000)
    return ((app.day * sumXY) - (sumX * sumY)) / ((app.day * sumXSquared) - (sumX ** 2))


def calculateSimpleMovingAverage(app, ticker, numDays, startingDay):
    SMA = 0
    for i in range(numDays):
        SMA += app.stockData[ticker]['Close'][app.day - i]
    return SMA / numDays

def calculateExponentialMovingAverage(app, ticker, numDays, startingDay):
    EMA = 0
    percentageValueAdded = 0
    for i in range(numDays):
        EMA += app.stockData[ticker]['Close'][startingDay - i] * (1 - i * (.8 / numDays))
        percentageValueAdded += (1 - i * (.8 / numDays))
    return EMA / percentageValueAdded


def calculatePortfolioValue(app, pCash, portfolio):
    value = pCash
    for ticker in portfolio:
        value += (app.stockData[ticker]['Close'][app.day]) * portfolio[ticker]
    return value


def AAPLMovingAverageConvergenceDivergence(app):
    addToAAPLMACDList(app)
    if checkIfMovingAverageConvergenceDivergenceBuyAAPL(app):
        app.stockBuySellList['AAPL'].append('Buy')
    elif checkIfMovingAverageConvergenceDivergenceSellAAPL(app):
        app.stockBuySellList['AAPL'].append('Sell')
    else:
        app.stockBuySellList['AAPL'].append('None')


def addToAAPLMACDList(app):
    #goes through each stock in portfolio
    if len(app.AAPLMACDList) == 0:
        app.AAPLMACDList = [calculateExponentialMovingAverage(app, 'AAPL', 12, app.day) - 
            calculateExponentialMovingAverage(app, 'AAPL', 26, app.day)]
    else:
        app.AAPLMACDList.append(calculateExponentialMovingAverage(app, 'AAPL', 12, app.day) - 
            calculateExponentialMovingAverage(app, 'AAPL', 26, app.day))


def checkIfMovingAverageConvergenceDivergenceSellAAPL(app):
    if app.AAPLMACDPortfolio['AAPL'] != 0:
        nineDayMACD = 0
        for i in range (app.day - 8, app.day + 1):
            nineDayMACD += app.AAPLMACDList[i]
        nineDayMACD /= 9
        if nineDayMACD > app.AAPLMACDList[app.day]:
            sellAAPLMACD(app)
            return True
    return False

def checkIfMovingAverageConvergenceDivergenceBuyAAPL(app):
    if app.AAPLMACDPortfolio['AAPL'] == 0:
        nineDayMACD = 0
        if app.day >= 8:
            for i in range (app.day - 8, app.day + 1):
                nineDayMACD += app.AAPLMACDList[i]
            nineDayMACD /= 9
            if nineDayMACD < app.AAPLMACDList[app.day]: #I could check if the MACD just broke through the nineDayMACD here as well
                buyAAPLMACD(app)
                return True
    return False

def buyAAPLMACD(app):
    if app.AAPLMACDPortfolio['AAPL'] == 0:
        stockCount = app.AAPLMACDCash / app.stockData['AAPL']['Close'][app.day]
        app.AAPLMACDPortfolio['AAPL'] = stockCount
        app.AAPLMACDCash -= app.stockData['AAPL']['Close'][app.day] * stockCount


def sellAAPLMACD(app):
    app.AAPLMACDCash += app.stockData['AAPL']['Close'][app.day] * app.AAPLMACDPortfolio['AAPL']
    app.AAPLMACDPortfolio['AAPL'] = 0


def movingAverageConvergenceDivergenceRandom(app):
    randomTicker = random.choice(app.stockList)
    randomTicker2 = random.choice(app.stockList)
    addToMACDList(app)
    checkIfMovingAverageConvergenceDivergenceBuy(app, randomTicker)
    checkIfMovingAverageConvergenceDivergenceBuy(app, randomTicker2)
    checkIfMovingAverageConvergenceDivergenceSell(app)


def addToMACDList(app):
    #goes through each stock in portfolio
    for ticker in app.stockList:
        if ticker not in app.MACDList:
            app.MACDList[ticker] = [calculateExponentialMovingAverage(app, ticker, 12, app.day) - 
                calculateExponentialMovingAverage(app, ticker, 26, app.day)]
        else:
            app.MACDList[ticker].append(calculateExponentialMovingAverage(app, ticker, 12, app.day) - 
                calculateExponentialMovingAverage(app, ticker, 26, app.day))


def checkIfMovingAverageConvergenceDivergenceSell(app):
    for ticker in app.MACDPortfolio:
        if app.MACDPortfolio[ticker] != 0:
            nineDayMACD = 0
            for i in range (app.day - 9, app.day):
                nineDayMACD += app.MACDList[ticker][i]
            nineDayMACD /= 9
            if nineDayMACD > app.MACDList[ticker][app.day]:
                sellStockMACD(app, ticker)


def checkIfMovingAverageConvergenceDivergenceBuy(app, randomTicker):
    if randomTicker not in app.MACDPortfolio or app.MACDPortfolio[randomTicker] == 0:
        nineDayMACD = 0
        if app.day >= 8:
            for i in range (app.day - 8, app.day + 1):
                nineDayMACD += app.MACDList[randomTicker][i]
            nineDayMACD /= 9
            if nineDayMACD < app.MACDList[randomTicker][app.day]:
                buyStockMACD(app, randomTicker)


def buyStockMACD(app, ticker):
    if ticker not in app.MACDPortfolio:
        app.MACDPortfolio[ticker] = 0
    if app.MACDPortfolio[ticker] == 0:
        stockCount = 0
        if app.stockData[ticker]['Close'][app.day] < 15000 and app.MACDCash > 15000:
            stockCount = 10000 // app.stockData[ticker]['Close'][app.day]
        else:
            stockCount = app.MACDCash / app.stockData[ticker]['Close'][app.day]
        app.MACDPortfolio[ticker] = stockCount
        app.MACDCash -= app.stockData[ticker]['Close'][app.day] * stockCount


def sellStockMACD(app, ticker):
    app.MACDCash += app.stockData[ticker]['Close'][app.day] * app.MACDPortfolio[ticker]
    app.MACDPortfolio[ticker] = 0


def randomRelativeStrengthIndex(app):
    randomTicker = random.choice(app.stockList)
    rsi = 50
    gain = 0
    gainCount = 0
    loss = 0
    lossCount = 0
    if app.day >= 13:
        for i in range(app.day - 14, app.day):
            if app.RSIGainLossList[randomTicker][i] < 0:
                loss += app.RSIGainLossList[randomTicker][i]
                lossCount += 1
            else:
                gain += app.RSIGainLossList[randomTicker][i]
                gainCount += 1
        if app.RSIGainLossList[randomTicker][app.day] < 0:
            rsi = (100000 - (100000 / (1 + ((loss / lossCount) * 13 - app.RSIGainLossList[randomTicker][app.day]) / 
                ((gain / gainCount) * 13))))
        if app.RSIGainLossList[randomTicker][app.day] > 0:
            rsi = (100000 - (100000 / (1 + ((loss / lossCount) * 13) / 
                ((gain / gainCount) * 13 + app.RSIGainLossList[randomTicker][app.day]))))
    if rsi > 70 and (randomTicker in app.RSIPortfolio and app.RSIPortfolio[randomTicker] != 0): 
        app.RSICash += app.stockData[randomTicker]['Close'][app.day] * app.RSIPortfolio['MSFT']
        app.RSIPortfolio[randomTicker] = 0
    #fix the selling, make sure it checks everything to see if it is a sell
    elif rsi < 30 and (randomTicker in app.RSIPortfolio and app.RSIPortfolio[randomTicker] == 0): 
        app.RSIPortfolio[randomTicker] = (app.RSICash / 8) / app.stockData[randomTicker]['Close'][app.day]
        app.RSICash -= app.stockData[randomTicker]['Close'][app.day] * app.RSIPortfolio[randomTicker]


def MSFTRelativeStrengthIndex(app):
    rsi = 50
    gain = 0
    gainCount = 0
    loss = 0
    lossCount = 0
    if app.day >= 13:
        for i in range(app.day - 14, app.day):
            if app.RSIGainLossList['MSFT'][i] < 0:
                loss += app.RSIGainLossList['MSFT'][i]
                lossCount += 1
            else:
                gain += app.RSIGainLossList['MSFT'][i]
                gainCount += 1
        if app.RSIGainLossList['MSFT'][app.day] < 0:
            rsi = (100000 - (100000 / (1 + ((loss / lossCount) * 13 - app.RSIGainLossList['MSFT'][app.day]) / 
                ((gain / gainCount) * 13))))
        if app.RSIGainLossList['MSFT'][app.day] > 0:
            rsi = (100000 - (100000 / (1 + ((loss / lossCount) * 13) / 
                ((gain / gainCount) * 13 + app.RSIGainLossList['MSFT'][app.day]))))
    if rsi > 70 and app.MSFTRSIPortfolio['MSFT'] != 0: 
        app.MSFTRSICash = app.stockData['MSFT']['Close'][app.day] * app.MSFTRSIPortfolio['MSFT']
        app.MSFTRSIPortfolio['MSFT'] = 0
        app.stockBuySellList['MSFT'].append('Sell')
    elif rsi < 30 and app.MSFTRSIPortfolio['MSFT'] == 0:
        app.MSFTRSIPortfolio['MSFT'] = app.MSFTRSICash / app.stockData['MSFT']['Close'][app.day]
        app.MSFTRSICash = 0
        app.stockBuySellList['MSFT'].append('Buy')
    else:
        app.stockBuySellList['MSFT'].append('None')
    

def AMZNGoldenCross(app):
    if app.day >= 14:
        if calculateExponentialMovingAverage(app, 'AMZN', 14, app.day) > calculateExponentialMovingAverage(app, 'AMZN', 7, app.day):
            if 'AMZN' not in app. AMZNGCPortfolio: 
                app.AMZNGCPortfolio['AMZN'] = app.AMZNGCCash / app.stockData['AMZN']['Close'][app.day]
                app.AMZNGCCash = 0
                app.stockBuySellList['AMZN'].append('Buy')
            elif app.AMZNGCPortfolio['AMZN'] == 0:
                app.AMZNGCPortfolio['AMZN'] = app.AMZNGCCash / app.stockData['AMZN']['Close'][app.day]
                app.AMZNGCCash = 0
                app.stockBuySellList['AMZN'].append('Buy')
            else:
                app.stockBuySellList['AMZN'].append('None')
        elif calculateExponentialMovingAverage(app, 'AMZN', 14, app.day) < calculateExponentialMovingAverage(app, 'AMZN', 7, app.day) and \
            ('AMZN' in app. AMZNGCPortfolio and app.AMZNGCPortfolio['AMZN'] != 0):
            app.AMZNGCCash = app.AMZNGCPortfolio['AMZN'] * app.stockData['AMZN']['Close'][app.day]
            app.AMZNGCPortfolio['AMZN'] = 0
            app.stockBuySellList['AMZN'].append('Sell')
        else:
            app.stockBuySellList['AMZN'].append('None')
    else:
        app.stockBuySellList['AMZN'].append('None')


def randomGoldenCross(app):
    ticker = random.choice(app.stockList)
    if app.day >= 14:
        if calculateExponentialMovingAverage(app, ticker, 14, app.day) > calculateExponentialMovingAverage(app, ticker, 7, app.day) and \
            (ticker in app.GCPortfolio and app.GCPortfolio[ticker] == 0):
            app.GCPortfolio[ticker] = app.GCCash / app.stockValues[ticker]['Close'][app.day]
            app.GCCash = 0
        elif calculateExponentialMovingAverage(app, ticker, 14, app.day) < calculateExponentialMovingAverage(app, ticker, 7, app.day) and \
            (ticker in app.GCPortfolio and app.GCPortfolio[ticker] != 0):
            app.GCCash = app.GCPortfolio[ticker] * app.stockValues[ticker]['Close'][app.day]
            app.GCPortfolio[ticker] = 0


#these 2 functions below run the index valuation and index graph
def calculateIndexAverage(app):
    numStocks = 100000 / app.stockData['DJI']['Close'][0]
    return numStocks * app.stockData['DJI']['Close'][app.day]

def getHighestValue(app, ticker):
    highest = app.stockData[ticker]['Close'][0]
    for i in range(app.day):
        if app.stockData[ticker]['Close'][i] > highest:
            highest = app.stockData[ticker]['Close'][i]
    return highest

def getLowestValue(app, ticker):
    lowest = app.stockData[ticker]['Close'][0]
    for i in range(app.day):
        if app.stockData[ticker]['Close'][i] < lowest:
            lowest = app.stockData[ticker]['Close'][i]
    return lowest

def getHighestPortfolioValue(app, portfolio):
    highest = portfolio[0]
    for i in range(app.day):
        if portfolio[i] > highest:
            highest  = portfolio[i]
    return highest


def getLowestPortfolioValue(app, portfolio):
    lowest = portfolio[0]
    for i in range(app.day):
        if portfolio[i] < lowest:
            lowest = portfolio[i]
    return lowest


def drawPortfolioGraph(app, canvas, left, top, width, height, portfolio):
    if len(portfolio) > 0: 
        if getHighestPortfolioValue(app, portfolio) < 105000 and getLowestPortfolioValue(app, portfolio) > 95000:
            canvas.create_line(left, top, left, top + height, width = 3) # y axis
            canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
            canvas.create_text(left - 30, top + 5, text = '$105,000')
            canvas.create_line(left, top, left + width, top)
            canvas.create_text(left - 30, top + height / 4 + 3, text = '$102,500')
            canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
            canvas.create_text(left - 30, top + height / 2, text = '$100,000')
            canvas.create_line(left, top + height / 2, left + width, top + height / 2)
            canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$97,500')
            canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
            canvas.create_text(left - 30, top + height - 5, text = '$95,000')
            previousLineData = []
            for i in range(app.day):
                if i != 0:
                    canvas.create_line(previousLineData[0], previousLineData[1], \
                    left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 10000 * height, \
                    width = 3)
                if app.day == 0:
                    previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 10000 * height,]
                else:
                    previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 10000 * height,]

        elif getHighestPortfolioValue(app, portfolio) < 110000 and getLowestPortfolioValue(app, portfolio) > 90000:
            canvas.create_line(left, top, left, top + height, width = 3) # y axis
            canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
            canvas.create_text(left - 30, top + 5, text = '$110,000')
            canvas.create_line(left, top, left + width, top)
            canvas.create_text(left - 30, top + height / 4 + 3, text = '$105,000')
            canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
            canvas.create_text(left - 30, top + height / 2, text = '$100,000')
            canvas.create_line(left, top + height / 2, left + width, top + height / 2)
            canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$95,000')
            canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
            canvas.create_text(left - 30, top + height - 5, text = '$90,000')
            previousLineData = []
            for i in range(app.day):
                if i != 0:
                    canvas.create_line(previousLineData[0], previousLineData[1], \
                    left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 20000 * height + app.graphCircleRadius / 2, \
                    width = 3)
                if app.day == 0:
                    previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 20000 * height + app.graphCircleRadius / 2,]
                else:
                    previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 20000 * height + app.graphCircleRadius / 2,]

        elif getHighestPortfolioValue(app, portfolio) < 115000 and getLowestPortfolioValue(app, portfolio) > 85000:
            canvas.create_line(left, top, left, top + height, width = 3) # y axis
            canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
            canvas.create_text(left - 30, top + 5, text = '$115,000')
            canvas.create_line(left, top, left + width, top)
            canvas.create_text(left - 30, top + height / 4 + 3, text = '$107,500')
            canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
            canvas.create_text(left - 30, top + height / 2, text = '$100,000')
            canvas.create_line(left, top + height / 2, left + width, top + height / 2)
            canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$92,500')
            canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
            canvas.create_text(left - 30, top + height - 5, text = '$85,000')
            previousLineData = []
            for i in range(app.day):
                if i != 0:
                    canvas.create_line(previousLineData[0], previousLineData[1], \
                    left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 30000 * height + app.graphCircleRadius / 2, \
                    width = 3)

                if app.day == 0:
                    previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 30000 * height + app.graphCircleRadius / 2,]
                else:
                    previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 30000 * height + app.graphCircleRadius / 2,]

        elif getHighestPortfolioValue(app, portfolio) < 120000 and getLowestPortfolioValue(app, portfolio) > 80000:
            canvas.create_line(left, top, left, top + height, width = 3) # y axis
            canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
            canvas.create_text(left - 30, top + 5, text = '$120,000')
            canvas.create_line(left, top, left + width, top)
            canvas.create_text(left - 30, top + height / 4 + 3, text = '$110,000')
            canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
            canvas.create_text(left - 30, top + height / 2, text = '$100,000')
            canvas.create_line(left, top + height / 2, left + width, top + height / 2)
            canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$90,000')
            canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
            canvas.create_text(left - 30, top + height - 5, text = '$80,000')
            previousLineData = []
            for i in range(app.day):
                if i != 0:
                    canvas.create_line(previousLineData[0], previousLineData[1], \
                    left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 40000 * height + app.graphCircleRadius / 2, \
                    width = 3)

                if app.day == 0:
                    previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 40000 * height + app.graphCircleRadius / 2,]
                else:
                    previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 40000 * height + app.graphCircleRadius / 2,]

        else:
            canvas.create_line(left, top, left, top + height, width = 3) # y axis
            canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
            canvas.create_text(left - 30, top + 5, text = '$150,000')
            canvas.create_line(left, top, left + width, top)
            canvas.create_text(left - 30, top + height / 4 + 3, text = '$125,000')
            canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
            canvas.create_text(left - 30, top + height / 2, text = '$100,000')
            canvas.create_line(left, top + height / 2, left + width, top + height / 2)
            canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$75,000')
            canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
            canvas.create_text(left - 30, top + height - 5, text = '$50,000')
            previousLineData = []
            for i in range(app.day):
                if i != 0:
                    canvas.create_line(previousLineData[0], previousLineData[1], \
                    left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 100000 * height + app.graphCircleRadius / 2, \
                    width = 3)
                if app.day == 0:
                    previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 100000 * height + app.graphCircleRadius / 2,]
                else:
                    previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - portfolio[i]) / 100000 * height + app.graphCircleRadius / 2,] 


def drawStockGraph(app, canvas, left, top, width, height, ticker):
    if getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.05) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .95):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = '$105,000')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = '$102,500')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = '$100,000')
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$97,500')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = '$95,000')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2,]

    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.1) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .9):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = '$110,000')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = '$105,000')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = '$100,000')
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$95,000')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = '$90,000')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2,]
    
    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.15) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .85):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = '$115,000')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = '$107,500')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = '$100,000')
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$92,500')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = '$85,000')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2,]

    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.2) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .8):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = '$120,000')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = '$110,000')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = '$100,000')
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$90,000')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = '$80,000')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2,]
    
    else: #if getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.5) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .5):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = '$150,000')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = '$125,000')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = '$100,000')
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = '$75,000')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = '$50,000')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 100000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 100000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 100000 * height + app.graphCircleRadius / 2,]

def drawStockGraphUserPage(app, canvas, left, top, width, height, ticker):
    point5 = round(app.stockData[ticker]['Close'][0] * .5, 2)
    point8 = round(app.stockData[ticker]['Close'][0] * .8, 2)
    point85 = round(app.stockData[ticker]['Close'][0] * .85, 2)
    point9 = round(app.stockData[ticker]['Close'][0] * .9, 2)
    point925 = round(app.stockData[ticker]['Close'][0] * .925, 2)
    point95 = round(app.stockData[ticker]['Close'][0] * .95, 2)
    point975 = round(app.stockData[ticker]['Close'][0] * .975, 2)
    point = round(app.stockData[ticker]['Close'][0], 2)
    onePoint025 = round(app.stockData[ticker]['Close'][0] * 1.025, 2)
    onePoint05 = round(app.stockData[ticker]['Close'][0] * 1.05, 2)
    onePoint075 = round(app.stockData[ticker]['Close'][0] * 1.075, 2)
    onePoint1 = round(app.stockData[ticker]['Close'][0] * 1.1, 2)
    onePoint15 = round(app.stockData[ticker]['Close'][0] * 1.15, 2)
    onePoint2 = round(app.stockData[ticker]['Close'][0] * 1.2, 2)
    onePoint5 = round(app.stockData[ticker]['Close'][0] * 1.5, 2)
    two = round(app.stockData[ticker]['Close'][0] * 2, 2)

    if getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.05) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .95):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = f'${onePoint05}')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = f'${onePoint025}')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = f'${point}') # change to price values of stock
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = f'${point975}')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = f'${point95}')
        currentValue = round(app.stockData[ticker]['Close'][app.day], 2)
        canvas.create_text(left + width / 2, top - 15, text = f'{ticker}: {currentValue}')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 10000 * height + app.graphCircleRadius / 2,]

    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.1) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .9):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = f'${onePoint1}')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = f'${onePoint05}')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = f'${point}') # change to price values of stock
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = f'${point95}')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = f'${point9}')
        currentValue = round(app.stockData[ticker]['Close'][app.day], 2)
        canvas.create_text(left + width / 2, top - 15, text = f'{ticker}: {currentValue}')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 20000 * height + app.graphCircleRadius / 2,]
    
    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.15) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .85):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = f'${onePoint15}')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = f'${onePoint075}')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = f'${point}') # change to price values of stock
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = f'${point925}')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = f'${point85}')
        currentValue = round(app.stockData[ticker]['Close'][app.day], 2)
        canvas.create_text(left + width / 2, top - 15, text = f'{ticker}: {currentValue}')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 30000 * height + app.graphCircleRadius / 2,]

    elif getHighestValue(app, ticker) < (app.stockData[ticker]['Close'][0] * 1.2) and getLowestValue(app, ticker) > (app.stockData[ticker]['Close'][0] * .8):
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = f'${onePoint2}')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = f'${onePoint1}')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = f'${point}') # change to price values of stock
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = f'${point9}')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = f'${point8}')
        currentValue = round(app.stockData[ticker]['Close'][app.day], 2)
        canvas.create_text(left + width / 2, top - 15, text = f'{ticker}: {currentValue}')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 40000 * height + app.graphCircleRadius / 2,]
    else:
        canvas.create_line(left, top, left, top + height, width = 3) # y axis
        canvas.create_line(left, top + height, left + width, top + height, width = 3) # x axis
        canvas.create_text(left - 30, top + 5, text = f'${two}')
        canvas.create_line(left, top, left + width, top)
        canvas.create_text(left - 30, top + height / 4 + 3, text = f'${onePoint5}')
        canvas.create_line(left, top + height / 4 + 3, left + width, top + height / 4 + 3)
        canvas.create_text(left - 30, top + height / 2, text = f'${point}') # change to price values of stock
        canvas.create_line(left, top + height / 2, left + width, top + height / 2)
        canvas.create_text(left - 30, top + 3 * height / 4 - 3, text = f'${point5}')
        canvas.create_line(left, top + 3 * height / 4 - 3, left + width, top + 3 * height / 4 - 3)
        canvas.create_text(left - 30, top + height - 5, text = f'$0')
        currentValue = round(app.stockData[ticker]['Close'][app.day], 2)
        canvas.create_text(left + width / 2, top - 15, text = f'{ticker}: {currentValue}')
        previousLineData = []
        for i in range(app.day):
            if i != 0:
                canvas.create_line(previousLineData[0], previousLineData[1], \
                left + width * i / app.day + app.graphCircleRadius / 2, \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 200000 * height + app.graphCircleRadius / 2, \
                width = 3)
            if app.day == 0:
                previousLineData = [left + width * i + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 200000 * height + app.graphCircleRadius / 2,]
            else:
                previousLineData = [left + width * i / app.day + app.graphCircleRadius / 2, \
                    top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / 200000 * height + app.graphCircleRadius / 2,]


def drawStockGraphBuySellTriangles(app, canvas, left, top, width, height, ticker):
    previousData = []
    for i in range(len(app.stockBuySellList[ticker])):
        if app.stockBuySellList[ticker][i] == 'Buy':
            canvas.create_polygon(previousData[0] - 6, previousData[1] - 30, 
            (previousData[0] + left + width * i / len(app.indexValueList) + app.graphCircleRadius / 2) / 2, 
            previousData[1] - 15, 
            6 + left + width * i / len(app.indexValueList) + app.graphCircleRadius / 2, 
            previousData[1] - 30, 
            fill = 'green')
        
        if app.stockBuySellList[ticker][i] == 'Sell':
            canvas.create_polygon(previousData[0] - 6, previousData[1] - 30, 
            (previousData[0] + left + width * i / len(app.indexValueList) + app.graphCircleRadius / 2) / 2, 
            previousData[1] - 15, 
            6 + left + width * i / len(app.indexValueList) + app.graphCircleRadius / 2, 
            previousData[1] - 30, 
            fill = 'red')

        if len(app.indexValueList) > 0:
            previousData = [left + width * i / len(app.indexValueList), \
                top + height / 2 + (100000 - app.stockData[ticker]['Close'][i] * app.stockCount[ticker]) / app.triangleDivisor * height]

def userBuyStock(app, ticker, stockCount):
    app.userPortfolio[ticker] = app.userPortfolio[ticker] + stockCount
    app.userCash -= app.stockData[ticker][app.day] * stockCount

def userSellStock(app, ticker, stockCount):
    app.userCash += app.stockData[ticker]['Close'][app.day] * stockCount
    app.userPortfolio[ticker] = app.userPortfolio[ticker] - stockCount

def drawStockRotation(app, canvas):
    drawStockGraphUserPage(app, canvas, 65, 400, 175, 175, app.stockList[3 * app.stockRotationNumber])
    drawStockGraphUserPage(app, canvas, 320, 400, 175, 175, app.stockList[3 * app.stockRotationNumber + 1])
    drawStockGraphUserPage(app, canvas, 575, 400, 175, 175, app.stockList[3 * app.stockRotationNumber + 2])

def drawUserPortfolioList(app, canvas):
    canvas.create_text(658, 20, anchor = 'w', text = 'Portfolio:', font = 'Helvetica 14')
    for i in range(len(app.stockList)):
        if  app.stockList[i] in app.userPortfolio:
            canvas.create_text(730, 40 + 14 * i, anchor = 'e', text = f'{app.stockList[i]}: {app.userPortfolio[app.stockList[i]]}', font = 'Helvetica 9')
        else:
            canvas.create_text(730, 40 + 14 * i, anchor = 'e', text = f'{app.stockList[i]}: 0', font = 'Helvetica 9')

def appStarted(app):
    app.timerDelay = 5
    app.period = '101d'
    app.day = 0
    app.stockData = dict()
    app.stockBuySellList = dict()
    app.stockList = ['KO', 'DIS', 'AAPL', 'MSFT', 'ADBE', 'AI', 'TSLA', 'GGPI', 'BA', 'BABA', \
        'LCID', 'F', 'M', 'NVDA', 'GOOG', 'RBLX', 'AMD', 'T', 'CSCO', 'AMZN', 'HOG', 'TM', 'V', 'DJI']
    
    #this top one will only be used for the index graph, it is not in the stockList
    app.stockData['DJI'] = yf.download('DJI', period = '130d')
    app.stockData['KO'] = yf.download('KO', period = '130d')
    app.stockData['DIS'] = yf.download('DIS', period = '130d')
    app.stockData['AAPL'] = yf.download('AAPL', period = '130d')
    app.stockData['MSFT'] = yf.download('MSFT', period = '130d')
    app.stockData['ADBE'] = yf.download('ADBE', period = '130d')
    app.stockData['AI'] = yf.download('AI', period = '130d')
    app.stockData['TSLA'] = yf.download('TSLA', period = '130d')
    app.stockData['GGPI'] = yf.download('GGPI', period = '130d')
    app.stockData['BA'] = yf.download('BA', period = '130d')
    app.stockData['BABA'] = yf.download('BABA', period = '130d')
    app.stockData['LCID'] = yf.download('LCID', period = '130d')
    app.stockData['F'] = yf.download('F', period = '130d')
    app.stockData['M'] = yf.download('M', period = '130d')
    app.stockData['NVDA'] = yf.download('NVDA', period = '130d')
    app.stockData['GOOG'] = yf.download('GOOG', period = '130d')
    app.stockData['RBLX'] = yf.download('RBLX', period = '130d')
    app.stockData['AMD'] = yf.download('AMD', period = '130d')
    app.stockData['T'] = yf.download('T', period = '130d')
    app.stockData['CSCO'] = yf.download('CSCO', period = '130d')
    app.stockData['AMZN'] = yf.download('AMZN', period = '130d')
    app.stockData['HOG'] = yf.download('HOG', period = '130d')
    app.stockData['TM'] = yf.download('TM', period = '130d')
    app.stockData['V'] = yf.download('V', period = '130d')
    app.stockCount = dict()
    app.stockValues = dict()
    app.stockValuesList = dict()
    for ticker in app.stockData:
        app.stockCount[ticker] = 100000 / app.stockData[ticker]['Close'][0]
        app.stockValues[ticker] = 100000
        for n in app.stockData[ticker]['Close']:
            if ticker not in app.stockValuesList:
                app.stockValuesList[ticker] = [n * app.stockCount[ticker]]
            else:
                app.stockValuesList[ticker].append(n * app.stockCount[ticker])


    app.triangleDivisor = 10000 #weird name, but it's a weird topic
    app.isPaused = False

    app.AAPLStockValue = 100000
    app.LRAAPL = 0
    app.MSFTStockValue = 100000
    app.LRMSFT = 0
    app.LRAMZN = 0
    app.AMZNStockValue = 100000

    #portfolio 1
    app.MACDCash = 100000.0
    app.MACDPortfolio = dict()
    app.MACDList = dict()
    app.MACDPortfolioValue = calculatePortfolioValue(app, app.MACDCash, app.MACDPortfolio)
    app.MACDPortfolioValueList = []
    app.LRMACD = 0


    #new MACD Portfolio with Just AAPL stock
    app.AAPLMACDCash = 100000
    app.AAPLMACDPortfolio = {'AAPL': 0}
    app.AAPLMACDList = []
    app.AAPLMACDPortfolioValue = calculatePortfolioValue(app, app.AAPLMACDCash, app.AAPLMACDPortfolio)#, app.AAPLMACDCash, app.AAPLMACDPortfolio)
    app.AAPLMACDPortfolioValueList = []
    app.stockBuySellList['AAPL'] = []
    app.LRAAPLMACD = 0

    #MSFT RSI Portfolio
    app.MSFTRSICash = 100000
    app.MSFTRSIPortfolio = {'MSFT': 0}
    app.MSFTGainLossList = []
    for i in range(len(app.stockData['MSFT']['Close']) - 1):
        app.MSFTGainLossList.append((app.stockData['MSFT']['Close'][i + 1] / app.stockData['MSFT']['Close'][i]) - 1)
    app.MSFTRSIPortfolioValue = calculatePortfolioValue(app, app.MSFTRSICash, app.MSFTRSIPortfolio)
    app.MSFTRSIPortfolioValueList = []
    app.stockBuySellList['MSFT'] = []
    app.LRMSFTRSI = 0

    #Random RSI Portfolio
    app.RSICash = 100000
    app.RSIPortfolio = dict()
    app.RSIGainLossList = dict()
    for ticker in app.stockData:
        for i in range(len(app.stockData[ticker]['Close']) - 1):
            if ticker not in app.RSIGainLossList:
                app.RSIGainLossList[ticker] = [(app.stockData[ticker]['Close'][i + 1] / app.stockData[ticker]['Close'][i]) - 1]
            else:
                app.RSIGainLossList[ticker].append((app.stockData[ticker]['Close'][i + 1] / app.stockData[ticker]['Close'][i]) - 1)
    app.RSIPortfolioValue = calculatePortfolioValue(app, app.RSICash, app.RSIPortfolio)
    app.RSIPortfolioValueList = []
    app.LRRSI = 0

    #AMZN Golden Cross Portfolio
    app.AMZNGCCash = 100000
    app.AMZNGCPortfolio = dict()
    app.AMZNGCPortfolioValue = calculatePortfolioValue(app, app.AMZNGCCash, app.AMZNGCPortfolio)
    app.AMZNGCPortfolioValueList = []
    app.stockBuySellList['AMZN'] = []
    app.LRAMZNGC = 0

    #random GC Portfolio
    app.GCCash = 100000
    app.GCPortfolio = dict()
    app.AMZNGCPortfolioValue = calculatePortfolioValue(app, app.AMZNGCCash, app.AMZNGCPortfolio)
    app.AMZNGCPortfolioValueList = []
    app.LRGC = 0

    #index portfolio 1 or 2 of these might be useless
    app.indexStartingValue = 100000
    app.indexValue = calculateIndexAverage(app) 
    app.indexValueList = [100000]
    app.LRIndex = 0

    #user bought portfolio
    app.userCash = 100000
    app.userPortfolio = dict()
    app.userPortfolioValueList = [100000]
    app.userPortfolioValue = 100000
    app.buyInput = ''
    app.sellInput = ''
    app.stockRotationNumber = 0 # starts at 0 and has 1,2,3,

    #default screen is 0, port1 is 1, port2 is 2 & so on
    app.screen = 0
    app.startButtonWidth = 160
    app.startButtonHeight = 80
    app.graphCircleRadius = 2



def mousePressed(app, event):
    if app.screen == 0:
        if (event.x > app.width / 4.5 and event.x < app.width / 4.5 + app.startButtonWidth) and \
            (event.y > 19 * app.height / 64 and event.y < 19 * app.height / 64 + app.startButtonHeight):
            app.screen = 1
        if (event.x > app.width / 4.5 and event.x < app.width / 4.5 + app.startButtonWidth) and \
            (event.y > 32 * app.height / 64 and event.y < 32 * app.height / 64 + app.startButtonHeight):
            app.screen = 2
        if (event.x > app.width / 4.5 and event.x < app.width / 4.5 + app.startButtonWidth) and \
            (event.y > 45 * app.height / 64 and event.y < 45 * app.height / 64 + app.startButtonHeight):
            app.screen = 3
        if (event.x < 3.5 * app.width / 4.5 and event.x > 3.5 * app.width / 4.5 - app.startButtonWidth) and \
            (event.y > 32 * app.height / 64 and event.y < 32 * app.height / 64 + app.startButtonHeight):
            app.screen = 4
            app.timerDelay = 13000
    
    if app.screen == 1:
        if (event.x > 30 and event.x < 80) and (event.y > 25 and event.y < 60):
            app.screen = 0
            app.day = 0
            app.indexValueList = [100000]
            app.MACDCash = 100000.0
            app.MACDPortfolio = dict()
            app.MACDList = dict()
            app.MACDPortfolioValue = calculatePortfolioValue(app, app.MACDCash, app.MACDPortfolio)
            app.MACDPortfolioValueList = []
            app.AAPLMACDCash = 100000.0
            app.AAPLMACDPortfolio = {'AAPL': 0}
            app.AAPLMACDList = dict()
            app.AAPLMACDPortfolioValue = calculatePortfolioValue(app, app.AAPLMACDCash, app.AAPLMACDPortfolio)
            app.MACDPortfolioValueList = []
            app.AAPLMACDPortfolioValueList = []
            app.stockBuySellList['AAPL'] = []

    if app.screen == 2:
        if (event.x > 30 and event.x < 80) and (event.y > 25 and event.y < 60):
            app.screen = 0
            app.day = 0
            app.indexValueList = [100000]
            app.stockBuySellList['MSFT'] = []

    if app.screen == 3:
        if (event.x > 30 and event.x < 80) and (event.y > 25 and event.y < 60):
            app.screen = 0
            app.day = 0
            app.indexValueList = [100000]
            app.stockBuySellList['AMZN'] = []


    if app.screen == 4:
        #back button
        if (event.x > 30 and event.x < 80) and (event.y > 25 and event.y < 60):
            app.screen = 0
            app.day = 0
            app.timerDelay = 5
        #reset button
        if (event.x > 100 and event.x < 150) and (event.y > 25 and event.y < 60):
            app.userPortfolio = dict()
            app.day = 0
            app.userPortfolioValue = 100000
            app.userPortfolioValueList = [100000]
            app.userCash = 100000
        #buy button
        if (event.x > app.width / 16 and event.x < app.width / 16 + app.startButtonWidth) and \
            (event.y > 19 * app.height / 64 and event.y < 19 * app.height / 64 + app.startButtonHeight):
            app.inputTicker = app.getUserInput('What do you want to buy?')
            if app.inputTicker in app.stockList:
                app.inputAmount = app.getUserInput("How many?")
                if app.inputAmount != None and app.inputAmount.isnumeric():
                    app.inputAmount = int(app.inputAmount)
                    if app.stockData[app.inputTicker]['Close'][app.day] * app.inputAmount < app.userCash:
                        if app.inputTicker in app.userPortfolio:
                            app.userPortfolio[app.inputTicker] += app.inputAmount
                            app.userCash -= app.stockData[app.inputTicker]['Close'][app.day] * app.inputAmount
                        else:
                            app.userPortfolio[app.inputTicker] = app.inputAmount
                            app.userCash -= app.stockData[app.inputTicker]['Close'][app.day] * app.inputAmount

        #sell button
        if (event.x > app.width / 16 and event.x < app.width / 16 + app.startButtonWidth) and \
            (event.y > 26 * app.height / 64 and event.y < 26 * app.height / 64 + app.startButtonHeight):
            app.inputTicker = app.getUserInput('What do you want to sell?')
            if app.inputTicker in app.userPortfolio:
                app.inputAmount = app.getUserInput('How many?')
                if app.inputAmount != None and app.inputAmount.isnumeric():
                    app.inputAmount = int(app.inputAmount)
                    if app.userPortfolio[app.inputTicker] >= app.inputAmount:
                        app.userCash += app.stockData[app.inputTicker]['Close'][app.day] * app.inputAmount
                        app.userPortfolio[app.inputTicker] -= app.inputAmount

        #move to next day
        if (event.x > 138 and event.x < 213) and (event.y > 120 and event.y < 164):
            daysForward = app.getUserInput('How many days forward?')
            if daysForward != None and daysForward.isnumeric():
                daysForward = int(daysForward)
                if isinstance(daysForward, int) and app.day + daysForward < 100:
                    for i in range(daysForward):
                        app.day += 1
                        app.userPortfolioValue = calculatePortfolioValue(app, app.userCash, app.userPortfolio)
                        app.userPortfolioValueList.append(app.userPortfolioValue)
            
        #triangles for left and right stockRotation
        if (event.x > 80 and event.x < 120) and (event.y > 325 and event.y < 365):
            app.stockRotationNumber -= 1
            if app.stockRotationNumber == -1:
                app.stockRotationNumber = 7
        if (event.x > 141 and event.x < 175) and (event.y > 325 and event.y < 365):
            app.stockRotationNumber += 1
            if app.stockRotationNumber == 8:
                app.stockRotationNumber = 0



def timerFired(app):
    if app.screen == 1:
        if app.day < int(app.period[:-1]) - 1:
            movingAverageConvergenceDivergenceRandom(app)
            AAPLMovingAverageConvergenceDivergence(app)
            app.MACDPortfolioValue = int(calculatePortfolioValue(app, app.MACDCash, app.MACDPortfolio) // 1)
            app.MACDPortfolioValueList.append(app.MACDPortfolioValue)
            app.AAPLMACDPortfolioValue = int(calculatePortfolioValue(app, app.AAPLMACDCash, app.AAPLMACDPortfolio) // 1)
            app.AAPLMACDPortfolioValueList.append(app.AAPLMACDPortfolioValue)
            app.indexValue = int(calculateIndexAverage(app) // 1)
            app.indexValueList.append(app.indexValue)
            app.day += 1
            for ticker in app.stockData:
                app.stockValues[ticker] = app.stockCount[ticker] * app.stockData[ticker]['Close'][app.day]
            app.AAPLStockValue = int((app.stockCount['AAPL'] * app.stockData['AAPL']['Close'][app.day]) // 1)
            if app.day > 1:
                app.LRIndex = (calculateLeastSquaresRegression(app, app.indexValueList) * 100) // 100
                app.LRMACD = (calculateLeastSquaresRegression(app, app.MACDPortfolioValueList) * 100) // 100
                app.LRAAPLMACD = (calculateLeastSquaresRegression(app, app.AAPLMACDPortfolioValueList) * 100) // 100
                app.LRAAPL = (calculateLeastSquaresRegression(app, app.stockValuesList['AAPL']) * 100) // 100
            if getHighestValue(app, 'AAPL') < (app.stockData['AAPL']['Close'][0] * 1.05) and getLowestValue(app, 'AAPL') > (app.stockData['AAPL']['Close'][0] * .95):
                app.triangleDivisor = 10000
            elif getHighestValue(app, 'AAPL') < (app.stockData['AAPL']['Close'][0] * 1.1) and getLowestValue(app, 'AAPL') > (app.stockData['AAPL']['Close'][0] * .9):
                app.triangleDivisor = 20000
            elif getHighestValue(app, 'AAPL') < (app.stockData['AAPL']['Close'][0] * 1.15) and getLowestValue(app, 'AAPL') > (app.stockData['AAPL']['Close'][0] * .85):
                app.triangleDivisor = 30000
            elif getHighestValue(app, 'AAPL') < (app.stockData['AAPL']['Close'][0] * 1.2) and getLowestValue(app, 'AAPL') > (app.stockData['AAPL']['Close'][0] * .8):
                app.triangleDivisor = 40000
            elif getHighestValue(app, 'AAPL') < (app.stockData['AAPL']['Close'][0] * 1.5) and getLowestValue(app, 'AAPL') > (app.stockData['AAPL']['Close'][0] * .5):
                app.triangleDivisor = 100000

    if app.screen == 2:
        if app.day < int(app.period[:-1]) - 1:
            randomRelativeStrengthIndex(app)
            randomRelativeStrengthIndex(app)
            MSFTRelativeStrengthIndex(app)
            randomRelativeStrengthIndex(app)
            app.indexValue = int(calculateIndexAverage(app) // 1)
            app.indexValueList.append(app.indexValue)
            app.MSFTStockValue = int((app.stockCount['MSFT'] * app.stockData['MSFT']['Close'][app.day]) // 1)
            app.MSFTRSIPortfolioValue = int(calculatePortfolioValue(app, app.MSFTRSICash, app.MSFTRSIPortfolio) // 1)
            app.MSFTRSIPortfolioValueList.append(app.MSFTRSIPortfolioValue)
            app.day += 1
            if app.day > 1:
                app.LRIndex = (calculateLeastSquaresRegression(app, app.indexValueList) * 100) // 100
                app.LRMSFTRSI = (calculateLeastSquaresRegression(app, app.MSFTRSIPortfolioValueList) * 100) // 100
                app.LRMSFT = (calculateLeastSquaresRegression(app, app.stockValuesList['MSFT']) * 100) // 100
            if getHighestValue(app, 'MSFT') < (app.stockData['MSFT']['Close'][0] * 1.05) and getLowestValue(app, 'MSFT') > (app.stockData['MSFT']['Close'][0] * .95):
                app.triangleDivisor = 10000
            elif getHighestValue(app, 'MSFT') < (app.stockData['MSFT']['Close'][0] * 1.1) and getLowestValue(app, 'MSFT') > (app.stockData['MSFT']['Close'][0] * .9):
                app.triangleDivisor = 20000
            elif getHighestValue(app, 'MSFT') < (app.stockData['MSFT']['Close'][0] * 1.15) and getLowestValue(app, 'MSFT') > (app.stockData['MSFT']['Close'][0] * .85):
                app.triangleDivisor = 30000
            elif getHighestValue(app, 'MSFT') < (app.stockData['MSFT']['Close'][0] * 1.2) and getLowestValue(app, 'MSFT') > (app.stockData['MSFT']['Close'][0] * .8):
                app.triangleDivisor = 40000
            elif getHighestValue(app, 'MSFT') < (app.stockData['MSFT']['Close'][0] * 1.5) and getLowestValue(app, 'MSFT') > (app.stockData['MSFT']['Close'][0] * .5):
                app.triangleDivisor = 100000

    if app.screen == 3:
        if app.day < int(app.period[:-1]) - 1:
            AMZNGoldenCross(app)
            randomGoldenCross(app)
            app.indexValue = int(calculateIndexAverage(app) // 1)
            app.indexValueList.append(app.indexValue)
            app.AMZNGCPortfolioValue = int(calculatePortfolioValue(app, app.AMZNGCCash, app.AMZNGCPortfolio) // 1)
            app.AMZNGCPortfolioValueList.append(app.AMZNGCPortfolioValue)
            app.AMZNStockValue = int((app.stockCount['AMZN'] * app.stockData['AMZN']['Close'][app.day]) // 1)
            app.day += 1
            if app.day > 1:
                app.LRIndex = (calculateLeastSquaresRegression(app, app.indexValueList) * 100) // 100
                app.LRAMZNGC = (calculateLeastSquaresRegression(app, app.AMZNGCPortfolioValueList) * 100) // 100
                app.LRAMZN = (calculateLeastSquaresRegression(app, app.stockValuesList['AMZN']) * 100) // 100
            if getHighestValue(app, 'AMZN') < (app.stockData['AMZN']['Close'][0] * 1.05) and getLowestValue(app, 'AMZN') > (app.stockData['AMZN']['Close'][0] * .95):
                app.triangleDivisor = 10000
            elif getHighestValue(app, 'AMZN') < (app.stockData['AMZN']['Close'][0] * 1.1) and getLowestValue(app, 'AMZN') > (app.stockData['AMZN']['Close'][0] * .9):
                app.triangleDivisor = 20000
            elif getHighestValue(app, 'AMZN') < (app.stockData['AMZN']['Close'][0] * 1.15) and getLowestValue(app, 'AMZN') > (app.stockData['AMZN']['Close'][0] * .85):
                app.triangleDivisor = 30000
            elif getHighestValue(app, 'AMZN') < (app.stockData['AMZN']['Close'][0] * 1.2) and getLowestValue(app, 'AMZN') > (app.stockData['AMZN']['Close'][0] * .8):
                app.triangleDivisor = 40000
            elif getHighestValue(app, 'AMZN') < (app.stockData['AMZN']['Close'][0] * 1.5) and getLowestValue(app, 'AMZN') > (app.stockData['AMZN']['Close'][0] * .5):
                app.triangleDivisor = 100000


    if app.screen == 4:
        app.stockRotationNumber += 1
        if app.stockRotationNumber == 8:
            app.stockRotationNumber = 0


def redrawAll(app, canvas):
    if app.screen == 0:
        fontSize = app.width // 40
        canvas.create_rectangle(0, 0, app.width, app.height, fill = '#00FA9B')
        canvas.create_text(app.width / 2, app.height / 8, text = 'Stock Trading', 
            font = f'Chelsea {fontSize}')
        canvas.create_text(app.width / 2, app.height / 8  + 46, text = 'Algorithm Simulator', 
            font = f'Chelsea {fontSize}')

        canvas.create_rectangle(app.width / 4.5, 19 * app.height / 64, 
            app.width / 4.5 + app.startButtonWidth, 19 * app.height / 64 + app.startButtonHeight, fill = '#F08B75', width = 1)
        canvas.create_text(app.width / 4.5 + app.startButtonWidth / 2, 19 * app.height / 64 + app.startButtonHeight / 2, \
            text = 'MACD Algorithm\n       Simulator', font = 'Chelsea 12')

        canvas.create_rectangle(app.width / 4.5, 32 * app.height / 64, 
            app.width / 4.5 + app.startButtonWidth, 32 * app.height / 64 + app.startButtonHeight, fill = '#F08B75', width = 1)
        canvas.create_text(app.width / 4.5 + app.startButtonWidth / 2, 32 * app.height / 64 + app.startButtonHeight / 2, \
            text = 'RSI Algorithm\n   Simulator', font = 'Chelsea 12')
        
        canvas.create_rectangle(app.width / 4.5, 45 * app.height / 64, 
            app.width / 4.5 + app.startButtonWidth, 45 * app.height / 64 + app.startButtonHeight, fill = '#F08B75', width = 1)
        canvas.create_text(app.width / 4.5 + app.startButtonWidth / 2, 45 * app.height / 64 + app.startButtonHeight / 2, \
            text = '      Golden Cross  \n Algorithm Simulator', font = 'Chelsea 12')

        canvas.create_rectangle(3.5 * app.width / 4.5, 32 * app.height / 64, 
            3.5 * app.width / 4.5 - app.startButtonWidth, 32 * app.height / 64 + app.startButtonHeight, fill = '#F08B75', width = 1)
        canvas.create_text(3.5 * app.width / 4.5 - app.startButtonWidth / 2, 32 * app.height / 64 + app.startButtonHeight / 2, \
            text = ' Trade\nStocks', font = 'Chelsea 12')

    if app.screen == 1: #MACD
        canvas.create_rectangle(0, 0, app.width, app.height, fill = '#FFFFFF')
        canvas.create_text(570, 35, text = f'Index Average: ${app.indexValue}')
        if app.LRIndex == 0:
            canvas.create_text(570, 284, text = f'LR Index: 100000')
        elif app.LRIndex > 0:
            canvas.create_text(570, 284, text = f'LR Index: 100000 + {app.LRIndex}')
        else:
            canvas.create_text(570, 284, text = f'LR Index: 100000 {app.LRIndex}')
        canvas.create_text(270, 35, text = f'MACD Portfolio Value: ${app.MACDPortfolioValue}')
        if app.LRMACD == 0:
            canvas.create_text(270, 284, text = f'LR MACD: 100000')
        elif app.LRMACD > 0:
            canvas.create_text(270, 284, text = f'LR MACD: 100000 + {app.LRMACD}')
        else:
            canvas.create_text(270, 284, text = f'LR MACD: 100000 {app.LRMACD}')
        canvas.create_text(270, 305, text = f'AAPL MACD Portfolio Value: ${app.AAPLMACDPortfolioValue}')
        if app.LRAAPLMACD == 0:
            canvas.create_text(270, 556, text = f'LR AAPL MACD: 100000')
        elif app.LRAAPLMACD > 0:
            canvas.create_text(270, 556, text = f'LR AAPL MACD: 100000 + {app.LRAAPLMACD}')
        else:
            canvas.create_text(270, 556, text = f'LR AAPL MACD: 100000 {app.LRAAPLMACD}')
        canvas.create_text(570, 305, text = f'AAPL Portfolio Value: ${app.AAPLStockValue}')
        if app.LRAAPL == 0:
            canvas.create_text(570, 556, text = f'LR AAPL: 100000')
        elif app.LRAAPL > 0:
            canvas.create_text(570, 556, text = f'LR AAPL: 100000 + {app.LRAAPL}')
        else:
            canvas.create_text(570, 556, text = f'LR AAPL: 100000 {app.LRAAPL}')
        canvas.create_text(55, 78, text = f'day: {app.day}')
        canvas.create_rectangle(30, 25, 80, 60, fill = '#F0745A', width = 1)
        canvas.create_text(55, 42, text = 'back', font = 'Chelsea 12')

        #pause button
        #canvas.create_rectangle(30, 90, 80, 125, fill = '#F0745A', width = 1)
        #canvas.create_text(55, 107, text = 'pause', font = 'Chelsea 12')


        #drawMACDPortfolioGraph(app, canvas)
        #drawMarketAverageGraph(app, canvas)
        #drawAAPLMACDPortfolioGraph(app, canvas)
        drawPortfolioGraph(app, canvas, 160, 50, 220, 220, app.MACDPortfolioValueList)
        drawPortfolioGraph(app, canvas, 460, 50, 220, 220, app.indexValueList)
        drawPortfolioGraph(app, canvas, 160, 320, 220, 220, app.AAPLMACDPortfolioValueList)
        drawStockGraph(app, canvas, 460, 320, 220, 220, 'AAPL')
        drawStockGraphBuySellTriangles(app, canvas, 460, 320, 220, 220, 'AAPL')

    if app.screen == 2: #RSI
        canvas.create_rectangle(0, 0, app.width, app.height, fill = '#FFFFFF')
        canvas.create_rectangle(30, 25, 80, 60, fill = '#F0745A', width = 1)
        canvas.create_text(55, 42, text = 'back', font = 'Chelsea 12')
        canvas.create_text(420, 35, text = f'Index Average: ${app.indexValue}')
        if app.LRIndex == 0:
            canvas.create_text(420, 284, text = f'LR Index: 100000 + {app.LRIndex}')
        elif app.LRIndex > 0:
            canvas.create_text(420, 284, text = f'LR Index: 100000 + {app.LRIndex}')
        else:
            canvas.create_text(420, 284, text = f'LR Index: 100000 {app.LRIndex}')
        #canvas.create_text(270, 35, text = f'RSI Portfolio Value: ${app.RSIPortfolioValue}')
        #if app.LRRSI == 0:
        #    canvas.create_text(270, 284, text = f'LR RSI: 100000')
        #elif app.LRRSI > 0:
        #    canvas.create_text(270, 284, text = f'LR RSI: 100000 + {app.LRRSI}')
        #else:
        #    canvas.create_text(270, 284, text = f'LR RSI: 100000 {app.LRRSI}')
        canvas.create_text(270, 305, text = f'MSFT RSI Portfolio Value: ${app.MSFTRSIPortfolioValue}')
        if app.LRMSFTRSI == 0:
            canvas.create_text(270, 556, text = f'LR MSFT RSI: 100000')
        elif app.LRMSFTRSI > 0:
            canvas.create_text(270, 556, text = f'LR MSFT RSI: 100000 + {app.LRMSFTRSI}')
        else:
            canvas.create_text(270, 556, text = f'LR MSFT RSI: 100000 {app.LRMSFTRSI}')
        canvas.create_text(570, 305, text = f'MSFT Portfolio Value: ${app.MSFTStockValue}')
        if app.LRMSFT == 0:
            canvas.create_text(570, 556, text = f'LR MSFT: 100000')
        elif app.LRMSFT > 0:
            canvas.create_text(570, 556, text = f'LR MSFT: 100000 + {app.LRMSFT}')
        else:
            canvas.create_text(570, 556, text = f'LR MSFT: 100000 {app.LRMSFT}')
        canvas.create_text(55, 78, text = f'day: {app.day}')
        drawPortfolioGraph(app, canvas, 310, 50, 220, 220, app.indexValueList)
        drawPortfolioGraph(app, canvas, 160, 320, 220, 220, app.MSFTRSIPortfolioValueList)
        drawStockGraph(app, canvas, 460, 320, 220, 220, 'MSFT')
        drawStockGraphBuySellTriangles(app, canvas, 460, 320, 220, 220, 'MSFT')

    if app.screen == 3: #GC
        canvas.create_rectangle(0, 0, app.width, app.height, fill = '#FFFFFF')
        canvas.create_rectangle(30, 25, 80, 60, fill = '#F0745A', width = 1)
        canvas.create_text(55, 42, text = 'back', font = 'Chelsea 12')
        canvas.create_text(420, 35, text = f'Index Average: ${app.indexValue}')
        if app.LRIndex == 0:
            canvas.create_text(420, 284, text = f'LR Index: 100000 + {app.LRIndex}')
        elif app.LRIndex > 0:
            canvas.create_text(420, 284, text = f'LR Index: 100000 + {app.LRIndex}')
        else:
            canvas.create_text(420, 284, text = f'LR Index: 100000 {app.LRIndex}')
        canvas.create_text(270, 305, text = f'AMZN GC Portfolio Value: ${app.AMZNGCPortfolioValue}')
        if app.LRMSFTRSI == 0:
            canvas.create_text(270, 556, text = f'LR AMZN GC: 100000')
        elif app.LRMSFTRSI > 0:
            canvas.create_text(270, 556, text = f'LR AMZN GC: 100000 + {app.LRAMZNGC}')
        else:
            canvas.create_text(270, 556, text = f'LR AMZN GC: 100000 {app.LRAMZNGC}')
        canvas.create_text(570, 305, text = f'AMZN Portfolio Value: ${app.AMZNStockValue}')
        if app.LRAMZN == 0:
            canvas.create_text(570, 556, text = f'LR AMZN: 100000')
        elif app.LRAMZN > 0:
            canvas.create_text(570, 556, text = f'LR AMZN: 100000 + {app.LRAMZN}')
        else:
            canvas.create_text(570, 556, text = f'LR MSFT: 100000 {app.LRAMZN}')
        canvas.create_text(55, 78, text = f'day: {app.day}')
        drawPortfolioGraph(app, canvas, 310, 50, 220, 220, app.indexValueList)
        drawPortfolioGraph(app, canvas, 160, 320, 220, 220, app.AMZNGCPortfolioValueList)
        drawStockGraph(app, canvas, 460, 320, 220, 220, 'AMZN')
        drawStockGraphBuySellTriangles(app, canvas, 460, 320, 220, 220, 'AMZN')


    if app.screen == 4: #Buy and Sell Stocks
        canvas.create_rectangle(0, 0, app.width, app.height, fill = '#FFFFFF')
        #reset button
        canvas.create_rectangle(100, 25, 150, 60, fill = '#F0745A', width = 1)
        canvas.create_text(125, 42, text = 'reset', font = 'Chelsea 12')
        #back button
        canvas.create_rectangle(30, 25, 80, 60, fill = '#F0745A', width = 1)
        canvas.create_text(55, 42, text = 'back', font = 'Chelsea 12')

        #next day
        canvas.create_text(83, 100, text = f'Day: {app.day}', font = 'Chelsea 12')
        canvas.create_text(90, 140, text = f'Next Day', font = 'Chelsea 12')
        canvas.create_polygon(138, 120, 138, 164, 173, 142, fill = 'green')

        #Buy and sell buttons
        canvas.create_rectangle(app.width / 16, 19 * app.height / 64, 
            app.width / 16 + app.startButtonWidth, 19 * app.height / 64 + app.startButtonHeight * 2 / 3, fill = 'green', width = 1)
        canvas.create_text(app.width / 16 + app.startButtonWidth / 2, 19 * app.height / 64 + app.startButtonHeight / 3, \
            text = 'Buy a stock', font = 'Chelsea 12')

        canvas.create_rectangle(app.width / 16, 26 * app.height / 64, 
            app.width / 16 + app.startButtonWidth, 26 * app.height / 64 + app.startButtonHeight * 2 / 3, fill = 'red', width = 1)
        canvas.create_text(app.width / 16 + app.startButtonWidth / 2, 26 * app.height / 64 + app.startButtonHeight / 3, \
            text = 'Sell a stock', font = 'Chelsea 12')

        #back and forth triangles for stockRotation
        canvas.create_polygon(80, 345, 120, 325, 120, 365, fill = 'green')
        canvas.create_polygon(141, 325, 141, 365, 175, 345, fill = 'green')

        #draw main portfolio
        drawPortfolioGraph(app, canvas, 300, 47, 300, 300, app.userPortfolioValueList)
        canvas.create_text(380, 30, text = f'Portfolio Value: ${round(app.userPortfolioValue, 2)}')
        canvas.create_text(530, 30, text = f'Portfolio Cash: ${round(app.userCash, 2)}')
        drawStockRotation(app, canvas)
        drawUserPortfolioList(app, canvas)



runApp(width = 800, height = 600)
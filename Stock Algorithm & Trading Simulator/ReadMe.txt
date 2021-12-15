Overview:
This app has two main purposes: First to demonstrate how various stocks will be traded using
various stock indicators, and to show whether these indicator algorithms can beat the market
as represented by the Dow Jones. Second is to allow to user to buy their own stocks from a list
of 24, and see how well they can do in the stock market based on the current graphs of the
available stocks.

How To Use:
- To open the program go into:
Github Stock Simulator => yfinance-main => animationsAndFunctions.py 
- To see the indicator algorithms, click on any of the three buttons on the left side of the
starting screen. The user will see 3-4 graphs on each screen: an index (Dow Jones), a stock, 
a portfolio of one stock being traded using the indicator, and just on the MACD screen, a
graph of random stocks being traded using the MACD indicator. Every second or so a day passes
and the user can see the progression of each of the portfolios/graphs. On the stock graphs,
the green triangles represent when the algorithm says to buy, and the red triangles represent
when the algorithm says to sell. You can see the values of the portfolios above each graph, 
and the linear regression lines of each portfolio below each graph.
- To use the stock trading simulator, click on "Trade Stocks". A screen will appear with a 
back button taking you back to the homescreen, a reset button bring the portfolio back to the
original and the day/stock graphs back to day 1. There is a triangle that can be clicked to
move forward a certain number of days, which will cause the graphs to display how your
portfolio and the stocks at the bottom have done. On the right side of the screen is a list
of available tickers to buy, and how many of the stocks for those tickers are in the users
portfolio. There is a buy stock button where the user can enter a ticker in capital letters 
as shown on the right, then enter how many of that stock they want, and that stock will be 
added to their portfolio. The sell stock button does the opposite. Then on the bottom there
are three graphs of stocks that rotate every 12 seconds. These are meant to allow the user 
to see the progress of the stocks up to the current date to decide based on their momentum
whether to buy or sell. Lastly, right below the sell button are two arrows that move the
stock rotation forwards or backwards.

How It Works:
This program uses the yfinance api to get data from the past 100 days of the stock market. 
It creates portfolios traded with algorithms that use the recommended trading strategy for
each momentum indicator. The graphs are made using the values of the portfolios and can
scale up 2 times the portfolio's original value. 
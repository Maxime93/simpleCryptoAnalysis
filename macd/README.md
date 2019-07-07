# simpleCryptoAnalysis

https://towardsdatascience.com/cryptocurrency-analysis-with-python-macd-452ceb251d7c

### Strategy
We are going to apply Moving Average Convergence Divergence (MACD) trading strategy, which is a popular indicator used in technical analysis. MACD calculates two moving averages of varying lengths to identify trend direction and duration. Then, it takes the difference in values between those two moving averages (MACD line) and an exponential moving average (signal line) of those moving averages.
We will simulate:
- exit trade (sell) when MACD line crosses below the MACD signal line,
- enter the trade (buy) when MACD line crosses above the MACD signal line.


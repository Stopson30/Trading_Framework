# Trading_Framework
System of files and IT architecture behind trading n assets all price-based. Assume $500k initial bankroll, 0.05% slippage, 1% txn fee, high volatility assets preferred with low or negative correlation. If an asset goes up x%, we sell in increments of 10k. If it goes down, we do the same. Expandable into 3 assets. Traditional stock & crypto. Data from yf.

Possible enhancements:

Allow the stop loss level to be a parameter
Use a more sophisticated method to distribute proceeds from a sale (e.g., considering factors such as expected return or volatility)
Consider transaction fees and slippage when determining whether a price change is sufficient to trigger a transaction
Consider more sophisticated risk management strategies, such as using options to hedge downside risk
Use a machine learning model to predict price changes and adjust the strategy accordingly
Use more sophisticated performance metrics and risk measures
Use a more realistic data source that includes bid/ask spread and volume
Consider other assets and diversification strategies
Include taxes in the calculations (which can have a significant impact on net returns)
Include consideration for correlations between the assets to minimize risk

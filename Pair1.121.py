#doesn't calculate the bankroll/ portfolio balance correctly

import pandas as pd
import yfinance as yf
import openpyxl
import os
from datetime import datetime

# Constants
ASSETS = ['TSLA', 'ETH-USD']
START_DATE = '2021-01-01'
END_DATE = '2023-07-01'
INITIAL_INVESTMENT = 10000
BANKROLL = 500000
REBUY_AMOUNT = 10000
SELL_TRIGGER = 1.05  # 5% gain
BUY_TRIGGER = 0.95   # 5% loss

# Prepare data
asset_data = {}
for asset in ASSETS:
    asset_data[asset] = yf.download(asset, start=START_DATE, end=END_DATE)

# Initialize portfolio and bankroll
portfolio = {asset: INITIAL_INVESTMENT / asset_data[asset]['Close'].iloc[0] for asset in ASSETS}
bankroll = BANKROLL - 2 * INITIAL_INVESTMENT  # 2 assets, 10k each

# Prepare excel writer
home = os.path.expanduser("~")
writer = pd.ExcelWriter(os.path.join(home, 'backtest_results.xlsx'), engine='openpyxl')

# Track transactions
transactions = []

for asset in ASSETS:
    prev_close = asset_data[asset]['Close'].iloc[0]

    for date, row in asset_data[asset].iterrows():
        close_price = row['Close']
        value = portfolio[asset] * close_price

        if close_price >= prev_close * SELL_TRIGGER and value >= REBUY_AMOUNT:
            # Sell
            sell_amount = REBUY_AMOUNT / close_price
            portfolio[asset] -= sell_amount
            bankroll += REBUY_AMOUNT
            transactions.append({
                'Date': date,
                'Asset': asset,
                'Action': 'Sell',
                'Amount': sell_amount,
                'Price': close_price,
                'Bankroll': bankroll,
                'Portfolio Value': portfolio[asset] * close_price
            })

        elif close_price <= prev_close * BUY_TRIGGER and bankroll >= REBUY_AMOUNT:
            # Buy
            buy_amount = REBUY_AMOUNT / close_price
            portfolio[asset] += buy_amount
            bankroll -= REBUY_AMOUNT
            transactions.append({
                'Date': date,
                'Asset': asset,
                'Action': 'Buy',
                'Amount': buy_amount,
                'Price': close_price,
                'Bankroll': bankroll,
                'Portfolio Value': portfolio[asset] * close_price
            })

        prev_close = close_price

# Save to Excel
df = pd.DataFrame(transactions)
df.to_excel(writer, index=False)
writer.close()

print("Backtesting completed. Results saved to 'backtest_results.xlsx' in the home directory.")

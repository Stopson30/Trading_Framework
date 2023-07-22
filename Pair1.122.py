#CORRECT EXCEL but trading at random (as instructed)


import yfinance as yf
import pandas as pd
import numpy as np
import random
import os

# Download historical data
start_date = '2021-01-01'
end_date = '2023-06-01'

eth = yf.download('ETH-USD', start=start_date, end=end_date)
tsla = yf.download('TSLA', start=start_date, end=end_date)

# Initialize trading variables
balance = 100000
eth_quantity = 0
tsla_quantity = 0
investment = 200
transactions = []
bankroll = []

# Get intersection of the dates for which both ETH and TSLA data is available
common_dates = eth.index.intersection(tsla.index)

# Simulate trading
for date in common_dates:
    # Pick a random choice of either buying ETH, buying TSLA, or doing nothing if balance is insufficient
    if balance >= investment:
        choice = random.choice(['ETH', 'TSLA', 'NOTHING'])
    else:
        choice = 'NOTHING'
    
    eth_price = eth.loc[date]['Close']
    tsla_price = tsla.loc[date]['Close']

    if choice == 'ETH':
        eth_quantity += investment / eth_price
        balance -= investment
        action = 'Bought ETH'
    elif choice == 'TSLA':
        tsla_quantity += investment / tsla_price
        balance -= investment
        action = 'Bought TSLA'
    else:
        action = 'Did nothing'

    portfolio_value = eth_quantity * eth_price + tsla_quantity * tsla_price
    bankroll.append(balance)
    
    transactions.append([date.date(), balance, eth_quantity, tsla_quantity, eth_price, tsla_price, action])

# Prepare pandas DataFrame for the transactions
df_transactions = pd.DataFrame(transactions, columns=['Date', 'Balance', 'ETH Quantity', 'TSLA Quantity', 'ETH Price', 'TSLA Price', 'Action'])

# Save the transaction data to Excel
filename = os.path.join(os.path.expanduser('~'), 'transaction_data.xlsx')

with pd.ExcelWriter(filename) as writer:  
    df_transactions.to_excel(writer, sheet_name='Transactions', index=False)
    
    # Save the portfolio and bankroll data in new sheets in the same workbook
    df_portfolio = pd.DataFrame({'Portfolio': [balance + eth_quantity * eth.loc[date]['Close'] + tsla_quantity * tsla.loc[date]['Close'] for date in common_dates]}, index=common_dates)
    df_bankroll = pd.DataFrame({'Bankroll': bankroll}, index=common_dates)

    df_portfolio.to_excel(writer, sheet_name='Portfolio')
    df_bankroll.to_excel(writer, sheet_name='Bankroll')

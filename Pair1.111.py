import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define the transaction fee
transaction_fee = 0.01  # 1%

# Define the total bankroll
total_bankroll = 100000  # $100k

# Initial investment in each asset
initial_investment = 10000  # $10k

# Define slippage
slippage = 0.0005  # 0.05%

# Download historical data from Yahoo Finance
matic_data = yf.download('MATIC-USD', start='2022-07-03', end='2023-07-03')
eth_data = yf.download('ETH-USD', start='2022-07-03', end='2023-07-03')

# Forward fill any missing data
matic_data.ffill(inplace=True)
eth_data.ffill(inplace=True)

def backtest(change_threshold):
    matic_quantity = initial_investment / matic_data.iloc[0]['Open']
    eth_quantity = initial_investment / eth_data.iloc[0]['Open']
    matic_quantity = matic_quantity * (1 - transaction_fee) * (1 - slippage)
    eth_quantity = eth_quantity * (1 - transaction_fee) * (1 - slippage)
    total_bankroll_remaining = total_bankroll - 2 * initial_investment
    total_fees_paid = 2 * initial_investment * transaction_fee
    portfolio_values = pd.DataFrame(index=matic_data.index, columns=['value'])
    portfolio_values.iloc[0]['value'] = total_bankroll_remaining + matic_quantity * matic_data.iloc[0]['Open'] + eth_quantity * eth_data.iloc[0]['Open']

    for i in range(1, len(matic_data)):
        current_matic_price = matic_data.iloc[i]['Open']
        current_eth_price = eth_data.iloc[i]['Open']
        matic_change = (current_matic_price - matic_data.iloc[i-1]['Open']) / matic_data.iloc[i-1]['Open']
        eth_change = (current_eth_price - eth_data.iloc[i-1]['Open']) / eth_data.iloc[i-1]['Open']

        if matic_change > change_threshold and eth_change < -change_threshold:
            total_fees_paid += matic_quantity * current_matic_price * transaction_fee
            total_bankroll_remaining += matic_quantity * current_matic_price * (1 - transaction_fee) * (1 - slippage)
            matic_quantity = 0
            buy_eth = total_bankroll_remaining / 2
            eth_quantity += buy_eth / current_eth_price * (1 - transaction_fee) * (1 - slippage)
            total_fees_paid += buy_eth * transaction_fee
            total_bankroll_remaining -= buy_eth

        elif matic_change < -change_threshold and eth_change > change_threshold:
            total_fees_paid += eth_quantity * current_eth_price * transaction_fee
            total_bankroll_remaining += eth_quantity * current_eth_price * (1 - transaction_fee) * (1 - slippage)
            eth_quantity = 0
            buy_matic = total_bankroll_remaining / 2
            matic_quantity += buy_matic / current_matic_price * (1 - transaction_fee) * (1 - slippage)
            total_fees_paid += buy_matic * transaction_fee
            total_bankroll_remaining -= buy_matic

        elif abs(matic_change) > change_threshold and abs(eth_change) > change_threshold:
            if matic_change > 0:  # If both went up, sell both
                total_fees_paid += (matic_quantity * current_matic_price + eth_quantity * current_eth_price) * transaction_fee
                total_bankroll_remaining += matic_quantity * current_matic_price * (1 - transaction_fee) * (1 - slippage)
                total_bankroll_remaining += eth_quantity * current_eth_price * (1 - transaction_fee) * (1 - slippage)
                matic_quantity = 0
                eth_quantity = 0
            else:  # If both went down, buy more of both
                buy_matic = total_bankroll_remaining / 2
                matic_quantity += buy_matic / current_matic_price * (1 - transaction_fee) * (1 - slippage)
                total_fees_paid += buy_matic * transaction_fee
                total_bankroll_remaining -= buy_matic
                buy_eth = total_bankroll_remaining
                eth_quantity += buy_eth / current_eth_price * (1 - transaction_fee) * (1 - slippage)
                total_fees_paid += buy_eth * transaction_fee
                total_bankroll_remaining = 0

        portfolio_values.iloc[i]['value'] = total_bankroll_remaining + matic_quantity * current_matic_price + eth_quantity * current_eth_price

    final_value = total_bankroll_remaining + matic_quantity * matic_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage) + eth_quantity * eth_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage)

    total_return = (final_value - 100000) / 100000
    annualized_return = (1 + total_return) ** (365.25 / len(portfolio_values)) - 1
    max_drawdown = (portfolio_values['value'].cummax() - portfolio_values['value']).max() / portfolio_values['value'].cummax().max()
    sharpe_ratio = (annualized_return - 0.01) / (portfolio_values['value'].pct_change().std() * np.sqrt(252))

    final_matic_value = initial_investment / matic_data.iloc[0]['Open'] * matic_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage)
    final_eth_value = initial_investment / eth_data.iloc[0]['Open'] * eth_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage)

    return final_value, sharpe_ratio, total_fees_paid, final_matic_value, final_eth_value

change_thresholds = np.arange(0.01, 0.10, 0.01)  # 1% to 10% with a step of 1%
results = []

best_sharpe_ratio = -np.inf
best_change_threshold = None
best_final_value = 0

for change_threshold in change_thresholds:
    final_value, sharpe_ratio, total_fees_paid, final_matic_value, final_eth_value = backtest(change_threshold)
    results.append((final_value, sharpe_ratio, total_fees_paid, final_matic_value, final_eth_value))

    if sharpe_ratio > best_sharpe_ratio:
        best_sharpe_ratio = sharpe_ratio
        best_change_threshold = change_threshold
        best_final_value = final_value

plt.figure(figsize=(12, 6))
plt.plot(change_thresholds, [r[0] for r in results], label='Final value')
plt.plot(change_thresholds, [r[1]*100000 for r in results], label='Sharpe ratio x 100k')
plt.legend()
plt.xlabel('Change threshold')
plt.title('Backtest results over different change thresholds')
plt.show()

print(f"Best change threshold: {best_change_threshold * 100}%")
print(f"Best final portfolio value: ${best_final_value}")
print(f"Best Sharpe ratio: {best_sharpe_ratio}")
print(f"Final value if held MATIC: ${results[-1][3]}")
print(f"Final value if held ETH: ${results[-1][4]}")
print(f"Total fees paid: ${results[-1][2]}")

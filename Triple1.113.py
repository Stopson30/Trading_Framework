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

# Define stop loss level
stop_loss = 0.30  # 30%

# Download historical data from Yahoo Finance
tsla_data = yf.download('TSLA', start='2022-07-03', end='2023-07-03')
eth_data = yf.download('ETH-USD', start='2022-07-03', end='2023-07-03')
matic_data = yf.download('MATIC-USD', start='2022-07-03', end='2023-07-03')

# Forward fill any missing data
tsla_data.ffill(inplace=True)
eth_data.ffill(inplace=True)
matic_data.ffill(inplace=True)

# Define the backtest function
def backtest(change_threshold):
    # Initialize quantities
    tsla_quantity = initial_investment / tsla_data.iloc[0]['Open']
    eth_quantity = initial_investment / eth_data.iloc[0]['Open']
    matic_quantity = initial_investment / matic_data.iloc[0]['Open']
    tsla_quantity = tsla_quantity * (1 - transaction_fee) * (1 - slippage)
    eth_quantity = eth_quantity * (1 - transaction_fee) * (1 - slippage)
    matic_quantity = matic_quantity * (1 - transaction_fee) * (1 - slippage)

    # Initialize other variables
    total_bankroll_remaining = total_bankroll - 3 * initial_investment
    total_fees_paid = 3 * initial_investment * transaction_fee
    portfolio_values = pd.DataFrame(index=tsla_data.index, columns=['value'])
    portfolio_values.iloc[0]['value'] = total_bankroll_remaining + tsla_quantity * tsla_data.iloc[0]['Open'] + eth_quantity * eth_data.iloc[0]['Open'] + matic_quantity * matic_data.iloc[0]['Open']
    max_value = portfolio_values.iloc[0]['value']

    # Loop over each day
    for i in range(1, len(tsla_data)):
        # Calculate price changes
        current_tsla_price = tsla_data.iloc[i]['Open']
        current_eth_price = eth_data.iloc[i]['Open']
        current_matic_price = matic_data.iloc[i]['Open']
        tsla_change = (current_tsla_price - tsla_data.iloc[i - 1]['Open']) / tsla_data.iloc[i - 1]['Open']
        eth_change = (current_eth_price - eth_data.iloc[i - 1]['Open']) / eth_data.iloc[i - 1]['Open']
        matic_change = (current_matic_price - matic_data.iloc[i - 1]['Open']) / matic_data.iloc[i - 1]['Open']
        portfolio_value = total_bankroll_remaining + tsla_quantity * current_tsla_price + eth_quantity * current_eth_price + matic_quantity * current_matic_price
        portfolio_values.iloc[i]['value'] = portfolio_value

        # Check for stop loss
        max_value = max(max_value, portfolio_value)
        if portfolio_value < (1 - stop_loss) * max_value:
            break

        # Check price changes and perform transactions
        # Similar logic as before, but now considering three assets
        # For simplicity, proceeds from a sale are split equally between the two other assets
        # In a more advanced model, you might want to consider factors such as relative volatility or expected return
        if abs(tsla_change) > change_threshold:
            total_fees_paid += tsla_quantity * current_tsla_price * transaction_fee
            proceeds = tsla_quantity * current_tsla_price * (1 - transaction_fee) * (1 - slippage)
            tsla_quantity = 0
            eth_quantity += proceeds / (2 * current_eth_price) * (1 - transaction_fee) * (1 - slippage)
            matic_quantity += proceeds / (2 * current_matic_price) * (1 - transaction_fee) * (1 - slippage)
            total_fees_paid += proceeds * transaction_fee

        if abs(eth_change) > change_threshold:
            total_fees_paid += eth_quantity * current_eth_price * transaction_fee
            proceeds = eth_quantity * current_eth_price * (1 - transaction_fee) * (1 - slippage)
            eth_quantity = 0
            tsla_quantity += proceeds / (2 * current_tsla_price) * (1 - transaction_fee) * (1 - slippage)
            matic_quantity += proceeds / (2 * current_matic_price) * (1 - transaction_fee) * (1 - slippage)
            total_fees_paid += proceeds * transaction_fee

        if abs(matic_change) > change_threshold:
            total_fees_paid += matic_quantity * current_matic_price * transaction_fee
            proceeds = matic_quantity * current_matic_price * (1 - transaction_fee) * (1 - slippage)
            matic_quantity = 0
            tsla_quantity += proceeds / (2 * current_tsla_price) * (1 - transaction_fee) * (1 - slippage)
            eth_quantity += proceeds / (2 * current_eth_price) * (1 - transaction_fee) * (1 - slippage)
            total_fees_paid += proceeds * transaction_fee

    final_value = total_bankroll_remaining + tsla_quantity * tsla_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage) + eth_quantity * eth_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage) + matic_quantity * matic_data.iloc[-1]['Close'] * (1 - transaction_fee) * (1 - slippage)

    total_return = (final_value - 100000) / 100000
    annualized_return = (1 + total_return) ** (365.25 / len(portfolio_values)) - 1
    max_drawdown = (portfolio_values['value'].max() - portfolio_values['value'].min()) / portfolio_values['value'].max()
    volatility = portfolio_values['value'].pct_change().std() * np.sqrt(len(portfolio_values))
    sharpe_ratio = (annualized_return - 0.01) / volatility  # Assume 1% risk-free rate
    calmar_ratio = annualized_return / max_drawdown
    sortino_ratio = (annualized_return - 0.01) / portfolio_values['value'].pct_change()[portfolio_values['value'].pct_change() < 0].std() * np.sqrt(len(portfolio_values))

    return final_value, sharpe_ratio, total_fees_paid, calmar_ratio, sortino_ratio, portfolio_values

change_thresholds = np.arange(0.01, 0.1, 0.01)
results = []
for change_threshold in change_thresholds:
    results.append(backtest(change_threshold))

best_change_threshold = change_thresholds[np.argmax([x[1] for x in results])]  # Select the change threshold with the highest Sharpe ratio
best_final_value = max([x[0] for x in results])
best_sharpe_ratio = max([x[1] for x in results])
best_calmar_ratio = max([x[3] for x in results])
best_sortino_ratio = max([x[4] for x in results])

plt.figure(figsize=(10, 6))
plt.plot(change_thresholds * 100, [x[0] for x in results], label='Final portfolio value')
plt.plot(change_thresholds * 100, [x[1] * 100000 for x in results], label='Sharpe ratio x 100k')
plt.plot(change_thresholds * 100, [x[3] for x in results], label='Calmar ratio')
plt.plot(change_thresholds * 100, [x[4] for x in results], label='Sortino ratio')
plt.legend()
plt.xlabel('Change threshold (%)')
plt.title('Backtest results over different change thresholds')
plt.show()

print(f"Best change threshold: {best_change_threshold * 100}%")
print(f"Best final portfolio value: ${best_final_value}")
print(f"Best Sharpe ratio: {best_sharpe_ratio}")
print(f"Best Calmar ratio: {best_calmar_ratio}")
print(f"Best Sortino ratio: {best_sortino_ratio}")
print(f"Total fees paid: ${sum([x[2] for x in results])}")

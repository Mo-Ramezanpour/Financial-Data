import yfinance as yf
import pandas as pd

# Fetch Intel data
intel = yf.Ticker("INTC")

# Get quarterly financials, balance sheet, and cash flow
quarterly_financials = intel.quarterly_financials
quarterly_balance_sheet = intel.quarterly_balance_sheet
quarterly_cashflow = intel.quarterly_cashflow

# Define the keys to fetch from financials, balance sheet, and cashflow
keys = {
    "Revenue": "Total Revenue",
    "Total Expenses": "Total Expenses",
    "Gross Margin": "Gross Profit",
    "Net Income": "Net Income",
    "Operating Income": "Operating Income",  # EBIT equivalent
    "Operating Expenses": "Operating Expense",
    "Operating Cash Flow": "Operating Cash Flow",
    "Free Cash Flow": "Free Cash Flow",
    "Total Assets": "Total Assets",
    "Total Liabilities": "Total Liabilities Net Minority Interest",
    "Interest Expense": "Interest Expense"
}

# Function to get quarterly data


def get_quarterly_data(data_source, label, key):
    if label in data_source.index:
        return data_source.loc[label].iloc[key]
    return None  # Return None if data is not available


# Fetch the data for Q1 and Q2
data = {
    "Q1": {key: get_quarterly_data(quarterly_financials, value, 1) or
           get_quarterly_data(quarterly_balance_sheet, value, 1) or
           get_quarterly_data(quarterly_cashflow, value, 1)
           for key, value in keys.items()},

    "Q2": {key: get_quarterly_data(quarterly_financials, value, 0) or
           get_quarterly_data(quarterly_balance_sheet, value, 0) or
           get_quarterly_data(quarterly_cashflow, value, 0)
           for key, value in keys.items()}
}

# Convert the dictionary to a DataFrame for better visualization
df = pd.DataFrame(data)

# Add important credit risk ratios
df.loc['Debt-to-Equity Ratio'] = df.loc['Total Liabilities'] / \
    df.loc['Total Assets']
df.loc['Interest Coverage Ratio'] = df.loc['Operating Income'] / \
    df.loc['Interest Expense']
df.loc['Return on Assets (ROA)'] = df.loc['Net Income'] / \
    df.loc['Total Assets']
df.loc['Leverage Ratio'] = df.loc['Total Liabilities'] / df.loc['Total Assets']

# Z-score calculation (Altman Z-score formula)
working_capital = df.loc['Total Assets'] - df.loc['Total Liabilities']
retained_earnings = df.loc['Net Income']  # Simplified assumption
market_value_of_equity = 1.0  # This would need stock price and shares outstanding

z_scores = 1.2 * (working_capital / df.loc['Total Assets']) + \
    1.4 * (retained_earnings / df.loc['Total Assets']) + \
    3.3 * (df.loc['Operating Income'] / df.loc['Total Assets']) + \
    0.6 * (market_value_of_equity / df.loc['Total Liabilities']) + \
    1.0 * (df.loc['Revenue'] / df.loc['Total Assets'])

df.loc['Z-Score'] = z_scores

# Risk categorization for Z-Score


def zscore_risk_category(z):
    if z > 2.99:
        return "Low risk"
    elif 1.81 <= z <= 2.99:
        return "Medium risk"
    else:
        return "High risk"

# Risk categorization for Debt-to-Equity Ratio


def debt_equity_risk_category(de_ratio):
    if de_ratio < 0.5:
        return "Low risk"
    elif 0.5 <= de_ratio <= 1.5:
        return "Medium risk"
    else:
        return "High risk"

# Risk categorization for Interest Coverage Ratio


def interest_coverage_risk_category(icr):
    if icr > 3:
        return "Low risk"
    elif 1.5 <= icr <= 3:
        return "Medium risk"
    else:
        return "High risk"


# Add percentage formatting and risk level
df.loc['Debt-to-Equity Ratio Risk'] = df.loc['Debt-to-Equity Ratio'].map(
    debt_equity_risk_category)
df.loc['Interest Coverage Ratio Risk'] = df.loc['Interest Coverage Ratio'].map(
    interest_coverage_risk_category)
df.loc['Z-Score Risk'] = df.loc['Z-Score'].map(zscore_risk_category)

# Format percentages for ratios
# Convert to %
df.loc['Return on Assets (ROA)'] = df.loc['Return on Assets (ROA)'] * 100
df.loc['Return on Assets (ROA)'] = df.loc['Return on Assets (ROA)'].map(
    lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x)
df.loc['Debt-to-Equity Ratio'] = df.loc['Debt-to-Equity Ratio'].map(
    lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
df.loc['Interest Coverage Ratio'] = df.loc['Interest Coverage Ratio'].map(
    lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
df.loc['Leverage Ratio'] = df.loc['Leverage Ratio'].map(
    lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
df.loc['Z-Score'] = df.loc['Z-Score'].map(
    lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)

# Format all financial figures with commas and two decimal places
df = df.map(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)

# Handle potential nan values in Z-Score and ratios
df.fillna("N/A", inplace=True)

# Display the DataFrame
print("\nIntel Financial Data with Credit Risk Ratios, Z-Score, and Risk Levels:")
print(df)

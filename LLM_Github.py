#!/usr/bin/env python
# coding: utf-8

# In[10]:


from datetime import datetime, timedelta
import requests
import pandas as pd

def fetch_news_by_date(api_key, company):
    # Define the current time in PST
    current_time = datetime.now() - timedelta(hours=7)  # Adjust for PST
    start_time = current_time - timedelta(days=1) + timedelta(hours=13)  # 1 PM previous day
    end_time = current_time + timedelta(hours=13)  # 1 PM current day

    # Format dates
    from_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    to_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Build URL
    url = (f'https://newsapi.org/v2/everything?'
           f'q={company}&'
           f'from={from_str}&'
           f'to={to_str}&'
           f'sortBy=relevancy&'
           f'apiKey={api_key}&'
           f'language=en')
    
    # Fetch data
    response = requests.get(url)
    data = response.json()
    
    # Add articles to the list
    articles = data.get('articles', [])
    for article in articles:
        article['fetch_date'] = current_time.strftime('%Y-%m-%d')
        article['company'] = company
    
    # Convert list of articles to DataFrame
    df = pd.DataFrame(articles)
    return df

def get_stock_trend(api_key, symbol):
    # Define the API endpoint and parameters
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '60min',
        'apikey': api_key
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract time series data
    time_series = data.get('Time Series (60min)', {})
    
    # Get the latest and previous day's closing prices
    if not time_series:
        raise ValueError(f"Could not retrieve data for {symbol}. Please check your API key and network connection.")
    
    # Find the latest and previous day's data
    today_date = datetime.now().strftime('%Y-%m-%d')
    closing_prices = []
    for timestamp, values in time_series.items():
        date = timestamp.split()[0]
        if date == today_date:
            closing_prices.append(float(values['4. close']))
    
    if len(closing_prices) < 2:
        raise ValueError(f"Not enough data for today's trading to determine the trend for {symbol}.")
    
    # Determine the trend
    latest_close = closing_prices[0]
    previous_close = closing_prices[-1]
    
    trend = "Up" if latest_close > previous_close else "Down"
    return trend

# List of companies and their stock symbols
companies = {
    'Apple': 'AAPL',
    'Amazon': 'AMZN',
    'Disney': 'DIS',
    'Google': 'GOOGL',
    'Netflix': 'NFLX',
    'Nvidia': 'NVDA',
    'Tesla': 'TSLA'
}

# Your Alpha Vantage API key
alpha_vantage_api_key = 'C5094DG9ITHLDY0R'
news_api_key = 'f28b3f1b39c84a34b8ac8e566dee7c2a'

# Fetch news for all companies and concatenate the results
all_responses = pd.concat([fetch_news_by_date(news_api_key, company) for company in companies], ignore_index=True)

# Clean the data
all_responses = all_responses.dropna(subset=['description'])
all_responses = all_responses[all_responses['description'] != '[Removed]']

# Fetch trends for all companies
trends = {}
for company, symbol in companies.items():
    try:
        trend = get_stock_trend(alpha_vantage_api_key, symbol)
        trends[company] = trend
    except ValueError as e:
        print(e)
        trends[company] = None

# Add "Up/Down" column to all_responses
all_responses['Up/Down'] = all_responses['company'].map(trends)

# Trim all_responses to the specified columns and order
all_responses = all_responses.rename(columns={'company': 'Company', 'fetch_date': 'Date'})
trimmed_responses = all_responses[['Company', 'title', 'description', 'Date', 'Up/Down']]

# Save to CSV
trimmed_responses.to_csv('articles.csv', index=False)


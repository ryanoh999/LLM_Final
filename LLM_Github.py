#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

# List of companies
companies = ['Apple', 'Amazon', 'Disney', 'Google', 'Netflix', 'Nvidia', 'Tesla']

# Example API key usage
api_key = 'YOUR_NEWS_API_KEY'

# Fetch news for all companies and concatenate the results
all_responses = pd.concat([fetch_news_by_date(api_key, company) for company in companies], ignore_index=True)

# Clean the data
all_responses = all_responses.dropna(subset=['description'])
all_responses = all_responses[all_responses['description'] != '[Removed]']

# Save to CSV
all_responses.to_csv('stockmarket_daily.csv', index=False)


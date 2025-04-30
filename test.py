import yfinance as yf

ticker = yf.Ticker("META")
news_data = ticker.news

# Let's take the first news article
if news_data:
    article = news_data[0]
    content = article.get('content', {})

    title = content.get('title')
    summary = content.get('summary')
    url = content.get('clickThroughUrl', {}).get('url')
    image_url = content.get('thumbnail', {}).get('originalUrl')
    provider = content.get('provider', {}).get('displayName')
    pub_date = content.get('pubDate')

    print("Title:", title)
    print("Summary:", summary)
    print("URL:", url)
    print("Image URL:", image_url)
    print("Provider:", provider)
    print("Published Date:", pub_date)
else:
    print("No news articles available.")

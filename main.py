import os
import requests
from twilio.rest import Client
import smtplib 
from dotenv import load_dotenv

load_dotenv()

STOCK = "AMZN"
COMPANY_NAME = "Amazon.com, Inc."

#You can get your free key from alphavantage.co
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

#newsapi.org key
NEWS_KEY = os.getenv("NEWS_KEY")

#twilio
ACCAUNT_SID = os.getenv("ACCAUN_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

#Mail
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


alpha_vantage_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHA_VANTAGE_KEY
}

def change_percentage():
    stock_r = requests.get("https://www.alphavantage.co/query?", params=alpha_vantage_parameters)
    stock_r.raise_for_status()
    stock_data = stock_r.json()["Time Series (Daily)"]
    stock_list = list(stock_data)
    yesterday = stock_list[0]
    day_after = stock_list[1]
    yesterday_close = float(stock_data[yesterday]['4. close'])
    day_after_close = float(stock_data[day_after]['4. close'])
    close_difference = yesterday_close - day_after_close
    if close_difference > 0:
        percentage = close_difference * (100/day_after_close)
        increase = "increased"
        return (increase, percentage)
    elif close_difference < 0:
        difference = close_difference*-1
        percentage = difference * (100/day_after_close)
        decrease = "decreased"
        return (decrease, percentage)
    else:
        percentage = None
        no_change = "not changed"
        return no_change, percentage

is_increased = change_percentage()[0]
change =  round(change_percentage()[1], 3)
change_mail = f"Amazon Prices {is_increased} by {change}%"

newsapi_parameters = {
    "q": "Amazon",
    "category": "business",
    "sortBy": "publishedAt",
    "apiKEY": NEWS_KEY,
    "pageSize": 3,
    "page": 1,
    "country": "us",

}

def get_news():
    news_r = requests.get("https://newsapi.org/v2/top-headlines?", params=newsapi_parameters)
    news_r.raise_for_status()
    news_data = news_r.json()["articles"]
    article_list = [articles for articles in news_data]
    articles_ready = []
    for data in article_list:
        title = data["title"]
        description = data["description"]
        url = data["url"]
        message = f"Headline: {title}\n {description} \n for more: {url}"
        articles_ready.append(message)
    if len(articles_ready) >= 3:
        return articles_ready[:2]
    else:
        return articles_ready


news = get_news()
print(get_news())
mail_news = "\n".join(news)

mail_notification = f"{change_mail} \n {mail_news}"

print(mail_notification)

with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()
    connection.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    connection.sendmail(
        from_addr = EMAIL_ADDRESS,
        to_addrs = TO_EMAIL,
        msg=f"Subject:Amazon Stock Information \n\n {mail_notification}"
    )




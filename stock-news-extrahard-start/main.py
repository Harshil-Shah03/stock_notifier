import requests
import datetime as dt
import re
import os
from twilio.rest import Client

pattern = re.compile('<.*?>')

#account_sid = os.environ['TWILIO_ACCOUNT_SID']
account_sid = "AC88d9c6532f1b2e8fde1eb7212ed7b7e4"
#auth_token = os.environ['TWILIO_AUTH_TOKEN']
auth_token = "622dee4653b0af593d58f28b7975f78f"
client = Client(account_sid, auth_token)

test = "2023-05-11"
current = dt.datetime.now()
yesterdays_date = str(current.date() - dt.timedelta(days=1))
day_before_yesterdays_date = str(current.date() - dt.timedelta(days=2))

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_api_key = "MO6Q4FB4OSH3N0KJ"
news_api_key = "f7839477a4e542439f2929e023758280"

param = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": stock_api_key
}

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
response = requests.get(url="https://www.alphavantage.co/query", params=param)
response.raise_for_status()

print(yesterdays_date)
print(day_before_yesterdays_date)

y_stock_price = float(response.json()["Time Series (Daily)"][yesterdays_date]["4. close"])
dby_stock_price = float(response.json()["Time Series (Daily)"][day_before_yesterdays_date]["4. close"])

print(y_stock_price)
print(dby_stock_price)

difference: float = (y_stock_price - dby_stock_price)
percent_change = (abs(difference) / dby_stock_price) * 100

compare = 0.05 * dby_stock_price

print(difference)
print(percent_change)
print(compare)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
if abs(difference) >= compare:
    news_response = requests.get(url="https://newsapi.org/v2/everything", params={"q": COMPANY_NAME,
                                                                                  "apiKey": news_api_key})
    list_news = news_response.json()["articles"][:3]
    msg = [re.sub(pattern, '', item["description"]) for item in list_news]
    if difference > 0:
        format_val = "🔺"
    else:
        format_val = "🔻"
    msg_f = '\n'.join(msg)

    message = client.messages \
        .create(
        body=f"{format_val} {'{0:.2f}'.format(percent_change)}%\n{msg_f}",
        from_='+14065005661',
        to='+917045633887'
    )

    print(message.status)


## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

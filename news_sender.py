import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot

# 환경변수에서 직접 읽음
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EXCLUDE_CATEGORIES = os.getenv("EXCLUDE_CATEGORIES", "").split(",")

NEWS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"

def get_news_titles(url, max_count=20):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml-xml")
    items = soup.find_all("item")
    news_list = []
    for item in items:
        title = item.title.text.strip()
        link = item.link.text.strip()
        if not any(cat in title for cat in EXCLUDE_CATEGORIES):
            news_list.append(f"• [{title}]({link})")
        if len(news_list) >= max_count:
            break
    return news_list

def send_to_telegram(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

def main():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    news_items = get_news_titles(NEWS_URL)
    if news_items:
        message = f"🗞️ *{today} 구글 뉴스*\n\n" + "\n".join(news_items)
        send_to_telegram(BOT_TOKEN, CHAT_ID, message)
    else:
        print("❗ 필터링된 뉴스가 없습니다.")

if __name__ == "__main__":
    main()

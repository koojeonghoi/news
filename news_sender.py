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

def get_news_titles(url):
    res = requests.get(url)
    print(f"HTTP Status: {res.status_code}")
    print(f"Content length: {len(res.content)}")
    
    soup = BeautifulSoup(res.content, features="xml")
    
    # RSS의 item 태그들 찾기
    news_items = soup.find_all("item")
    print(f"Found {len(news_items)} news items")
    
    # 처음 몇 개 아이템의 제목 출력해보기
    for i, item in enumerate(news_items[:3]):
        title_tag = item.find("title")
        if title_tag:
            print(f"Title {i+1}: {title_tag.get_text()}")
    
    titles = []
    for item in news_items:
        title_tag = item.find("title")
        if title_tag:
            title = title_tag.get_text()
            titles.append(title)
    
    return titles  # 이 줄이 빠져있을 가능성!

import asyncio

async def send_to_telegram(BOT_TOKEN, CHAT_ID, message):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

def send_telegram_sync(BOT_TOKEN, CHAT_ID, message):
    asyncio.run(send_to_telegram(BOT_TOKEN, CHAT_ID, message))

def main():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    news_items = get_news_titles(NEWS_URL)
    if news_items:
        message = f"🗞️ *{today} 구글 뉴스*\n\n" + "\n".join(news_items)
        send_telegram_sync(BOT_TOKEN, CHAT_ID, message)
    else:
        print("❗ 필터링된 뉴스가 없습니다.")

if __name__ == "__main__":
    main()

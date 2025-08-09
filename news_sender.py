import os
import asyncio
import feedparser
from telegram import Bot

# 환경변수
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"

def get_news_titles(url):
    feed = feedparser.parse(url)
    print(f"Found {len(feed.entries)} news items")
    news_list = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        news_list.append(f"{title}\n{link}")
    return news_list

async def send_to_telegram(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=None)

def send_telegram_sync(bot_token, chat_id, message):
    asyncio.run(send_to_telegram(bot_token, chat_id, message))

def main():
    print("Fetching news...")
    news_items = get_news_titles(NEWS_URL)
    message = "📢 오늘의 주요 뉴스\n\n" + "\n\n".join(news_items)
    send_telegram_sync(BOT_TOKEN, CHAT_ID, message)
    print("Sent to Telegram.")

if __name__ == "__main__":
    main()

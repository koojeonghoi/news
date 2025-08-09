import asyncio
import feedparser
from datetime import datetime
from telegram import Bot

# === 환경설정 ===
BOT_TOKEN = "여기에_봇_토큰"
CHAT_ID = "여기에_CHAT_ID"

# === 구글 뉴스 가져오기 ===
def fetch_news():
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    return feed.entries

# === 텔레그램 전송 (비동기) ===
async def send_to_telegram(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    for i in range(0, len(message), 4000):
        chunk = message[i:i+4000]
        await bot.send_message(chat_id=chat_id, text=chunk)  # Markdown 제거

# === 동기 래퍼 ===
def send_telegram_sync(bot_token, chat_id, message):
    asyncio.run(send_to_telegram(bot_token, chat_id, message))

# === 메인 로직 ===
def main():
    print("구글 뉴스 가져오는 중...")
    news_items = fetch_news()
    print(f"뉴스 {len(news_items)}건 수신 완료")

    message_lines = []
    message_lines.append(f"📢 오늘의 구글 뉴스 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    message_lines.append(f"총 {len(news_items)}건\n")

    for idx, item in enumerate(news_items, start=1):
        title = item.title
        link = item.link
        message_lines.append(f"{idx}. {title}")
        message_lines.append(link)
        message_lines.append("")  # 줄바꿈

    message = "\n".join(message_lines)

    print("텔레그램 전송 시작")
    send_telegram_sync(BOT_TOKEN, CHAT_ID, message)
    print("전송 완료")

if __name__ == "__main__":
    main()

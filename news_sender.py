import os
import asyncio
import feedparser
from telegram import Bot

def get_news_titles(url):
    """Google News RSS에서 뉴스 제목과 링크를 가져오는 함수"""
    feed = feedparser.parse(url)
    print(f"Found {len(feed.entries)} news items")
    
    news_list = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        news_list.append(f"• {title}\n  {link}")
    
    return news_list

async def send_to_telegram(bot_token, chat_id, message):
    """텔레그램으로 메시지를 전송하는 비동기 함수"""
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        print("✅ 텔레그램 전송 완료")
    except Exception as e:
        print(f"❌ 텔레그램 전송 실패: {e}")
        raise

def send_telegram_sync(bot_token, chat_id, message):
    """동기적으로 텔레그램 메시지 전송"""
    asyncio.run(send_to_telegram(bot_token, chat_id, message))

def main():
    # Repository secrets에서 환경변수 가져오기
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    NEWS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    
    # 환경변수 확인
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN 환경변수가 설정되지 않았습니다!")
        print("GitHub Secrets에 TELEGRAM_BOT_TOKEN을 설정했는지 확인해주세요.")
        exit(1)
        
    if not CHAT_ID:
        print("❌ CHAT_ID 환경변수가 설정되지 않았습니다!")
        print("GitHub Secrets에 TELEGRAM_CHAT_ID를 설정했는지 확인해주세요.")
        exit(1)
    
    print("📰 뉴스 가져오는 중...")
    
    try:
        # 뉴스 가져오기
        news_items = get_news_titles(NEWS_URL)
        
        if not news_items:
            print("⚠️ 가져온 뉴스가 없습니다.")
            return
        
        # 메시지 생성 (텔레그램 메시지 길이 제한 고려)
        header = "📢 <b>오늘의 주요 뉴스</b>\n\n"
        
        # 뉴스 항목들을 하나씩 추가하면서 길이 체크
        message = header
        max_length = 4000  # 텔레그램 메시지 길이 제한 (여유분 고려)
        
        for i, news_item in enumerate(news_items):
            test_message = message + news_item + "\n\n"
            if len(test_message) > max_length:
                print(f"📝 메시지 길이 제한으로 {i}개 뉴스만 전송합니다.")
                break
            message = test_message
        
        # 텔레그램 전송
        print("📤 텔레그램으로 전송 중...")
        send_telegram_sync(BOT_TOKEN, CHAT_ID, message.strip())
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()

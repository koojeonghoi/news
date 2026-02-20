import os
import asyncio
import feedparser
from telegram import Bot

def get_news_titles(url):
    """Google News RSS에서 뉴스 제목과 링크를 가져오는 함수 (필터링 추가)"""
    feed = feedparser.parse(url)
    print(f"Found {len(feed.entries)} news items")
    
    # 제외하고 싶은 키워드 설정
    exclude_keywords = ['정치', '건강', '의료', '대통령', '국회', '정당'] 
    
    news_list = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        
        # 키워드 필터링: 제목에 제외 키워드가 포함되어 있으면 건너뜀
        if any(keyword in title for keyword in exclude_keywords):
            continue
            
        # HTML 형식으로 링크가 숨겨진 제목 생성
        news_list.append(f'• <a href="{link}">{title}</a>')
    
    print(f"Filtered down to {len(news_list)} items")
    return news_list

# ... (중략: send_multiple_messages 및 기타 함수는 기존과 동일) ...

def main():
    # Repository secrets에서 환경변수 가져오기
    # 팁: GitHub Secrets 이름과 os.getenv 이름을 동일하게 맞추는 것이 좋습니다.
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    NEWS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 환경변수(BOT_TOKEN 또는 CHAT_ID)가 설정되지 않았습니다!")
        exit(1)
    
    print("📰 뉴스 가져오는 중 (정치/건강 제외)...")
    
    try:
        news_items = get_news_titles(NEWS_URL)
        
        if not news_items:
            print("⚠️ 필터링 후 가져온 뉴스가 없습니다.")
            return
        
        messages = []
        current_message = "📢 <b>오늘의 주요 뉴스 (정치/건강 제외)</b>\n\n"
        max_length = 4000
        
        for i, news_item in enumerate(news_items):
            test_line = news_item + "\n\n"
            if len(current_message + test_line) > max_length:
                messages.append(current_message.strip())
                current_message = f"📢 <b>오늘의 주요 뉴스 (계속)</b>\n\n{test_line}"
            else:
                current_message += test_line
        
        if current_message.strip():
            messages.append(current_message.strip())
        
        asyncio.run(send_multiple_messages(BOT_TOKEN, CHAT_ID, messages))
        print(f"✅ 전송 완료! (총 {len(news_items)}개)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()

import os
import asyncio
import feedparser
from telegram import Bot

def get_news_titles(url):
    """Google News RSS에서 뉴스 제목과 링크를 가져오고 특정 키워드를 필터링하는 함수"""
    feed = feedparser.parse(url)
    print(f"Found {len(feed.entries)} news items")
    
    # 제외하고 싶은 키워드 설정 (원하시는 대로 추가/삭제 가능합니다)
    exclude_keywords = ['정치', '건강', '의료', '대통령', '국회', '정당', '백신', '암', '여야', '검찰'] 
    
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

async def send_multiple_messages(bot_token, chat_id, messages):
    """여러 개의 메시지를 순차적으로 전송하는 함수"""
    bot = Bot(token=bot_token)
    
    for i, message in enumerate(messages):
        try:
            await bot.send_message(
                chat_id=chat_id, 
                text=message, 
                parse_mode='HTML',
                disable_web_page_preview=True  # 링크 미리보기 비활성화
            )
            print(f"✅ 메시지 {i+1}/{len(messages)} 전송 완료")
            
            # 메시지 간 짧은 딜레이 (텔레그램 API 제한 방지)
            if i < len(messages) - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ 메시지 {i+1} 전송 실패: {e}")
            raise

def main():
    # GitHub Secrets 설정과 일치하도록 환경변수 이름 수정 완료
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    NEWS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 환경변수가 설정되지 않았습니다!")
        exit(1)
    
    print("📰 뉴스 가져오는 중 (정치/건강 제외)...")
    
    try:
        # 뉴스 가져오기
        news_items = get_news_titles(NEWS_URL)
        
        if not news_items:
            print("⚠️ 필터링 후 가져온 뉴스가 없습니다.")
            return
        
        # 메시지들을 여러 개로 분할 (텔레그램 길이 제한 방지)
        messages = []
        current_message = "📢 <b>오늘의 주요 뉴스 (정치/건강 제외)</b>\n\n"
        max_length = 4000
        
        for i, news_item in enumerate(news_items):
            test_line = news_item + "\n\n"
            test_message = current_message + test_line
            
            if len(test_message) > max_length:
                messages.append(current_message.strip())
                current_message = f"📢 <b>오늘의 주요 뉴스 (계속)</b>\n\n{test_line}"
            else:
                current_message = test_message
        
        if current_message.strip():
            messages.append(current_message.strip())
        
        print(f"📤 총 {len(messages)}개 메시지로 {len(news_items)}개 뉴스 전송 중...")
        
        # 메시지 전송 실행
        asyncio.run(send_multiple_messages(BOT_TOKEN, CHAT_ID, messages))
        print(f"✅ 모든 뉴스 전송 완료! (총 {len(news_items)}개)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()

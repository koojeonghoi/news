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
        # HTML 형식으로 링크가 숨겨진 제목 생성
        news_list.append(f'• <a href="{link}">{title}</a>')
    
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

def send_multiple_messages_sync(bot_token, chat_id, messages):
    """동기적으로 여러 메시지 전송"""
    asyncio.run(send_multiple_messages(bot_token, chat_id, messages))

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
        
        # 메시지들을 여러 개로 분할
        messages = []
        current_message = "📢 <b>오늘의 주요 뉴스</b>\n\n"
        max_length = 4000  # 텔레그램 메시지 길이 제한
        
        for i, news_item in enumerate(news_items):
            # 뉴스 항목 + 빈 줄 추가
            test_line = news_item + "\n\n"
            test_message = current_message + test_line
            
            # 길이 제한 체크
            if len(test_message) > max_length:
                # 현재 메시지를 저장하고 새 메시지 시작
                messages.append(current_message.strip())
                current_message = f"📢 <b>오늘의 주요 뉴스 (계속)</b>\n\n{test_line}"
                print(f"📝 메시지 분할: {len(messages)}번째 메시지 완료 ({i}개 뉴스)")
            else:
                current_message = test_message
        
        # 마지막 메시지 추가
        if current_message.strip():
            messages.append(current_message.strip())
        
        print(f"📤 총 {len(messages)}개 메시지로 {len(news_items)}개 뉴스 전송 중...")
        
        # 모든 메시지 전송
        send_multiple_messages_sync(BOT_TOKEN, CHAT_ID, messages)
        print(f"✅ 모든 뉴스 전송 완료! (총 {len(news_items)}개)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()

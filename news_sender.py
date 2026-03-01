import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

def get_naver_category_news():
    """네이버 뉴스에서 특정 카테고리의 헤드라인 뉴스를 크롤링하는 함수"""
    
    # 가져올 카테고리 (정치 100, 사회 102, 생활/건강 103 제외)
    categories = {
        '101': '💰 경제',
        '105': '💻 IT/과학',
        '104': '🌍 세계'
    }
    
    # 네이버는 일반적인 봇 접근을 막으므로 사람처럼 보이도록 User-Agent 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_list = []
    
    for section_id, category_name in categories.items():
        url = f"https://news.naver.com/section/{section_id}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 뉴스 섹션의 헤드라인 기사 블록을 찾음 (sa_text_title 클래스)
            # HTML 구조는 네이버 업데이트에 따라 변경될 수 있음
            headlines = soup.select('.sa_text_title')
            
            # 각 카테고리별로 상위 5개 기사만 추출
            for article in headlines[:5]:
                title = article.text.strip()
                link = article['href']
                
                news_list.append(f'• [{category_name}] <a href="{link}">{title}</a>')
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {category_name} 뉴스 가져오기 실패: {e}")
            continue
            
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
                disable_web_page_preview=True
            )
            print(f"✅ 메시지 {i+1}/{len(messages)} 전송 완료")
            
            if i < len(messages) - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ 메시지 {i+1} 전송 실패: {e}")
            raise

def main():
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ 환경변수가 설정되지 않았습니다!")
        exit(1)
    
    print("📰 네이버 카테고리별 뉴스 크롤링 중...")
    
    news_items = get_naver_category_news()
    
    if not news_items:
        print("⚠️ 가져온 뉴스가 없습니다.")
        return
    
    messages = []
    current_message = "📢 <b>오늘의 네이버 주요 뉴스 (경제/IT/세계)</b>\n\n"
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
    
    try:
        asyncio.run(send_multiple_messages(BOT_TOKEN, CHAT_ID, messages))
        print(f"✅ 모든 뉴스 전송 완료! (총 {len(news_items)}개)")
    except Exception as e:
        print(f"❌ 전송 중 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()

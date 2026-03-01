import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

def get_top_30_news():
    """다음 뉴스 통합 랭킹(많이 본 뉴스) 상위 30개를 크롤링하는 함수"""
    
    url = "https://news.daum.net/ranking/popular"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_list = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 다음 뉴스 랭킹 리스트 추출 (보통 ul.list_news2 안의 a.link_txt에 있음)
        articles = soup.select('ul.list_news2 li a.link_txt')
        
        # 1위부터 30위까지만 추출
        for i, article in enumerate(articles[:30], 1):
            title = article.text.strip()
            link = article['href']
            
            # 1. 기사제목 형식으로 저장
            news_list.append(f'{i}. <a href="{link}">{title}</a>')
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 뉴스 랭킹 가져오기 실패: {e}")
        
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
    
    print("📰 통합 랭킹 뉴스 크롤링 중...")
    
    news_items = get_top_30_news()
    
    if not news_items:
        print("⚠️ 가져온 뉴스가 없습니다.")
        return
    
    messages = []
    current_message = "📢 <b>오늘의 가장 많이 본 뉴스 Top 30</b>\n\n"
    max_length = 4000
    
    for news_item in news_items:
        test_line = news_item + "\n\n"
        test_message = current_message + test_line
        
        if len(test_message) > max_length:
            messages.append(current_message.strip())
            current_message = f"📢 <b>많이 본 뉴스 (계속)</b>\n\n{test_line}"
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

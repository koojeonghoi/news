import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

def get_nate_top_30_news():
    """네이트 시사 종합 랭킹 상위 30개를 확실하게 크롤링하는 함수 (제목만 추출)"""
    
    url = "https://news.nate.com/rank/interest?sc=sisa"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    news_list = []
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        count = 1
        seen_links = set()
        
        # 페이지 내 모든 a 태그 검사
        for item in soup.find_all('a'):
            if count > 30:
                break
                
            link = item.get('href', '')
            
            # 네이트 뉴스 기사 본문 링크 필터링
            if not link or '/view/' not in link:
                continue
            
            # 1. 제목이 특정 태그(.tit, strong)로 감싸져 있는 경우 우선 추출
            title_tag = item.select_one('.tit, strong, h2')
            if title_tag:
                title = title_tag.text.strip()
            else:
                # 2. 태그가 없다면 전체 텍스트에서 첫 번째 줄만 추출 (요약 내용 제거)
                raw_text = item.text.strip().replace('\r', '')
                if not raw_text:
                    continue
                title = raw_text.split('\n')[0].strip()
                
            # 텍스트가 너무 짧거나 무의미한 단어인 경우 건너뛰기
            if len(title) < 5 or title in ['사진', '동영상', '포토']:
                continue
                
            # 상대 경로를 절대 경로로 변환
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = 'https://news.nate.com' + link
                
            # 기사 고유 주소만 추출하여 중복 방지
            base_link = link.split('?')[0]
            
            if base_link not in seen_links:
                news_list.append(f'{count}. <a href="{link}">{title}</a>')
                seen_links.add(base_link)
                count += 1
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 네이트 뉴스 가져오기 실패: {e}")
        
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
    
    print("📰 네이트 많이 본 뉴스 30개 크롤링 중 (제목만 추출)...")
    
    news_items = get_nate_top_30_news()
    
    if not news_items:
        print("⚠️ 가져온 뉴스가 없습니다.")
        return
    
    messages = []
    current_message = "📢 <b>오늘의 가장 많이 본 뉴스 Top 30</b>\n\n"
    max_length = 4000
    
    for i, news_item in enumerate(news_items):
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

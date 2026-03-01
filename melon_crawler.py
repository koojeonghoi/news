import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 토큰 또는 챗 ID가 설정되지 않았습니다.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text
        # 노래 제목 특수문자 에러를 막기 위해 parse_mode='Markdown' 옵션 삭제
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"전송 실패: {response.text}")

def crawl_melon_new_entries():
    url = "https://www.melon.com/chart/day/index.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    songs = soup.select('tbody > tr')
    new_entries = []
    
    for song in songs:
        # 화면에 'NEW'라고 뜨는 곡의 내부 클래스 확인
        if song.select_one('.rank_new'):
            rank = song.select_one('span.rank').text
            title = song.select_one('div.ellipsis.rank01 a').text
            artist = song.select_one('div.ellipsis.rank02 span a').text
            
            # 마크다운 에러를 피하기 위해 별표 대신 동그라미(•) 사용
            new_entries.append(f"• {rank}위 (NEW) : {title} - {artist}")
            
    return new_entries

if __name__ == "__main__":
    new_songs = crawl_melon_new_entries()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y년 %m월 %d일")
    
    message = f"🔔 [멜론 일간차트 진입 곡]\n기준일: {yesterday}\n\n"
    
    if new_songs:
        message += "\n".join(new_songs)
    else:
        message += "오늘은 차트에 새로 진입한 곡이 없습니다."
        
    message += "\n\n🔗 차트 확인하기: https://www.melon.com/chart/day/index.htm"
    
    send_telegram_message(message)
    print("멜론 차트 크롤링 및 알림 전송 완료!")

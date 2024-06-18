import requests
import json
import xmltodict
import html
import os
from datetime import datetime

# GitHub Secrets에서 환경 변수 가져오기
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def makePayloadItem(newsItem):
    제목_하이퍼링크 = f"<{newsItem['link']}|{html.unescape(newsItem['title'])}>"
    pubDate_datetime = datetime.strptime(newsItem['pubDate'], "%a, %d %b %Y %H:%M:%S %Z")
    pubDate_formatted = pubDate_datetime.strftime("%Y년 %m월 %d일 %H:%M")
    return {
        "color": "#ff0044",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{제목_하이퍼링크}\n*{pubDate_formatted}*"
                }
            },
            {
                "type": "divider"
            }
        ]
    }

def callWebhook(payload):
    headers = {
        'Content-type': 'application/json',
    }
    res = requests.post(SLACK_WEBHOOK_URL, headers=headers, json=payload)
    print(res.text)

def getNewsFromRss():
    RSS_URLS = [
        'https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR%3Ako&oc=11&q=%22%ED%85%8C%EC%9D%B4%EB%B8%94%EC%98%A4%EB%8D%94%22%20when%3A1d',
        'https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR%3Ako&oc=11&q=%22AI%22%20when%3A1d',
        'https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR%3Ako&oc=11&q=%22blockchain%22%20when%3A1d'
    ]

    allNewsList = []
    
    for RSS_URL in RSS_URLS:
        try:
            res = requests.get(RSS_URL)
            ordered_dict = xmltodict.parse(res.text)
            json_type = json.dumps(ordered_dict)
            res_dict = json.loads(json_type)

            itemList = res_dict['rss']['channel']['item']
            
            for item in itemList:
                news_dict = {
                    'title': item['title'],
                    'link': item['link'],
                    'pubDate': item['pubDate']
                }
                allNewsList.append(news_dict)
        except Exception as e:
            print(f"뉴스 파싱 중 오류 발생 ({RSS_URL}): {e}")

    return allNewsList

def main():
    print(f'\n\n뉴스 기사 수집을 시작합니다...')
    newsList = getNewsFromRss()
    newsLen = len(newsList)
    print(f'>>> {newsLen}개의 기사를 수집하였습니다')

    print(f'\n\n뉴스 카드 생성을 시작합니다...')
    cardList = {"attachments": []}
    for idx, newsItem in enumerate(newsList):
        item = makePayloadItem(newsItem)
        cardList["attachments"].append(item)
        print(f'>>> [{idx + 1}/{newsLen}] 번째 NEWS CARD를 생성하였습니다.')

    print(f'\n\nSLACK 발송을 시작합니다...')
    callWebhook(
        {"blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*오늘 테이블오더 뉴스*"
                }
            },
            {
                "type": "divider"
            }
        ]}
    )
    callWebhook(cardList)

if __name__ == "__main__":
    main()

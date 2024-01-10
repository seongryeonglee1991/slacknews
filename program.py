import requests
import json
import xmltodict
import html
from datetime import datetime

# github라는 오픈소스 공간에서 SLACK_WEBHOOK_URL을 암호화하기 위한 코드
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def makePayloadItem(newsItem):
  기사링크 = f"<{newsItem['link']}>"
  pubDate_datetime = datetime.strptime(newsItem['pubDate'], "%a, %d %b %Y %H:%M:%S %Z")
  pubDate_formatted = pubDate_datetime.strftime("%Y년 %m월 %d일 %H:%M")
  return      {
          "type": "section",
          "color": "#ff0044",
          "title": f"{html.unescape(newsItem['title'])}",
          "fields": [
          {
           "type": "mrkdwn",
           "value": f"*{pubDate_formatted}*",
           "short": True
          },
          {
                    "type": "divider"
              },
          {
               "type": "mrkdwn",
               "value": f"{기사링크}",
               "short": 'true'
              },
          {
                    "type": "divider"
              }
          ]
      }

def callWebhook (payload):
  headers = {
    'Content-type' : 'application/json',
  }
  res = requests.post(SLACK_WEBHOOK_URL, headers=headers, json=payload)
  print(res.text)

def getNewsFromRss():
    try:
        RSS_URL = 'https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR%3Ako&oc=11&q=%22%ED%85%8C%EC%9D%B4%EB%B8%94%EC%98%A4%EB%8D%94%22%20when%3A1d'
        res = requests.get(RSS_URL)
        ordered_dict = xmltodict.parse(res.text)
        json_type = json.dumps(ordered_dict)
        res_dict = json.loads(json_type)

        itemList = res_dict['rss']['channel']['item']
        newsList = []

        for item in itemList:
            news_dict = {
                'title': item['title'],
                'link': item['link'],
                'pubDate' : item['pubDate']
            }
            newsList.append(news_dict)

        return newsList
    except Exception as e:
        print(f"뉴스 파싱 중 오류 발생: {e}")
        return []

def main():
  print(f'\n\n뉴스 기사 수집을 시작합니다...')
  newsList = getNewsFromRss()
  newsLen = len(newsList)
  print(f'>>> {newsLen}개의 기사를 수집하였습니다')

  print(f'\n\n뉴스 카드 생성을 시작합니다...')
  cardList = dict()
  cardList['attachments'] = []
  for idx,newsItem in enumerate(newsList):
    item = makePayloadItem(newsItem)
    cardList['attachments'].append(item)
    print(f'>>> [{idx}/{newsLen}] 번째 NEWS CARD를 생성하였습니다.')

  print(f'\n\nSLACK 발송을 시작합니다...')
  callWebhook(
    {'blocks':[
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*오늘 테이블오더 뉴스*"
        }
      },
      {
        "type": "divider"
      },
    ]}
  )
  callWebhook(cardList)

if __name__ == "__main__":
  main()

import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred, {
	'databaseURL': 'https://team1-2cd93-default-rtdb.firebaseio.com/'
	})
ref = db.reference('/')


# API 가져오기
encoding = 'mLdp5G9f%2FnMVvCQJvr3m2wEicXIaM75%2BSiC03dJ8g6UnxzXg6R%2BK6KGy6XDhkrewGP2QMy1ngCzpvM0VPjYlpg%3D%3D'
decoding = 'mLdp5G9f/nMVvCQJvr3m2wEicXIaM75+SiC03dJ8g6UnxzXg6R+K6KGy6XDhkrewGP2QMy1ngCzpvM0VPjYlpg=='
url = f'http://openapi.onbid.co.kr/openapi/services/KamcoPblsalThingInquireSvc/getKamcoPbctCltrList?serviceKey={encoding}&pageNo=1&numOfRows=100&DPSL_MTD_CD=0001&PBCT_CLS_DTM=20230228'
result = requests.get(url)
soup = BeautifulSoup(result.text, 'lxml')
items = soup.find_all('item')

# 용도, 공매번호, 위치, 감정가, 최저입찰가, 입찰 시작, 끝

for i, item in enumerate(items):
  category = item.find('ctgr_full_nm').get_text()
  cat_idx = category.find('/') - 1
  category = category[:cat_idx]
  num = item.find('pbct_no').get_text()
  location = item.find('ldnm_adrs').get_text()
  gamjung = item.find('apsl_ases_avg_amt').get_text()
  lowest = item.find('min_bid_prc').get_text()
  rate = item.find('fee_rate').get_text()
  name = item.find('cltr_nm').get_text()
  rate_idx = rate.find(')')
  rate = rate[1:rate_idx]
  start_date = item.find('pbct_begn_dtm').get_text()[:8]
  end_date = item.find('pbct_cls_dtm').get_text()[:8]

  # 파이어베이스 저장
  ref.child(str(i)).set({
    'category': category,
    'name' : name,
    'num' : num,
    'location': location,
    'gamjung' : gamjung,
    'lowest' : lowest,
    'rate' : rate,
    'start_date' : start_date,
    'end_date' : end_date
  })

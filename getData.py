import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

# token, url 숨겨서 가져오기
def get_config() -> str:
    f = open('setting.json')
    config_json = json.load(f)
    url = config_json['firebase_url']
    api_key = config_json['encodig_key']
    return url, api_key

firebase_url, encodig_key = get_config()

cred = credentials.Certificate("serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred, {
	'databaseURL': firebase_url
	})
ref = db.reference('/')


# API 가져오기
url = f'http://openapi.onbid.co.kr/openapi/services/KamcoPblsalThingInquireSvc/getKamcoPbctCltrList?serviceKey={encodig_key}&pageNo=1&numOfRows=100&DPSL_MTD_CD=0001&PBCT_CLS_DTM=20230228'
result = requests.get(url)
soup = BeautifulSoup(result.text, 'lxml')
items = soup.find_all('item')

for i, item in enumerate(items):
  # 용도
  category = item.find('ctgr_full_nm').get_text()
  cat_idx = category.find('/') - 1
  category1 = category[:cat_idx]
  category2 = category[cat_idx+2:]
  # 공고번호
  announce_num = item.find('plnm_no').get_text()
  # 공매번호
  sale_num = item.find('pbct_no').get_text()
  # 공매조건번호
  sale_cdtn_num = item.find('pbct_cdtn_no').get_text()
  # 물건번호
  item_num = item.find('cltr_no').get_text()
  # 물건이력번호
  item_record_num = item.find('cltr_hstr_no').get_text()
  # 유찰횟수
  fail_cnt = item.find('uscbd_cnt').get_text()
  # 소재지
  location = item.find('ldnm_adrs').get_text()
  # 감정가
  gamjung = item.find('apsl_ases_avg_amt').get_text()
  # 입찰 최저가
  lowest = item.find('min_bid_prc').get_text()
  # 최저입찰율
  rate = item.find('fee_rate').get_text()
  rate_idx = rate.find(')')
  rate = rate[1:rate_idx]
  # 그룹코드
  grp_code = item.find('scrn_grp_cd').get_text()
  # 물건명
  name = item.find('cltr_nm').get_text()
  # 입착 시작, 마감일
  start_date = item.find('pbct_begn_dtm').get_text()[:8]
  start_date = f'{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}'
  end_date = item.find('pbct_cls_dtm').get_text()[:8]
  end_date = f'{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}'
  duration = f'{start_date} ~ {end_date}'
  page_url = f'https://www.onbid.co.kr/op/cta/cltrdtl/collateralRealEstateDetail.do?searchAddr=&searchSiDo=&searchSiGunGu=&searchEmd=&collateralGbnCd=0001&bizDvsnCd=0001&cltrHstrNo={item_record_num}&cltrNo={item_num}&plnmNo={announce_num}&pbctNo={sale_num}&scrnGrpCd={grp_code}&pbctCdtnNo={sale_cdtn_num}&viewGbn=&menuId=2021&searchYn=Y&searchDpslMtdCd=&searchCltrNm=&searchCltrMnmtNo=&searchBegnDtm=2023-01-26&searchClsDtm={end_date}&searchFromMinBidPrc=&searchToMinBidPrc=&searchOrgNm=&searchFromApslAsesAmt=&searchToApslAsesAmt=&searchCltrAdrsType=road&siDo=&siGunGu=&emd=&searchAddrDtl=&searchFromLandSqms=&searchToLandSqms=&searchFromBldSqms=&searchToBldSqms=&searchFromUsbdCnt=&searchToUsbdCnt=&searchShrYn=&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&_searchArrayPrptDvsnCd=on&searchAdtnInfo1=&searchAdtnInfo2=&searchAdtnInfo3=&searchMbsNm=&searchScrtNm=&searchItemNm=&searchScrtKind=&searchDpslFincComp=&searchPoorBondKind=&searchHdorAstFixDyFrom=&searchHdorAstFixDyTo=&_searchKamcoYn=on&searchOrderBy=&pageUnit=10&pageIndex=1&srchNm=&_csrf=1e958df3-63e4-4a06-a53e-fa7bf37f19f1&_csrf=1e958df3-63e4-4a06-a53e-fa7bf37f19f1'
  

  # 파이어베이스 저장
  ref.child('items').update({
    str(i) : {
    'category1': category1,
    'category2' : category2,
    'name' : name,
    'item_num' : item_num,
    'item_record_num' : item_record_num,
    'fail_cnt' : fail_cnt,
    'announce_num' : announce_num,
    'sale_num' : sale_num,
    'sale_cdtn_num' : sale_cdtn_num,
    'location': location,
    'gamjung' : gamjung,
    'lowest' : lowest,
    'rate' : rate,
    'grp_code' : grp_code,
    'start_date' : start_date,
    'end_date' : end_date,
    'duration' : duration,
    'link' : page_url
    }
  })

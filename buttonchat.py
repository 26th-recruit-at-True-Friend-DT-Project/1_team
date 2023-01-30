import firebase_admin
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
import json

# token, url 숨겨서 가져오기
def get_config() -> str:
    f = open('setting.json')
    config_json = json.load(f)
    url = config_json['firebase_url']
    token = config_json['bot_token']
    return url, token

firebase_url, bot_token = get_config()

cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL' : firebase_url})
ref = db.reference('/')

first_result = ""
second_result = ""
category = ""
price_range = ()

price_dict = {
    '가격1' : 0,
    '가격2' : 100000000,
    '가격3' : 500000000,
    '가격4' : 1000000000,
    '가격5' : 10000000000
}

type_dict = {
    '용도1' : '토지',
    '용도2' : '주거용건물',
    '용도3' : '상가용및업무용건물',
    '용도4' : '산업용및기타특수용건물',
    '용도5' : '용도복합용건물'
}

# 버튼1
def first_filter(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='1억 미만', callback_data='가격1'),
                                                      InlineKeyboardButton(text='1억 이상 5억 미만', callback_data='가격2')],
                                                     [InlineKeyboardButton(text='5억 이상 10억 미만', callback_data='가격3'),
                                                      InlineKeyboardButton(text='10억 이상', callback_data='가격4')]])

    bot.sendMessage(chat_id, '최저 가격을 클릭해주세요', reply_markup=keyboard)

#버튼2
keyboard2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='토지', callback_data='용도1')],
                                                     [InlineKeyboardButton(text='주거용건물', callback_data='용도2')],
                                                     [InlineKeyboardButton(text='상가용및업무용건물', callback_data='용도3')],
                                                     [InlineKeyboardButton(text='산업용및기타특수용건물', callback_data='용도4')],
                                                     [InlineKeyboardButton(text='용도복합용건물', callback_data='용도5')]])
'''
def get_config():

	f = open("config.json")

	config_json = json.load(f)

	api_key = config_json['api_key']

	#req_url = service_url + "?crtfc_key=" + api_key

	return api_key
'''

# 가격 범위 선택
def selectPrice(price: str, id: str) -> None:
    bot.sendMessage(id, '용도를 선택해주세요.', reply_markup=keyboard2)
    change_first_answer(price)

# 용도 선택
def selectType(category: str, id: str) -> None:
    change_second_answer(category)
    print_answer(id)

# 첫번째 문항
def change_first_answer(first_answer):
    global first_result
    first_result = first_answer
    global price_range
    price_range = (price_dict[first_result], price_dict[first_result[:2]+ str(int(first_result[-1])+1)])

# 두번째 문항
def change_second_answer(second_answer):
    global second_result
    second_result = second_answer
    global category 
    category = type_dict[second_result]


# 결과 출력
def print_answer(id: str) -> None:
    print("1: ", first_result)
    print("2: ", second_result)
    print(f'category: {category}, price_range: {price_range}')
    output_list = find_object()
    result_list = []
    # 위치 중복 제거
    tmp = []
    flag = True
    for idx, item in enumerate(output_list):
        for i in tmp:
            if(i[1] == item['location']):
                flag = False
                break
        if flag == True:
            tmp.append((idx, item['location']))
        flag = True

    for i in tmp:
        result_list.append(output_list[i[0]])

    print(f'size: {len(result_list)}')
    
    bot.sendMessage(id, f'총 {len(result_list)}건이 도출되었습니다.')
    for i in result_list:
        bot.sendMessage(id, f"지번: {i['location']}\n")

def find_object() -> list:
    result = []
    for item in ref.get():
        if(item['category'] == category and (int(item['lowest']) >= price_range[0] and int(item['lowest']) < price_range[1])):
            result.append(item)
    return result


# callback 담겨있는 값
def on_callback_query(msg):

    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print(query_id)
    print('Callback Query:', query_id, from_id, query_data)
    query_data = msg['data']
    if query_data[:2] == '가격':
        selectPrice(query_data, from_id)

    elif query_data[:2] == '용도':
        selectType(query_data, from_id)

    return first_result, second_result



token = bot_token
bot = telepot.Bot(token)

MessageLoop(bot, {'chat': first_filter,
                  'callback_query': on_callback_query}).run_forever()
print('Listening ...')
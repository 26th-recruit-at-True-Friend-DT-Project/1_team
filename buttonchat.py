import time

import firebase_admin
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import db
from firebase_admin import credentials
import firebase_admin

cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL' : 'https://team1-2cd93-default-rtdb.firebaseio.com/'})
ref = db.reference('/')
print(ref.get()[0]['lowest'])

token = get_config()

bot = telepot.Bot(token)
result = []

price_dic = {
    '가격1' : '1억미만',
    '가격2' : '5억 미만'
}


first_answer = ""
second_answer = ""
go_to_second_flag = False

#버튼 만드는 함수(필터링)

keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text='토지', callback_data='용도1'),
          InlineKeyboardButton(text='주거용건물', callback_data='용도2'),
          InlineKeyboardButton(text='상가용및업무용건물', callback_data='용도3'),
          InlineKeyboardButton(text='산업용및기타특수용건물', callback_data='용도4'),
          InlineKeyboardButton(text='용도복합용건물', callback_data='용도5'),
          ],
])

def get_config():

	f = open("config.json")

	config_json = json.load(f)

	api_key = config_json['api_key']

	#req_url = service_url + "?crtfc_key=" + api_key

	return api_key


def first_filter(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='1억 미만', callback_data='가격1'),
                    InlineKeyboardButton(text='1억 이상 5억 미만', callback_data='가격2'),
                    InlineKeyboardButton(text='5억 이상 10억 미만', callback_data='가격3'),
                    InlineKeyboardButton(text='10억 이상', callback_data='가격4'),
                    ],
               ])

    bot.sendMessage(chat_id, '최저 가격을 클릭해주세요', reply_markup=keyboard)

def second_filter(msg):
     content_type, chat_type, chat_id = telepot.glance(msg)

     keyboard = InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text='토지', callback_data='용도1'),
          InlineKeyboardButton(text='주거용건물', callback_data='용도2'),
          InlineKeyboardButton(text='상가용및업무용건물', callback_data='용도3'),
          InlineKeyboardButton(text='산업용및기타특수용건물', callback_data='용도4'),
          InlineKeyboardButton(text='용도복합용건물', callback_data='용도5'),
          ],
     ])

     bot.sendMessage(chat_id, '용도를 클릭해주세요', reply_markup=keyboard)
'''
def on_callback_query(msg):
     query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
     print('Callback Query:', query_id, from_id, query_data)

     bot.answerCallbackQuery(query_id, text='Got it')
'''

# callback 담겨있는 값
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print(query_id)
    print('Callback Query:', query_id, from_id, query_data)
    query_data = msg['data']
    if query_data == "가격1":
        bot.sendMessage(from_id, text = "물건1")
        bot.sendMessage(from_id, '용도를 선택해주세요', reply_markup=keyboard2)
        first_answer = "1억미만"
    elif query_data == "가격2":
        bot.sendMessage(from_id, text = "물건2")
        bot.sendMessage(from_id, '용도를 선택해주세요', reply_markup=keyboard2)
        first_answer = "1억-5억"
    elif query_data == "가격3":
        bot.sendMessage(from_id, text = "물건3")
        bot.sendMessage(from_id, '용도를 선택해주세요', reply_markup=keyboard2)
        first_answer = "5억-10억"
    elif query_data == "가격4":
        bot.sendMessage(from_id, text="물건4")
        bot.sendMessage(from_id, '용도를 선택해주세요', reply_markup=keyboard2)
        first_answer = "10억 이상"
    print(first_answer)

def on_callback_query2(msg):
     query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
     print(query_id)
     print('Callback Query:', query_id, from_id, query_data)
     query_data = msg['data']
     first_filter(msg)
     if query_data == "용도1":
          bot.sendMessage(from_id, text = "물건12")
     elif query_data == "용도2":
          bot.sendMessage(from_id, text = "물건23")
     elif query_data == "용도3":
          bot.sendMessage(from_id, text = "물건34")
     elif query_data == "용도4":
          bot.sendMessage(from_id, text="물건45")

MessageLoop(bot, {'chat': first_filter,
                  'callback_query': on_callback_query}).run_forever()
print('Listening ...')

while 1:
    time.sleep(10)

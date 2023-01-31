import firebase_admin
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
import json

#Alarm Setting
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CommandHandler, JobQueue, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
import datetime, pytz



#visualization
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import dataframe_image as dfi
from pandas.plotting import table


#lock implementation for user management. 동시에 여러 유저들이 global 변수에 접근하는 것을 대비
#고유 User id를 포함한 dictionary를 atomic하게 생성.

import threading

#system
from os import path





#race condition 방지
lock = threading.Lock()




#To-Do : user 정보 저장 db, users.json을 불러오는 부분을 firebase에서 불러오면 됨.
#jsonArray형태로 반환됨.
filename = "./users.json"

#유저, filter 선택 정보 반환
def get_user():
    user_list = []

    with open(filename, 'r') as user_file:
        user_list = json.load(user_file)


    return user_list

#########user정보 반환함수 끝 #####


# token, url 숨겨서 가져오기
def get_config() -> str:
    f = open('setting.json')
    config_json = json.load(f)
    url = config_json['firebase_url']
    token = config_json['bot_token']
    return url, token


#firebase, telegram-bot 설정
firebase_url, bot_token = get_config()

cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL' : firebase_url})
ref = db.reference('/items')


#가격에 대한 응답
first_result = ""
#용도에 대한 응답
second_result = ""
#가격에 대한 응답
category1 = ""
#용도에 대한 응답
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

#용도 선택 키보드
keyboard2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='토지', callback_data='용도1')],
                                                     [InlineKeyboardButton(text='주거용건물', callback_data='용도2')],
                                                     [InlineKeyboardButton(text='상가용및업무용건물', callback_data='용도3')],
                                                     [InlineKeyboardButton(text='산업용및기타특수용건물', callback_data='용도4')],
                                                     [InlineKeyboardButton(text='용도복합용건물', callback_data='용도5')]])






# 가격 범위 선택
def selectPrice(price: str, id: str) -> None:
    bot.send_message(id, '용도를 선택해주세요.', reply_markup=keyboard2)
    change_first_answer(price)

# 용도 선택
def selectType(category: str, id: str) -> None:
    change_second_answer(category)
    #print_answer(id)

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
    global category1
    category1 = type_dict[second_result]



# 결과 출력
def print_answer(id: str) -> None:
    print("1: ", first_result)
    print("2: ", second_result)
    print(f'category1: {category1}, price_range: {price_range}')
    output_list = find_object(id)
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

    bot.send_message(id, f'총 {len(result_list)}건이 도출되었습니다.')

    for data in result_list:
        btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='상세페이지로 이동', url=data['link'])]])
        bot.sendMessage(id, f"용도명: {data['category1']} / {data['category2']}\n\n지번: {data['location']}\n\n입찰일시: {data['duration']}\n\n감정가: {format(int(data['gamjung']), ',')}\n\n최저입찰가(비율): {format(int(data['lowest']), ',')}({data['rate']})\n\n유찰횟수: {data['fail_cnt']}", reply_markup=btn)
    #결과 값을 dataframe으로 변환
    #ax = plt.subplot(111, frame_on=False) # no visible frame
    #ax.xaxis.set_visible(False)  # hide the x axis
    #ax.yaxis.set_visible(False)  # hide the y axis


    #dataframe 변환
    #df = pd.DataFrame(result_list)

    #user-specific한 결과값을 저장하기 위해 img 변환후 id값을 filename으로 부여
    #dfi.export(df,"mytable"+str(id)+".png")
    #이미지 채팅창으로 전송
    #bot.send_photo(chat_id=id, caption="link", photo=open('mytable'+str(id)+'.png', 'rb'))


def find_object(id) -> list:

    result = []



    #user list(유저id, filter)정보 반환.
    user_list = get_user()

    #user_list의 user_id값만 따로 빼서 list로 만들기
    user_names = [x['user_id'] for x in user_list]


    #id값이 username에 있을 경우
    if id in user_names:
        #index 반환후
        select_count = user_names.index(id)
        #user 선택 및 category 및 가격  filter 가져오기
        #db에 저장된 user-specific filter값 활용하여 물건 탐색
        category1 = user_list[select_count]["filter"][0]
        print("test1",category1)
        price_range = user_list[select_count]["filter"][1]
        print("test2",price_range)
        #select_count += 1

        #user-specific filter 적용
        for item in ref.get():
            if(item['category1'] == category1 and (int(item['lowest']) >= price_range[0] and int(item['lowest']) < price_range[1])):
                result.append(item)

    #user가 없을 경우 = 필터 미등록
    else:
        bot.send_message(chat_id=id, text="필터를 등록하세요")




    return result



# callback 담겨있는 값
def callback_query_handler(update, context):
    query_data = update.callback_query.data
    from_id = update.effective_chat.id

    print(type(query_data))

    if query_data == '가격1' or query_data == '가격2' or query_data == '가격3' or query_data == '가격4':
        selectPrice(query_data, from_id)

    elif query_data == '용도1' or query_data == '용도2' or query_data == '용도3' or query_data == '용도4' or query_data == '용도5':

        selectType(query_data, from_id)
        bot.send_message(chat_id=from_id, text="물건 탐색중...")
        #race condition 방지
        lock.acquire()

        user_id = update.effective_chat.id
        print(user_id)

        #user list (id, filter) 정보 반환
        user_list = get_user()
        print("listobj: ", user_list)
        print("length?:", len(user_list))

        #사용자가 선택한 filter 정보
        user_dict = {"user_id" : user_id, "filter" : [category1, price_range]}


        #user name만 따로 빼서 list로 만들기
        user_names = [x['user_id'] for x in user_list]


        #이미 username이 존재 = 기존 패턴 등록
        if user_id in user_names:


            select_count = user_names.index(user_id)

            #filter값만 바꿔서 다시 users.json(db)에 등록
            user_list[select_count]["filter"] = user_dict["filter"]

            with open(filename, 'w',  encoding='utf-8') as json_file:
                json.dump(user_list, json_file,
                                    ensure_ascii=False,
                                    indent=4,
                                    separators=(',',': '))

        #username이 없을 경우 = 필터 새로 등록
        else :
            user_list.append(user_dict)
            with open(filename, 'w',  encoding='utf-8') as json_file:
                json.dump(user_list, json_file,
                                    ensure_ascii=False,
                                    indent=4,
                                    separators=(',',': '))

                #selectType(query_data, from_id)
        print_answer(from_id)

        lock.release()

        #selectType(query_data, from_id)


# 알람 세팅 부분
def search_msgs(update, context) -> None:

    #알람 세팅

    chat_id = update.message.from_user.id
    print("who are you? : ", chat_id)


    #알람 시간 세팅 hour = 시 min = 분
    t = datetime.time(hour=16, minute=23, tzinfo=pytz.timezone('Asia/Seoul'))

    #days = 월요일 0 기준
    context.job_queue.run_daily(callback_search_msgs,t,days=(0,1,2,3,4,5,6), context=update.message.chat_id, name=str(update.effective_chat.id))




def callback_search_msgs(context) -> None:

    chat_id = context.job.context


    #기존의 선택값 쌍(가격,용도)에 맞추어서 주기적으로 알람 발송
    print_answer(chat_id)

    #print_answer(user_id, recent_cnt)
    search_msgs(context, chat_id)


def display_handler_start(bot, update):
    chat_id = update.message.from_user.id
    print("who are you? : ", chat_id)
    user = update.message.from_user
    user_id = user['id']
    print("user id? : ", user_id)

    bot.send_message(
        chat_id=chat_id,
        text='최저 가격을 클릭해주세요',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='1억 미만', callback_data='가격1'),
                                                          InlineKeyboardButton(text='1억 이상 5억 미만', callback_data='가격2')],
                                                         [InlineKeyboardButton(text='5억 이상 10억 미만', callback_data='가격3'),
                                                          InlineKeyboardButton(text='10억 이상', callback_data='가격4')]]
            )
        )


#명령어 (물건탐색, 알림설정, 알림해제) handling
def handler(update, context) -> None:
    user_text = update.message.text
    lastChatId = update.message.chat_id
    if user_text == "알림설정": #ㅋㅋ라고 보내면 왜웃냐고 답장
        #context.job_queue.start()

        #if alarm 미등록 = 에러 출력

        bot.sendMessage(chat_id=lastChatId, text="일요일 오후 7시에 알림이 도착합니다") # 답장 보내기
        search_msgs(update, context)

        #bot.sendMessage(chat_id=lastChatId, text="일요일 오후 7시에 알림이 도착합니다") # 답장 보내기
    elif user_text == "알림해제":

        #if alarm 미등록 = 에러 출력


        bot.sendMessage(chat_id=lastChatId, text="알림을 해제합니다")
        #context.job_queue.stop()
        job_names = [job.name for job in context.job_queue.jobs()]
        name = job_names[0]
        current_jobs = context.job_queue.get_jobs_by_name(name)

        for job in current_jobs:
            job.schedule_removal()

    elif user_text == "물건탐색":
        display_handler_start(bot, update)

#handler 등록
def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher


    dp.add_handler(CommandHandler("search_msgs",search_msgs, pass_job_queue=True,
                                  pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.text, handler, pass_user_data=True))


    dp.add_handler(CommandHandler("start_select",display_handler_start, pass_job_queue=True,
                                  pass_user_data=True))

    dp.add_handler(CallbackQueryHandler(callback_query_handler))

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':

    token = bot_token

    #bot = telepot.Bot(token)
    bot = telegram.Bot(token = token)

    main()

    print('Listening ...')

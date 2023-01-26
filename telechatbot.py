import telegram
from telegram.ext import Updater,CommandHandler, JobQueue
from telegram.ext import MessageHandler, Filters
import datetime, pytz
import json


token = config[]
bot = telegram.Bot(token=token)



def get_config():

	f = open("config.json")

	config_json = json.load(f)

	api_key = config_json['api_key']

	#req_url = service_url + "?crtfc_key=" + api_key

	return api_key


# Search specific msgs on user request
def search_msgs(update, context):
    t = datetime.time(hour=14, minute=45, tzinfo=pytz.timezone('Asia/Seoul'))
    #context.job_queue.run_once(callback_search_msgs, context=update.message.chat_id, when=0)
    context.job_queue.run_daily(callback_search_msgs,t,days=(0,3,6), context=update.message.chat_id, name=str(update.effective_chat.id))
    #context.job_queue.run_repeating(callback_search_msgs, 7, context=update.message.chat_id, name=str(update.effective_chat.id))



def callback_search_msgs(context):
    print('안수혜 말보주', context.args)
    chat_id = context.job.context
    bot.sendMessage(chat_id=chat_id, text="Merry Meritz~~~")
    search_msgs(context, chat_id)

def handler(update, context):
    user_text = update.message.text
    lastChatId = update.message.chat_id
    if user_text == "알림설정": #ㅋㅋ라고 보내면 왜웃냐고 답장
        #context.job_queue.start()
        bot.send_message(chat_id=lastChatId, text="일요일 오후 7시에 알림이 도착합니다") # 답장 보내기
        search_msgs(update, context)
        #bot.send_message(chat_id=lastChatId, text="일요일 오후 7시에 알림이 도착합니다") # 답장 보내기
    elif user_text == "알림해제":
        bot.send_message(chat_id=lastChatId, text="알림을 해제합니다")
        #context.job_queue.stop()

        job_names = [job.name for job in context.job_queue.jobs()]
        name = job_names[0]
        current_jobs = context.job_queue.get_jobs_by_name(name)
        print("current_jobs:",current_jobs)
        for job in current_jobs:
            job.schedule_removal()
        #bot.setChatMute(lastChatId, mute=True)




def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    #updater.start_polling()
    #updates = bot.getUpdates()


    dp.add_handler(CommandHandler("search_msgs",search_msgs, pass_job_queue=True,
                                  pass_user_data=True))

    dp.add_handler(MessageHandler(Filters.text, handler, pass_user_data=True))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':

    token = get_config
    bot = telegram.Bot(token=token)
    main()

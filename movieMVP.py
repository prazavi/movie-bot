from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ChatAction
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
token = '1027310698:AAHzvAqsnIIdulMandJoltka8HkAFoOdLAM'
texts = {
    'btn1pg1': 'دانلود فیلم',
    'btn2pg1': 'دانلود سریال',
    'btn1pg2': 'ایرانی',
    'btn2pg2': 'خارجی',
    'btn1pg3': 'دوبله',
    'btn2pg3': 'زبان اصلی',
    'return': 'بازگشت به اول',
    'nextpage':'رفتن به صفحه ی بعد جست و جو'
}
global category
global language
global lanTalk
global listresult
listresult=[]
category = ''
language = ''
lanTalk = ''


def start_handler(update: Update, context: CallbackContext):
    menu(update, context)


def menu(update: Update, context: CallbackContext):
    buttons = [
        [texts['btn1pg1'], texts['btn2pg1']]
    ]
    update.message.reply_text(
        text='لطفا نوع فیلم یا سریال مورد نظر خود را انتخاب کنیم',
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def page2(update: Update, context: CallbackContext):
    global category
    if update.message.text == 'دانلود سریال':
        category = 'سریال'
    elif update.message.text == 'دانلود فیلم':
        category = 'فیلم'
    buttons = [
        [texts['btn1pg2'], texts['btn2pg2']],
        [texts['return']]
    ]
    update.message.reply_text(
        text='لطفا کشور سازنده را مشخص کنید',
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def page3(update: Update, context: CallbackContext):
    global language
    language = update.message.text
    buttons = [
        [texts['btn1pg3'], texts['btn2pg3']],
        [texts['return']]
    ]
    update.message.reply_text(
        text='لطفا زبان را مشخص کنید',
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def noresult(update: Update, context: CallbackContext):
    buttons = [
        [texts['return']]
    ]
    global category
    global language
    global lanTalk
    global listresult
    a = category
    b = language
    c = lanTalk
    ua = UserAgent()
    agent = ua.chrome
    df = pd.read_csv('movieMVP.csv')
    l = []
    temp = []
    s2=''
    if b == 'ایرانی':
        c = ' '
    if c==texts['btn2pg3']:
        s=f'{a}+{update.message.text}'
    else:
        s=f'{a}+{c}+{update.message.text}'
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    for i in range(len(df)):
        temp.append([])
        z = df['url'][i]
        url = df['url'][i] + (s.replace(' ', '+'))
        css_selector = df['search selector'][i]
        headers = {'User-Agent': f'{agent}'}
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.text, 'html.parser')
        title = soup.select(css_selector)
        temp[-1] += [[i.get_text(), re.findall('href="([^"]+)', str(i))[0], z] for i in title]
    while (temp != [0] * len(temp)):
        for i in range(len(temp)):
            if temp[i] == 0 or len(temp[i]) == 0:
                temp[i] = 0
                continue
            l.append(temp[i][0])
            temp[i].pop(0)
    l = l[-1:-len(l) - 1:-1]
    listresult=l
    if len(l)==0:
        update.message.reply_text(
            text=f' {a} {b} {c} {update.message.text} هنوز در ربات قرار داده نشده است ',
            reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
    else:
        for i in range(len(l)):
            s2 += f'''{i + 1})  {l[i][0]}
  
  '''
    update.message.reply_text(f'{s2} ')
    update.message.reply_text('لطفا شماره مطلب مورد نظر خود را وارد کنید')
    category = language = lanTalk = ''


def searchpage(update: Update, contex: CallbackContext):
    global lanTalk
    lanTalk = update.message.text
    a = category
    update.message.reply_text(f' لطفا نام {a} را وارد کنید ')


def newresult(update:Update,context:CallbackContext):
    s=''
    if update.message.text=='0' or int(update.message.text) > len(listresult):
        update.message.reply_text('کد داده شده صحیح نمی باشد. لطفا دوباره سعی کنید')
    else:
        l=listresult
        selected=int(update.message.text)-1
        ua = UserAgent()
        agent = ua.chrome
        df = pd.read_csv('movieMVP.csv')

        for i in range(len(df)):
            if df['url'][i] == l[selected][2]:
                css_selector = df['main selector'][i]
                stopper = df['stopper'][i]
                break

        url = l[selected][1]
        chat_id=update.message.chat_id
        context.bot.send_chat_action(chat_id,ChatAction.TYPING)
        headers = {'User-Agent': f'{agent}'}
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.text, 'html.parser')
        title = soup.select(css_selector)
        for i in title:
            if stopper == 'yes' and i == title[-1]:
                break
            # print(i.get_text())
            if 'href' in str(i):
                s2=re.sub(':.*$','',str(i.get_text()))
                s+=f'''{s2}
{re.findall('href="([^"]+)', str(i))[0]}
 '''
        update.message.reply_text(f'{s}')
updater = Updater(token, use_context=True)

start_command = CommandHandler('start', start_handler)

updater.dispatcher.add_handler(start_command)
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn1pg1']), page2))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn2pg1']), page2))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn1pg2']), searchpage))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn2pg2']), page3))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn1pg3']), searchpage))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['btn2pg3']), searchpage))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(texts['return']), start_handler))
updater.dispatcher.add_handler(MessageHandler(Filters.regex('^([0-9]+)$'), newresult))
updater.dispatcher.add_handler(MessageHandler(Filters.text, noresult))
updater.start_polling()

updater.idle()

from flask import Flask
from flask import request
import flask
import telebot
from config import TOKEN
from datetime import datetime
from telebot import types
import telebot_calendar
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import requests
from bs4 import BeautifulSoup
import os

URL = 'https://api.telegram.org/bot%s/' % TOKEN


app = Flask(__name__)
bot = telebot.TeleBot(TOKEN) 
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1 = CallbackData('calendar_1', 'action', 'year', 'month', 'day')
now = datetime.now()
info = []
cloc = []

# Функция чтение даты записи
def dcloc(time):
     with open("/opt/home/bot/data.txt") as f:
         lines = f.readlines()
     for line in lines:
         if time == line[:-1]:
             return True
     return False
     
# Функция чтение tmp файла            
def reeder(score):
     with open(f"/opt/home/bot/temp/{score}.txt") as f:
         lines = f.readlines()
     num = len(lines)
     st = lines[num-1]
     text = st.split("|")
     return text
     
# Функция запись в файл            
def write_f(data, filename):
     with open(filename, 'a+', encoding='utf-8') as f:
         f.write(str(data))
         
# Бот парсит сайт на определенной вкладке и отправляет информацию в телеграм канал
@app.route('/parse', methods=['POST', 'GET'])
def parse():
     channel_id = "-"  #Ваш логин канала
     URL = "ссылка вкладки сайта"
     URL_1 = "ссылка главной страницы сайта"
     page = requests.get(URL)
     soup = BeautifulSoup(page.content, "html.parser")
     #запись в файл последний пост
     def write_f(data, filename):
         with open(filename, 'a+') as f:
             f.write(str(data))
     #Чтение из файл
     def reeder(str):
         with open("name.txt") as f:
             lines = f.read()
         if str in lines:
             return True
         else:
             return False
     l_list = []
     for url in soup.find_all("a", "preview__href ae--hover-effect__parent js--hover-effect__parent", href=True):
         u = url['href']
         l_list.append(u)
     title = soup.find("div", class_="preview__title f__h3").text.strip()
     if reeder(title) == True:
         print("ok")
     elif reeder(title) == False:
         bot.send_message(channel_id, l_list)
         write_f(title + "\n", 'name.txt')
     return '<h1>Привет!!!</h1>'
     
# Бот записи клиента на услугу     
@app.route('/%s'%(TOKEN), methods=['POST', 'GET'])
def webhook():
	 if flask.request.headers.get('content-type') == 'application/json':
		 json_string = flask.request.get_data().decode('utf-8')
		 update = telebot.types.Update.de_json(json_string)
		 bot.process_new_updates([update])
		 return '<h1>Вы на главной странице!!!</h1>'
	 else:
		 flask.abort(403)

        
@bot.message_handler(commands=['start'])
def start(message):
     t = datetime.now()
     str_t = t.strftime("%H")
     d = int(str_t)
     if 5 <= d <= 11:
         mes = f'Доброе утро, {message.from_user.first_name}!'
     elif 12 <= d <= 17:
         mes = f'Добрый день, {message.from_user.first_name}!'
     elif 18<= d <= 21:
         mes = f'Добрый вечер, {message.from_user.first_name}!'
     elif 22 <= d <= 24 or 0 <= d <= 4:
         mes = f'Доброй ночи, {message.from_user.first_name}!' 
     bot.send_message(message.chat.id, mes)
     
@bot.message_handler(commands=['web'])
def website(message):
     markup = types.InlineKeyboardMarkup()
     button1 = types.InlineKeyboardButton('Сайт', url='сайт')
     button2 = types.InlineKeyboardButton('Телеграм канал', url='ссылка на соц.сеть')
     button3 = types.InlineKeyboardButton('ВК', url='ссылка на соц.сеть')
     markup.add(button1,button2,button3)
     bot.send_message(message.chat.id, "Нажмите", reply_markup=markup)
     
@bot.message_handler(commands=['recoding'])
def recod(message):
     keyboard = types.ReplyKeyboardMarkup(True)
     button1 = types.KeyboardButton('Да')
     button2 = types.KeyboardButton('Нет')
     keyboard.add(button1,button2)
     bot.send_message(message.chat.id, 'Планируете записаться?', reply_markup=keyboard)
     
@bot.message_handler(content_types=['text'])
def city(message):
     if message.text == 'Да':
         info.clear()
         keyboard = types.ReplyKeyboardMarkup(True)
         button1 = types.KeyboardButton('Москва/Подмосковье')
         button2 = types.KeyboardButton('Санкт-Петербург')
         button3 = types.KeyboardButton('Казань')
         button4 = types.KeyboardButton('Выход')
         keyboard.add(button1)
         keyboard.add(button2)
         keyboard.add(button3)
         keyboard.add(button4)
         bot.send_message(message.chat.id, "Из какого вы города?", reply_markup = keyboard)
         bot.register_next_step_handler(message,shooting)
         num_id = message.chat.id
         name_us = message.from_user.first_name
         mess_time = datetime.now().replace(second=0, microsecond=0)
         #Запись в log file
         write_f(str(num_id) + " | " + str(mess_time) + " | " + name_us + " | ", "name.txt")
         
     elif message.text == 'Нет':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, 'Вы вышли из сервиса', reply_markup=remove)
         
def shooting(message):
     text = message.text
     if text.lower() == "москва/подмосковье" or text.lower() == "санкт-петербург" or text.lower() == "казань":
         keyboard = types.ReplyKeyboardMarkup(True)
         button1 = types.KeyboardButton('Свадебная')
         button2 = types.KeyboardButton('Беременность')
         button3 = types.KeyboardButton('Love story')
         button4 = types.KeyboardButton('Семейная')
         button5 = types.KeyboardButton('Выход')
         keyboard.add(button1)
         keyboard.add(button2)
         keyboard.add(button3)
         keyboard.add(button4)
         keyboard.add(button5)
         bot.send_message(message.chat.id, "Выберете формат съемки",reply_markup=keyboard)
         bot.register_next_step_handler(message, hour)
         #Запись в log file
         write_f(text + " | ", "name.txt")
         
     elif text.lower() == 'выход':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, 'Заявка анулирована', reply_markup=remove)
         #Удалаяем из файла данные которые записали
         os.system(r'>/name.txt')
     
def hour(message):
     if message.text == 'Свадебная' or message.text == 'Беременность' or message.text == 'Love story' or message.text == 'Семейная':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, "Напишите количество часов:\n\nДля выхода из записи - напишите 'Выход'", reply_markup=remove)
         bot.register_next_step_handler(message, call)
         #Запись в log file
         write_f(message.text + " | ", "name.txt")
         
     elif message.text == 'Выход':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, 'Заявка анулирована', reply_markup=remove)
         #Удалаяем из файла данные которые записали
         os.system(r'>/name.txt')
     
             
def call(message):
    #высвечиваем календарь
     if message.text.isdigit() == True:
         bot.send_message(message.chat.id, 'Выберите дату', reply_markup=calendar.create_calendar(name=calendar_1.prefix,year=now.year,month=now.month))
         bot.register_next_step_handler(message, result)
         #Запись в log file
         write_f(message.text + " | ", "name.txt")
     elif message.text == 'Выход':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, 'Заявка анулирована', reply_markup=remove)
         #Удалаяем из файла данные которые записали
         os.system(r'>/name.txt')
         
def result(message):
     number = message.text
     #Запись в log file
     write_f(number + "\n", "/name.txt")
     spisok = reeder(message.chat.id)
     key = ['id','generated','name','city','shooting','quantity','date','number']
     diction = dict(zip(key,spisok))
     keyboard = types.ReplyKeyboardMarkup(True)
     button1 = types.KeyboardButton('Все правильно')
     button2 = types.KeyboardButton('Есть ошибки')
     button3 = types.KeyboardButton('Изменить имя')
     button4 = types.KeyboardButton('Выход')
     keyboard.add(button1,button2,button3)
     keyboard.add(button4)
     bot.send_message(message.chat.id, f"Проверим, все ли я правильно запомнил:\n-Ваше имя: {diction['name']}\n-Город, провередния съемки: {diction['city']}\n-Формат съемки: {diction['shooting']}\n-Количество часов: {diction['quantity']}\n-Дата: {diction['date']}\n-Номер вашего телефона: {diction['number']}\n\nЕсли ваш nickname в телеграмме отличается, от настоящего, то вы можете изменить имя, нажав на кнопку.\nЕсли все правильно, то нажмите на соотвествующую кнопку.", reply_markup = keyboard)
     bot.register_next_step_handler(message, itsok)

def itsok(message):
     if message.text == 'Все правильно':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, "Отлично, я вас записал!",reply_markup = remove)
         diction.clear()
     elif message.text == 'Есть ошибки':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, "Напишите в свободной форме с пометкой, что не правильно и я перезапишу ваши данные", reply_markup = remove)
         bot.register_next_step_handler(message, thend)
     elif message.text == 'Изменить имя':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, "Напишите, ваше имя",reply_markup=remove)
         bot.register_next_step_handler(message, thend)
     elif message.text == 'Выход':
         remove = types.ReplyKeyboardRemove()
         bot.send_message(message.chat.id, 'Заявка анулирована', reply_markup=remove)
         os.system(r'>/opt/home/bot/temp/{}.txt'.format(message.chat.id))
         
def thend(message):
     bot.send_message(message.chat.id, "Изменил!\nСпасибо, что воспользовались данным сервисом.")
     #Запись в log file
     write_f("Изменения: " + message.text + "\n", "/name.txt")
     diction.clear()
     
#Обработчик календаря    
@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: types.CallbackQuery):
     name, action, year, month, day = call.data.split(calendar_1.sep)
     date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
     if action == 'DAY':
         datnum = str(date.strftime("%d.%m.%Y"))
         if dcloc(datnum) == True:
             bot.send_message(chat_id=call.from_user.id, text='Данная дата занята')
             bot.send_message(chat_id=call.from_user.id, text='Попробуйте снова выбрать дату', reply_markup=calendar.create_calendar(name=calendar_1.prefix,year=now.year,month=now.month))
         elif dcloc(datnum) == False:
             bot.send_message(chat_id=call.from_user.id, text=f'Вы выбрали {date.strftime("%d.%m.%Y")}\nОставьте свой контактный номер телефона, чтобы с вами связаться:', reply_markup=types.ReplyKeyboardRemove())
             #Запись в log file
             write_f(str(date.strftime("%d.%m.%Y")) + ' | ',  f"/name.txt")
     elif action == 'CANCEL':
         bot.send_message(chat_id=call.from_user.id, text='Запись отменена', reply_markup=types.ReplyKeyboardRemove())
         os.system(r'>/name.txt')
         
if __name__ == '__main__':
	 app.run()
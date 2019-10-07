# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.datawars
users=db.users
chats=db.chats
cdatas=db.cdatas


def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode) 


@bot.message_handler(commands=['start'])
def start(m):
    register(m)
    

def register(m):
    user=users.find_one({'id':m.from_user.id})
    if user==None:
        users.insert_one(createuser(m.from_user))
        bot.send_message(m.chat.id, 'Добро пожаловать в Data collectors, '+m.from_user.first_name+'! Собирай данные, и используй их для создания и модернизации '+
                         'своего оборудования!')

@bot.message_handler(commands=['mount'])
def mount_to_chat(m):
    if chats.find_one({'id':m.chat.id})==None:
        if m.message_id>=1000:
            chats.insert_one(createchat(m))
        
            bot.send_message(m.chat.id, 'Монтирование...\n...\n...\n...\n...\n...\n...\n...\n...\n...\n...\n...\n...'+
                         '\n...\n...\n...\n...\n...\n...\nУспех! Теперь в этом чате можно собирать '+
                         'данные! Ожидайте их появления в случайные промежутки времени.')
        else:
            bot.send_message(m.chat.id, 'Монтирование...\nОшибка! Чат существует слишком мало!')
    else:
        bot.send_message(m.chat.id, 'Монтирование...\nОшибка! Оборудование уже было установлено в данный чат!')
        
  

def createchat(m):
    return {
        'id':m.chat.id,
        'count':bot.get_chat_members_count(m.chat.id),
        'last_data':0
    }


def createuser(user):
    return {
        'id':user.id,
        'name':user.first_name,
        'username':user.username,
        'base_speed':100,      # Добыча данных за 1 клик
        'data_romb_blue':0,
        'data_romb_orange':0,
        'data_triangle_red':0,
        'data_circle_black':0,
        'data_volume':0,
        'data_energy':0,
        'data_time':0,
        'data_universal':0
    }
        


def data_spawn(id):
    x=time.ctime()
    x=x.split(" ")
    month=0
    year=0
    ind=0
    num=0
    for ids in x:
       for idss in ids:
          if idss==':':
             tru=ids
             ind=num
       num+=1
    day=x[ind-1]
    month=x[1]
    year=x[ind+1]
    x=tru 
    x=x.split(":")  
    mins=int(x[1])     # минуты
    hours=int(x[0])+3  # часы (+3, потому что heroku в Великобритании)
    
    avalaible=[]
    
    if hours>=23 or hours<=8:
        avalaible.append('data_romb_blue')
    if mins>=50 and mins<=60:
        avalaible.append('data_romb_orange')
    if day>=15:
        avalaible.append('data_volume')
    if day<=15:
        avalaible.append('data_time')
    if day==1 and hours>=12 and hours<=20:
        avalaible.append('data_universal')
    avalaible.append('data_energy')
    if hours>=12 and hours<=20:
        avalaible.append('data_triangle_red')
    if mins<=15:
        avalaible.append('data_circle_black')
    
    cdata=random.choice(avalaible)
    value=random.randint(300, 600)
    if random.randint(1,100)<=30:
        value=random.randint(600, 1000)
    if random.randint(1,100)<=15:
        value=random.randint(1000, 2000)
    uid=idgen()
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text=convert(what=cdata, to='emoji')+' ('+str(value)+')', callback_data='catch '+uid))
    msg=bot.send_message(id, 'Новые данные!', reply_markup=kb)
    cdatas.insert_one(createdata(cdata, value, id, time.time(), msg.message_id, uid))
    
    

    
def convert(what, to):
    if to=='emoji':
        if what=='data_romb_blue':
            return '🔹'
        if what=='data_romb_orange':
            return '🔸'
        if what=='data_triangle_red':
            return '🔻'
        if what=='data_circle_black':
            return '⚫'
        if what=='data_volume':
            return '🔊'
        if what=='data_energy':
            return '🔋'
        if what=='data_time':
            return '⏱'
        if what=='data_universal':
            return '🧿'
    return 'error'
        


def createdata(cdata, value, id, ctime, msgid, uid):
    return {
        'type':cdata,
        'value':value,
        'chatid':id,
        'createtime':ctime,
        'message_id':msgid,
        'uid':uid
    }


def idgen():
    names=[]
    for ids in cdatas.find({}):
        names.append(ids['data'])
        
    symb=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
           '1' , '2' , '3' , '4' , '5' , '6' , '7' , '8' , '9' , '0']
    lenght=5
    x=''
    while len(x)<lenght:
        x+=random.choice(symb)
    while x in names:
        x=''
        while len(x)<lenght:
            x+=random.choice(symb)
    return x
                                      
    
def data_catch():
    threading.Timer(60, data_catch).start()
    for ids in chats.find({}):
        coef=(time.time()-ids['last_data'])/1000
        if random.randint(1, 100)<=coef:
            data_spawn(ids['id'])
            


print('7777')
bot.polling(none_stop=True,timeout=600)


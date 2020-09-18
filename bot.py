from boto.s3.connection import S3Connection
from flask import Flask, request
import apiai
import datetime
import gspread
import json
import random
import re
import vk
import os
import wolframalpha
s3 = S3Connection(os.environ['app_id'], # 0
                  os.environ['df_key'], # 1
                  os.environ['VK_API_ACCESS_TOKEN'], # 2
                  os.environ['gspread'],# 3
                  os.environ['service_account'])  # 4

# const
app_id = os.environ['app_id']
client = wolframalpha.Client(app_id)
app = Flask(__name__)
df_key = os.environ['df_key']
VK_API_ACCESS_TOKEN = os.environ['VK_API_ACCESS_TOKEN']
VK_API_VERSION = '5.85'
session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
vk = vk.API(session, v=VK_API_VERSION)

weekDaysNames = ('Понедельник', 'Вторник', 'Среда', 'Четверг',
                 'Пятница', 'Суббота', 'Воскресенье')
deleteNames = 'princesscarolyn', 'princesscarolyn,', '[club196031603|]', '*princesscarolyn','*princesscarolyn,','[club196031603|],'

sendDataID = 0, 229550415
# datetime.datetime.today().weekday()

def sendMsg(id, text):
    vk.messages.send(
        peer_id=id,
        message=text,
        random_id=random.randint(1, 2147483647)
    )

def sendFile(id, File, text='&#13;'):
    vk.messages.send(
        peer_id=id,
        message=text,
        attachment=File,
        random_id=random.randint(1, 2147483647)
    )


def askDialogFlow(clientText):
    ai_req = apiai.ApiAI(df_key).text_request()
    ai_req.lang = 'ru'
    ai_req.session_id = '8871'
    ai_req.query = clientText
    responseJson = json.loads(
        ai_req.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech']
    if response:
        ask = response
    else:
        ask = ""
    return ask

def askWolfram(clientText):
    res = client.query(clientText)
    return next(res.results).text

def findPhotos(answer):
    all_photos_text = ''
    if 'photo-' in answer:
        photo_pattern = r'photo-[\S]+'
        photos = re.findall(photo_pattern, answer)
        if(len(photos)) > 1:
            for i in range(0, len(photos)):
                answer = answer.replace(photos[i], '')
                all_photos_text += photos[i]
                if i != len(photos):
                    all_photos_text += ','
        else:
            answer = answer.replace(photos[0], '')
            all_photos_text = photos
    return (answer, all_photos_text)


def checkWeek(answer):
    WeekText = ''
    if 'time' in answer:
        WeekText = '\nТекущая неделя '
        now = datetime.datetime.now()
        answer = answer.replace('time', '')
        wckNumber = datetime.date(
            now.year, now.month, now.day).isocalendar()[1]
        if wckNumber % 2 == 0:
            WeekText += str(wckNumber - 35) + \
                ', ЕДИНИЧКА (смотри расп. под 1)'
        else:
            WeekText += str(wckNumber - 35) + \
                ', ДВОЙКА  (смотри расп. под 2)'
    return (answer, WeekText)


def checkSchedule(answer):
    HaveSchedule = False
    # check photos
    listAnswers = findPhotos(answer)
    answer = listAnswers[0]
    all_photos_text = listAnswers[1]
    # check date
    listAnswers = checkWeek(answer)
    answer = listAnswers[0]
    WeekText = listAnswers[1]

    if all_photos_text != '' or WeekText != '':
        HaveSchedule = True
    return (HaveSchedule, all_photos_text, answer + WeekText)

def dataPost():
    #difference 3 hours
    answerText = askDialogFlow(
        weekDaysNames[datetime.datetime.today().weekday()])
    listAnswers = checkSchedule(answerText)
    for i in range(1, len(sendDataID)):
        sendMsg(sendDataID[i], "С добрым утром!")
        sendFile(sendDataID[i], listAnswers[1], listAnswers[2])


def HomeWorkAnswer():
    gc = gspread.service_account(filename='/home/Mentoster/mysite/homework.json')
    sh = gc.open_by_key(os.environ['gspread'])
    worksheet = sh.sheet1
    NameOfPars = worksheet.col_values(6)
    HomeWork = worksheet.col_values(7)
    dates = worksheet.col_values(8)
    answer = ("Держи! Не забудь сказать спасибо! \n\nНазвание предмета : Задание : Дата\n\n================================\n")
    for i in range(2, len(HomeWork)):
        if HomeWork[i] != '':
            answer += ("\n"+str(NameOfPars[i])+" : \n" +
                        str(HomeWork[i])+"\nНужно выполнить к: "+str(dates[i])+'\n\n================================\n')
    answer+="\nссылка с ДЗ: https://vk.cc/azk3aW"
    return answer
# function for answers
app = Flask(__name__)

sendMsg(229550415, "Я запустилась!")

@ app.route('/', methods=["POST"])
def main():
    data = json.loads(request.data)
    if data["type"] == "confirmation":
        return "0c945684"
    elif data["type"] == "message_new":
        object = data["object"]
        id = object["peer_id"]
        body = object["text"]
        clientText = body.lower()

        # удаляем обращение, если оно есть
        # удаляем обращение, если оно есть
        for word in deleteNames:
            clientText = clientText.replace( word, '')
            break
        if 'инфо' in clientText:
            answer = "Привет, я Принцесса Кэролин, и я являюсь персональным менеджером @dimamakarov12345!\n Он меня нанял, чтобы помочь вам! \n С помощью меня, вы можете быстро создавать заметки, или спросить о чем-нибудь важном,\n   Надеюсь, что я буду вам очень полезна! ❤",
            answer2 = "\n Так же я умею считать сложные уровнения.\n Для того, чтобы обратиться к моему модулю wolfram alpha\n Набери команду WTF (wolfram talk function) и действие, которое хочешь сделать"
            sendMsg(id, answer)
            sendMsg(id, answer2)
            return "ok"
        elif 'wtf' in clientText:
            clientText = clientText.replace('wtf ', ' ')
            answer = askWolfram(clientText)
            sendMsg(id, answer)

            return "ok"
        else:
            answer = askDialogFlow(clientText)
            if answer != '':
                listAnswers = checkSchedule(answer)
                if listAnswers[0]==True:
                    sendFile(id, listAnswers[1], listAnswers[2])
                else:
                    if 'homework' in answer:
                        answer=HomeWorkAnswer()
                    sendMsg(id, answer)
            return "ok"
    elif data["type"] =="wall_post_new":
        dataPost()
    return "ok"


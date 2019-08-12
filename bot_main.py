import requests
import random
from copy import deepcopy
import json
from time import sleep
from time import time
from time import ctime
import pandas as pd
import yaml
import pickle
from ast import literal_eval

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
url = config['url']
with open('synonyms.pickle', 'rb') as fp:
    synonyms = pickle.load(fp)
df = pd.read_csv('df_final.csv', delimiter="$")
df2 = pd.read_csv('df_grammar.csv', converters={'form_variants': literal_eval}, delimiter="$")
df3 = pd.read_csv('df_mistakes.csv', delimiter="$")

with open('photos_heroku_bot.pickle', 'rb') as fp:
     photos = pickle.load(fp)
good_photos = photos['good_photos']
bad_photos = photos['bad_photos']
good = ["Oh, uh, okay, that's fine, that's great.", "You're doing great, you're doing fine.", "You're right, you're right. Ah, you are so yumm.", "Wow, you are really gettin' good at that", "God, you are so lucky.", "Man you are incredible.", "Oh God, you are about to get sooo lucky.", "Great, oh you are such a sweetheart", "you're right, you are absolutely right", "You are gonna be a huge star!", "You are unbelievable.", "You are really good!", "You are incredible", "You are such a nice person.", "You are SO going to Heaven!","Oh boy. You are doin' so good."]
bad = ['Oh, this is so stupid!', 'What are you just some big, dumb, stupid, doofy idiot, with a doofy idiot hairdo, huh?! Huh?!', 'Idiot!! Stupid little, fuzzy, yellow creature!!', "God, you're so stupid, how are you not yet extinct!!", "Well that didn't really work out too well for you did it you idiot!!", "No, you messed it up. You're stupid.", "Are you an idiot?", "Dude, you are sick.", "You are way off, pal.", "We think you're a horrible human being, and bad things should happen to you.",
       "You know I just want to say..That you are a horrible, horrible person."]

bad_dict={'Oh, this is so stupid!': "I'm ready to do better!",
 'What are you just some big, dumb, stupid, doofy idiot, with a doofy idiot hairdo, huh?! Huh?!':"I'm not an idiot!!! You are an idiot!!!",
 'Idiot!! Stupid little, fuzzy, yellow creature!!':"I'm an intelligent creature and I'll solve this puzzle",
 "God, you're so stupid, how are you not yet extinct!!":"I'm very bright. I'll figure it out",
 "Well that didn't really work out too well for you did it you idiot!!":"I'm very smart. I'll get it this time",
 "No, you messed it up. You're stupid.":"This time I'll get it right",
 "Are you an idiot?":"No, I'm definitely not!",
 "Dude, you are sick.":"It's you who are sick, dude",
 "You are way off, pal.":"I'll get it this time",
 "We think you're a horrible human being, and bad things should happen to you.":"I'm a wonderful human being and only marvellous things should happen to me!!!",
 "You know I just want to say..That you are a horrible, horrible person.": "I'm an extremely good, kind and smart person and I'll figure out the right answer!"}

def log_in_file(text):
    with open('python.log', 'a', encoding='utf-8') as log_file:
        log_file.write(str(ctime(time())) + text + '\n')


def get_updates_json(request, offset):
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(request + 'getUpdates', data=params)
    return response.json()


def get_chat_id(update):
    chat_id = update['message']['chat']['id']
    return chat_id


def last_update(data): # возвращает json последнего сообщения
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]


def send_mess(params):
    response = requests.post(url + 'sendMessage', data=params)
    return response


def send_start_mes(chat_id):
    reply_markup = {'keyboard': [['Make English with Friends']], 'resize_keyboard': True,
                    'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    params = {"reply_markup": reply_markup, 'chat_id': chat_id, 'text': 'Press the button to begin'}
    send_mess(params)


questions = {}


def make_quiz1():
    random_num = random.randint(0, len(df)-1)
    row = df.iloc[random_num]
    text = row['t_for_user']
    answer = row['w_form'].lower()
    list_syn = row['list_syn']
    but_list = deepcopy(synonyms[list_syn])
    if answer in but_list:
        but_list.remove(answer)
    but_list = random.sample(but_list, 3)
    but_list.append(answer)
    random.shuffle(but_list)
    but_list = [[i] for i in but_list]
    return answer, but_list, text


def make_quiz2():
    random_num = random.randint(0, len(df2) - 1)
    row = df2.iloc[random_num]
    text = row['sent_for_user']
    answer = row['answer'].lower()
    list_syn = row['form_variants']
    but_list = deepcopy(list_syn)
    if answer in but_list:
        but_list.remove(answer)
    but_list = random.sample(but_list, 3)
    but_list.append(answer)
    random.shuffle(but_list)
    but_list = [[i] for i in but_list]
    return answer, but_list, text

def make_quiz3():
    random_num = random.randint(0, len(df3)-1)
    row = df3.iloc[random_num]
    text = row['t_for_user']
    answer = row['w_form'].lower()
    list_syn = row['list_syn']
    common_mistake = row['common_mistake'].lower()
    but_list = deepcopy(synonyms[list_syn])
    if answer in but_list:
        but_list.remove(answer)
    if common_mistake in but_list:
        but_list.remove(common_mistake)
    but_list = random.sample(but_list, 2)
    but_list.append(answer)
    but_list.append(common_mistake)
    random.shuffle(but_list)
    but_list = [[i] for i in but_list]
    return answer, but_list, text

def choose_quiz():
    i = random.randint(1, 3)
    if i == 1:
        return make_quiz1()
    elif i == 2:
        return make_quiz2()
    else:
        return make_quiz3()




def quiz_info(chat_id):
    answer, but_list1, text = choose_quiz()
    but_list = [[but_list1[0][0], but_list1[1][0]],[but_list1[2][0], but_list1[3][0]] ]
    but_list.append(['STOP IT'])
    reply_markup = {'keyboard': but_list, 'resize_keyboard': True,
                    'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    params = {"reply_markup": reply_markup, 'chat_id': chat_id, 'text': text}
    return answer, params


def send_quiz_mes(chat_id,  questions):
    answer, params = quiz_info(chat_id)
    questions[chat_id] = {}
    questions[chat_id]['answer'] = answer
    questions[chat_id]['params'] = params
    send_mess(params)
    return questions


def send_same_quiz(chat_id, questions):
    params = questions[chat_id]['params']
    send_mess(params)


def send_result_mes(chat_id, result):
    params = {'chat_id': chat_id, 'text': result}
    send_mess(params)


def send_good_result_mes(chat_id):
    random_photo = random.randint(0, len(good_photos)-1)
    random_text = random.randint(0, len(good)-1)
    params = {'chat_id': chat_id, 'photo': good_photos[random_photo], 'caption': good[random_text]}
    requests.get(url + 'sendPhoto', data=params)
    print('random_photo, random_text: ', random_photo, random_text)
    log_in_file(' good random_photo, random_text: ' + str(random_photo) + str(random_text))


def send_bad_result_mes(chat_id): # send foto with text and key with text
    random_photo = random.randint(0, len(bad_photos)-1)
    random_text = random.randint(0, len(bad)-1)
    questions[chat_id]['bad_reply'] = bad_dict[bad[random_text]]
    print('questions in send bad result mes: ', questions)
    reply_markup = {'keyboard': [[bad_dict[bad[random_text]]]], 'resize_keyboard': True,
                                    'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    params = {'chat_id': chat_id, 'photo': bad_photos[random_photo], 'caption': bad[random_text], "reply_markup": reply_markup}
    requests.get(url + 'sendPhoto', data=params)
    print('random_photo, random_text: ', random_photo, random_text)
    log_in_file('  bad random_photo, random_text: ' + str(random_photo) + str(random_text))


def next_one(chat_id):
    reply_markup = {'keyboard': [['I want next quiz!']], 'resize_keyboard': True,
                    'one_time_keyboard': True}
    reply_markup = json.dumps(reply_markup)
    params = {"reply_markup": reply_markup, 'chat_id': chat_id, 'text': 'Next one?'}
    send_mess(params)


user_info = {}


def get_all_info(offset):
    try:
        all_updates = get_updates_json(url, offset)
        print('all data: ', all_updates)
        log_in_file('  all data: ' + str(all_updates))

        print('LEN inner cycle: ', len(all_updates['result']))
        log_in_file('  LEN inner cycle: ' + str(len(all_updates['result'])))
        update_for_offset = last_update(all_updates)['update_id']
        print('update for upset: ', update_for_offset)
        log_in_file(' update for upset: ' + str(update_for_offset))

    except:
        print('tried and failed')
        log_in_file(' tried and failed')
        return
    update_dict = {}
    for el in all_updates['result']:
        id = el['update_id']
        print('id: ', id)
        log_in_file(' id: '+ str(id))
        chat_id = el['message']['chat']['id']
        print('chat id:', chat_id)
        log_in_file(' chat id:' + str(chat_id))

        try:
            user_id = el['message']['from']['id']
        except:
            user_id = 'hidden'
        try:
            first_name = el['message']['from']['first_name']
        except:
            first_name = '*'
        try:
            last_name = el['message']['from']['last_name']
        except:
            last_name = '*'
        try:
            username = el['message']['from']['username']
        except:
            username = '*'
        name = first_name + ' ' + last_name + ' ' + username
        if user_id not in user_info:
            user_info[user_id] = name
        try:
            last_mes = el['message']['text']
        except Exception:
            last_mes = '*'
        print("last_mes: ", last_mes)
        log_in_file(" last_mes: " + str(last_mes))
        is_bot = el['message']['from']['is_bot']
        update_dict[id] = [chat_id, last_mes, is_bot]
    print('update_dict: ', update_dict)
    log_in_file(' update_dict: ' + str(update_dict))
    return update_for_offset, update_dict


def answer(chat_id, last_mes, is_bot):
    if is_bot==False:
        print('last_mes in answer: ', last_mes)
        if last_mes == '/start':
            print("last_mes == '/start'")
            log_in_file(" last_mes == '/start'")
            send_start_mes(chat_id)
        elif last_mes == 'STOP IT' or last_mes == '/stop':
            print("last_mes == 'stop it'")
            log_in_file(" last_mes == 'stop it'")
            if chat_id in questions:
                del questions[chat_id]
            send_start_mes(chat_id)
            print(' after stop ', questions)
            log_in_file(' after stop ' + str(questions))
        elif last_mes == 'Make English with Friends' or last_mes == 'I want next quiz!':
            print("last_mes == ", last_mes)
            log_in_file(" last_mes == " + str(last_mes))
            send_quiz_mes(chat_id, questions)
            print('quiz: ', questions)
            log_in_file('quiz: ' + str(questions))
        elif chat_id in questions:
            print('chat_id in questions: ', questions)
            print('last_mes if chat_id in questions:', last_mes)
            try:
                print("questions[chat_id]['bad_reply']: ", questions[chat_id]['bad_reply'])
                print(last_mes == questions[chat_id]['bad_reply'])
            except:
                pass

            if last_mes.lower() == questions[chat_id]['answer']:
                send_good_result_mes(chat_id)
                del questions[chat_id]
                next_one(chat_id)

            elif ('bad_reply' in questions[chat_id]) and (last_mes == questions[chat_id]['bad_reply']):
                print('sending_same_quiz')
                send_same_quiz(chat_id, questions)
            else:
                send_bad_result_mes(chat_id)
                print('sending_bad_result_mes')


            print(' questions after reply ', questions)
            log_in_file(' questions after reply ' + str(questions))


def main():
    offset = None
    while True:
        try:
            data = get_updates_json(url, offset)
            print('get_updates_json first while:', data)
            log_in_file(' get_updates_json first while: ' + str(data))
            print('LEN: ', len(data['result']))
            log_in_file(' LEN: ' + str(len(data['result'])))
            data1 = last_update(data)
            print('last_update first while:', data1)
            log_in_file(' last_update first while:' + str(data1))
            update_id = data1['update_id']
            break
        except:
            print('tried and failed get first update')
            log_in_file(' tried and failed get first update')
    print('update_id 1: ', update_id)
    log_in_file(' update_id 1: ' + str(update_id))
    count = 1
    while True:
        print('while True: ', count)
        log_in_file(' while True: ' + str(count))
        count += 1
        try:
            update_for_offset, update_dict = get_all_info(offset)
        except:
            print('continue')
            log_in_file(' continue')
            continue
        print('update_id: ', update_id, 'last_update_var: ', update_for_offset)
        log_in_file(' update_id: ' + str(update_id) + ' last_update_var: ' + str(update_for_offset))
        if update_id == update_for_offset or update_id < update_for_offset:
            print('update_for_offset:', update_for_offset)
            log_in_file(' update_for_offset:' + str(update_for_offset))
            for key, item in update_dict.items():
                answer(item[0], item[1], item[2])
            offset = update_for_offset + 1
            update_id = offset
            print('update+1 ', update_id)
            log_in_file(' update+1 ' + str(update_id))
            sleep(1)
        print('user_info', user_info)
        print('LEN USER_INFO', len(user_info))
        log_in_file(' user_info' + str(user_info))
        log_in_file(' LEN USER_INFO' + str(len(user_info)))


if __name__ == '__main__':
    main()

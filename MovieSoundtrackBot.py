import os
import pytube
import telebot
from telebot import types
from pytube import YouTube, Search
from imdbpie import Imdb

bot = telebot.TeleBot("5471405122:AAGyoP6IdfDAoTwouPdjYyegfXIvjhxL-n8")
imdb = Imdb()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Enter the title of the movie")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    global raw_name
    raw_name = message.text.lower()
    mid_name = raw_name.split(' ')
    name = "".join(mid_name)
    print(name)
    search = imdb.search_for_title(name)
    list_id = []
    button_list = []
    n = 1

    for movie in search:
        print(n, movie['title'], movie['year'])
        try:
            button = types.InlineKeyboardButton(movie['title'] + movie['year'], callback_data=movie['imdb_id'])
        except:
            button = types.InlineKeyboardButton(movie['title'], callback_data=movie['imdb_id'])
        button_list.append(button)
        keyboard = types.InlineKeyboardMarkup()
        for button in button_list:
            keyboard.add(button)
        list_id.append(movie['imdb_id'])
        n += 1
        global chatid
        chatid = message.chat.id
    bot.send_message(chat_id=message.chat.id, text='*****     which movie would you like to choose?     *****',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if len(call.data) > 1:
        soundtrack_data = {}
        tracks_button = []
        chosen_movie = imdb.get_title_soundtracks(call.data)
        print(chosen_movie)
        if 'soundtracks' in chosen_movie:
            for tracks in chosen_movie['soundtracks']:
                for artist in tracks['relatedNames']:
                    if 'relateNames' in tracks:
                        soundtrack_data[tracks['name']] = artist['name']
                    else:
                        soundtrack_data[tracks['name']] = raw_name
        elif 'albums' in chosen_movie:
            soundtrack_data[chosen_movie['albums'][0]['albumTitle']] = raw_name
        else:
            bot.send_message(chat_id=chatid, text="Sorry! Your movie's soundtracks do not exist in IMDB")
        print(soundtrack_data)

        for key, val in soundtrack_data.items():
            ind = str(list(soundtrack_data).index(key))
            print(ind)
            butto = types.InlineKeyboardButton(key + soundtrack_data[key], callback_data=ind)
            tracks_button.append(butto)
        keyboard_music = types.InlineKeyboardMarkup()
        for button in tracks_button:
            keyboard_music.add(button)
        print(chatid)
        bot.send_message(chat_id=chatid, text='*****     Which soundtrack would you like to choose?     *****',
                         reply_markup=keyboard_music)
        print(call.data)

    else:
        print(list(soundtrack_data)[int(call.data)] + list(soundtrack_data.values())[int(call.data)])
        try:
            s = Search(list(soundtrack_data)[int(call.data)] + list(soundtrack_data.values())[int(call.data)])
            yt = YouTube(s.results[0].watch_url)
            video = yt.streams.filter(only_audio=True).order_by("abr").desc()[0].download()
            base, ext = os.path.splitext(video)
            new_file = base + '.mp3'
            os.rename(video, new_file)
            bot.send_audio(chat_id=chatid, audio=open(f'{new_file}', 'rb'))
        except:
            bot.send_message(chat_id=chatid, text="Sorry! Not Found")


bot.infinity_polling()
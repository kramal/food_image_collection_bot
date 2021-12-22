# -*- coding: utf-8 -*-
from os import listdir
from random import choice

from telebot import TeleBot
from telebot.types import InlineKeyboardButton
from telebot.types import InlineKeyboardMarkup
from telebot.types import ReplyKeyboardMarkup
from telebot.types import ReplyKeyboardRemove

from pymysql import cursors, connect
import urllib.request
import pathlib
import os
import random
from datetime import date

# mysql database connection
MYSQL_DB_NAME = 'food_image_collection'
MYSQL_USER = 'food_image_collection'
MYSQL_PASS = 'p@ssw0rd'

# 'food_image_collection'@'localhost' IDENTIFIED BY 'p@ssw0rd';
# telegram bot private token
TELEGRAM_TOKEN = '2119928735:AAF1tIblJDwrMamrodkTSJGa-sAPw2Udo5w'

# vote max
VOTE_MAX = 10

global BOT
BOT = TeleBot ( TELEGRAM_TOKEN, parse_mode='HTML' )

from getText import getText as TEXT


def get_user_language_code(user_id) :
    db_conn = get_connection ()

    with db_conn :
        with db_conn.cursor () as cursor :
            sql_select = "SELECT code FROM t_users u LEFT JOIN t_languages l ON u.language_id = l.id WHERE telegram_id = %s"
            cursor.execute ( sql_select, (int ( user_id )) )
            result = cursor.fetchone ()
        db_conn.commit ()

    if result :
        return result['code']

    return 'en'


def get_connection() :
    db_conn = connect ( host='localhost',
                        user=MYSQL_USER,
                        password=MYSQL_PASS,
                        database=MYSQL_DB_NAME,
                        cursorclass=cursors.DictCursor )

    return db_conn


def create_user(tid, consent) :
    db_conn = get_connection ()

    with db_conn :
        with db_conn.cursor () as cursor :
            sql_select = "INSERT INTO t_users(telegram_id, consent)  VALUES( %s, %s )"
            cursor.execute ( sql_select, (int ( tid ), int ( consent )) )
        db_conn.commit ()


def is_user_exists(tid) :
    db_conn = get_connection ()

    with db_conn :
        with db_conn.cursor () as cursor :
            sql_select = "SELECT telegram_id FROM t_users WHERE telegram_id = %s"
            cursor.execute ( sql_select, (int ( tid )) )
            result = cursor.fetchone ()
        db_conn.commit ()

    if result :
        return True

    return False


def is_user_filled_form(tid) :
    db_conn = get_connection ()

    with db_conn :
        with db_conn.cursor () as cursor :
            sql_select = "SELECT consent, age, gender, occupation, region, ethnicy, "\
            + " height, weight, city, is_smoking, language_id, schedule, iweight, waist, "\
            + " breakfast, lunch, dinner, activity, sleep, sport, dietbefore, dietchanged "\
            + "FROM t_users WHERE telegram_id = %s"
            cursor.execute ( sql_select, (int ( tid )) )
            result = cursor.fetchone ()
        db_conn.commit ()

    if result is None :
        return False
    
    are_fields_filled = True
    for value in result:
        are_fields_filled = are_fields_filled and (value is not None)

    if are_fields_filled:
        return True

    return False


def save_user_region(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    region_id = message.text

    if region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_south' ) :
        region_id = 1
    elif region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_north' ) :
        region_id = 2
    elif region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_west' ) :
        region_id = 3
    elif region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_east' ) :
        region_id = 4
    elif region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_center' ) :
        region_id = 5
    elif region_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_other' ) :
        region_id = 6
    else :
        region_id = 6

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET region = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (region_id, user_id) )
        db_conn.commit ()

    require_city_action ( message )


def save_user_city(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    city = message.text

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET city = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (city, user_id) )
        db_conn.commit ()

    require_height_action( message )


def save_user_gender(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    gender_id = message.text

    if gender_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender_man' ) :
        gender_id = 1
    elif gender_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender_female' ) :
        gender_id = 2
    else :
        gender_id = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET gender = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (gender_id, user_id) )
        db_conn.commit ()

    require_occ_action ( message )


def save_user_occ(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    occ_id = message.text

    if occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_student' ) :
        occ_id = 1
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_managers' ) :
        occ_id = 2
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_professional' ) :
        occ_id = 3
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_tech' ) :
        occ_id = 4
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_clerical' ) :
        occ_id = 5
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_service' ) :
        occ_id = 6
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_skilled' ) :
        occ_id = 7
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_craft' ) :
        occ_id = 8
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_operator' ) :
        occ_id = 9
    elif occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_unemployed' ) :
        occ_id = 10
    else :
        occ_id = 11

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET occupation = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (occ_id, user_id) )
        db_conn.commit ()
        
    require_schedule_action( message )


def save_user_schedule(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    work_id = message.text

    if work_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_9_5' ) :
        work_id = 1
    elif work_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_flexible' ) :
        work_id = 2
    elif work_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_hight' ) :
        work_id = 3
    else :
        work_id = 4

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET schedule = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (work_id, user_id) )
        db_conn.commit ()
        
    require_ethnicy_action( message )


def save_user_height(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    height = message.text
    
    if not height.isnumeric():
        height = -1

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET height = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (height, user_id) )
        db_conn.commit ()

    require_weight_action ( message )


def save_user_weight(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    weight = message.text

    if not weight.isnumeric():
        weight = -1

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET weight = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (weight, user_id) )
        db_conn.commit ()

    require_waist_action( message )
    

def save_user_iweight(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    iweight = message.text

    if not iweight.isnumeric():
        iweight = -1

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET iweight = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (iweight, user_id) )
        db_conn.commit ()

    require_breakfast_action( message )
    
    
def save_user_waist(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    waist = message.text

    if not waist.isnumeric():
        waist = -1

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET waist = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (waist, user_id) )
        db_conn.commit ()
        
    require_smoking_action( message )


def save_user_ethnicy(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    ethnicy = message.text
    
    if ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_1' ) :
        ethnicy = 1
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_2' ) :
        ethnicy = 2
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_3' ) :
        ethnicy = 3
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_4' ) :
        ethnicy = 4
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_5' ) :
        ethnicy = 5
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_6' ) :
        ethnicy = 6
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_7' ) :
        ethnicy = 7
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_8' ) :
        ethnicy = 8
    elif ethnicy == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_9' ) :
        ethnicy = 9
    else :
        ethnicy = 10

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET ethnicy = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (ethnicy, user_id) )
        db_conn.commit ()
        
    if ethnicy != 10:
        require_region_action( message )
    else:
        require_ethnicyother_action( message )


def save_user_ethnicyother(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    nationality = message.text

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET ethnicy_other = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (nationality, user_id) )
        db_conn.commit ()

    require_region_action ( message )

def save_user_breakfast(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    breakfast = message.text

    if breakfast == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_1' ) :
        breakfast = 1
    elif breakfast == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_2' ) :
        breakfast = 2
    elif breakfast == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_3' ) :
        breakfast = 3
    else :
        breakfast = 4

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET breakfast = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (breakfast, user_id) )
        db_conn.commit ()
   
    require_lunch_action( message )
    

def save_user_lunch(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    lunch = message.text

    if lunch == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_1' ) :
        lunch = 1
    elif lunch == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_2' ) :
        lunch = 2
    elif lunch == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_3' ) :
        lunch = 3
    else :
        lunch = 4

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET lunch = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (lunch, user_id) )
        db_conn.commit ()
   
    require_dinner_action( message )
    

def save_user_dinner(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    dinner = message.text

    if dinner == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_1' ) :
        dinner = 1
    elif dinner == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_2' ) :
        dinner = 2
    elif dinner == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_3' ) :
        dinner = 3
    else :
        dinner = 4

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET dinner = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (dinner, user_id) )
        db_conn.commit ()
   
    require_activity_action( message )


def save_user_activity(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    activity = message.text

    if activity == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity_low' ) :
        activity = 1
    elif activity == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity_normal' ) :
        activity = 2
    else :
        activity = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET activity = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (activity, user_id) )
        db_conn.commit ()
   
    require_sleeping_action(message)


def save_user_sleeping(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    sleep = message.text

    if sleep == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_min' ) :
        sleep = 1
    elif sleep == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_normal' ) :
        sleep = 2
    elif sleep == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_long' ) :
        sleep = 2
    else :
        sleep = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET sleep = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (sleep, user_id) )
        db_conn.commit ()
   
    require_sport_action(message)


def save_user_sport(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    sport = message.text

    if sport == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout_high' ) :
        sport = 1
    elif sport == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout_low' ) :
        sport = 2
    else :
        sport = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET sport = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (sport, user_id) )
        db_conn.commit ()
   
    require_dietbefore_action(message)
    
    
def save_user_dietbefore(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    dietbefore = message.text

    if dietbefore == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ) :
        dietbefore = 1
    elif dietbefore == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ) :
        dietbefore = 2
    else :
        dietbefore = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET dietbefore = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (dietbefore, user_id) )
        db_conn.commit ()
   
    require_dietchanged_action(message)
    

def save_user_dietchanged(message) : 
    chat_id = message.chat.id
    user_id = message.from_user.id
    dietchanged = message.text

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET dietchanged = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (dietchanged, user_id) )
        db_conn.commit ()

    require_imageinfo_action( message )


def save_user_smoking(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    smoking = message.text

    if smoking == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ) :
        smoking = 1
    elif smoking == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ) :
        smoking = 2
    else :
        smoking = 3

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET is_smoking = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (smoking, user_id) )
        db_conn.commit ()
   
    require_iweight_action( message )


def save_user_language(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = message.text
    language_id = 1

    markup = ReplyKeyboardRemove ( selective=False )
    if language == 'Қазақша' :
        language_id = 0
    if language == 'English' :
        language_id = 1
    if language == 'Русский' :
        language_id = 2

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET language_id = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (language_id, user_id) )
        db_conn.commit ()
    
    require_consent_action ( message )


def save_user_age(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    age = message.text

    if not str ( age ).isnumeric () :
        age = -1

    markup = ReplyKeyboardRemove ( selective=False )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET age = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (age, user_id) )
        db_conn.commit ()
    
    require_occ_action( message )


def save_user_consent(message) :
    """
    saves user consent for experiment
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    consent = message.text

    markup = ReplyKeyboardRemove ( selective=False )

    if consent == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ) :
        consent = 1
    else :
        consent = 0

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET consent = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (consent, user_id) )
        db_conn.commit ()

    try:
        if consent == 0 :
            BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( user_id ), 'thanks_return' ) )
        else :
            require_age_action ( message )
    except:
        BOT.send_message ( chat_id, str('jhjghgjg') )


def save_user_consentweek(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    consent = message.text

    if consent == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ) :
        consent = 1
    else :
        consent = 0

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET one_week_consent = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (consent, user_id) )
        db_conn.commit ()

    if consent == 0 :
        BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks_return' ) )
    else :
        require_save_action( message )


def save_user_image(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    try :
        fileID = message.photo [ -1 ].file_id
        file = BOT.get_file ( fileID )
        file_path = file.file_path

        BOT.send_message ( chat_id, file_path )

        url = 'https://api.telegram.org/file/bot' + TELEGRAM_TOKEN + '/' + file_path
        file_name, filename_suffix = os.path.splitext ( file_path )

        n = random.randint ( 1000000, 9999999 )

        isDataDirExist = os.path.exists (  os.path.join ( pathlib.Path ().resolve (), 'data' ) )
        if not isDataDirExist :
            os.makedirs ( os.path.join ( pathlib.Path ().resolve (), 'data' ) )

        isUserDirExist = os.path.exists ( os.path.join (  os.path.join ( pathlib.Path ().resolve (), 'data' ), str(user_id) ) )
        if not isUserDirExist :
            os.makedirs ( os.path.join (  os.path.join ( pathlib.Path ().resolve (), 'data' ), str(user_id) ) )

        to_file_body = 'data/' + str(user_id) + '/' + str ( user_id ) + '_' + str ( date.today() ) + '_' + str(n) + '.' + filename_suffix
        to_file = os.path.join ( pathlib.Path ().resolve (), to_file_body )

        urllib.request.urlretrieve ( url, to_file )

        require_save_action ( message )
    except Exception as e :  # work on python 3.x
        # BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'load_again' ) )
        # BOT.send_message ( chat_id, str ( e ) )

        require_language_action ( message )


def require_language_action(message) :
    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( 'Қазақша', callback_data='1' ),
        InlineKeyboardButton ( 'English', callback_data='2' ),
        InlineKeyboardButton ( 'Русский', callback_data='3' )
    ]
    markup.row ( markup_items [ 0 ] )
    markup.row ( markup_items [ 1 ], markup_items [ 2 ] )

    markup_title = 'Тіл | Language | Язык'
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_language ( msg ) )


def require_imageinfo_action(message) :
    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'comment_to_image' )
    BOT.send_message ( message.chat.id, markup_title )
    
    # send examplar image
    img_ex = open('example.jpeg', 'rb')
    BOT.send_photo(message.chat.id, img_ex)
    
    require_save_action(message)


def require_consent_action(message) :
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_language = get_user_language_code ( user_id )

    hello_text = TEXT.get_text ( user_language, 'hello' )
    brief_info = TEXT.get_text ( user_language, 'brief_info' )

    text = f"{hello_text} {user_name}! \n{brief_info} "
    BOT.reply_to ( message, text )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ),
                               callback_data='2' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )

    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'consent' )
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_consent ( msg ) )


def require_age_action(message) :
    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'age' )
    msg = BOT.send_message ( message.chat.id, markup_title )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_age ( msg ) )


def require_region_action(message) :
    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_center' ),
                               callback_data='5' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_south' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_east' ),
                               callback_data='4' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_west' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_north' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_other' ),
                               callback_data='6' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ], markup_items [ 3 ], markup_items [ 4 ] )

    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_kz' )
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_region ( msg ) )


def require_city_action(message) :
    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region_outside' )
    msg = BOT.send_message ( message.chat.id, markup_title )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_city ( msg ) )


def require_gender_action(message) :
    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender_man' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender_female' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender_other' ),
                               callback_data='3' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ], markup_items [ 2 ] )

    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'gender' )
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_gender ( msg ) )


def require_occ_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occupation' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_other' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_student' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_managers' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_professional' ),
                               callback_data='4' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_tech' ),
                               callback_data='5' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_clerical' ),
                               callback_data='6' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_service' ),
                               callback_data='7' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_skilled' ),
                               callback_data='8' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_craft' ),
                               callback_data='9' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_operator' ),
                               callback_data='10' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_unemployed' ),
                               callback_data='11' )
    ]
    
    for i in range(0, len(markup_items)):
        markup.row( markup_items[i] )
    
    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_occ ( msg ) )
    
    
def require_schedule_action(message) : 
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'schedule' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )

    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_9_5' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_flexible' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_hight' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'work_no' ),
                               callback_data='4' )
    ]
    markup.row ( markup_items [ 0 ],
                 markup_items [ 1 ] )

    markup.row ( markup_items [ 2 ],
                 markup_items [ 3 ] )
    
    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_schedule ( msg ) )


def require_height_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'height' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_height ( msg ) )


def require_weight_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'weight' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_weight ( msg ) )


def require_iweight_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ideal_weight' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_iweight ( msg ) )


def require_waist_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'waist_circumference' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_waist ( msg ) )


def require_ethnicy_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_1' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_2' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_3' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_4' ),
                               callback_data='4' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_5' ),
                               callback_data='5' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_6' ),
                               callback_data='6' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_7' ),
                               callback_data='7' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_8' ),
                               callback_data='8' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_9' ),
                               callback_data='9' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_10' ),
                               callback_data='10' ),
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ], markup_items [ 2 ] )
    markup.row ( markup_items [ 3 ], markup_items [ 4 ], markup_items [ 5 ] )
    markup.row ( markup_items [ 6 ], markup_items [ 7 ], markup_items [ 8 ] )
    markup.row ( markup_items [ 9 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_ethnicy ( msg ) )


def require_ethnicyother_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy_other' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_ethnicyother ( msg ) )


def require_smoking_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'is_smoking' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sometimes' ),
                               callback_data='3' ),
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ], markup_items [ 2 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_smoking ( msg ) )


def require_breakfast_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_1' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_2' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_3' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'breakfast_4' ),
                               callback_data='4' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ], markup_items [ 3 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_breakfast ( msg ) )
    
    
def require_lunch_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_1' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_2' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_3' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'lunch_4' ),
                               callback_data='4' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ], markup_items [ 3 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_lunch ( msg ) )


def require_dinner_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_1' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_2' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_3' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'dinner_4' ),
                               callback_data='4' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ], markup_items [ 3 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_dinner ( msg ) )


def require_activity_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity_low' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity_normal' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'activity_mixed' ),
                               callback_data='3' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_activity ( msg ) )
    

def require_sleeping_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_min' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_normal' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_long' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'sleep_2long' ),
                               callback_data='4' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ], markup_items [ 3 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_sleeping ( msg ) )


def require_sport_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout_high' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout_low' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'workout_very_low' ),
                               callback_data='3' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_sport ( msg ) )
    

def require_dietbefore_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'diet' )

    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'a_bit' ),
                               callback_data='3' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )
    markup.row ( markup_items [ 2 ] )

    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_dietbefore ( msg ) )
    

def require_dietchanged_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'diet_change' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_dietchanged ( msg ) )


def require_save_action(message) :
    msg = BOT.send_message ( message.chat.id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'load_image_please' ) )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_image ( msg ) )


@BOT.message_handler ( content_types=[ 'text', 'photo' ], commands=[ 'start' ] )
def handle_command(message) :
    is_bot = message.from_user.is_bot

    if is_bot :
        BOT.reply_to ( message, "ONLY_HUAMNS_ALLOWED" )
    else :
        user_id = message.from_user.id

        if user_id and not is_user_exists ( user_id ) :
            create_user ( user_id, 1 )
        
        require_language_action ( message )
        
        #  TO BE UNCOMMENTED
        # if is_user_filled_form( user_id ):
        #     require_save_action( message )
        # else:  
        #     require_language_action ( message )


BOT.polling ()

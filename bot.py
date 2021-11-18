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
MYSQL_USER = 'root'
MYSQL_PASS = ''

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
            sql_select = "SELECT age, region, consent, city, gender, one_week_consent FROM t_users WHERE telegram_id = %s"
            cursor.execute ( sql_select, (int ( tid )) )
            result = cursor.fetchone ()
        db_conn.commit ()

    if result is None :
        return False

    if result [ 'age' ] and result [ 'region' ]  and result [ 'city' ] and result [ 'gender' ] and result [ 'one_week_consent' ]:
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
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

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

    markup = ReplyKeyboardRemove ( selective=False )
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET city = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (city, user_id) )
        db_conn.commit ()

    require_gender_action ( message )


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
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

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

    if occ_id == TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_health' ) :
        occ_id = 1
    else :
        occ_id = 3

    markup = ReplyKeyboardRemove ( selective=False )
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET occupation = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (occ_id, user_id) )
        db_conn.commit ()

    require_height_action ( message )


def save_user_height(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    height = message.text

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

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET weight = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (weight, user_id) )
        db_conn.commit ()

    require_ethnicy_action ( message )


def save_user_ethnicy(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    ethnicy = message.text

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET ethnicy = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (ethnicy, user_id) )
        db_conn.commit ()

    require_smoking_action ( message )


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

    require_consentweek_action(message)


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

    if is_user_filled_form ( message.from_user.id ) :
        require_save_action ( message )
    else :
        require_consent_action ( message )


def save_user_age(message) :
    chat_id = message.chat.id
    user_id = message.from_user.id
    age = message.text

    if not str ( age ).isnumeric () :
        age = -1

    markup = ReplyKeyboardRemove ( selective=False )
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

    db_conn = get_connection ()
    with db_conn :
        with db_conn.cursor () as cursor :
            sql_insert = "UPDATE t_users SET age = %s WHERE telegram_id = %s"
            cursor.execute ( sql_insert, (age, user_id) )
        db_conn.commit ()

    require_region_action ( message )


def save_user_consent(message) :
    """
    saves user consent for experiment
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    consent = message.text

    markup = ReplyKeyboardRemove ( selective=False )
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

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

    markup = ReplyKeyboardRemove ( selective=False )
    BOT.send_message ( chat_id, TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'thanks' ),
                       reply_markup=markup )

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
        BOT.send_message ( chat_id, str ( e ) )

        require_save_action ( message )


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


def require_consentweek_action(message) :
    markup = ReplyKeyboardMarkup ( one_time_keyboard=True )
    markup_items = [
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'yes' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'no' ),
                               callback_data='2' )
    ]
    markup.row ( markup_items [ 0 ], markup_items [ 1 ] )

    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'consent_week' )
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_consentweek ( msg ) )


def require_consent_action(message) :
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_language = get_user_language_code ( user_id )

    hello_text = TEXT.get_text ( user_language, 'hello' )
    greeting_info = TEXT.get_text ( user_language, 'greeting' )
    brief_info = TEXT.get_text ( user_language, 'brief_info' )

    text = f"{hello_text} {user_name}! {greeting_info}\n{brief_info} "
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

    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'region' )
    msg = BOT.send_message ( message.chat.id, markup_title, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_region ( msg ) )


def require_city_action(message) :
    markup_title = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'city' )
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
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_science' ),
                               callback_data='1' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_health' ),
                               callback_data='2' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_teaching' ),
                               callback_data='3' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_business' ),
                               callback_data='4' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_it' ),
                               callback_data='5' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'oc_legal' ),
                               callback_data='6' ),
        InlineKeyboardButton ( TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'occ_other' ),
                               callback_data='7' )
    ]
    markup.row ( markup_items [ 0 ],
                 markup_items [ 1 ],
                 markup_items [ 2 ] )

    markup.row ( markup_items [ 3 ],
                 markup_items [ 4 ],
                 markup_items [ 5 ],
                 markup_items [ 6 ] )
    msg = BOT.send_message ( message.chat.id, text, reply_markup=markup )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_occ ( msg ) )


def require_height_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'height' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_height ( msg ) )


def require_weight_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'weight' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_weight ( msg ) )


def require_ethnicy_action(message) :
    text = TEXT.get_text ( get_user_language_code ( message.from_user.id ), 'ethnicy' )
    msg = BOT.send_message ( message.chat.id, text )
    BOT.register_next_step_handler ( msg, lambda msg : save_user_ethnicy ( msg ) )


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


BOT.polling ()

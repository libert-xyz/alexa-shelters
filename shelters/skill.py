import logging
import os
from flask import Flask, render_template
from flask_ask import Ask, request, session, question, statement, audio
import requests
import random
import json


app = Flask(__name__)
ask = Ask(app, "/")

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
logging.getLogger('flask_ask').setLevel(logging.DEBUG)


logo = 'https://s3.amazonaws.com/simpletime-skill/visual/my_tracker_108.png'
logo = 'https://s3.amazonaws.com/voicesummit-alexa-skill/visuals/voice_summit_logo_1026_600.png'

dc_opendata_url = 'https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Public_Service_WebMercator/MapServer/25/query?where=1%3D1&outFields=OBJECTID,OWNER_RENTER,FACILITY_NAME,ADDRESS,CITY,STATE,TYPE,NUMBER_OF_BEDS,ON_SITE_MEDICAL_CLINIC,HOW_TO_ACCESS,AGES_SERVED&returnGeometry=false&outSR=4326&f=json'

@ask.launch
def launch():

    welcome_q = render_template('welcome')


    url_request = requests.get(dc_opendata_url).text
    data_json = json.loads(url_request)

    shelter_count = len(data_json['features'])

    #int
    session.attributes['number_of_shelter'] = shelter_count
    #dict
    session.attributes['shelters'] = data_json

    #List of numbers
    shelter_id_list = range(0,shelter_count)
    session.attributes['shelter_id_list'] = shelter_id_list

    session.attributes['shelter_id'] = session.attributes['shelter_id_list'].pop(random.choice(shelter_id_list))

    welcome_q = render_template('welcome',shelters_n=shelter_count)

    return question(welcome_q) \
        .reprompt(welcome_q) \
        .standard_card(title='Shelters DC',
        text=welcome_q,
        large_image_url=logo)


@ask.intent('AMAZON.YesIntent')
def yes_fn():
    
    if session.attributes['number_of_shelter'] != 0:
        sh = session.attributes['shelters']['features'][(session.attributes['shelter_id'])]

        sh_name = sh['attributes']['FACILITY_NAME']
        sh_address = sh['attributes']['ADDRESS']
        sh_ages = sh['attributes']['AGES_SERVED']
        sh_owner = sh['attributes']['OWNER_RENTER']
        sh_access = sh['attributes']['HOW_TO_ACCESS']


        shelter_info = render_template('shelter_info',sh_name=sh_name,sh_address=sh_address,sh_ages=sh_ages, \
                        sh_owner=sh_owner,sh_access=sh_access)


        #Update Global Variables
        session.attributes['shelter_id'] = session.attributes['shelter_id_list'].pop(random.choice(session.attributes['shelter_id_list']))
        session.attributes['number_of_shelter'] = session.attributes['number_of_shelter'] - 1


        return question(shelter_info) \
                        .standard_card(title='Shelters DC',
                        text=shelter_info,
                        large_image_url=logo)

    else:
        return statement('No more shelters')

@ask.intent('AMAZON.NoIntent')
def stop():

    return statement('ok bye') \
        .standard_card(title='Shelters DC',
        text='ok bye',
        large_image_url=logo)


@ask.intent('AMAZON.StopIntent')
def stop():

    return statement('ok bye') \
        .standard_card(title='Shelters DC',
        text='ok bye',
        large_image_url=logo)

@ask.intent('AMAZON.CancelIntent')
def cancel_fnc():

    return statement('ok bye') \
        .standard_card(title='Shelters DC',
        text='ok bye',
        large_image_url=logo)

@ask.intent('AMAZON.FallbackIntent')
def fallback():


    return statement('')


# @ask.intent('AMAZON.HelpIntent')
#
# def help_fn():
#
#     session.attributes['error'] = 1
#
#     help_tmp = render_template('help')
#     help_tmp_tts = render_template('help_tts')
#
#     return question(help_tmp) \
#             .standard_card(title='Voice Summit Guide',
#             text=help_tmp_tts,
#             large_image_url=logo)




if __name__ == '__main__':
    app.run(debug=True)

#!/usr/bin/env python3
"""Example bot that returns a synchronous response."""

from flask import Flask, request, json, jsonify, Response
import requests
from os import listdir
from PIL import Image as PImage
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from flask import send_file
import base64
import webbrowser
app = Flask(__name__)
INTERACTIVE_TEXT_BUTTON_ACTION = "doTextButtonAction"
INTERACTIVE_IMAGE_BUTTON_ACTION = "doImageButtonAction"
INTERACTIVE_BUTTON_PARAMETER_KEY = "param_key"


@app.route('/hangoutAPI', methods=['POST'])
def on_event():
    """Handles an event from Hangouts Chat."""
    event = request.get_json()
    if event['type'] == 'ADDED_TO_SPACE' and not event['space']['singleUserBotDm']:
        text = 'Thanks for adding me to "%s"!' % (
            event['space']['displayName'] if event['space']['displayName'] else 'this chat')
    elif event['type'] == 'MESSAGE':
        text = 'You said: `%s`' % event['message']['text']
        response = get_FAQ_Response(event['message']['text'])
        text = response
        print(text)
    elif event['type'] == 'CARD_CLICKED':
        #Handles an onclick event from Hangouts Chat."
        print("event", event)
        type = event['action']['actionMethodName']
        formid= event['action']['parameters'][0]['key']
        print(formid)
        text = multiple_types(type, event)
    else:
        return
    return text


def get_FAQ_Response(msg):
    """ Gets the response of a single message hitting the below URL and request body"""
    try:
        URL = "https://bmp-api.demo.botzer.io/bmpapi/getNLPResponse"
        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            "botId": "2c9faf6072a3022c0172a32c80080061",
            "type": "FAQ",
            "textInputUtterance": msg,
            "sessionId": "ABCDEF",
            "channel": "Hangouts"
        }
        print(msg)
        json_string = json.dumps(data)
        print(json_string)
        print("before calling")
        # sending get request and saving the response as response object
        response = requests.request("POST", URL, headers=headers, data=json_string)
        print("calling api")
        nlpresponse = response.json()
        print(nlpresponse)
        text = nlpresponse['elements'][0]['data']['text']
        print(text)
        # buttons = gets the name of the buttons
        #buttonkey = gets teh actiontype of the button
        #formid = gets the form id of the button
        buttons = []
        buttonkey = []
        formid =[]
        for i in range(1, len(nlpresponse['elements'])):
            if "name" in nlpresponse['elements'][i]['data']:
                buttons.append(nlpresponse['elements'][i]['data']['name'])
                formid.append(nlpresponse['elements'][i]['id'])
            if "actionType" in nlpresponse['elements'][i]:
                buttonkey.append(nlpresponse['elements'][i]['actionType'])
            if "actionType" not in nlpresponse['elements'][i]:
                    buttonkey.append(nlpresponse['elements'][i]['target'])
        print(buttons)
        print(buttonkey)
        print(formid)
        #displays the list of buttons
        result = display_buttons(buttons, buttonkey,formid ,text)
        print(result)
        return result

    except Exception as e:
        print("Error", e)
        return "Failure"


def openLink(url):
    """Opens the URL"""
    webbrowser.open(url)

def multiple_types(type, event):
    """Checks multiple actiontype and perform actions accordingly"""
    if type == "FAQ List":
        formid = event['action']['parameters'][0]['key']
        data = call_API("FAQ List", "FAQ List",formid)
        result = create_buttons(data, "FAQ List")
    elif type == "Form":
        msg = event['action']['parameters'][0]['value']
        print(msg)
        formid = event['action']['parameters'][0]['key']
        data = call_API(type,msg,formid)
        print("data",data)
        result= create_buttons(data,msg)
        print(result)
    elif type == "Task":
        msg = event['action']['parameters'][0]['value']
        print(msg)
        formid = event['action']['parameters'][0]['key']
        data = call_API(type, msg, formid)
        print("data", data)
        result = create_buttons(data, msg)
        print(result)
    elif event['action']['parameters'][0]['value']=="Facebook":
        openLink(event['action']['actionMethodName'])
        return "Done"
    else:
        print(event['action']['parameters'][0]['value'])
        result = get_FAQ_Response(event['action']['parameters'][0]['value'])
        print("result mult", result)
    return result


def call_API(type, msg,formid):
    """Handles multiple API calls for different action types"""
    URL = "https://bmp-api.demo.botzer.io/bmpapi/getNLPResponse"
    headers = {
        'Content-Type': 'application/json'
    }
    if type == "FAQ List":
        data = {
            "botId": "2c9faf6072a3022c0172a32c80080061",
            "type": type,
            "textInputUtterance": msg,
            "sessionId": "ABCDEF",
            "channel": "Hangouts"
        }
    elif type == "Form":
        data = {
            "botId": "2c9faf6072a3022c0172a32c80080061",
            "type": type,
            "channel": "Hangouts",
            "textInputUtterance": msg,
            "sessionId": "asdasdas123123123",
            "data": {
                "id": formid
            }
        }
    elif type == "Task":
        data ={
            "botId": "2c9faf6072a3022c0172a32c80080061",
            "type": type,
            "channel": "Hangouts",
            "textInputUtterance": msg,
            "sessionId": "asdasdas123123123",
            "data": {
                "id": formid
            }
        }

    json_string = json.dumps(data)
    print(json_string)
    print("before calling")
    response = requests.request("POST", URL, headers=headers, data=json_string)
    print("calling api")
    nlpresponse = response.json()
    return nlpresponse


def create_buttons(nlpresponse, text):
    buttons = []
    buttonkey =[]
    formid =[]
    print("nlp",nlpresponse)
    text = nlpresponse['elements'][0]['data']['text']
    response = jsonify({"text": text})
    print("resp",response)
    for i in range(1, len(nlpresponse['elements'])):
       if "name" in nlpresponse['elements'][i]['data']:
           buttons.append(nlpresponse['elements'][i]['data']['name'])
           buttonkey.append(nlpresponse['elements'][i]['actionType'])
           formid.append(nlpresponse['elements'][i]['id'])
           response = display_buttons(buttons,buttonkey,formid,nlpresponse['elements'][0]['data']['text'])
    print("response",response)
    return response


def display_buttons(buttons, buttonkey,formid, text):
    response = dict()
    cards = list()
    widgets = list()
    widgets.append({
        'textParagraph': {
            'text': text
        }
    })
    length = len(buttons)
    if len(buttons)> 10:
        length=10
    for i in range(length):
        widgets.append({
            'buttons': [
                {
                    'textButton': {
                        'text': buttons[i],
                        'onClick': {
                            'action': {
                                'actionMethodName': buttonkey[i],
                                'parameters': [{
                                    #'id': formid[i],
                                    'key': formid[i],
                                    'value': buttons[i]
                                }]
                            }
                        }
                    }
                }
            ]
        })

    cards.append({'sections': [{'widgets': widgets}]})
    response['cards'] = cards
    #print(response)
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=8080, debug=True)

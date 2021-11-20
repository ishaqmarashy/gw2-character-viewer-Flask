from flask import Blueprint, render_template,request
import os
from dotenv import load_dotenv
import requests
load_dotenv()
views=Blueprint(__name__,"views")


#   DC96889C-7090-A445-9806-FBA2D0C8508BC622FA93-8506-41C2-9F56-8FCCC11F35DB 
#   215E7ED2-8B7D-2842-A5B0-B6F438ECB5998AB6FBC2-59BA-41CC-B54C-B96011624A9B 
#	551A0BBB-00CF-424F-BFD7-2492760F5933C6974D7A-9F7E-49E6-87EF-8FB7611863D4


apikey="215E7ED2-8B7D-2842-A5B0-B6F438ECB5998AB6FBC2-59BA-41CC-B54C-B96011624A9B"
responseList={}

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res
def  api(arg,apikey):
    #   My Own API Key you may use yours if you'd like
    url=f'https://api.guildwars2.com/v2/{arg}'
    print(url)
    if not (url+apikey) in responseList:
        response= requests.get(url,data={'access_token':apikey})
        if not ('https://api.guildwars2.com/v2/characters/' in url):
            responseList[url+apikey]=response.json()
        return response.json()
    
    return responseList[url+apikey]
    
def getItem(arg,apikey):
    if(arg):
        return api(f'items/{arg}',apikey)
def getItemStats(arg,apikey):
    if(arg):
        return api(f'itemstats/{arg}',apikey)
def listCharacters(arg,apikey):
    if(arg):
        return api(f'characters/{arg}',apikey)
    else:
        return api('characters/',apikey)
def listEquipment(arg,apikey):
    return listCharacters(f'{arg}',apikey)
def build(apikey):
    equipmentList={}
    context={}
    characterlist=listCharacters('',apikey)
    try:
        for character in characterlist:
            equipmentList[character]=listCharacters(character,apikey)['equipment']
        context['characters']=characterlist
        context['equipments']=equipmentList
        for items in context['equipments']:
            context['equipments'][items]=context['equipments'][items]
            for item in context['equipments'][items]:
                try :
                    upgradeList=[]
                    for upgrade in item['upgrades']:
                        upgradeList.append(getItem(upgrade,apikey))
                    item['upgrades']=upgradeList
                except: 
                    item['upgrades']={'Non'}
                try:
                    item['stats']
                except:
                    item['stats']={'attributes': ''}
                newItem=getItem(item['id'],apikey)
                item['id']=newItem['name']
                item['icon']=newItem['icon']
                try:
                    attributesList={}
                    for x in newItem['details']['infix_upgrade']['attributes']:
                        attributesList[x["attribute"]]=x["modifier"]
                    item['stats']={'attributes':attributesList}
                except:
                    ""
    except:
        return ""
    return context


@views.route("/")
def home():
    return render_template('index.html')

@views.route('/index', methods = ['GET','POST'])
def index():
    if(not request.form.get("api_key")):
        data=build(apikey)
        return render_template("chars.html", characters=(data['characters']),equipments=(data['equipments']))
    elif(len(request.form.get("api_key"))>0):
        return key(request.form.get("api_key"))
    return render_template("index.html",data='Invalid API-key')

@views.route('/<api_key>')
def key(api_key):
    data=build(api_key)
    if (data ==''):
        return render_template("index.html",data='Invalid API-key')
    return render_template("chars.html", characters=(data['characters']),equipments=(data['equipments']))   


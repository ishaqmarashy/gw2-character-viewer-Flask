from flask import Flask
from flask import Blueprint, render_template, request
from dotenv import dotenv_values
from pymongo import MongoClient
import requests

app = Flask(__name__)

ids={}
config = dotenv_values(".env")
client = MongoClient(config['CONNECTION_STRING'])
db = client['gw2_database']
collection = db['api_cache']
url='https://api.guildwars2.com/v2/'
apikey = config['ACCESS_TOKEN']
def insertIntoDB(data,collection):
    print('insert db')
    if data:
        collection.insert_many(data)
def checkDB(args,collection):
    print('checking db')
    if(args):
        query ={'arg':{ '$in': args }}
        existing_entry = list(collection.find(query))
        return existing_entry

def api(path, args, apikey, chunk_size=150):
    items=[]
    newRes=[]
    ids=set()

    if path !='characters':
        items=checkDB(args,collection)
        for item in items:
            ids.add(item['arg'])

    if not isinstance(args, list):
        args = [args]
    args=list(set(args).difference(ids))

    if len(args)==0:
        return items
    
    if args:
        i = 0
        while i < len(args):
            chunk = args[i:i + chunk_size]  # Get the next chunk of arguments
            newreq = f'{url}{path}?'
            if path == 'items' or (path == 'characters' and chunk[0] != ''):
                newreq += 'ids='
                newreq += f','.join(map(str, chunk))
            else:
                newreq += '='
            res = requests.get(newreq, params={'access_token': apikey}).json()
            res += items
            i += chunk_size
            if path=='characters' and args[0]=='':
                return [{'arg':args ,'data':res}]
            x=0
            while x<len(chunk):
                newRes += [{'arg':chunk[x] ,'data':res[x]}]
                x+=1
    
    if not path=='characters':
        insertIntoDB(newRes,collection)
    newRes+=items
    return newRes


def removePreCached(upgradesUrl):
    index=0
    while index<len(upgradesUrl):
            id=upgradesUrl[index]
            while id in ids and index<len(upgradesUrl):
                id=upgradesUrl[index]
                upgradesUrl.pop(index)
            index+=1
    return upgradesUrl
def populateChache(upgradesUrl):
  if upgradesUrl:
        for item in getItem(upgradesUrl,apikey):
            ids[item['data']['id']]=item
def getItem(args,apikey):
    if(args):
        return api('items',args,apikey)
def getItemStats(args,apikey):
    if(args):
        return api('itemstats',args,apikey)
def listCharacters(args,apikey):
    if(args):
        return api('characters',args,apikey)
    else:
        return api('characters',"",apikey)
def listEquipment(args,apikey):
    return listCharacters('',args,apikey)
def build(apikey):
    equipmentList={}
    context={}
    characterlist=[]
    equipmentlist={}
    upgradesUrl=[]
    characterlist=listCharacters('',apikey)[0]
    equipmentList=listCharacters(characterlist['data'],apikey)
    characterlist=[]
    for equipment in equipmentList:
        characterlist+=[equipment['data']['name']]
        equipmentlist[equipment['data']['name']]=equipment['data']['equipment']
    context['characters']=characterlist
    context['equipments']=equipmentlist
    for character in context['equipments']:
        for character_equipemnt in context['equipments'][character]:
            if 'upgrades' in character_equipemnt:
                upgradesUrl+=character_equipemnt['upgrades']
            if 'stats' in character_equipemnt:
                upgradesUrl+=[character_equipemnt['stats']['id']]
            if 'infusions' in character_equipemnt:
                upgradesUrl+=character_equipemnt['infusions']
            if 'id' in character_equipemnt:
                upgradesUrl+=[character_equipemnt['id']]
    upgradesUrl=removePreCached(upgradesUrl)
    populateChache(upgradesUrl)
    for character in context['equipments']:
        for items in context['equipments'][character]:
            if 'id' in items and items['id'] in ids:
                if ids[items['id']]['data']['icon']:
                    items['icon']=ids[items['id']]['data']['icon']
                if ids[items['id']]['data']['name']:
                    items['name']=ids[items['id']]['data']['name']
            if 'upgrades' in items:
                if  isinstance(items['upgrades'], list):
                    index=0
                    while index<len (items['upgrades']):
                        items['upgrades'][index]=ids[items['upgrades'][index]]['data']
                        index+=1
                else : items['upgrades']={['None']}
            if 'infix_upgrade' in ids[items['id']]['data']['details'] :
                attributes={}
                for attribute in ids[items['id']]['data']['details']['infix_upgrade']['attributes']:
                    attributes[attribute['attribute']]=attribute['modifier']
                items['stats']={'attributes': attributes}
            elif 'stat_choices' in ids[items['id']]['data']['details'] :
                items['stats']={'attributes': {'stat_choices':ids[items['id']]['data']['details']['stat_choices']}}
            else :
                items['stats']={'attributes': ids[items['id']]['data']['details']}
    return context

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/index', methods = ['GET','POST'])
def index():
    if(not request.form.get("api_key")):
        data=build(apikey)
        return render_template("chars.html", characters=(data['characters']),equipments=(data['equipments']))
    elif(len(request.form.get("api_key"))>0):
        return key(request.form.get("api_key"))
    return render_template("index.html",data='Invalid API-key')
@app.route('/<api_key>')
def key(api_key):
    data=build(api_key)
    if (data ==''):
        return render_template("index.html",data='Invalid API-key')
    return render_template("chars.html", characters=(data['characters']),equipments=(data['equipments']))   

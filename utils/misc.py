#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

from requests.compat import urlparse
import names,random,re,requests,os.path,json

from utils.scan import scan_file

def isAdmin(ctx):
	return ctx.author.guild_permissions.manage_channels

def Clean_Url(url):
	return 'https://%s'%urlparse(url.rstrip('/')).hostname

def Check_Ctfd(url):
    try:
        res = requests.get(url).text
        if('Powered by CTFd' in res):
            return True
        elif('We are checking your browser' in res):
            return True
        return False
    except Exception as ex:
        logger('Error during ctfd check : %s'%str(ex),"error",1,0)
        return False



def Create_Rdn_PPL():
	pseudo = names.get_last_name()+str(random.randint(1,99))
	charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;."
	user = {
		"pseudo":pseudo,
		"email":pseudo+'@tempr.email',
		"password":''.join(random.choice(charset) for i in range(12)),
		"team":pseudo+"_Team",
		"team_password":''.join(random.choice(charset) for i in range(12)),
	}
	return user

def Resolve_CTF(url):
	return ' '.join(urlparse(url).hostname.split('.')[:-1])

def Cleaner(name):
	return re.sub(r'[^\w]','', name).lower()


def Get_ChallMSG(chall,url,config):
	message	= '''
**Name**: %s
**Points**: %s
**Category**: %s
**Max Attempts**: %s
**Description**: 
```
%s
```'''%(chall['name'],
			chall['value'],
			chall['category'],
			chall['max_attempts'],
			chall['infos'])
	
	if(len(chall['files']) > 0):
		message += '**File(s)**:\n'
	for f in chall['files']:
		message += '- %s%s'%(url,f)
		scan = scan_file(url+f,config)
		if scan:
			message += '\n``Scan Url``: %s\n'%(scan)
	return message

def Init():
	if not os.path.exists('./config'):
		os.mkdir('config')
	if not os.path.exists('./config/example.json'):
		data = {
		  "team": "TeamExample",
		  "teampwd": "123IamRo0t!",
		  "users": [
		    [
		      "PlayerNumber1",
		      "playerNumber1@protonmail.com",
		      "Player1Password"
		    ],
		    [
		      "PlayerNumber2",
		      "playerNumber2@protonmail.com",
		      "Player2Password"
		    ],
		    [
		      "PlayerNumber3",
		      "playerNumber3@protonmail.com",
		      "Player3Password"
		    ]
		  ]
		}
		open('./config/example.json','w').write(json.dumps(data, indent=4))

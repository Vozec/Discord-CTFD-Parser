#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

from requests.compat import urlparse
import names,random,re

def isAdmin(ctx):
	if(ctx.author.guild_permissions.manage_channels):
		return True
	return False

def Clean_Url(url):
	url = url.rstrip('/')
	return 'https://%s'%urlparse(url).hostname


def Create_Rdn_PPL():
	pseudo = names.get_last_name()+str(random.randint(1,99))
	user = {
		"pseudo":pseudo,
		"email":pseudo+'@tempr.email',
		"password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
		"team":pseudo+"_Team",
		"team_password":''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12)),
	}
	return user

def Resolve_CTF(url):
	return ' '.join(urlparse(url).hostname.split('.')[:-1])

def Cleaner(name):
	return re.sub(r'[^\w]','', name).lower()


def Get_ChallMSG(chall,url):
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
		message += '**File(s)**:'
	for f in chall['files']:
		message += '- %s%s'%(url,f)
	return message
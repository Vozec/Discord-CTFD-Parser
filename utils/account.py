#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022


import requests,re,json

from utils.logger import logger
from utils.misc   import Create_Rdn_PPL

def isRecaptched(url):
	resp = requests.get(url).text
	if('https://www.google.com/recaptcha/api.js' in resp):
		return True
	return False

def Get_Nonce(url,session):
	res = session.get('%s/login'%url)
	match = re.search('name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"', res.text)
	if(match):
		return match.group(1)
	return ""

async def Register_Random(ctx,url):
	user = Create_Rdn_PPL()
	session = requests.session()
	if(Register_Account(session,user,url)):
		Create_Team(session,user,url)
		username,passw = user['pseudo'],user['password']
		logger('Account Created: %s | %s'%(username,passw),'log',0,1)
		return user
	return {'pseudo':'','password':''}

def CheckTeam_User(session,user,url):
	try:
		verif = session.get(url+'/api/v1/users/me').text
		if(type(json.loads(verif)["data"]["team_id"]) == int):
			return True
	except Exception as ex:
		logger("Error to check user account : %s"%str(ex),"error",1,0)
	return False

def CheckUser_Exist(session,user,url):
	try:
		resp = session.get(url+'/users?field=name&q=%s'%user['pseudo']).text.replace("\n","").replace("\t","")
		all_ = list(zip(*list(re.findall(r'<a href="/users/(.*?)">(.*?)</a>',resp))))
		if(len(all_) != 0):
			if(user["pseudo"].lower() in list((map(lambda x: x.lower(), all_[1])))):
				return True  
		return False
	except Exception as ex:
		logger(" [+] Error to check if user exist : %s"%str(ex),"error",1,0)
		return False

def Join_Team(session,user,url):
	try:
		html = session.get(url + "/teams/join").text
		token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1); # Get token csrf
		post = {"name":user["team"],"password":user["team_password"],"_submit":"Join","nonce":token}	# Post Data
		resp = session.post(url+'/teams/join',post).text	# Create Team
		return CheckTeam_User(session,user,url)
	except Exception as ex:  
		logger(" [+] Error to join the team : %s"%str(ex),"error",1,0)
		return False

def Create_Team(session,user,url):
	try:
		html = session.get(url + "/teams/new").text
		token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);
		resp = session.post(url+'/teams/new',{
			"name":user["team"],
			"password":user["team_password"],
			"_submit":"Create",
			"nonce":token
		}).text
		return CheckTeam_User(session,user,url)
	except Exception as ex:
		logger("Error during team creation : %s"%str(ex),"error",1,0)
		return False

def CheckTeam_Exist(session,user,url):
	try:
		resp = session.get(url+'/teams?field=name&q=%s'%user['team']).text
		all_ = list(zip(*list(re.findall(r'<a href="/teams/(.*?)">(.*?)</a>',resp))))
		if(len(all_) != 0):
			if(user["team"].lower() in list((map(lambda x: x.lower(), all_[1])))):
				return True  
		return False
	except Exception as ex:
		logger(" [+] Error to check if team exist : %s"%str(ex),"error",1,0)
		return False

def Register_Account(session,user,url):
	try:
		html = session.get("%s/register"%url).text
		token = re.search(r"csrfNonce': \"(.*?)\",",html).group(1);
		rep = session.post('%s/register'%url,{
			"name":user['pseudo'],
			"email":user['email'],
			"password":user['password'],
			"nonce":token,
			"_submit":"Submit"
		}).text
		return True if('Logout' in rep) else False
	except Exception as ex:
		logger("Error during registration : %s"%str(ex),"error",1,0)
		return False,False

def Login_Account(session,user,url):
	nonce = Get_Nonce(url,session)
	rep = session.post('%s/login'%url,
		data={
			'name': user['pseudo'],
			'password': user['password'],
			'nonce': nonce,
		}
	)
	if('Logout' in rep.text):
		return True
	else:
		return False

async def Login4Parsing(ctx,username,password,url,config):	
	if(not username or not password):
		return False,None

	session = requests.session()

	# Login Using Token
	if 'CTFD_TOKEN' in config.keys():		
		await ctx.send('**[+] Login using token ...**')
		session.headers.update({
			"Content-Type": "application/json",
			"Authorization": "Token %s"%config['CTFD_TOKEN']
		})
		resp = json.loads(session.get('%s/api/v1/users/me'%url).text)
		if 'success' in resp and resp['success']:
			return True,session
		await ctx.send("```\nMessage:\n%s```"%(resp['message']))

	# Check if recaptcha
	if(isRecaptched(url)):
		logger('\nRecaptcha Detected !!\n','info',1,0)
		await ctx.send('''
			**[+] Recaptcha Detected !!**
			```
			->  Create a token here: %s/settings**
			->  Use: %stoken "your token"**
			```'''%(url,config['PREFIX'])
		)
		return False,None

	# Login Using Credentials
	session.cookies.clear()
	if(Login_Account(session,{"pseudo":username,"password":password},url)):
		return True,session
	else:
		logger('Unable to Login With those credentials','error',0,1)
		return False,None
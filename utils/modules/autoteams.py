import json
import random

from utils.account import *
from utils.logger import logger

def check_json(json_config):
	try:
		json.loads(json_config)
		return True
	except ValueError as ex:
		return False

def Complete_user(user):
	if(user[1] == ""):
		user[1] = "%s@tempmail.com"%(''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for i in range(12)))
	if(user[2] == ""):
		user[2] = ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;.") for i in range(12))
	return user

def Get_data(data):
	final  = "```\n"
	final += f"- {'Name:':<12}\t{data['pseudo']:>12}\n"
	final += f"- {'Password:':<12}\t{data['password']:>12}\n"
	final += f"- {'Email:':<12}\t{data['email']:>12}\n"
	if(inTeam):
		final += f"- {'Team:':<12}\t{data['team']:>12}\n"
		final += f"- {'Team Pass:':<12}\t{data['team_password']:>12}\n"
	final += "```"
	return final
	
def Create_team(data,url):
	if not check_json(data):
		return '**[+] Error : Invalid Json**'
	try:
		config = json.loads(data)
		session = requests.session()
		final = ''
		logger('Creating %s users for the team %s'%(len(config['users']),config['team']),'info',0,1)
		for user in config["users"]:
			user = Complete_user(user)
			session.cookies.clear()
			
			data = {
				"pseudo":user[0],
				"email":user[1],
				"password":user[2],
				"team":config["team"],
				"team_password":config["teampwd"],
			}

			if(CheckUser_Exist(session,data,url)):
				succeed = Login_Account(session,data,url)
			else:
				succeed = Register_Account(session,data,url)
				
			if(succeed):
				if(CheckTeam_Exist(session,data,url)):
 					inTeam = Join_Team(session,data,url)
				else:
					inTeam = Create_Team(session,data,url)

				final += Get_data(data)				
			else:
				final += "\n**[+] Failed To Login/Create the account %s**"%user[0]
		return final
	except Exception as ex:
		print(ex)
		return '**[+] Error : Invalid Config | Check here https://github.com/Vozec/Ctfd-Account-Creator**'
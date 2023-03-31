#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import discord
import deepl
from os		  import environ as env
from os.path	 import exists
from discord.ext import commands
from requests	import session

from utils.logger	import logger
from utils.misc		 import *
from utils.account   import *
from utils.parser	import *
from utils.manager   import *

from utils.modules.ctftime   import *
from utils.modules.autoteams import *
from utils.modules.translator import *

config = {
	'TOKEN':env['DISCORD_TOKEN'],
	'PREFIX':'?',
	'CATEGORY':'CTF',
	'DESCRIPTION':'CTFd Parser BOT',
	'DEEPL_KEY':'d92e2e38-fcf1-d4e6-dff0-0595d5bb0b99:fx',
}

translator = deepl.Translator(config['DEEPL_KEY']) if config['DEEPL_KEY'] else None

bot	= commands.Bot(command_prefix=config['PREFIX'], description=config['DESCRIPTION'], help_command=None,intents = discord.Intents.all())

@bot.event
async def on_ready():
	logger('%s has connected to Discord!\n'%bot.user.name,"info",1,2)
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(config['PREFIX'] + 'help'))

@bot.command()
async def help(ctx,message=None):
	embed = discord.Embed(title="Help Menu", description="",color=0x00ff00)
	embed.add_field(name='%sCreateCTFD <Url> <Mode> <Username> <Password>'%config['PREFIX'],value='Parse & Create Channels/Categories/Threads for CTF CTFd-based',inline=False)
	embed.add_field(name='%stoken <mytoken>'%config['PREFIX'],value='Set token account to login & bypass recaptcha',inline=False)
	embed.add_field(name='%sflag '%config['PREFIX'],value='Add \'🚩\' to the name of a channel',inline=False)	
	embed.add_field(name='%sgen <url>'%config['PREFIX'],value='Generate new random credentials',inline=False)
	embed.add_field(name='%sgenteam <url> <config>'%config['PREFIX'],value='Generate a full team on the CTFd , based on config provided in input or using .json files',inline=False)
	embed.add_field(name='%snext <days>'%config['PREFIX'],value='Return the next ctfs that will take place in a few days',inline=False)	
	embed.add_field(name='%shelp'%config['PREFIX'],	value='Display this menu',inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def token(ctx,token=None):
	global config
	if(token):
		logger("Storing new token: %s"%token,"log",1,0)
		config['CTFD_TOKEN'] = token
		await ctx.message.delete()
		await ctx.send("**[+] Token Stored **")		
	else:
		await ctx.send("**[+] Empty token !!**")

@bot.command()
async def next(ctx,day=7):
	if('next' in ctx.message.channel.name):
		# Max days > Avoid Flood
		if(day>30):
			day = 30
			await ctx.send('**Max Days Limite : 30**')
		resp = NextCtf(day)
		for s in resp:
			await ctx.send(s)
	else:
		await ctx.send('**Invalid Channel ! "next" in channel name required **')

@bot.command()
async def flag(ctx):
	Thread_name = ctx.message.channel.name
	if Thread_name[0] == "🚩":
		await ctx.reply("**%s already flagged**"%Thread_name.split('|')[0].strip())
	else:
		new_Thread_name = "🚩" + Thread_name
		await ctx.message.channel.edit(name=new_Thread_name)
		await ctx.send('**%s has been flagged !**'%Thread_name)
		logger("%s has been flagged !"%Thread_name,"log",0,1)
		await ctx.message.delete()

@bot.command()
async def genteam(ctx,url,config=None):
	if url is not None and config is not None:
		current_dir = os.path.dirname(os.path.abspath(__file__))
		path = current_dir+'/config/%s.json'%(config.replace(".json",""))
		url = Clean_Url(url)
		if(isRecaptched(url)):
			await ctx.send('**Recaptcha Detected !!**')
		elif exists(path):
			data = open(path,'r').read()
			await ctx.send(Create_team(data,url))
		else:
			await ctx.send('**Invalid Parameter ! config \'%s\' doesn\'t exist**'%path)
	else:
		await ctx.send('**Invalid Parameter ! \'url\' & \'config\' required **')


@bot.command()
async def gen(ctx,url):
	logger(f"Creating account ...","info",1,0)
	await ctx.send('**Creating account ...**')
	if url == None:
		await ctx.send("**Failed to Create account : Invalid URL **")
	else:
		user = await Register_Random(ctx,Clean_Url(url))
		if(user != None):
			embed = discord.Embed(title="New Account :", description="Gen Account: %s"%url,color=0x00ff00)
			msg = """
			Name: %s
			Password: %s
			Email: %s
			Team: %s
			Team Pass:  %s
			Link: https://tempr.email/
			"""%(user['pseudo'],user['password'],user['email'],user['team'],user['team_password'])
			embed.add_field(name="Credentials : \n", value=msg)
			await ctx.send(embed=embed)
		else:
			await ctx.send("**Failed to Create account ...**") 

@bot.command()
async def f2e(ctx,msg):
	if msg:
		logger("Translating '%s' to english"%(msg),"log",0,0)
		res = translate_to_english(ctx,translator,msg)
		await ctx.message.delete()
		await ctx.send(embed=res) 

@bot.command()
async def e2f(ctx,msg):
	if msg:
		logger("Translating '%s' to english"%(msg),"log",0,0)
		res = translate_to_french(ctx,translator,msg)
		await ctx.message.delete()
		await ctx.send(embed=res) 


@bot.command()
async def CreateCTFD(ctx,url=None,mode=None,username=None, password=None):
	if(not url):
		logger(" [-] Bad arguments","error",0,0)
		await help(ctx)
	elif(not Check_Ctfd(url)):
		logger(" [-] Not a ctf CTFD Based","error",0,0)
	elif(not isAdmin(ctx)):
		logger(' [-] %s not allowed.'%(ctx.author),"error",1,0)
		await ctx.send("**[-] You are not allowed to run this command!**")
	else:
		if(not username or not password):
			user = await Register_Random(ctx,url)
			username,password = user['pseudo'],user['password']
		url = Clean_Url(url)
		logger("Trying to login to : %s"%url,"info",1,1)
		isLogged,session = await Login4Parsing(ctx,username,password,url,config)
		if(isLogged):
			logger("Logged in with user: %s"%username,"log",0,1)
			ctfd_challenges = await Parse_Challenges(ctx,session,url)
			await Result_manager(bot,ctx,url,ctfd_challenges,config,mode)
	logger("\n\nParsing of %s ended !"%url,"log",0,1)


if __name__ == '__main__':
	Init()
	bot.run(config['TOKEN'])

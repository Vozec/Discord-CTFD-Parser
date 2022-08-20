#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import discord
from os import environ as env
from discord.ext import commands
from requests import session

from utils.logger  import logger
from utils.misc	import *
from utils.account import *
from utils.parser  import *
from utils.manager import *
from utils.ctftime import *

config = {
	'TOKEN':env['DISCORD_TOKEN'],
	'PREFIX':'?',
	'CATEGORY':'CTF',
	'DESCRIPTION':'CTFd Parser BOT',
}

bot	= commands.Bot(command_prefix=config['PREFIX'], description=config['DESCRIPTION'], help_command=None)

@bot.event
async def on_ready():
	logger('%s has connected to Discord!\n'%bot.user.name,"info",1,2)
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(config['PREFIX'] + 'help'))

@bot.command()
async def help(ctx,message=None):
	embed = discord.Embed(title="Help Menu", description="",color=0x00ff00)
	embed.add_field(name='%sCreateCTFD <Url> <Mode> <Username> <Password>'%config['PREFIX'],value='Parse & Create Channels/Categories/Threads for CTF CTFd-based',inline=False)
	embed.add_field(name='%stoken <mytoken>'%config['PREFIX'],value='Set token account to login & bypass recaptcha',inline=False)
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
async def CreateCTFD(ctx,url=None,mode=None,username=None, password=None):
	if(not url):
		logger(" [-] Bad arguments","error",0,0)
		await help(ctx) 
	elif(not isAdmin(ctx)):
		logger(' [-] %s not allowed.'%(ctx.author),"error",1,0)
		await ctx.send("**[-] You are not allowed to run this command!**")
	else:
		if(not username or not password):
			user = await Register_Random(ctx,url)
			username,password = user['username'],user['password']
		url = Clean_Url(url)
		logger("Trying to login to : %s"%url,"info",1,1)
		isLogged,session = await Login(ctx,username,password,url,config)
		if(isLogged):
			logger("Logged in with user: %s"%username,"log",0,1)
			ctfd_challenges = await Parse_Challenges(ctx,session,url)
			await Result_manager(bot,ctx,url,ctfd_challenges,config,mode)
	logger("Parsing of %s ended !"%url,"info",0,1)


if __name__ == '__main__':
	bot.run(config['TOKEN'])
import time,discord
from rich import progress
from datetime import datetime

from utils.misc import Resolve_CTF,Cleaner,Get_ChallMSG
from utils.logger import logger

async def Result_manager(bot,ctx,url,challenges,config,mode='1'):
	mode 	 = '1' if(mode not in ['1','2','3']) else mode
	ctf_name = Cleaner(Resolve_CTF(url))
	category = config['CATEGORY'] if mode == '2' else ctf_name

	# Create Main Category & General Channel
	category = await Create_Category(bot,ctx,category)
	main 	 = await Create_Channel(bot,ctx,category,Cleaner(ctf_name))
	await main.send('**Url:** %s'%url)
	with progress.Progress() as p:
		progress_bar = p.add_task("%s | \t "%datetime.now().strftime("%H:%M:%S"), total=len(challenges))
		for chall in challenges:
			if(mode == '1'):
				main = await Create_Channel(bot,ctx,category,Cleaner(chall['category']))
			if(mode == '3'):
				sender = await Create_Channel(bot,ctx,category,Cleaner(chall['name']))
			else:
				sender = await Create_Thread(bot,main,chall['category'],chall['name'])
			if(sender):
				p.update(progress_bar, advance=1)		
				await sender.send(Get_ChallMSG(chall,url))
			else:
				challenges.append(chall) # If fail => chall go back in list


async def Create_Category(guild,ctx,category):
	for obj in ctx.guild.categories:
		if(obj.name == category):
			return obj.name
	res = await ctx.guild.create_category(category)
	logger('Creating Category "%s".'%(category),"warning",0,2)
	return res.name



async def Create_Channel(bot,ctx,category,channel):
	query = discord.utils.get(bot.get_all_channels(),
		category=discord.utils.get(ctx.guild.categories,name=category),
		name=channel)
	if not query:
		logger('Creating Channel "%s" in "%s".'%(channel,category),"warning",0,2)
		return await ctx.guild.create_text_channel(
			channel,
			category=discord.utils.get(ctx.guild.categories,name=category)
		)
	return query



async def Create_Thread(bot,ctx,category,name):
	message = await ctx.send('[%s] %s'%(category,name))
	try:
		thread = await message.create_thread(name=message.content)
		channel = bot.get_channel(message.id)
		logger('Creating Thread "%s".'%(message.content),"warning",0,2)
		if(channel):
			return channel
	except Exception as ex:
		logger('Failed to Create Channel: %s'%message.content,"error",0,1)
		logger(str(ex),"error",0,1)
		if ('We are being rate limited' in str(ex)):
			logger('Timeout ! Waiting 5 seconds',"error",1,2)
			time.sleep(5000)
	return None
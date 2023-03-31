import requests 
import discord

def translate_to_english(ctx,translator,msg):
	result = translator.translate_text(msg, target_lang="EN-GB")
	embed = discord.Embed(title=ctx.author.name, description=result.text,color=0x00ff00)
	return embed

def translate_to_french(ctx,translator,msg):
	result = translator.translate_text(msg, target_lang="FR")
	embed = discord.Embed(title=ctx.author.name, description=result.text,color=0x00ff00)
	return embed
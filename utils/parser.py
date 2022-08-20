#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import json
from utils.logger import logger


async def Parse_Challenges(ctx,session,url):
	logger("Printing Challenges:","info",1,1)
	challenges = await Fetch_Infos(ctx,'%s/api/v1/challenges'%url,session)
	result 	   = []
	for challenge in challenges:
		try:
			res = await Fetch_Infos(ctx,'%s/api/v1/challenges/%s'%(url,challenge["id"]),session)
			result.append({
				'name':res['name'].replace(' ','_'),
				'value':str(res['value']),
				'infos':str(res['description']).replace('\r', '').replace('\n', ''),
				'category':res['category'],
				'files':res['files'] if 'files' in res else [],
				'max_attempts':str(res['max_attempts'])
			})
		except Exception as ex:
			logger("Error during fetching/grabbing a challenge: %s"%challenge['name'],'error',0,1)
			print(ex)
			pass
	return result

async def Fetch_Infos(ctx,url,session):
	res = json.loads(session.get(url).text)
	if 'message' in res:
		await ctx.send('** [+] %s**'%res['message'])
	elif 'success' not in res:
		logger('Failed fetching challenge!','error',1,0)
	else:
		return res['data']
	return []
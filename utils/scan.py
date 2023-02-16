import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder


def scan_file(url,config):
	try:
		res = requests.get(url)

		if res.status_code != 200:
			return ''

		content_lenght = int(res.headers['Content-Length'])
		max_cnt_lenght = 16777216

		if content_lenght < max_cnt_lenght:

			filename = res.headers['Content-Disposition'].split('filename=')[1]
			encoder = MultipartEncoder(fields={
						'password': '',
						'fflag': '',
						'files': (filename, res.content, 'text/plain')
				 })
			r = requests.post('%s/upload'%config['SCAN_URL'],data=encoder,
				headers={'Content-Type': encoder.content_type})
			h = json.loads(r.text)['hash']
			return '%s/%s'%(config['SCAN_URL'],h)
		else:
			return ''
	except Exception as ex:
		return ''

import os
import glob
import json

def fix_xml(response):
	old_body = response.body
	new_body = old_body.replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '<div>') + '</div>'
	return response.replace(body=new_body)

def latestJSON(folder):
	files = glob.glob('Data/' + folder + '/*')
	if len(files) > 0:
		latest = max(files, key=os.path.getctime)
		return json.loads(open(latest).read())
	else:
		return {}

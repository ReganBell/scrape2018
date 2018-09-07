import json
import os
import sys

def parseCookie(cookieString):
	results = {}
	for string in cookieString.split('; '):
		key = string.split('=')[0]
		value = string.split('=')[1]
		results[key] = value
	return results
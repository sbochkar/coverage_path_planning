import time
import datetime

def current_time():
	"""
	This helper function return current time in human readnable format
	:return time: Time string in human readable format
	"""
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

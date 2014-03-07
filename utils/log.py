import traceback

debug=False

DEBUG_LEVEL='debug'
INFO_LEVEL='info'
def PyLog(level,value):
	if debug:
		print value
	if level == 'info' and not debug:
		print value

def PyLogTB(level,tb):
	if debug:
		traceback.print_tb(tb)
	if level == 'info' and not debug:
		traceback.print_tb(tb)

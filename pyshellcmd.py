
class PyShellCmd(object):
	def __init__(self,shell,disk):
		self.disk = disk
		self.shell=shell

	def BasicHelp(self):
		print 'You can use !xdg-open file-name to open the file on gnome'

	def do_command(self,arg):
		pass

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyLsCmd(PyShellCmd):
	def __init__(self,shell,disk,detail):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None
		self.isdetail=detail

	def do_command(self,arg):
		self.BasicHelp()
		self.disk.Dir(arg,self.isdetail)

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyCdCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		if not arg:
			self.do_help()
		else:
			self.disk.Enter_Dir(arg)
			self.shell.SetPrompt()

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyPwdCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		print self.disk.Pwd()

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyDlCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		if not arg:
			self.help_dl()
		else:
			arglist = arg.split()
			if self.disk.DownloadFile(arglist):
				self.BasicHelp()

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyUlCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		if not arg:
			self.help_dl()
		else:
			arglist = arg.split()
			if self.disk.UploadFile(arglist):
				self.BasicHelp()

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyLogoutCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		pass

	def do_help(self):
		pass

	def do_complete(self):
		pass

class PyQuitCmd(PyShellCmd):
	def __init__(self,shell,disk):
		PyShellCmd.__init__(self,shell,disk)
		self.arger = None

	def do_command(self,arg):
		return True

	def do_help(self):
		pass

	def do_complete(self):
		pass


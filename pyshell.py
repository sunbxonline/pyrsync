import cmd
import subprocess
from pydisk import CloudDisk
import pyshellcmd

class PyShell(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.disk= CloudDisk(None)
	
	def Init(self):
		if not self.disk.Init():
			log.PyLog(log.INFO_LEVEL,'Init Fail')
			raise SystemExit(1)
		self.prompt=self.disk.GetUserName() + ':/# '
		quitcmd=pyshellcmd.PyQuitCmd(self,self.disk)
		self.cmddict={
				'ls':pyshellcmd.PyLsCmd(self,self.disk,False),
				'll':pyshellcmd.PyLsCmd(self,self.disk,True),
				'cd':pyshellcmd.PyCdCmd(self,self.disk),
				'dl':pyshellcmd.PyDlCmd(self,self.disk),
				'ul':pyshellcmd.PyUlCmd(self,self.disk),
				'quit':quitcmd,
				'exit':quitcmd,
				'pwd':pyshellcmd.PyPwdCmd(self,self.disk)
				}
	def SetPrompt(self):
		self.prompt=self.disk.GetUserName() + ':' + self.disk.Pwd() + '# '
	
	def do_diff(self):
		pass

	def do_shell(self, arg):
		print ">", arg
		sub_cmd = subprocess.Popen(arg,shell=True, stdout=subprocess.PIPE)
		print sub_cmd.communicate()[0]
	
if __name__ == '__main__':
	pyshell = PyShell()
	pyshell.Init()
	for item in pyshell.cmddict.keys():
		 pyshell.__dict__['do_' + item]=pyshell.cmddict[item].do_command
	pyshell.cmdloop('Welcome to use pyrsync!')


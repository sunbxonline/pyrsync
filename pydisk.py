from oauth import pyoauth
from utils import log
import json
import sys
import os
import shutil

class CloudDisk(object):
	def __init__(self,collector):
		self.oauther = pyoauth.PyOAuth('','',collector)
		self.local_path =os.path.abspath('.')#local path
		self.remote_path = '/' #remote path
		self.account_info = None

	def Init(self):
		try:
			with open(".pyrsync.conf",'a+') as f:
				try:
					confObj = json.load(f)
					self.oauther.SetToken(confObj['oauth_token']).SetTokenSecret(confObj['oauth_tokensecret'])
					self.account_info=confObj
				except Exception:
					pass

				if self.oauther.GetToken() == '' or self.oauther.GetTokenSecret() == '':
					f = open('.pyrsync.conf','w+')
					if not self.oauther.Authorize():
						log.PyLog(log.INFO_LEVEL,'authorize fail,exit')
						raise SystemExit(1)
					account = self.RequestAccountInfo()
					if account == None:
						log.PyLog(log.INFO_LEVEL,'get user account fail,exit')
						raise SystemExit(1)
					account['oauth_token'] = self.oauther.GetToken()
					account['oauth_tokensecret'] = self.oauther.GetTokenSecret()
					self.WriteJson(account,f)
				return True
		except IOError as e:
			print e
			type,value,tb = sys.exc_info()
			log.PyLogTB(log.INFO_LEVEL,tb)
			return False
	
	def WriteJson(self,confObj,f):
		try:
			value = json.JSONEncoder().encode(confObj)
			f.write(value)
		except Exception as e:
			print e
			type,value,tb = sys.exc_info()
			log.PyLogTB(log.INFO_LEVEL,tb)
			raise SystemExit(1)
	
	def GetUserName(self):
		return self.account_info['user_name']

	def CreateFoler(self,folder_name):
		create_folder_url = 'http://openapi.kuaipan.cn/1/fileops/create_folder'
		param_list = []
		param_list.append(('root','app_folder'))
		param_list.append(('path',folder_name))
		jsonobj = self.oauther.GetRestJson(create_folder_url,param_list)
		if jsonobj!=None and jsonobj['msg'] == 'ok':
			return True
		else:
			return False

	def UploadFile(self,arglist):
		if len(arglist)>=1:
			file_name=arglist[0]
		else:
			return False
		if len(arglist)>=2:
			dest_dir=arglist[1]
		else:
			dest_dir = self.remote_path

		file_name = self.PrepareLocalDir(file_name)
		dest_dir = self.PrepareRemoteDir(dest_dir)
		try:
			#get target filename from dest_dir firstly
			target_dir,target_filename = os.path.splitext(dest_dir)
			if target_filename == '':
				#or from the clound disk path
				target_filename = os.path.split(file_name)[1] 
				dest_dir = self.AssemblePath(dest_dir,target_filename)
		except IOError as e:
			log.PyLog(log.DEBUG_LEVEL,'upload error:' + str(e))
			return False


		log.PyLog(log.INFO_LEVEL,'uploading file %s-->kuaipan/app_folder%s' % (file_name,dest_dir))

		upload_locate_url = 'http://api-content.dfs.kuaipan.cn/1/fileops/upload_locate'
		jsonobj = self.oauther.GetRestJson(upload_locate_url,[])
		if jsonobj == None:
			return False
		try:
			log.PyLog(log.DEBUG_LEVEL,'Upload loate url:' + jsonobj['url'])
			upload_url = jsonobj['url'] + '1/fileops/upload_file'
			#upload_url ='http://p5.dfs.kuaipan.cn:8080/cdlnode/1/fileops/upload_file'
			log.PyLog(log.DEBUG_LEVEL,'upload_url:' + upload_url)
			param_list = []
			param_list.append(('root','app_folder'))
			param_list.append(('path',dest_dir))
			param_list.append(('overwrite','False'))

			reporter=PosterReporter(file_name)
			self.oauther.PostFile(upload_url,file_name,param_list,reporter)
			return True
		except KeyError as e:
			log.PyLog(log.DEBUG_LEVEL,'upload error:' + str(e))
			log.PyLog(log.INFO_LEVEL,'upload error')
			return False

	def DownloadFile(self,arglist):
		if len(arglist)>=1:
			file_name=arglist[0]
		else:
			return False
		if len(arglist)>=2:
			dest_dir=arglist[1]
		else:
			dest_dir = self.local_path

		file_name = self.PrepareRemoteDir(file_name)
		dest_dir = self.PrepareLocalDir(dest_dir)

		log.PyLog(log.INFO_LEVEL,'downloading file : kuaipan/app_folder' + file_name + '--->' + dest_dir)

		download_url = 'http://api-content.dfs.kuaipan.cn/1/fileops/download_file'
		param_list = []
		param_list.append(('root','app_folder'))
		param_list.append(('path',file_name))
		jsonobj,length = self.oauther.DownloadData(download_url,param_list)
		if jsonobj == None:
			log.PyLog(log.INFO_LEVEL,'download fail')
			return False
		try:
			#get target filename from dest_dir firstly
			target_dir,target_filename = os.path.splitext(dest_dir)
			if target_filename == '':
				#or from the clound disk path
				target_filename = os.path.split(file_name)[1] 
			#now we get the dir and the name
			f = open(self.AssemblePath(target_dir,target_filename),'w+')
			#shutil.copyfileobj(jsonobj,f)
			try:
				writelength = 0
				data = jsonobj.read(1024)
				while len(data) > 0:
					f.write(data)
					writelength += len(data)
					print 'downloading:%d%%\r' % (writelength*100/length),
					data = jsonobj.read(1024)
				print
				log.PyLog(log.INFO_LEVEL,'download ok')
				return True
			finally:
				f.close()
		except IOError as e:
			log.PyLog(log.INFO_LEVEL,str(e))
			return False
	
	def AssemblePath(self,dir_name,file_name):
		return os.path.normpath(os.path.join(dir_name,file_name))


	def Dir(self,dir_name,is_detail):
		if not dir_name:
			dir_name = self.remote_path
		else:
			dir_name = self.PrepareRemoteDir(dir_name)
		log.PyLog(log.INFO_LEVEL,'directory : kuaipan/app_folder' + dir_name)

		dir_url = 'http://openapi.kuaipan.cn/1/metadata/app_folder' + dir_name
		jsonobj = self.oauther.GetRestJson(dir_url,[])

		dir_type = jsonobj['type']
		print '[type]:%s\t[size]:%d\t[create time]:%s\t[modify time]:%s' %  (dir_type,jsonobj['size'],jsonobj['create_time'],jsonobj['modify_time'])
		print '--------------------------------------------'
		print 'files in the directory:'
		if dir_type == 'folder':
			if is_detail:
				for item in jsonobj['files']:
					print '%s\t%d\t%s\t%s\t%s' % ('-' if item['type']=='file' else 'D',item['size'],item['create_time'],item['modify_time'],item['name'])
			else:
				listvalue = ''
				for item in jsonobj['files']:
					listvalue += item['name'] + '\t'
				print listvalue
	def PrepareRemoteDir(self,dir_name):
		if os.path.isabs(dir_name):
			return dir_name
		else:
			return os.path.normpath(os.path.join(self.remote_path,dir_name))
	
	def PrepareLocalDir(self,dir_name):
		if os.path.isabs(dir_name):
			return dir_name
		else:
			return os.path.normpath(os.path.join(self.local_path,dir_name))


	def Enter_Dir(self,dir_name):
		self.remote_path = self.PrepareRemoteDir(dir_name)
	
	def Pwd(self):
		return self.remote_path
	
	def RequestAccountInfo(self):
		account_info_url = 'http://openapi.kuaipan.cn/1/account_info'
		self.account_info = self.oauther.GetRestJson(account_info_url,[])
		return self.account_info

class PosterReporter(object):
	def __init__(self,file_name):
		self.file_size = os.stat(file_name).st_size 
		self.current_size = 0

	def report_progress(self,size):
		self.current_size += size
		print "uploading:%d%%\r" % (self.current_size*100/self.file_size),

'''
debug_oauth = False
if debug_oauth:
	targetdict = {}
	targetdict['base_string']='POST&http%3A%2F%2Fp5.dfs.kuaipan.cn%3A8080%2Fcdlnode%2F%2F1%2Ffileops%2Fupload_file&oauth_consumer_key%3DxcacXzSyi73VztlL%26oauth_nonce%3D2Bher6s0%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1390895251%26oauth_token%3D0031514710c5c7aa3714c2e4%26oauth_version%3D1.0%26overwrite%3Dtrue%26path%3D%252Fabc.txt%26root%3Dapp_folder'
	targetdict['secret']='riurw930DQhs0bj1&20a1d46e140c41bca141073575340b9d'
	targetdict['signature']='S7uimMk4o9yPzJq3094Iokhbg%2Bg%3D'
	targetdict['request_url']='http://p5.dfs.kuaipan.cn:8080/cdlnode/1/fileops/upload_file?oauth_signature=S7uimMk4o9yPzJq3094Iokhbg%2Bg%3D&oauth_consumer_key=xcacXzSyi73VztlL&oauth_nonce=2Bher6s0&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1390895251&oauth_token=0031514710c5c7aa3714c2e4&oauth_version=1.0&overwrite=true&path=%2Fabc.txt&root=app_folder'
	testrand='2Bher6s0'
	testtimestamp='1390895251'
	kuaipan = CloudDisk(os.path.abspath('.'),pyoauth.OAuthDebugCollector(testrand,testtimestamp,targetdict))
else:
	kuaipan = CloudDisk(os.path.abspath('.'),None)

	if kuaipan.Init():
		log.PyLog(log.INFO_LEVEL,'Init OK')
	else:
		log.PyLog(log.INFO_LEVEL,'Init Fail')
		raise SystemExit(1)
'''

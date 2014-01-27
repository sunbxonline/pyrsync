from oauth import pyoauth
from utils import log
import json
import sys
import os
import shutil

class CloudDisk(object):
	def __init__(self,root_path,collector):
		self.oauther = pyoauth.PyOAuth('','',collector)
		self.root_path = root_path

	def Init(self):
		try:
			with open(".pyrsync.conf",'a+') as f:
				try:
					confObj = json.load(f)
					self.oauther.SetToken(confObj['oauth_token']).SetTokenSecret(confObj['oauth_tokensecret'])
				except Exception:
					pass

				if self.oauther.GetToken() == '' or self.oauther.GetTokenSecret() == '':
					f = open('.pyrsync.conf','w+')
					if not self.oauther.Authorize():
						return False
					else:
						confObj = {}
						confObj['oauth_token'] = self.oauther.GetToken()
						confObj['oauth_tokensecret'] = self.oauther.GetTokenSecret()
						try:
							value = json.JSONEncoder().encode(confObj)
							f.write(value)
						except Exception as e:
							print e
							type,value,tb = sys.exc_info()
							log.PyLogTB(log.INFO_LEVEL,tb)
							return False
				return True
		except IOError as e:
			print e
			type,value,tb = sys.exc_info()
			log.PyLogTB(log.INFO_LEVEL,tb)
			return False

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

	def UploadFile(self,file_name):
		upload_locate_url = 'http://api-content.dfs.kuaipan.cn/1/fileops/upload_locate'
		jsonobj = self.oauther.GetRestJson(upload_locate_url,[])
		if jsonobj == None:
			return False

		upload_url = jsonobj['url'] + '1/fileops/upload_file'
		print 'upload_url:' + upload_url

		self.oauther.PostFile(upload_url,file_name)

	def DownloadFile(self,file_name):
		log.PyLog(log.INFO_LEVEL,'downloading file : kuaipan/app_folder' + file_name)

		download_url = 'http://api-content.dfs.kuaipan.cn/1/fileops/download_file'
		param_list = []
		param_list.append(('root','app_folder'))
		param_list.append(('path',file_name))
		jsonobj = self.oauther.DownloadData(download_url,param_list)
		if jsonobj == None:
			return False
		try:	
			f = open(self.root_path +'/' + os.path.basename(file_name),'w+')
			shutil.copyfileobj(jsonobj,f)
		except IOError as e:
			log.PyLog(log.INFO_LEVEL,str(e))
	
	def Dir(self,dir_name):
		log.PyLog(log.INFO_LEVEL,'dir name: kuaipan/app_folder'+dir_name )

		dir_url = 'http://openapi.kuaipan.cn/1/metadata/app_folder' + dir_name
		jsonobj = self.oauther.GetRestJson(dir_url,[])

		print '%s%s' % (jsonobj['root'],jsonobj['path'])
		print 'create time:%s' % (jsonobj['create_time'])
		print 'modify time:%s' % (jsonobj['modify_time'])
		if jsonobj['type'] == 'folder':
			print 'Files in the directory:'
			for fitem in jsonobj['files']:
				print 'name:%s' % fitem['name']
				print 'type:%s' % fitem['type']
				print 'create time:%s' % (fitem['create_time'])
				print 'modify time:%s' % (fitem['modify_time'])

debug_oauth = False
if debug_oauth:
	targetdict = {}
	targetdict['base_string']='GET&http%3A%2F%2Fapi-content.dfs.kuaipan.cn%2F1%2Ffileops%2Fdownload_file&oauth_consumer_key%3DxcacXzSyi73VztlL%26oauth_nonce%3D2p7171yp%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1390804399%26oauth_token%3D0031514710c5c7aa3714c2e4%26oauth_version%3D1.0%26path%3Drsync%252FSTAR.torrent%26root%3Dapp_folder'
	targetdict['secret']='riurw930DQhs0bj1&20a1d46e140c41bca141073575340b9d'
	targetdict['signature']='xW%2F1c5N8WMtALTxdhJ1NpNVwZ5Y%3D'
	targetdict['request_url']='http://api-content.dfs.kuaipan.cn/1/fileops/download_file?oauth_signature=xW%2F1c5N8WMtALTxdhJ1NpNVwZ5Y%3D&oauth_consumer_key=xcacXzSyi73VztlL&oauth_nonce=2p7171yp&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1390804399&oauth_token=0031514710c5c7aa3714c2e4&oauth_version=1.0&path=rsync%2FSTAR.torrent&root=app_folder'
	testrand='2p7171yp'
	testtimestamp='1390804399'
	kuaipan = CloudDisk(os.path.abspath('.'),pyoauth.OAuthDebugCollector(testrand,testtimestamp,targetdict))
else:
	kuaipan = CloudDisk(os.path.abspath('.'),None)

if __name__ == '__main__':
	if kuaipan.Init():
		log.PyLog(log.INFO_LEVEL,'Init OK')
	else:
		log.PyLog(log.INFO_LEVEL,'Init Fail')
		raise SystemExit(1)

	#if kuaipan.CreateFoler('/linux'):
		#log.PyLog(log.INFO_LEVEL,'create folder OK')
	#else:
		#log.PyLog(log.INFO_LEVEL,'create foler Fail')
		#raise SystemExit(1)

	#kuaipan.DownloadFile('rsync/STAR.torrent')
	#kuaipan.UploadFile('abc.txt')
	kuaipan.Dir('/rsync')

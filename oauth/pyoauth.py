import urllib
import sys
import urllib2
import hmac
import hashlib
import time
import random
import json
import base64
from utils import log
from pyposter.encode import multipart_encode
from pyposter.streaminghttp import register_openers

REQUEST_TOKEN_URL = 'https://openapi.kuaipan.cn/open/requestToken'

OAUTH_CONSUMER_KEY = 'oauth_consumer_key'
OAUTH_SIGNATURE = 'oauth_signature'
OAUTH_TIMESTAMP = 'oauth_timestamp'
OAUTH_NONCE = 'oauth_nonce'
OAUTH_VERSION = 'oauth_version'
OAUTH_SIGNATURE_METHOD = 'oauth_signature_method'
OAUTH_TOKEN = 'oauth_token'
OAUTH_TOKEN_SECRET = 'oauth_token_secret'
OAUTH_VERIFIER = 'oauth_verifier'

PYRSYNC_CONSUMER_KEY = 'xcacXzSyi73VztlL'
PYRSYNC_CONSUMER_SECRET = 'riurw930DQhs0bj1'

HTTP_METHOD = 'GET'
SIGNATURE_METHOD = 'HMAC-SHA1'
OAUTH_VERSION_VALUE = '1.0'

AUTHORIZE_URL = 'https://www.kuaipan.cn/api.php?ac=open&op=authorise&oauth_token='

ACCESS_URL = 'https://openapi.kuaipan.cn/open/accessToken'
targetDict = {
		'base_string':'GET&https%3A%2F%2Fopenapi.kuaipan.cn%2Fopen%2FrequestToken&oauth_consumer_key%3DxcacXzSyi73VztlL%26oauth_nonce%3D86pfY5II%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1390659043%26oauth_version%3D1.0',
		'secret':'riurw930DQhs0bj1&',
		'signature':'8Yey7uLRd0Iy49D4iUxO19zAVKw%3D',
		'request_url':'https://openapi.kuaipan.cn/open/requestToken?oauth_signature=8Yey7uLRd0Iy49D4iUxO19zAVKw%3D&oauth_consumer_key=xcacXzSyi73VztlL&oauth_nonce=86pfY5II&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1390659043&oauth_version=1.0'
		}


class OAuthDebugCollector(object):
	def __init__(self,rand,timestamp,target):
		self.base_string=''
		self.secret=''
		self.signature=''
		self.request_url=''
		self.rand=rand
		self.timestamp=timestamp
		self.targetDict=target
		self.check=True
	def CollectBaseString(self,value):
		self.base_string = value
		print 'base_string:' + value
	
	def CollectSecret(self,value):
		self.secret=value
		print 'secret:' + value

	def CollectSignature(self,value):
		self.signature=value
		print 'signature:' + value

	def CollectRequestUrl(self,value):
		self.request_url = value
		print 'request_url:' + value

	def EvaluteItem(self,item,targetitem,targetvalue):
		if item == targetvalue:
			print targetitem + ' equal'
		else:
			self.check=False
			print targetitem + ' not equal'
			print 'My ' + targetitem + '=' + item
			print 'Tg ' + targetitem + '=' + targetvalue

	def Evalute(self):
		self.EvaluteItem(self.base_string,'base_string',self.targetDict['base_string'])
		self.EvaluteItem(self.secret,'secret',self.targetDict['secret'])
		self.EvaluteItem(self.signature,'signature',self.targetDict['signature'])
		self.EvaluteItem(self.request_url,'request_url',self.targetDict['request_url'])
		if not self.check:
			raise SystemExit(1)

class PyOAuth(object):
	def __init__(self,token,token_secret,collector):
		self.oauth_token = token
		self.oauth_tokensecret = token_secret
		self.timestamp = ''
		self.rand = ''
		self.collector = collector
	
	def GetToken(self):
		return self.oauth_token

	def SetToken(self,token):
		self.oauth_token = token
		return self

	def GetTokenSecret(self):
		return self.oauth_tokensecret

	def SetTokenSecret(self,secret):
		self.oauth_tokensecret = secret
		return self

	def FetchToken(self,response):
		try:
			content = response.read()
			log.PyLog(log.DEBUG_LEVEL,'HTTP STATUS:' + str(response.getcode()))
			log.PyLog(log.DEBUG_LEVEL,content)

			request_token = json.loads(content)
			self.oauth_token = request_token[OAUTH_TOKEN]
			self.oauth_tokensecret = request_token[OAUTH_TOKEN_SECRET]
			return True
		except IOError as e:
			log.PyLog(log.INFO_LEVEL,'user interrupt')
			return False
		except Exception as e:
			log.PyLog(log.INFO_LEVEL,'FetchToken unknown error')
			return False
	
	def Authorize(self):
		try:
			response = self.RequestToken()
			if not self.FetchToken(response):
				return False
			log.PyLog(log.INFO_LEVEL,'Getting Response from server...')

			log.PyLog(log.INFO_LEVEL,'Please browse the following url to authorize the app and input the verifier')
			log.PyLog(log.INFO_LEVEL,AUTHORIZE_URL + self.oauth_token) 

			verifier = raw_input('Input verifier you get:')

			response = self.AccessToken(verifier)
			if not self.FetchToken(response):
				return False
			log.PyLog(log.INFO_LEVEL,'Get Access Token from server')
			log.PyLog(log.INFO_LEVEL,self.oauth_token)
			return True

		except urllib2.URLError as e:
			log.PyLog(log.DEBUG_LEVEL,str(e))
			return False

	def UrlEncode(self,param):
		return urllib.quote(param,'~') 

	def GetBaseString(self,base_url,param_list):
		mylist = urllib.urlencode(param_list).split('&')
		mylist.sort()
		myurl = mylist[0] 
		for item in mylist[1:len(mylist)]:
			myurl += '&' + item 
		
		return HTTP_METHOD + '&' + self.UrlEncode(base_url) + '&' + self.UrlEncode(myurl)

	def ComputeSignature(self,base_url,param_list,tokensecret):
		base_string = self.GetBaseString(base_url,param_list)
		secret = PYRSYNC_CONSUMER_SECRET + '&' + tokensecret
		secret = secret.encode('ascii')

		if self.collector != None:
			self.collector.CollectBaseString(base_string)
			self.collector.CollectSecret(secret)

		hmacObj = hmac.new(secret,base_string,hashlib.sha1)
		signature =  self.UrlEncode(base64.b64encode(hmacObj.digest()))
		if self.collector != None:
			self.collector.CollectSignature(signature)
		return signature

	def GetRequestUrl(self,request_url,param_list):
		signature = self.ComputeSignature(request_url,param_list,self.oauth_tokensecret)

		request_token_url = request_url + '?'
		request_token_url += OAUTH_SIGNATURE + '=' + signature 

		param_list.sort()
		for item in param_list:
			request_token_url += '&' + item[0] + '=' + self.UrlEncode(item[1])

		if self.collector != None:
			self.collector.CollectRequestUrl(request_token_url)
			
		return request_token_url

	def PrepareRequest(self):
		if self.collector != None:
			self.timestamp = self.collector.timestamp
		else:
			self.timestamp = str(int(time.time()))
		if self.collector != None:
			self.rand = self.collector.rand
		else:
			self.rand = str(int(100000000*random.random()))
		param_list = []
		param_list.append((OAUTH_CONSUMER_KEY,PYRSYNC_CONSUMER_KEY)) 
		param_list.append((OAUTH_TIMESTAMP,self.timestamp))
		param_list.append((OAUTH_NONCE,self.rand))
		param_list.append((OAUTH_SIGNATURE_METHOD ,SIGNATURE_METHOD))
		param_list.append((OAUTH_VERSION,OAUTH_VERSION_VALUE))
		if self.oauth_token != '':
			param_list.append((OAUTH_TOKEN,self.oauth_token ))
		return param_list
		
	def RequestToken(self):
		request_token_url = self.GetRequestUrl(REQUEST_TOKEN_URL,self.PrepareRequest())

		return urllib2.urlopen(request_token_url)

	def AccessToken(self,verifier):
		param_list = self.PrepareRequest()
		param_list.append((OAUTH_VERIFIER,verifier))

		request_token_url = self.GetRequestUrl(ACCESS_URL,param_list)
		return urllib2.urlopen(request_token_url)

	def GetRestResponse(self,url,param_list):
		param_list += self.PrepareRequest()
		request_url = self.GetRequestUrl(url,param_list)

		if self.collector != None:
			self.collector.Evalute()
		try:
			log.PyLog(log.DEBUG_LEVEL,'request url:' + request_url)
			log.PyLog(log.INFO_LEVEL,'trying to request...')
			response = urllib2.build_opener(urllib2.HTTPCookieProcessor()).open(request_url)
			if response.getcode() == 200:
				log.PyLog(log.INFO_LEVEL,'receive response from server')
			else:
				log.PyLog(log.INFO_LEVEL,'receive error from server' + str(response.getcode()))
			return response
		except urllib2.HTTPError as e:
			log.PyLog(log.DEBUG_LEVEL,str(e))
			type,value,tb = sys.exc_info()
			log.PyLogTB(log.INFO_LEVEL,tb)
			return None
		except urllib2.URLError as e:
			log.PyLog(log.DEBUG_LEVEL,str(e))
			return None

	def GetRestJson(self,url,param_list):
		response = self.GetRestResponse(url,param_list)
		try:
			if response != None:
				res_json = json.load(response)
				return res_json
			else:
				log.PyLog(log.INFO_LEVEL,'request fail')
				return None
		except Exception as e:
			log.PyLog(log.DEBUG_LEVEL,str(e))
			return None

	def DownloadData(self,url,param_list):
		response = self.GetRestResponse( url,param_list)
		if response == None:
			log.PyLog(log.INFO_LEVEL,'request fail')
			return None

		if response.getcode() == 200:
			return response,int(response.info()["content-length"])
		else:
			try:
				res_json = json.load(response)
				log.PyLog(log.INFO_LEVEL,'server msg:' + res_json['msg'])
				log.PyLog(log.INFO_LEVEL,'request fail')
				return None
			except Exception as e:
				log.PyLog(log.DEBUG_LEVEL,str(e))
				return None

	def PostFile(self,url,file_name,param_list,reporter):
		try:
			register_openers(reporter)
			datagen, headers = multipart_encode({"file": open(file_name, "rb"),"name":file_name})

			param_list += self.PrepareRequest()
			request_url = self.GetRequestUrl(url,param_list)

			# Create the Request object
			request = urllib2.Request(url, datagen, headers)
			# Actually do the request, and get the response
			response = urllib2.urlopen(request)
			if response != None:
				print response.read()
		except urllib2.HTTPError as e:
			log.PyLog(log.INFO_LEVEL,str(e))



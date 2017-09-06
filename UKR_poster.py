import requests
from time import sleep
from multiprocessing import Pool
import random
import vk_api
import os

path = os.path.dirname(__file__) + 'Likes-Bots.txt'

class UkrainiansAPI:
	
	'''
	Options: userName, password, groupID, folderPath - path to folder with images,
	deleteFlag - set True for delete images after posting else - False,
	sleepTime - delay in seconds, text - message for publication,
	sharerange - set range for 'share', likesrange - set range for 'likes'
	'''

	imageUploadUrl = 'https://api.ukrainians.co/v1/post/uploadimages'
	url = 'https://api.ukrainians.co/v1/token'
	postUrl = 'https://api.ukrainians.co/v1/post/add'
	likeURL = 'https://api.ukrainians.co/v1/like'

	def __init__(self, userName, password, vkUserName, vkPassword, groupID, likesrange = [10, 20], sharerange = [5, 10], sleepTime = 1000, text=''):
		self.groupID = groupID
		self.text = text
		self.sleepTime = sleepTime
		self.likesrange = likesrange
		self.sharerange = sharerange
		self.vkPassword = vkPassword
		self.vkUserName = vkUserName
		self.vk_session = vk_api.VkApi(self.vkUserName, self.vkPassword)
		self.vk_session.auth()
		self.SessionObject = self.vk_session.get_api()
		self.AuthPL = {
			'grant_type': 'password',
			'userName': userName, 
			'password': password
		}

		self.token = requests.post(UkrainiansAPI.url, data = self.AuthPL).json()['access_token']

	def uploadImage(self, path, url = False): # upload image on Ukrainians server
		'''
		Example: uploadImage(path = 'path', url = False)
		Params: set path to folder on your PC if param url = False.
		If url = True, set url to image
		This method will return json object
		'''
		if url:
			uploadImagePayLoads = [
				('images', ('foo.png', requests.get(path).content, 'image/png'))
			]
		else:
			uploadImagePayLoads = [
		        ('images', ('foo.png', open(path, 'rb'), 'image/png'))
			]
		return requests.post(UkrainiansAPI.imageUploadUrl, files = uploadImagePayLoads, headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
			'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2',
			'Authorization': 'bearer ' + self.token
			}).json()

	def clickLike(self, usrInfo):
		print('HERE!!!')
		authpls = {
			'grant_type': 'password',
			'userName': usrInfo[0], 
			'password': usrInfo[1]
		}
		try:
			requests.post(UkrainiansAPI.likeURL, data = {
				"contentId": self.post_id,
				"likeType": 0,
				"isLiked": 'false'
				}, headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
				'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2',
				'Authorization': 'bearer ' + requests.post(UkrainiansAPI.url, data = authpls).json()['access_token']
				}) # like
		except Exception as Error:
			print(Error)

	def makeShare(self, usrInfo):
		authpls = {
			'grant_type': 'password',
			'userName': usrInfo[0], 
			'password': usrInfo[1]
		}
		try:
			requests.post(UkrainiansAPI.postUrl, data = {
				"sharePostId":self.post_id,
				"text":"",
				"receiverId":requests.post(UkrainiansAPI.url, data = authpls).json()['id'],
				"receiverType":0,
				"ownerType":0
				}, headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
				'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2',
				'Authorization': 'bearer ' + requests.post(UkrainiansAPI.url, data = authpls).json()['access_token']
				}) # Share
		except Exception as Error:
			print(Error)

	def getImageFrom4ch(self):
		if self.SessionObject.wall.get(owner_id=-66814271, count = 2, timeout = 100)['items'][1]['marked_as_ads'] != 1:
			return self.SessionObject.wall.get(owner_id=-66814271, count = 2, timeout = 100)['items'][1]['attachments'][0]['photo']['photo_604']
		return None
	def postImages(self, lastImage = None):
		while True:
			image = self.getImageFrom4ch()
			if lastImage != image and image is not None:
				imageInfo = self.uploadImage(path = image, url = True)
				self.post_id = requests.post(UkrainiansAPI.postUrl, data = {
					"receiverId":self.groupID,
					"receiverType":1,
					"ownerType":1,
					"text":self.text,
					"imagesCacheKey":imageInfo['cacheKey'],
					"images":[imageInfo['files'][0]],
					"link":'null'
				}, headers = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
					'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,uk;q=0.2',
					'Authorization': 'bearer ' + self.token
					}).json()['id']
				for i in [i.split() for i in open(path).readlines()][:random.randint(self.likesrange[0], self.likesrange[1])]:
					self.clickLike(i)
				for i in [i.split() for i in open(path).readlines()][:random.randint(self.sharerange[0], self.sharerange[1])]:
					self.makeShare(i)
				lastImage = image
			sleep(self.sleepTime)

if __name__ == '__main__':
	Poster = UkrainiansAPI(vkUserName = '380667113250', vkPassword = '3221852q', userName = 'slava3221852@gmail.com', password = '3221852q1337_alban', groupID = '40', sleepTime = 60, likesrange = [30, 45], sharerange = [8, 16])
	Poster.postImages()

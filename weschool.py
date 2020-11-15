#!/usr/bin/python
#
#	Fork of mircodezorzi/random -> weschool.py
#
import json
import re
import requests
import os
import time

FNAME = "weschool_secrets.json"

API_URL = 'https://api.weschool.com'

s = requests.Session()

def get(link):
	global s, bearer
	s.options(url = link)

	r = s.get(
		url = link,
		headers = {
		'Authorization':  f'Bearer {bearer}'
		})
	return r

def getMe():
	global API_URL
	MEURL = API_URL + "/v1/users/me?_={}".format(str(time.time()).replace(".","")[:13])
	return get(MEURL).json()

def getGroups():
	global s,bearer,API_URL
	#api v1 permette visione gruppi altri users
	#GROUP_URL = API_URL + '/v1/users/{}/groups?scope=list&start=0&_={}'.format(userid,str(time.time()).replace(".","")[:13])
	GROUP_URL = API_URL + '/v2/groups?start=0&max_timestamp={}'.format(str(time.time()).replace(".","")[:13])
	return get(GROUP_URL).json()


def getLoginInfos():
	global FNAME
	if not os.path.isfile(FNAME):
		with open(FNAME,"w") as f:
			json.dump({
				"username":str(input("Type username:")),
				"password":str(input("Type password:"))
				},f)

	with open(FNAME,"r") as f:
		infos = json.load(f)
		return {
			"scope":"user",
			"client_id":"%clientid%",
			"client_secret":"%clientsecret%",
			"grant_type":"password",
			"username":infos["username"],
			"password":infos["password"],
		}

def LogIn():
	global s,API_URL
	LOGIN_URL = API_URL + '/oauth/v2/token'
	r = s.post(
		url = LOGIN_URL,
		json = getLoginInfos())
	return r.json()

def getBoardList(groupId):
	global API_URL
	BOARDSURL = API_URL + "/v1/groups/{}/boards?limit=200&_={}".format(groupId,str(time.time()).replace(".","")[:13])
	return get(BOARDSURL).json()

def getGroupUsers(groupId):
	global API_URL
	USERSURL = API_URL + "/v1/groups/{}/users?with_pagination=1&offset=0&_={}".format(groupId,str(time.time()).replace(".","")[:13])
	return get(USERSURL).json()

def getBoard(boardId):
	global API_URL
	BOARD = API_URL + "/v1/boards/{}?_={}".format(boardId,str(time.time()).replace(".","")[:13])
	return get(BOARD).json()

def getExercises():
	global API_URL
	EXCURL = API_URL + f'/v1/exercises?filter=ASSIGNMENT&group_id={group}'
	return get(EXCURL).json()

def getDeadlines(groupId):
	global API_URL
	#https://api.weschool.com/v1/groups/186864/deadlines?_=1583316299405
	DEADURL = API_URL + "/v1/groups/{}/deadlines?_={}".format(groupId,str(time.time()).replace(".","")[:13])
	return get(DEADURL).json()
'''
#da migliorare
def getSolutions(exercise):
	global s, bearer, API_URL
	SOLVEURL = API_URL + '/v1/exercises/{}?_={}'.format(exercise,str(time.time()).replace(".","")[:13])
	s.options(url = SOLVEURL)

	r = get(SOLVEURL).json()
	print(r["title"]+"\n\n")
	for quiz in r["quizzes"]:
		print('\n\n-------------------------\n\n')
		print(quiz["title"])
		if 'index_1' in str(quiz["solutions"]):
			print("associaz")
		else:
			phrase = {}
			#print(quiz["quiz"]["questions"][0])
			for i in quiz["questions"]:
				phrase[i["index"]] = i["value"]
			for sol in quiz["solutions"]:
				phrase[sol["index"]] = sol["value"]
			print(" ".join([str(phrase[k]) for k in phrase.keys()]))
'''
def solve(exercise):
	global s, bearer, API_URL
	SOLVEURL = API_URL + f'/v1/exercises/{exercise}/executions'
	s.options(url = SOLVEURL)

	r = s.post(
		url = SOLVEURL,
		headers = {
			'Authorization':  f'Bearer {bearer}'
		})

	r = r.json()
	#print(json.dumps(r))
	r['vote'] = 100
	r['result'] = True
	r['quizzes_ok'] = len(r['quiz_executions'])
	r['status'] = 'finished'
	for quiz in r['quiz_executions']:
		quiz['result'] = True
		quiz['value'] = True
		quiz['answers'] = quiz["quiz"]["solutions"]


	#print(json.dumps(r))

	run = r['id']
	
	s.options(url = SOLVEURL+f'/{run}')

	r = s.put(
		url = SOLVEURL+f'/{run}',
		json = r,
		headers = {
			'Authorization':  f'Bearer {bearer}'
		})
	print(r.text)
	
	
##Exec

bearer = LogIn()['access_token']

group = getGroups()["groups"][0]["id"]
#for exercise in getExercises():
#	solve(exercise['id'])

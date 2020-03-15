#!/usr/bin/python

# ClasseViva Message Checker
# 0fabris
# 03/2020 
# Visualizza i messaggi nella prima aula virtuale disponibile ogni 30 secondi. (forse per verificare presenza studente in aula) 
#

import re
import json
import requests
import os
import sys
import base64
import time
from urllib.parse import urlencode

#File dove sono salvate le credenziali
FNAME = "cv-auth.json"

#Bot
class CVBot():
    def __init__(self,usr,psw):
        self.tinit = time.time()
        self.CV_URL = "https://web.spaggiari.eu"
        self.headers = {
            "User-Agent" : "Mozilla/5.0",
            "Cookie": "",
            "Referer" : self.CV_URL,
            "Origin" : self.CV_URL,
            "Host":  self.CV_URL.split('//')[-1],
            "Pragma" : "no-cache",
            "Cache-Control" : "no-cache",
            "Accept":"*/*"
        }
        self.me_infos = self.Login(usr,psw)
        self.headers["Cookie"] += "PHPSESSID=" +re.findall(r"PHPSESSID\=(.*?);",self.me_infos.headers["Set-Cookie"])[-1]+"; "
        self.log("Login Effettuato")
    
    def Login(self,usr,psw):
        args = {
            "cid": "",
            "uid" : usr,
            "pwd" : psw,
            "pin" : "",
            "target" : "",
        }
        data = urlencode(args)
        hds = {
                "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8"
            }
        hds.update(self.headers)
        r = requests.post(
            self.CV_URL + "/auth-p7/app/default/AuthApi4.php?a=aLoginPwd",
            data=data,
            headers = hds
            )
        return r if (r.status_code != 404) else self.Login(usr,psw)
        
    def getAuleVirtuali(self):
        pag_aule = requests.get(
            self.CV_URL+ "/cvp/app/default/sva_aule.php",
            headers = self.headers
            )
        return re.findall(r"aula_id\=\"(.*?)\"\>Entra",pag_aule.text)

    def getMessaggi(self,aulaid,idlast): #Ogni 60 secondi
        data = urlencode({
            "aula_id": aulaid,
            "mpp" : 50,
            "last_id" : idlast,
            "cerca" :"",
            })
        
        hds = dict({
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            },**self.headers)
        
        page_mess = requests.post(
            self.CV_URL + "/cvp/app/default/sva_liveforum.io.php?a=acGetMsgPag",
            headers = hds,
            data = data
        )
        
        return page_mess

    def setPresenza(self,aulaid): #Ogni 30 secondi
        data = urlencode({
            "aula_id": aulaid,
            })

        hds = dict({
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            },**self.headers)
        
        pres_resp = requests.post(
            self.CV_URL + "/cvp/app/default/sva_liveforum.io.php?a=acSetPresenza",
            headers = hds,
            data = data
        )
        
        if pres_resp.status_code == 200:
            bot.log(f"Segnato presente in aula {aulaid}")

    def getAgenda(self,data):
        args = {
            "stampa":":stampa:",
            "report_name":"",
            "tipo":"agenda",
            #"data":"08 03 20",
            #"autore_id":"",
            "tipo_export":"EVENTI_AGENDA_STUDENTI",
            "quad":":quad:",
            "materia_id":"",
            "classe_id":":classe_id:",
            "gruppo_id":":gruppo_id:",
            "ope":"RPT",
            "dal":data,
            "al":data,
            "formato" : "xls"
        }
        pag_agenda = requests.get(
            self.CV_URL + "/fml/app/default/xml_export.php?"+urlencode(args),
            headers = self.headers
        )
        #scarico l'xls
        with open("agend.xls","wb") as f:
            f.write(pag_agenda.content)
        return pag_agenda

    def log(self,msg):
        print("[{}] {}".format(str(time.time()-self.tinit)[:10], msg))

def getCredenziali():
    global FNAME
    if not os.path.isfile(FNAME):
        with open(FNAME,"w") as f:
            json.dump({
                "username" : str(input("Inserisci nome utente ClasseViva: ")),
                "password" : base64.b64encode(bytes(input("Inserisci password: ").encode('utf-8'))).decode("utf-8")
            },f)
    
    with open(FNAME,"r") as f:
        fl = json.load(f)
        fl["password"] = base64.b64decode(bytes(fl["password"].encode("utf-8"))).decode("utf-8") 
    
    return fl

if __name__ == "__main__":
    #pausa di 30 sec prima di ricontrollare i messaggi
    nSecPause = 30
    
    try:
        if len(sys.argv)==3:
            bot = CVBot(sys.argv[1],sys.argv[2])
        else:
            loginfos = getCredenziali()
            bot = CVBot(loginfos["username"],loginfos["password"])
        aulalista = bot.getAuleVirtuali()
        bot.log("Aule: " + ",".join(aulalista))
        aula = aulalista[0]
    except:
        print("Errore nella procedura di entrata nell'aula virtuale")
        exit()
    
    mlist = None
    mid_last = 0
    try:
        while True:
            try:
                res = bot.getMessaggi(aula,mid_last).json()
                bot.setPresenza(aula)
                if res != []:
                    mid_last = res["rows"][-1]["msg_id"]
                    if mlist is None or len(mlist["rows"]) != len(res["rows"]):
                        mlist = res
                        for msg in mlist["rows"]:
                            bot.log("Mittente: " + msg["sender"] + " ha detto " + msg["testo"] +" " + msg["date"])
                    else:
                        bot.log("No nuovi messaggi")
                else:
                    bot.log("No messaggi")
                bot.log(f"ReCheck Messaggi ogni {nSecPause*2} secondi.")
            except:
                bot.log("Errore nella lettura dei messaggi")
            
            time.sleep(nSecPause)
            bot.setPresenza(aula)
            time.sleep(nSecPause)
    except KeyboardInterrupt:
        print("Uscito dal Registro!")

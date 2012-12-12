# -*# -*- coding: iso8859-1 -*-
## -----------------------------------------------------
## Logik-Generator  V1.5
## -----------------------------------------------------
## Copyright © 2012, knx-user-forum e.V, All rights reserved.
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.de/documents/gpl-3.0.de.html>.

### USAGE:  python.exe LogikGenerator.py [--debug --en1=34 --en2="TEST"]



import sys
import codecs
import os
import base64 
import marshal
import re
try:
    from hashlib import md5
except ImportError:
    import md5 as md5old
    md5 = lambda x='': md5old.md5(x)
import inspect
import time
import socket
import tempfile
import zlib
import zipfile

##############
### Config ###
##############

## Name der Logik
LOGIKNAME="Buderus"
## Logik ID
LOGIKID="12264"

## Ordner im GLE
LOGIKCAT="www.knx-user-forum.de"


## Beschreibung
LOGIKDESC="""

"""
VERSION="V0.9"


## Bedingung wann die kompilierte Zeile ausgeführt werden soll
BEDINGUNG="EI"
## Formel die in den Zeitspeicher geschrieben werden soll
ZEITFORMEL=""
## Nummer des zu verwenden Zeitspeichers
ZEITSPEICHER="0"

## AUF True setzen um Binären Code zu erstellen
doByteCode=False
#doByteCode=True

## Base64Code über SN[x] cachen
doCache=False

## Doku erstellen Ja/Nein
doDoku=True

debug=False
livedebug=False

showList=False
#############################
########## Logik ############
#############################
LOGIK = '''# -*- coding: iso8859-1 -*-
## -----------------------------------------------------
## '''+ LOGIKNAME +'''   ### '''+VERSION+'''
##
## erstellt am: '''+time.strftime("%Y-%m-%d %H:%M")+'''
## -----------------------------------------------------
## Copyright © '''+ time.strftime("%Y") + ''', knx-user-forum e.V, All rights reserved.
##
## This program is free software; you can redistribute it and/or modify it under the terms
## of the GNU General Public License as published by the Free Software Foundation; either
## version 3 of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
## without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with this program;
## if not, see <http://www.gnu.de/documents/gpl-3.0.de.html>.

## -- ''' +re.sub("\n","\n## -- ",LOGIKDESC)+ ''' 

#5000|"Text"|Remanent(1/0)|Anz.Eingänge|.n.|Anzahl Ausgänge|.n.|.n.
#5001|Anzahl Eingänge|Ausgänge|Offset|Speicher|Berechnung bei Start
#5002|Index Eingang|Default Wert|0=numerisch 1=alphanummerisch
#5003|Speicher|Initwert|Remanent
#5004|ausgang|Initwert|runden binär (0/1)|typ (1-send/2-sbc)|0=numerisch 1=alphanummerisch
#5012|abbruch bei bed. (0/1)|bedingung|formel|zeit|pin-ausgang|pin-offset|pin-speicher|pin-neg.ausgang

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''_'''+VERSION+'''"|0|3|"E1 IP:Port"|"E2 config"|"E3 senden"|2|"A1 Daten"|"A2 SystemLog"

5001|3|2|0|1|1

# EN[x]
5002|1|"192.168.178.10:22"|1 #* IP:Port
5002|2|""|1 #* config
5002|3|""|1 #* Senden

# Speicher
5003|1||0 #* logic

# Ausgänge
5004|1|""|0|1|1 #* Daten
5004|2|""|0|1|1 #* SystemLog

#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
  global socket
  import socket
  class buderus_connect(object):
      def __init__(self,localvars):
          from hs_queue import Queue
          from hs_queue import hs_threading as threading
          import re
          self.id = "buderus_connect"
          
          self.logik = localvars["pItem"]
          self.MC = self.logik.MC
          
          EN = localvars['EN']
          self.device_connector = EN[1]
          
          ## Config
          self.config = {
              'debug': 0,
              'delaydirectendtime' : 1.0, # wartezeit beim beenden des directmodes
          }
          
          # 3964R Constants
          self._constants = {
              'STX': chr(0x02),
              'DLE': chr(0x10),
              'ETX': chr(0x03),
              'NAK': chr(0x15),
              'QVZ': 2,             # Quittungsverzugzeit (QVZ) 2 sec
              'ZVZ': 0.220,         # Der Abstand zwischen zwei Zeichen darf nicht mehr als die Zeichenverzugszeit (ZVZ) von 220 ms
              'BWZ': 4,             # Blockwartezeit von 4 sec
          }

          ## Gerätetypen
          self.device_types = {
              "80" : ("Heizkreis 1", 18),
              "81" : ("Heizkreis 2", 18),
              "82" : ("Heizkreis 3", 18),
              "83" : ("Heizkreis 4", 18),
              "84" : ("Warmwasser", 12),
              "85" : ("Strategie wandhängend", 12),
              "87" : ("Fehlerprotokoll", 42),
              "88" : ("bodenstehender Kessel", 42),
              "89" : ("Konfiguration", 24),
              "8A" : ("Heizkreis 5", 18),
              "8B" : ("Heizkreis 6", 18),
              "8C" : ("Heizkreis 7", 18),
              "8D" : ("Heizkreis 8", 18),
              "8E" : ("Heizkreis 9", 18),
              "8F" : ("Strategie bodenstehend", 30),
              "90" : ("LAP", 18),
              "92" : ("wandhängende Kessel 1", 60),
              "93" : ("wandhängende Kessel 2", 60),
              "94" : ("wandhängende Kessel 3", 60),
              "95" : ("wandhängende Kessel 4", 60),
              "96" : ("wandhängende Kessel 5", 60),
              "97" : ("wandhängende Kessel 6", 60),
              "98" : ("wandhängende Kessel 7", 60),
              "99" : ("wandhängende Kessel 8", 60),
              "9B" : ("Wärmemenge", 36),
              "9C" : ("Störmeldemodul", 6),
              "9D" : ("Unterstation", 6),
              "9E" : ("Solarfunktion", 54),
          }
          
          ## List für gefundene Geräte
          self.found_devices = []
          
          ## List die Geräte IDs enthällt bei denen Antworten ausstehen
          self.waiting_direct_bus = []
          
          ## threading Lock um _is_directmode und waiting_direct_bus zu beschreiben
          self.directmode_lock = threading.RLock()
          
          ## Derzeitiger Direct-mode status
          self._is_directmode = False
          
          ## Mit dem Kommando "0xA2 <ECOCAN-BUS-Adresse>" können die Monitordaten des ausgewählten 
          ## ECOCAN-BUS-Gerätes von der Kommunikationskarte ausgelesen werden. 
          ## Mit Hilfe des Kommandos "0xB0 <ECOCAN-BUS-Adresse>" gefolgt von einem entsprechenden 
          ## Datenblock können im Direkt-Modus einstellbare Parameter die für ein Regelgerät bestimmt sind an die 
          ## Schnittstelle geschickt werden. Die Schnittstelle schickt diese Daten dann weiter an das entsprechende 
          ## Regelgerät. 
          self.directmode_regex = re.compile("(?P<id>A2|B0)(?P<busnr>[0-9a-fA-F]{2})")


          ## Im "Normal-Modus" werden die Monitordaten nach folgendem Muster übertragen: 
          ## 0xA7 <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <DATUM> 
          ## 0xA7 = Kennung für einzelne Monitordaten 
          ## ECOCAN-BUS-Adresse = Herkunft´s Adresse des Monitordatum´s (hier Regelgeräteadresse) 
          ## TYP = Typ der empfangenen Monitordaten       
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s 
          ## DATUM = eigentlicher Messwert 

          ## Im "Direct-Modus" werden die Monitordaten nach folgendem Muster übertragen: 
          ## 0xAB <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <6 Daten-Byte> 
          ## 0xAB = Kennung für Monitordaten 
          ## ECOCAN-BUS-Adresse = die abgefragte Adresse zur Bestätigung 
          ## TYP = Typ der gesendeten Monitordaten
          ## Daten unter dem entsprechenden Typ werden nur gesendet wenn auch die entsprechende Funktionalität 
          ## im Regelgerät eingebaut ist. 
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s

          self.payload_regex = re.compile("(?P<id>AB|A7)(?P<busnr>[0-9a-fA-F]{2})(?P<type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{2})+)")

          ## Als Endekennung für das abgefragte Regelgerät oder falls keine Daten vorhanden sind, wird der 
          ## nachfolgende String 
          ## 0xAC <ECOCAN-BUS-Adresse> gesendet          
          self.directmode_finish_regex = re.compile("AC(?P<busnr>[0-9a-fA-F]{2})")
          
          self._moxa_thread = None
          
          ## Socket zum MOXA
          self.sock = None
          
          ## threading Lock für exklusives schreiben von entweder der Empfangs- oder Sende- Funktion
          self._buderus_data_lock = threading.RLock()

          ## Queue für Nachrichten zu den Ausgängen des Bausteins
          self._hs_message_queue = Queue()
          self._buderus_message_queue = Queue()

          ## Konfig an Eingang 2 parsen
          self.readconfig(EN[2])
          
          ## Consumer Thread der Nachrichten an die Ausgänge des Bausteins schickt
          self.hs_queue_thread = threading.Thread(target=self._send_to_hs_consumer,name='buderus_hs_consumer')
          self.hs_queue_thread.start()

          ## Consumer Thread der Nachrichten an das Buderus Gerät schickt
          self.buderus_queue_thread = threading.Thread(target=self._send_to_buderus_consumer,name='hs_buderus_consumer')
          self.buderus_queue_thread.start()

          ## jetzt zum MOXA verbinden
          self.connect()

      def readconfig(self,configstring):
          ## config einlesen
          import re
          for (option,value) in re.findall("(\w+)=(.*?)(?:\*|$)", configstring ):
              option = option.lower()
              _configoption = self.config.get(option)
              _configtype = type(_configoption)
              
              ## wenn es den Wert nicht gibt
              if _configtype == type(None):
                  self.log("unbekannte Konfig Option %s=%s" % (option,value) )
                  continue
              
              ## versuchen Wert im config string zum richtigen Type zu machen
              try:
                  _val = _configtype(value)
                  self.config[option] = _val
              except ValueError:
                  self.log("falscher Wert bei Konfig Option %s=%s (erwartet %r)" % (option,value, _configtype ) )
                  pass


      def debug(self,msg,lvl=5):
          ## wenn debuglevel zu klein gleich zurück
          if self.config.get("debug") < lvl:
              return
          import time
          
          ## FIXME sollte später gesetzt werden
          #self.log(msg,severity='debug')
          
          print "%s DEBUG: %r" % (time.strftime("%H:%M:%S"),msg,)

      def connect(self):
          ## _connect als Thread starten
          from hs_queue import hs_threading as threading
          self._moxa_thread = threading.Thread(target=self._connect,name='Buderus-Moxa-Connect')
          self._moxa_thread.start()

      def _send_to_buderus_consumer(self):
          import select,time
          while True:
              ## wenn noch keine Verbindung 
              if not self.sock:
                  self.debug("Socket nicht bereit ... warten")
                  ## 1 Sekunden auf Socket warten
                  time.sleep(1)
                  continue
              
              ## nächste payload aus der Queue holen
              msg = self._buderus_message_queue.get()

              ## nach gültigen zu sendener payload suchen
              _direct_mode = self.directmode_regex.search(msg)

              ## wenn keine gültige SENDE payload
              if not _direct_mode:
                  self.debug("ungültige sende Nachricht %r" % (msg,) )
                  continue
              
              _cmdid = _direct_mode.group("id")
              _busnr = _direct_mode.group("busnr")
              
              ## Wenn eine direct-mode anfrage
              if _cmdid == "A2":
                  if _busnr not in self.waiting_direct_bus:
                      ## busnr zur liste auf Antwort wartender hinzu
                      self.add_direct_waiting(_busnr)
                  else:
                      ## Bus wird schon abgefragt
                      continue

              self._buderus_data_lock.acquire()
              self.debug("sende Queue exklusiv lock erhalten")
              try:
                  ## wenn wir nicht auf den directmode schalten konnten
                  if not self.set_directmode(True):
                      ## payload verworfen und loop
                      continue
                  
                  ## payload per 3964R versenden
                  self._send3964r(msg)
                  
                  ## gucken ob wir den directmode noch brauchen
                  self.check_directmode_needed()
              finally:
                  self._buderus_data_lock.release()
                  self.debug("sende Queue exklusiv lock released")


      def add_direct_waiting(self,busnr):
          ## busnr zur liste zu erwartender Antworten hinzufügen
          try:
              self.directmode_lock.acquire()
              self.waiting_direct_bus.append(busnr)
          finally:
              self.directmode_lock.release()

      def remove_direct_waiting(self,busnr=None):
          ## busnr von der Liste der zu erwartetenden Antworten entfernen
          try:
              self.directmode_lock.acquire()
              
              ## wenn keine busnr übergeben wurde, dann alle entfernen
              if not busnr:
                  ## Flush
                  self.waiting_direct_bus =[]
                  self._is_directmode = False
              
              ## wenn die zu entfernenden busnr in der liste ist, entfernen
              elif busnr in self.waiting_direct_bus:
                  self.waiting_direct_bus.remove(busnr)
          finally:
              self.directmode_lock.release()

      def get_direct_waiting(self):
          ## threadsicheres abfragen der zu erwartenden Antworten
          try:
              self.directmode_lock.acquire()
              return self.waiting_direct_bus
          finally:
              self.directmode_lock.release()

      def is_directmode(self):
          ## threadsicheres abfragen von directmode
          try:
              self.directmode_lock.acquire()
              return self._is_directmode
          finally:
              self.directmode_lock.release()
          
      def check_directmode_needed(self):
          import time
          ## Die Abfrage der gesamten Monitordaten braucht nur zu Beginn oder nach einem Reset zu erfolgen. 
          ## Nach erfolgter Abfrage der Monitordaten sollte wieder mit dem Kommando 0xDC in den "Normal-Modus" 
          ## zurückgeschaltet werden. 
          
          ## wenn direct mode nicht an ist dann gleich zurück
          if not self.is_directmode():
              return
          
          ## wenn die Sendewarteschlange leer ist und keine Antworten(AC<busnr>) mehr von einem A2<busnr> erwartet werden dann directmode aus
          if self._buderus_message_queue.empty() and not self.get_direct_waiting():
              time.sleep( self.config.get('delaydirectendtime') )
              self.set_directmode(False)

      def set_directmode(self,mode):
          ## Bei dem Kommunikationsmodul wird zwischen einem "Normal-Modus" und einem "Direkt-Modus"
          ## unterschieden. 
          ## "Normal-Modus" Bei diesem Modus werden laufend alle sich ändernden Monitorwerte 
          ## sowie Fehlermeldungen übertragen. 
          ## "Direkt-Modus" Bei diesem Modus kann der aktuelle Stand aller bisher vom Regelgerät 
          ## generierten Monitordaten en Block abgefragt und ausgelesen werden. 
          ## Mittels des Kommandos 0xDD kann von "Normal-Modus" in den "Direkt-Modus" umgeschaltet werden. 
          ## In diesem Modus kann auf alle am ECOCAN-BUS angeschlossenen Geräte zugegriffen und es können 
          ## geräteweise die Monitorwerte ausgelesen werden. 
          import time
          _setmode = "DC"
          if mode:
              _setmode = "DD"
          try:
              self.directmode_lock.acquire()
              _loop = 0
              ## FIXME: keine Ahnung ob wir das öfter als einmal versuchen oder nicht
              while not self._is_directmode == mode:
                  if _loop == 2:
                      break
                  
                  
                  # wenn der rückgabewert vom Senden dem erwarteten mode erfolgreich ist, dann mode
                  if self._send3964r(_setmode):
                      self._is_directmode = mode
                  else:
                      self._is_directmode = not mode
                  
                  ## wenn kein erfolg dann 1 sekunde warten
                  time.sleep(1)
                  
                  _loop += 1
              
              return (self._is_directmode == mode)
          finally:
              self.directmode_lock.release()
        
      def _send3964r(self,payload):
          ## returnwert erstmal auf False
          _ret = False
          try:
              ## auf Freigabe STX/DLE vom Socket warten
              if self.wait_for_ready_to_receive():
                  
                  ## Payload jetzt senden
                  self.debug("jetzt payload %r senden" % (payload,) )
                  self.send_payload(payload)
                  
                  ## ertrunwert auf True
                  _ret = True
              else:
                  ## wenn kein DLE auf unser STX kam dann payload verwerfen
                  self.debug("payload %r verworfen" % (payload,) )
          
          except:
              ## Fehler auf die HS Debugseite
              self.MC.Debug.setErr(sys.exc_info(),"%r" % (payload,))
          return _ret

      def _send_to_hs_consumer(self):
          while True:
              (out,msg) = self._hs_message_queue.get()
              ## Auf iKO's schreiben
              for iko in self.logik.Ausgang[out][1]:
                  try:
                      ## Logik Lock im HS sperren
                      self.MC.LogikList.calcLock.acquire()
                      
                      ## Wert im iKO beschreiben
                      iko.setWert(out,msg)
                      
                      ## Logik Lock im HS freigeben
                      self.MC.LogikList.calcLock.release()
                      
                      iko.checkLogik(out)
                  except:
                      self.MC.Debug.setErr(sys.exc_info(),"%r" % msg)

      def send_to_output(self,out,msg):
          ## werte fangen bei 0 an also AN[1] == Ausgang[0]#
          out -= 1
          self._hs_message_queue.put((out,msg))

      def log(self,msg,severity='info'):
          import time
          try:
              from hashlib import md5
          except ImportError:
              import md5 as md5old
              md5 = lambda x,md5old=md5old: md5old.md5(x)
          
          _msg_uid = md5( "%s%s" % ( self.id, time.time() ) ).hexdigest()
          _msg = '<log><id>%s</id><facility>buderus</facility><severity>%s</severity><message>%s</message></log>' % (_msg_uid,severity,msg)
          
          self.send_to_output( 2, _msg )

      def incomming(self,msg):
          self.debug("incomming message %r" % msg)
          ## mit * getrennte messages hinzufügen
          for _msg in msg.split("*"):

              ## leerzeichen entfernen 
              _msg = _msg.replace(' ','')

              ## _msg in die sende Warteschlange
              self._buderus_message_queue.put( _msg )

      def parse_device_type(self,payload):
          ## nach gültiger payload suchen
          _payload = self.payload_regex.search(payload)
          
          ## wenn normal-mode oder direct mode antwort 
          if _payload:
              
              ## wenn einen normal mode antwort mit Typ A7 kommt und der direktmode lokal an ist, 
              ## dann ist der 60 Sekunden Timeout abgelaufen ohne die Daten rechtzeitig erhalten zu haben
              if _payload.group("id") == "A7" and self.is_directmode():
                  self.remove_direct_waiting()
                  ## Der "Direkt-Modus" kann durch das Kommando 0xDC wieder verlassen werden. 
                  ## Außerdem wird vom "Direkt-Modus" automatisch in den "Normal-Modus" zurückgeschaltet, wenn für die 
                  ## Zeit von 60 sec kein Protokoll des "Direkt-Modus" mehr gesendet wird. 
                  self.log("Directmode timeout")
              
              ## Gerätetype
              _type = _payload.group("type")
              
              ## wenn wir das Gerät noch nicht gefunden hatten kurze Info über den Fund loggen
              if _type not in self.found_devices:
                  self.found_devices.append( _type )
                  (_devicename, _datalen) = self.device_types.get( _type, ("unbekanntes Gerät (%s)" % _type, 0) )
                  self.log("Gerät %r an ECOCAN %s gefunden" % ( _devicename, _payload.group("busnr") ) , severity="info")
              
              return
          
          ## wenn ein AC<busnr> empfangen wurde die busnr aus der liste für direct Daten entfernen und evtl direct_mode beenden
          _direct = self.directmode_finish_regex.search(payload)
          if _direct:
              _busnr = _direct.group("busnr")
              
              ## bus von der liste auf antwort wartender im direct mode entfernen
              self.remove_direct_waiting(_busnr)

      def wait_for_ready_to_receive(self):
          import time
          ## 3 versuche warten bis wir auf ein STX ein DLE erhalten
          for _loop in xrange(3):
              ## STX senden
              self.debug("STX senden")
              self.sock.send( self._constants['STX'] )
              self.debug("STX gesendet / warten auf DLE")
              
              ## auf daten warten, timeout ist QVZ
              _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['QVZ'] )
              
              ## wenn kein timeout QVZ
              if self.sock in _r:
                  # 1 Zeichen lesen
                  data = self.sock.recv(1)
                  ## wenn wir ein DLE empfangen
                  if data == self._constants['DLE']:
                      self.debug("DLE empfangen")
                      
                      ## erfolg zurück
                      return True
                  
                  ## Wenn wir beim warten auf ein DLE ein STX der Gegenseite erhalten stellen wir unsere Sendung zurück und lassen das andere Gerät seine Daten erstmal senden
                  elif data == self._constants['STX']:
                      self.debug("STX empfangen Initialisierungskonflikt")
                      time.sleep(self._constants['ZVZ'])
                      ## DLE senden, dass wir Daten vom anderen Gerät akzeptieren senden
                      self.sock.send( self._constants['DLE'] )
                      self.debug("DLE gesendet")
                      
                      ## eigentlich Funktion aus dem connect zum lesen der payload hier ausführen
                      self.read_payload()
                      
                      ### danach loop und erneuter sende Versuch
                  else:
                      self.debug("%r empfangen" % (data,) )
                      
          self.debug("Nach 3x STX senden innerhalb QVZ kein DLE")
          return False
        

      ## Verbindung zum Moxa (gethreadet)
      def _connect(self):
          import time,socket,sys,select
          try:
              
              ## TCP Socket erstellen
              self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              
              ## IP:Port auslesen und dorthin verbinden
              try:
                  _ip,_port = self.device_connector.split(":")
                  self.sock.connect( ( _ip, int(_port) ) )
                  self.debug("connect zu moxa an %s:%s" % (_ip,_port))
              except (TypeError,ValueError):
                  self.log("ungültige IP:Port Kombination %r an Eingang 1" % self.device_connector, severity="error")
                  return
              
              while True:
                  # wenn keine Verbindung dann abbruch
                  if not self.sock:
                      break
                  _r,_w,_e = select.select( [ self.sock ],[],[], 10 )
                  
                  ## exklusiv lock
                  if not self._buderus_data_lock.acquire(blocking=False):
                      ## wenn nicht erhalten lesen wir nicht vom socket, da die Daten für die Sende Queue sind
                      continue
                  
                  self.debug("empfang exklusiv lock erhalten")
                  try:
                      ## wenn kein Timeout
                      if self.sock in _r:
                          ## wenn Daten da sind, ein zeichen lesen
                          data = self.sock.recv(1)
                          
                          ## wenn keine Daten trotz select dann Verbindung abgebrochen
                          if not data:
                              self.debug("Verbindung abgebrochen")
                              break
                          
                          ## wenn wir ein STX empfangen
                          if data == self._constants['STX']:
                              self.debug("STX empfangen sende DLE")
                              ## senden wir das DLE
                              self.sock.send( self._constants['DLE'] )
                              self.debug("DLE gesendet")
                              
                              ## jetzt die eigentliche payload vom socket lesen
                              self.read_payload()
                          else:
                              self.debug("ungültiges Zeichen %r empfangen" % (data,) ,lvl=4)
                          
                      ## Testen ob der directmode noch gesetzt ist, und evtl ausschalten
                      self.check_directmode_needed()
                  
                  finally:
                      ## den lock auf jedenfall relasen
                      self._buderus_data_lock.release()
                      self.debug("empfang exklusiv lock releasen")
                      

          except:
              ## fehler auf die HS Debugseite
              self.MC.Debug.setErr(sys.exc_info(),"")
              ## 10 sekunden pause
              time.sleep(10)
          
          ## dann reconnect
          self.connect()

      ## STX = 0x02
      ## DLE = 0x10
      ## ETX = 0x03
      ## NAK = 0x15
      ## Die Steuerzeichen für die Prozedur 3964R sind der Norm DIN 66003 für den 7-Bit-Code entnommen. Sie
      ## werden allerdings mit der Zeichenlänge 8 Bit übertragen (Bit I7 = 0). Am Ende jedes Datenblocks wird zur
      ## Datensicherung ein Prüfzeichen(BCC) gesendet.
      ## Das Blockprüfzeichen wird durch eine exklusiv-oder-Verknüpfung über alle Datenbytes der
      ## Nutzinformation, inclusive der Endekennung DLE, ETX gebildet.

      def send_payload(self,payload):
          ## Senden mit der Prozedur 3964R
          ## -----------------------------
          ## Zum Aufbau der Verbindung sendet die Prozedur 3964R das Steuerzeichen STX aus. Antwortet das
          ## Peripheriegerät vor Ablauf der Quittungsverzugzeit (QVZ) von 2 sec mit dem Zeichen DLE, so geht die
          ## Prozedur in den Sendebetrieb über. Antwortet das Peripheriegerät mit NAK, einem beliebigen anderen
          ## Zeichen (außer DLE) oder die Quittungsverzugszeit verstreicht ohne Reaktion, so ist der
          ## Verbindungsaufbau gescheitert. Nach insgesamt drei vergeblichen Versuchen bricht die Prozedur das
          ## Verfahren ab und meldet dem Interpreter den Fehler im Verbindungsaufbau.
          ## Gelingt der Verbindungsaufbau, so werden nun die im aktuellen Ausgabepuffer enthaltenen
          ## Nutzinformationszeichen mit der gewählten Übertragungsgeschwindigkeit an das Peripheriegerät
          ## gesendet. Das Peripheriegerät soll die ankommenden Zeichen in Ihrem zeitlichen Abstand überwachen.
          ## Der Abstand zwischen zwei Zeichen darf nicht mehr als die Zeichenverzugszeit (ZVZ) von 220 ms
          ## betragen.
          ## Jedes im Puffer vorgefundene Zeichen DLE wird als zwei Zeichen DLE gesendet. Dabei wird das Zeichen
          ## DLE zweimal in die Prüfsumme übernommen.
          ## Nach erfolgtem senden des Pufferinhalts fügt die Prozedur die Zeichen DLE, ETX und BCC als
          ## Endekennung an und wartet auf ein Quittungszeichen. Sendet das Peripheriegerät innerhalb der
          ## Quittungsverzugszeit QVZ das Zeichen DLE, so wurde der Datenblock fehlerfrei übernommen. Antwortet
          ## das Peripheriegerät mit NAK, einem beliebigen anderen Zeichen (außer DLE), einem gestörten Zeichen
          ## oder die Quittungsverzugszeit verstreicht ohne Reaktion, so wiederholt die Prozedur das Senden des
          ## Datenblocks. Nach insgesamt sechs vergeblichen Versuchen, den Datenblock zu senden, bricht die
          ## Prozedur das Verfahren ab und meldet dem Interpreter den Fehler im Verbindungsaufbau.
          ## Sendet das Peripheriegerät während einer laufenden Sendung das Zeichen NAK, so beendet die
          ## Prozedur den Block und wiederholt in der oben beschriebenen Weise.
          import select,binascii
          ## 6 versuche
          for _loop in xrange(6):
              self.debug("exklusiv senden / versuch %d" % _loop)
              
              ## checksumme
              _bcc = 0
              for _byte in binascii.unhexlify(payload):
                  
                  ## Byte an Gerät schicken
                  self.sock.send( _byte )
                  self.debug("Byte %r versendet" % binascii.hexlify(_byte))
                  
                  ## Checksumme berechnen
                  _bcc ^= ord(_byte)
                  
                  ## Wenn payload ein DLE ist
                  if _byte == self._constants['DLE']:

                      ## dann in der payload verdoppeln
                      self.sock.send( _byte )
                      self.debug("Payload enthällt DLE, ersetzt mit DLE DLE" ) 

                      ## doppeltes DLE auch in die Checksumme einrechenen
                      _bcc ^= ord(_byte)
              
              ## Abschluss der Prozedur 3964R durch senden von DLE ETX
              self.debug("Alle Daten gesendet, jetzt DLE und ETX")
              
              self.sock.send( self._constants['DLE'] )
              _bcc ^= ord( self._constants['DLE'] )
              
              self.sock.send( self._constants['ETX'] )
              _bcc ^= ord( self._constants['ETX'] )
              
              ## Berechnete Checksukmme
              self.debug("jetzt checksumme %r senden" % (_bcc) )
              self.sock.send( chr(_bcc) )

              ## auf daten warten, timeout ist Quittungsverzugszeit
              self.debug("warten auf DLE")
              _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['QVZ'] )
              
              ## wenn nicht Quittingsverzugszeit
              if self.sock in _r:
                  
                  ## 1 zeichen lesen
                  data = self.sock.recv(1)
                  
                  ## wenn empfangenes zeichen DLE ist
                  if data == self._constants['DLE']:
                      self.debug("DLE erhalten")
                      self.debug("Daten %r erfolgreich gesendet" % (payload,),lvl=2)
                      return True
              self.debug("Kein DLE erhalten loop")
          self.debug("Nach 6x STX senden innerhalb QVZ kein DLE",lvl=1)


      def read_payload(self):
          ## Empfangen mit der Prozedur 3964R
          ## --------------------------------
          ## Im Ruhezustand, wenn kein Sendeauftrag und kein Warteauftrag des Interpreters zu bearbeiten ist, wartet
          ## die Prozedur auf den Verbindungsaufbau durch das Peripheriegerät. Empfängt die Prozedur ein STX und
          ## steht ihr ein leerer Eingabepuffer zur Verfügung, wird mit DLE geantwortet.
          ## Nachfolgende Empfangszeichen werden nun in dem Eingabepuffer abgelegt. Werden zwei aufeinander
          ## folgende Zeichen DLE empfangen, wird nur ein DLE in den Eingabepuffer übernommen.
          ## Nach jedem Empfangszeichen wird während der Zeichenverzugszeit (ZVZ) auf das nächste Zeichen
          ## gewartet. Verstreicht die Zeichenverzugszeit ohne Empfang, wird das Zeichen NAK an das
          ## Peripheriegerät gesendet und der Fehler an den Interpreter gemeldet.
          ## Mit erkennen der Zeichenfolge DLE, ETX und BCC beendet die Prozedur den Empfang und sendet DLE
          ## für einen fehlerfrei (oder NAK für einen fehlerhaft) empfangenen Block an das Peripheriegerät.
          ## Treten während des Empfangs Übertragungsfehler auf (verlorenes Zeichen, Rahmenfehler), wird der
          ## Empfang bis zum Verbindungsabbau weitergeführt und NAK an das Peripheriegerät gesendet. Dann wird
          ## eine Wiederholung des Blocks erwartet. Kann der Block auch nach insgesamt sechs Versuchen nicht
          ## fehlerfrei empfangen werden, oder wird die Wiederholung vom Peripheriegerät nicht innerhalb der
          ## Blockwartezeit von 4 sec gestartet, bricht die Prozedur 3964R den Empfang ab und meldet den Fehler an
          ## den Interpreter.
          import select,binascii,time
          ## 6 versuche sind erlaubt
          for _loop in xrange(6):
              self.debug("exklusiv lesen / versuch %d" % _loop)
              
              ## speicher für das zuletzt empfangene zeichen um DLE DLE bzw DLE ETX zu erkennen
              _lastchar = ""
              
              ## checksumme
              _bcc = 0
              
              ## eigentliche Payload
              _payload = []
              
              ## nach erhalten von DLE ETX (Ende der Übermittlung) wird auf True gesetzt, somit ist das nächste Zeichen die gesendetet Checksumme
              _wait_for_checksum = False
              
              ## Timer für die Blockwartezeit
              _bwz_timer = time.time() + self._constants['BWZ']
              
              while True:
                  ## auf dem socket auf Veränderung warten
                  _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['ZVZ'] )
                  
                  ## wenn obiger select mit Timeout von Zeichenverzugszeit 
                  if not self.sock in _r:
                      
                      ## wenn schon Daten da nur zeichenverzugszeit/ wenn keine Daten dann Blockwartezeit
                      if len(_payload) > 0 or _bwz_timer <= time.time():
                          ## kein zeichen innerhalb ZVZ bzw BWZ
                          self.debug("abbruch ZVZ oder BWZ",lvl=1)
                          
                          ## NAK an Gerät senden
                          self.sock.send( self._constants['NAK'] )
                          
                          ## gegenseite zeit geben
                          time.sleep( self._constants['ZVZ'] )
                          
                          ## abruck der while Schleife zurück in connect
                          break
                      ## wenn noch keine daten und blockwartezeit nicht überschritten
                      else:
                          self.debug("weiter warten auf daten noch kein ZVZ/BWZ timeout")
                          continue
                  ## ein Zeichen lesen
                  data = self.sock.recv(1)

                  ## wenn keine Daten auf Socket (Verbindungsabbruch)
                  if not data:
                      self.debug("Keine Daten / verbindung verloren")
                      return

                  ## wenn checksumme erwartet wird
                  if _wait_for_checksum:
                      
                      ## empfangene Checksumme
                      _bcc_recv = ord(data)
                      self.debug("berechnete checksumme = %.2x empfange checksumme = %.2x" % ( _bcc,_bcc_recv) )
                      
                      ## wenn empfangene Checkumme der berechneten entspricht
                      if _bcc == _bcc_recv:
                          
                          ## payload von Type List zum String machen und alle hex Zeichen als Großbuchstaben
                          _hexpayload = "".join( _payload ).upper()
                          self.debug("Payload %r erfolgreich empfangen" % (_hexpayload),lvl=2)

                          ## DLE als Bestätigung senden
                          self.sock.send( self._constants['DLE'] )
                          
                          ## empfangene Payload analysieren
                          self.parse_device_type( _hexpayload )
                          
                          ## payload an Ausgang 1 senden
                          self.send_to_output(1, _hexpayload)
                          
                          return
                      
                      ## checksummen stimmen nicht überein
                      else:
                          self.debug("Checksum nicht korrekt %r != %r" % (_bcc, _bcc_recv) ,lvl=1)
                          
                          ## NAK an gerät senden
                          self.sock.send( self._constants['NAK'] )

                          ## FIXME BREAK heißt nochmal in die 6 versuche oder return wäre zurück zum mainloop warten auf STX
                          break
                  
                  ## checksum von jedem packet berechnen
                  _bcc ^= ord(data)

                  ## wenn 2mal DLE hintereinander bcc berechnen aber nur eins zum packet
                  if data == _lastchar == self._constants['DLE']:
                      self.debug("entferne doppeltes DLE")
                      
                      ## löschen damit bei DLE DLE DLE ETX nicht das 3te DLE auch wieder entfernt wird
                      _lastchar = ""
                      continue
                  
                  ## WENN DLE ETX dann Ende
                  if _lastchar == self._constants['DLE'] and data ==  self._constants['ETX']:
                      self.debug("DLE/ETX empfangen warte auf checksumme")
                      _wait_for_checksum = True
                      
                      ## letztes DLE entfernen denn das gehört nicht zur payload sondern zum 3964R
                      _payload = _payload[:-1]
                      continue
                      
                  ## daten zum packet hinzu
                  _payload.append( binascii.hexlify(data) )
                  self.debug("Daten %r empfangen" % (binascii.hexlify(data)),lvl=3)
                  
                  ## letztes zeichen speichern
                  _lastchar = data

"""])

debugcode = """

"""
postlogik=[0,"",r"""

5012|0|"EI"|"buderus_connect(locals())"|""|0|0|1|0
5012|0|"EC[3]"|"SN[1].incomming(EN[3])"|""|0|0|0|0

"""]

####################################################################################################################################################

###################################################
############## Interne Funktionen #################
###################################################

LGVersion="1.5"

livehost=""
liveport=0
doSend=False
noexec=False
nosource=False
doZip=False
for option in sys.argv:
    if option.find("--new")==0:
        try:
            LOGIKID=int(option.split("=")[1].split(":")[0])
            LOGIKNAME=option.split("=")[1].split(":")[1]
            try: 
                LOGIKCAT=option.split("=")[1].split(":")[2]
            except:
                pass
        except:
            print "--new=id:name[:cat]"
            raise
            sys.exit(1)

        if LOGIKID >99999 or LOGIKID == 0:
            print "invalid Logik-ID"
            sys.exit(1)

        if LOGIKID <10000:
            LOGIKID+=10000
        LOGIKID="%05d" % LOGIKID
        f=open(inspect.currentframe().f_code.co_filename,'r')
        data=""
        while True: 
            line = f.readline()
            if line.find("LOGIKID=") == 0:
                line = "LOGIKID=\""+LOGIKID+"\"\n"
            if line.find("LOGIKNAME=") == 0:
                line = "LOGIKNAME=\""+LOGIKNAME+"\"\n"
            if line.find("LOGIKCAT=") == 0:
                line = "LOGIKCAT=\""+LOGIKCAT+"\"\n"
            data += line
            if not line: 
                break 
        f.close()
        open(str(LOGIKID)+"_"+LOGIKNAME+".py",'w').write(data)
        sys.exit(0)

    if option=="--list":
        showList=True
      
    if option=="--debug":
        debug=True

    if option=="--noexec":
        noexec=True

    if option=="--nosource":
        nosource=True    

    if option=="--zip":
        doZip=True

    if option=="--nocache":
        doCache=False
      
    if option.find("--live")==0:
        livedebug=True
        debug=True
        doByteCode=False
        doCache=True
        try:
            livehost=option.split("=")[1].split(":")[0]
            liveport=int(option.split("=")[1].split(":")[1])
        except:
            print "--live=host:port"

    if option.find("--send")==0:
        doSend=True
        try:
            livehost=option.split("=")[1].split(":")[0]
            liveport=int(option.split("=")[1].split(":")[1])
        except:
            print "--send=host:port"
          

print "HOST: "+livehost+" Port:" +str(liveport)
### DEBUG ####
EI=True
EA=[]
EC=[]
EN=[]
SA=[]
SC=[]
SN=[]
AA=[]
AC=[]
AN=[]
OC=[]
ON=[]
if debug or doSend:
    EA.append(0)
    EC.append(False)
    EN.append(0)
    AA.append(0)
    AC.append(False)
    AN.append(0)
    SA.append(0)
    SC.append(False)
    SN.append(0)
    ON.append(0)
    OC.append(False)

    ## Initialisieren ##
    for logikLine in LOGIK.split("\n"):
        if logikLine.find("5001") == 0:
            for i in (range(0,int(logikLine.split("|")[3]))):
              ON.append(0)
              OC.append(False)
        if logikLine.find("5002") == 0:
            EN.append(logikLine.split("|")[2].replace('\x22',''))
            EA.append(logikLine.split("|")[2])
            EC.append(False)
        if logikLine.find("5003") == 0:
            if logikLine.split("|")[3][0] == "1":
                SN.append(re.sub('"','',logikLine.split("|")[2]))
            else:
                try:
                    SN.append(int(logikLine.split("|")[2]))
                except:
                    pass
                    SN.append(logikLine.split("|")[2])
            SA.append(logikLine.split("|")[2])
            SC.append(False)
        if logikLine.find("5004") == 0:
            AN.append(logikLine.split("|")[2])
            AA.append(logikLine.split("|")[2])
            AC.append(False)


def bool2Name(b):
  if int(b)==1:
    return "Ja"
  else:
    return "Nein"
def sbc2Name(b):
  if int(b)==1:
    return "Send"
  else:
    return "Send By Change"


def addInputDoku(num,init,desc):
  return '<tr><td class="log_e1">Eingang '+str(num)+'</td><td class="log_e2">'+str(init)+'</td><td class="log_e3">'+str(desc)+'</td></tr>\n'
def addOutputDoku(num,sbc,init,desc):
  return '<tr><td class="log_a1">Ausgang '+str(num)+' ('+sbc2Name(sbc)+')</td><td class="log_a2">'+str(init)+'</td><td class="log_a3">'+str(desc)+'</td></tr>\n'

LOGIKINHTM=""
LOGIKOUTHTM=""

i=0
LEXPDEFINELINE=LHSDEFINELINE=LINDEFINELINE=LSPDEFINELINE=LOUTDEFINELINE=0
for logikLine in LOGIK.split("\n"):
    if logikLine.find("5000") == 0:
        LEXPDEFINELINE=i
        LOGIKREMANT=bool2Name(logikLine.split("|")[2])
        LOGIKDEF=logikLine
    if logikLine.find("5001") == 0:
        LHSDEFINELINE=i
        ANZIN=int(logikLine.split("|")[1])
        ANZOUT=int(logikLine.split("|")[2])
        ANZSP=int(logikLine.split("|")[4])
        CALCSTARTBOOL=logikLine.split("|")[5]
        CALCSTART=bool2Name(CALCSTARTBOOL)
    if logikLine.find("5002") == 0:
        LINDEFINELINE=i
        desc=re.sub('"','',LOGIKDEF.split("|")[3+int(logikLine.split("|")[1])])
        if logikLine.find("#*") >0:
            desc=logikLine.split("#*")[1]
        LOGIKINHTM+=addInputDoku(logikLine.split("|")[1],logikLine.split("|")[2],desc)
    if logikLine.find("5003") == 0 or logikLine.find("# Speicher") == 0:
        LSPDEFINELINE=i
    if logikLine.find("5004") == 0:
        LOUTDEFINELINE=i
        desc=re.sub('"','',LOGIKDEF.split("|")[(4+ANZIN+int(logikLine.split("|")[1]))])
        if logikLine.find("#*") >0:
            desc=logikLine.split("#*")[1]
        LOGIKOUTHTM+=addOutputDoku(logikLine.split("|")[1],logikLine.split("|")[4],logikLine.split("|")[2],desc)
    i=i+1


if livedebug:
    EC.append(0)
    EN.append("")


sendVars=""

for option in sys.argv:
    if option.find("--sa") == 0:
        SA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="SA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--sn") == 0:
        SN[int(option[4:option.find("=")])]=option.split("=")[1]
        SC[int(option[4:option.find("=")])]=True
        sendVars+="SN["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        sendVars+="SC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--aa") == 0:
        AA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="AA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--an") == 0:
        AN[int(option[4:option.find("=")])]=option.split("=")[1]
        AC[int(option[4:option.find("=")])]=True
        sendVars+="AN["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1:]+"\n"
        sendVars+="AC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ea") == 0:
        EA[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="EA["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1:]+"\n"
    if option.find("--en") == 0:
        EN[int(option[4:option.find("=")])]="".join(option.split("=",1)[1])
        EC[int(option[4:option.find("=")])]=True
        sendVars+="EN["+str(int(option[4:option.find("=")]))+"]="+"".join(option.split("=")[1:])+"\n"
        sendVars+="EC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ec") == 0:
#        EC[int(option[4:option.find("=")])]=int(option.split("=")[1])
        sendVars+="EC["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        print sendVars
    if option.find("--sc") == 0:
#        EC[int(option[4:option.find("=")])]=int(option.split("=")[1])
        sendVars+="SC["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
        print sendVars
    if option.find("--on") == 0:
        ON[int(option[4:option.find("=")])]=option.split("=")[1]
        sendVars+="ON["+str(int(option[4:option.find("=")]))+"]="+option.split("=")[1]+"\n"
    if option.find("--oc") == 0:
        OC[int(option[4:option.find("=")])]=True
        sendVars+="OC["+str(int(option[4:option.find("=")]))+"]=1\n"
    if option.find("--ei") == 0:
        EI=(int(option.split("=")[1])==1)
        sendVars+="EI=1\n"
    if option.find("--run") == 0:
        sendVars+="eval(SN["+str(ANZSP+1)+"])\n"


def symbolize(LOGIK,code):
      symbols = {}
      for i in re.findall(r"(?m)^500([234])[|]([0-9]{1,}).*[@][@](.*)\s", LOGIK):
          varName=((i[0]=='2') and 'E') or ((i[0]=='3') and 'S') or ((i[0]=='4') and 'A')
          isunique=True
          try:
              type(symbols[i[2]])
              sym=i[2]
              isunique=False
          except KeyError:
              pass
          ## überprüft auch die alternativen Varianten
          if re.match("[ACN]",i[2][-1:]):
              try:
                  type(symbols[i[2][:-1]])
                  sym=i[2][:-1]
                  isunique=False
              except KeyError:
                  pass
          if isunique:
              symbols[i[2]]=[varName,"["+i[1]+"]"]
          else:
              print "Variablen Kollision :" +repr(i[2])+" ist in " +repr(symbols[sym]) + " und  "+ varName +"["+i[1]+"] vergeben"
              sys.exit(1)

      ## Symbole wieder entfernen
      LOGIK=re.sub("[@][@]\w+", "",LOGIK)

      #im Code tauschen
      for i in symbols.keys():
          code=[code[0],re.sub("[\@][\@]"+i+"([ACN])",symbols[i][0]+"\\1"+symbols[i][1],code[1]),re.sub("[\@][\@]"+i+"([ACN])",symbols[i][0]+"\\1"+symbols[i][1],code[2])]
          code=[code[0],re.sub("[\@][\@]"+i+"",symbols[i][0]+"N"+symbols[i][1],code[1]),re.sub("[\@][\@]"+i+"",symbols[i][0]+"N"+symbols[i][1],code[2])]
      return LOGIK,code

NCODE=[]
commentcode=[]
for codepart in code:
    NLOGIK,codepart=symbolize(LOGIK,codepart)

    NCODE.append(codepart)

    if codepart[0]==0 or codepart[0]==3:
        commentcode.append("##########################\n###### Quelltext: ########\n##########################"+"\n##".join(codepart[2].split("\n"))+"\n")
    #else:
    #    commentcode.append("#"+codepart[2].split("\n")[1]+"\n################################\n## Quelltext nicht Öffentlich ##\n################################")


NLOGIK,postlogik = symbolize(LOGIK,postlogik)
LOGIK=NLOGIK

code=NCODE

## Doku
doku = """
<html>
<head><title></title></head>
<link rel="stylesheet" href="style.css" type="text/css">
<body><div class="titel">"""+LOGIKNAME+"""</div>
<div class="nav"><A HREF="index.html">Hilfe</A> / <A HREF="logic.html">Logik</A> / """+LOGIKNAME+""" / <A HREF="#anker1">Eing&auml;nge</A> / <A HREF="#anker2">Ausg&auml;nge</A></div><div class="field0">Funktion</div>
<div class="field1">"""+re.sub("\r\n|\n","<br>",LOGIKDESC.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") )+"""</div>
<div class="field0">Eing&#228;nge</div>
<a name="anker1" /><table border="1" width="612" class="log_e" cellpadding="0" cellspacing="0">
<COL WIDTH=203><COL WIDTH=132><COL WIDTH=275>
<tr><td>Eingang</td><td>Init</td><td>Beschreibung</td></tr>
"""+LOGIKINHTM.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") +"""
</table>
<div class="field0">Ausg&#228;nge</div>
<a name="anker2" /><table border="1" width="612" class="log_a" cellpadding="0" cellspacing="0">
<COL WIDTH=203><COL WIDTH=132><COL WIDTH=275>
<tr><td>Ausgang</td><td>Init</td><td>Beschreibung</td></tr>
"""+LOGIKOUTHTM.decode("iso-8859-1").encode("ascii","xmlcharrefreplace") +"""
</table>
<div class="field0">Sonstiges</div>
<div class="field1">Neuberechnung beim Start: """+CALCSTART+"""<br />Baustein ist remanent: """+LOGIKREMANT+"""<br />Interne Bezeichnung: """+LOGIKID+"""<br />Der Baustein wird im "Experten" in der Kategorie '"""+LOGIKCAT+"""' einsortiert.<br /></div>
</body></html>

"""

if doDoku:
  open("log"+LOGIKID+".html",'w').write(doku)


LIVECODE="""
if EN["""+str(ANZIN+1)+"""].find("<id"""+LOGIKID+""">")!=-1:
    print "LivePort " +str(len(EN["""+str(ANZIN+1)+"""]))+ " Bytes erhalten"
    try:
        __LiveDebugCode_="".join(__import__('re').findall("(?i)<id"""+LOGIKID+""">(.*)</id"""+LOGIKID+""">",EN["""+str(ANZIN+1)+"""]))
        print "LiveDebug-Daten ID:"""+LOGIKID+" Name:"+LOGIKNAME+""" "
    except:
        pass
        print "Fehler Datenlesen"
        __LiveDebugCode_=''
    if __LiveDebugCode_.find("<inject>") != -1:
        SN["""+str(ANZSP+2)+"""]+="".join(__import__('re').findall("(?i)<inject>([A-Za-z0-9\\x2B\\x3D\\x2F]+?)</inject>", __LiveDebugCode_))
        print "Daten erhalten Buffer: " + str(len(SN["""+str(ANZSP+2)+"""]))
    elif  __LiveDebugCode_.find("<compile />") != -1:
        print "Compile"
        try:
            __LiveBase64Code_=__import__('base64').decodestring(SN["""+str(ANZSP+2)+"""])
            print __LiveBase64Code_
        except:
            pass
            print "Base64 Error"
            raise
        try:
            SN["""+str(ANZSP+1)+"""]=compile(__LiveBase64Code_,'<LiveDebug_"""+LOGIKID+""">','exec')
            SC["""+str(ANZSP+1)+"""]=1
            print "Running"
        except:
            pass
            SN["""+str(ANZSP+1)+"""]="0"
            SC["""+str(ANZSP+1)+"""]=1
            print "Compile Error"

        SN["""+str(ANZSP+2)+"""]=''
    elif __LiveDebugCode_.find("<vars>") == 0:
        print "Run Script"
        try:
            __LiveBase64Code_=__import__('base64').decodestring("".join(__import__('re').findall("(?i)<vars>([A-Za-z0-9\\x2B\\x3D\\x2F]+?)</vars>", __LiveDebugCode_)))
        except:
            pass
            print "Script Base64 Error"
            __LiveBase64Code_='0'
        try:
            eval(compile(__LiveBase64Code_,'<LiveDebugVars"""+LOGIKID+""">','exec'))
        except:
            print "Script Error" 
            print __LiveBase64Code_
            print  __import__('traceback').print_exception(__import__('sys').exc_info()[0],__import__('sys').exc_info()[1],__import__('sys').exc_info()[2])
            raise
    else:
        print "unbekanntes TAG: " + repr(__LiveDebugCode_)
"""




#print LIVECODE

LOGIKFILE=LOGIKID+"_"+LOGIKNAME

## Debug Lines
NCODE=[]
if debug or livedebug:
    for codepart in code:
        codepart[2]=re.sub("###DEBUG###","",codepart[2])
        NCODE.append(codepart)
    code=NCODE

#print "\n".join(code)
def commentRemover(code):
    ## Komentar Remover 
    ## thanks to gaston
    codelist=code[2].split("\n")
    removelist=[]
    lencode=len(codelist)-1
    for i in range(1,lencode):
        codeline=codelist[lencode-i].lstrip(" \t")
        if len(codeline)>0:
            if codeline[0]=='#':
                removelist.insert(0,"REMOVED: ("+str(lencode-i)+") "+codelist.pop(lencode-i))
        else:
            codelist.pop(lencode-i)
    return ([code[0],code[1],"\n".join(codelist)],"\n".join(removelist))

Nremoved=""
NCode=[]
for codepart in code:
    codepart, removed=commentRemover(codepart)
    Nremoved=Nremoved+removed
    NCode.append(codepart)

code=NCode

#print Nremoved
#print "\n\n"


#print code

if livedebug:
    NCODE="\n##### VERSION #### %04d-%02d-%02d %02d:%02d:%02d ###\n" % time.localtime()[:6]
    code.append(NCODE)

CODELENGTH=len(repr(code))



breakStart=str((int(CALCSTARTBOOL)-1)*-1)
LOGIKARRAY=LOGIK.split("\n")
lformel=""
def compileMe(code,doByteCode,BEDINGUNG=''):
    if doByteCode:
        data=compile(code,"<"+LOGIKFILE+">","exec")
        data=marshal.dumps(data)
        version = sys.version[:3]
        formel = ""
        if doByteCode==2:
            formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(__import__('marshal').loads(__import__('zlib').decompress(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(zlib.compress(data,6)))+"'))))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        else:
            formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(__import__('marshal').loads(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(data))+"')))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        formel+="\n"

    else:
        if doCache:
            LOGIKDEFARRAY=LOGIKARRAY[LHSDEFINELINE].split("|")
            if livedebug:
                LOGIKDEFARRAY[4]=str(ANZSP+2)
            else:
                LOGIKDEFARRAY[4]=str(ANZSP+1)
            LOGIKARRAY[LHSDEFINELINE]="|".join(LOGIKDEFARRAY)
            LOGIKARRAY[LSPDEFINELINE]+="\n"+"5003|"+str(ANZSP+1)+"|\"0\"|0 # Base64 Code-Cache"
            if livedebug:
                LOGIKARRAY[LSPDEFINELINE]+="\n"+"5003|"+str(ANZSP+2)+"|\"\"|0 # LivePortBase64Buffer"
            if livedebug:
                formel = "5012|0|\"EI or EC["+str(ANZIN+1)+"]\"|\"eval(compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(LIVECODE))+"'),'<"+LOGIKFILE+">','exec'))\"|\"\"|0|0|0|0\n"
                #formel += "5012|0|\"("+BEDINGUNG+") or SC["+str(ANZSP+1)+"]\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
                formel += "5012|0|\"\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
            else:
                formel = "5012|0|\"EI\"|\"compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(code))+"'),'<"+LOGIKFILE+">','exec')\"|\"\"|0|0|"+str(ANZSP+1)+"|0\n"
                formel += "5012|0|\""+BEDINGUNG+"\"|\"eval(SN["+str(ANZSP+1)+"])\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
        else:
            formel = "5012|0|\""+BEDINGUNG+"\"|\"eval(compile(__import__('base64').decodestring('"+re.sub("\n","",base64.encodestring(code))+"'),'<"+LOGIKFILE+">','exec'))\"|\""+ZEITFORMEL+"\"|0|"+ZEITSPEICHER+"|0|0"
    #formel+="\n## MD5 der Formelzeile: "+md5.new(formel).hexdigest()
    return formel

formel=""
for i in range(len(code)):
    codepart=code[i]
    if codepart[0]==1:
        tempBC=1
    if codepart[0]==2:
        tempBC=2
    else:
        tempBC=doByteCode
    if livedebug:
        doCache=True
        formel=compileMe(LIVECODE,False,BEDINGUNG="")
        break
    formel+=compileMe(codepart[2],tempBC,BEDINGUNG=codepart[1])
    #formel+=commentcode[i]+"\n\n"
        
### DEBUG ###

formel+="\n"+postlogik[2]

## Debuggerbaustein

if livedebug:
    LOGIKDEFARRAY=LOGIKARRAY[LEXPDEFINELINE].split("|")
    LOGIKDEFARRAY[3]=str(ANZIN+1)
    LOGIKDEFARRAY[3+ANZIN]+="|\"E"+str(ANZIN+1)+" DEBUG\""
    LOGIKARRAY[LEXPDEFINELINE]="|".join(LOGIKDEFARRAY)
    LOGIKDEFARRAY=LOGIKARRAY[LHSDEFINELINE].split("|")
    LOGIKDEFARRAY[1]=str(ANZIN+1)
    LOGIKARRAY[LHSDEFINELINE]="|".join(LOGIKDEFARRAY)
    LOGIKARRAY[LINDEFINELINE]+="\n"+"5002|"+str(ANZIN+1)+"|\"\"|1 # Debugger Live in"


LOGIK = "\n".join(LOGIKARRAY)

allcode=""
for i in code:
  allcode+=i[2]+"\n"

if showList:
    codeobj=allcode.split("\n")
    for i in range(0,len(codeobj)):
        print str(i)+": "+codeobj[i]

if debug and not livedebug:
    debugstart=time.clock()
    allcode += debugcode
    if not noexec:
        exec(allcode)
    else:
        compile(allcode,"<code>","exec")

    debugtime=time.clock()-debugstart
    print "Logikausfuehrzeit: %.4f ms" % (debugtime)
    if debugtime>1:
      print """
###############################################
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###
### !!!ACHTUNG: sehr lange Ausfürungszeit!! ###
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ###
###############################################
"""

if debug or doSend:
    del EN[0]
    del SN[0]
    del AN[0]

if livedebug:
    #formel=lformel
    LOGIK="""############################\n####  DEBUG BAUSTEIN #######\n############################\n"""+LOGIK
    livesend=re.sub("\n","",base64.encodestring(allcode))
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect((livehost,liveport))
    Livepackets=0
    while livesend!="":
        Livepackets+=1
        sock.sendall("<xml><id"+LOGIKID+"><inject>"+livesend[:4000]+"</inject></id"+LOGIKID+"></xml>")
        livesend=livesend[4000:]
        time.sleep(0.1)
    time.sleep(1)
    sock.sendall("<xml><id"+LOGIKID+"><compile /></id"+LOGIKID+"></xml>")
    print str(Livepackets)+ " Packet per UDP verschickt"
    sock.close()

if doSend:
    ## Das auslösen über den Debug verhindern
    sendVars="EC["+str(ANZIN+1)+"]=0\n"+sendVars
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.connect((livehost,liveport))
    sock.sendall("<xml><id"+LOGIKID+"><vars>"+re.sub("\n","",base64.encodestring(sendVars)+"</vars></id"+LOGIKID+"></xml>\n"))
    sock.close()


if VERSION !="":
    VERSION="_"+VERSION
if debug:
    VERSION+="_DEBUG"


open(LOGIKFILE+VERSION+".hsl",'w').write(LOGIK+"\n"+formel+"\n")
def md5sum(fn):
    m = md5()
    f=open(fn,'rb')
    while True: 
        data = f.read(1024) 
        if not data: 
            break 
        m.update(data) 
    f.close()
    return m.hexdigest() + " *" + fn + "\n"
    
#chksums = md5sum(LOGIKFILE+VERSION+".hsl")
#if not nosource:
#    chksums += md5sum(inspect.currentframe().f_code.co_filename)
#if doDoku:
#    chksums += md5sum("log"+LOGIKID+".html")
#
#open(LOGIKFILE+".md5",'w').write(chksums)

if doZip:
    #os.remove(LOGIKFILE+VERSION+".zip")
    z=zipfile.ZipFile(LOGIKFILE+VERSION+".zip" ,"w",zipfile.ZIP_DEFLATED)
    if not nosource:
        z.write(inspect.currentframe().f_code.co_filename)
    if doDoku:
        z.write("log"+LOGIKID+".html")
    z.write(LOGIKFILE+VERSION+".hsl")
#    z.write(LOGIKFILE+".md5")
    z.close()

print "Baustein \"" + LOGIKFILE + "\" erstellt"
print "Groesse:" +str(CODELENGTH)

if livedebug:
    print "########################################"
    print "####       DEBUGBAUSTEIN            ####"
    print "########################################"

print """
Neuberechnung beim Start: """+CALCSTART+"""
Baustein ist remanent: """+LOGIKREMANT+"""
Interne Bezeichnung: """+LOGIKID+"""
Kategorie: '"""+LOGIKCAT+"""'
Anzahl Eingänge: """+str(ANZIN)+"""   """+repr(EN)+"""
Anzahl Ausgänge: """+str(ANZOUT)+"""  """+repr(AN)+"""
Interne Speicher: """+str(ANZSP)+"""  """+repr(SN)+"""
"""

#print chksums

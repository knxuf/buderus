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
VERSION="V0.3"


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
          
          self.config = {
              'debug': 2,
              'ecocanmode' :0,
          }
          
          self._constants = {
              'STX': chr(0x02),
              'DLE': chr(0x10),
              'ETX': chr(0x03),
              'NAK': chr(0x15),
              'QVZ': 2,             # Quittungsverzugzeit (QVZ) 2 sec
              'ZVZ': 0.220,         # Der Abstand zwischen zwei Zeichen darf nicht mehr als die Zeichenverzugszeit (ZVZ) von 220 ms
              'BWZ': 4,             # Blockwartezeit von 4 sec
              'ECOCANTRANSMODE' : "\xdd\x00\x00\x04",
          }

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

          self.error_messages = {
              0 : "kein Fehler",
              1 : "Strategievorlauffühler defekt !",
              2 : "Aussenfühler defekt !",
              3 : "Vorlauffühler HK1 defekt !",
              4 : "Vorlauffühler HK2 defekt !",
              5 : "Vorlauffühler HK3 defekt !",
              6 : "Vorlauffühler HK4 defekt !",
              7 : "nicht belegt !",
              8 : "Warmwasserfühler defekt !",
              9 : "Warmwasser bleibt kalt !",
              10 : "Störung Therm. Desinfektion !",
              11 : "Fernbedienung HK 1 defekt !",
              12 : "Fernbedienung HK 2 defekt !",
              13 : "Fernbedienung HK 3 defekt !",
              14 : "Fernbedienung HK 4 defekt !",
              15 : "keine Kommun. mit Fernbed. HK 1!",
              16 : "keine Kommun. mit Fernbed. HK 2!",
              17 : "keine Kommun. mit Fernbed. HK 3!",
              18 : "keine Kommun. mit Fernbed. HK 4!",
              19 : "nicht belegt !",
              20 : "Störung Brenner 1",
              21 : "Störung Brenner 2",
              22 : "Störung Brenner 3",
              23 : "Störung Brenner 4",
              24 : "keine Verbindung mit Kessel 1 !",
              25 : "keine Verbindung mit Kessel 2 !",
              26 : "keine Verbindung mit Kessel 3 !",
              27 : "nicht belegt !",
              28 : "nicht belegt !",
              29 : "nicht belegt !",
              30 : "Interner Fehler Nr. 1 !",
              31 : "Interner Fehler Nr. 2 !",
              32 : "Interner Fehler Nr. 3 !",
              33 : "Interner Fehler Nr. 4 !",
              34 : "Vorlauffühler HK5 defekt !",
              35 : "Vorlauffühler HK6 defekt !",
              36 : "Vorlauffühler HK7 defekt !",
              37 : "Vorlauffühler HK8 defekt !",
              38 : "nicht belegt !",
              39 : "Fernbedienung HK 5 defekt !",
              40 : "Fernbedienung HK 6 defekt !",
              41 : "Fernbedienung HK 7 defekt !",
              42 : "Fernbedienung HK 8 defekt !",
              43 : "nicht belegt !",
              44 : "keine Kommun. mit Fernbed. HK 5!",
              45 : "keine Kommun. mit Fernbed. HK 6!",
              46 : "keine Kommun. mit Fernbed. HK 7!",
              47 : "keine Kommun. mit Fernbed. HK 8!",
              48 : "nicht belegt !",
              49 : "Kesselvorlauffühler defekt !",
              50 : "Kesselzusatzfühler defekt !",
              51 : "Kessel bleibt kalt !",
              52 : "Brennerstörung !",
              53 : "Störung Sicherheitskette !",
              54 : "Externe Störung Kessel !",
              55 : "Abgasfühler defekt !",
              56 : "Abgasgrenze überschritten !",
              57 : "Externer Störeing. (Pumpe) HK1 !",
              58 : "Externer Störeing. (Pumpe) HK2 !",
              59 : "Externer Störeing. (Pumpe) HK3 !",
              60 : "Externer Störeing. (Pumpe) HK4 !",
              61 : "Externer Störeing. (Pumpe) HK5 !",
              62 : "Externer Störeing. (Pumpe) HK6 !",
              63 : "Externer Störeing. (Pumpe) HK7 !",
              64 : "Externer Störeing. (Pumpe) HK8 !",
              65 : "nicht belegt !",
              66 : "Interner Fehler Nr. 5 !",
              67 : "Interner Fehler Nr. 6 !",
              68 : "Interner Fehler Nr. 7 !",
              69 : "Interner Fehler Nr. 8 !",
              70 : "Kein Master (Adr. 1) vorhanden !",
              71 : "Adresskonflikt auf CAN-Bus !",
              72 : "Adr.konflikt auf Steckplatz 1 !",
              73 : "Adr.konflikt auf Steckplatz 2 !",
              74 : "Adr.konflikt auf Steckplatz 3 !",
              75 : "Adr.konflikt auf Steckplatz 4 !",
              76 : "Adr.konflikt auf Steckplatz A !",
              77 : "Falsches Modul auf Steckplatz 1 !",
              78 : "Falsches Modul auf Steckplatz 2 !",
              79 : "Falsches Modul auf Steckplatz 3 !",
              80 : "Falsches Modul auf Steckplatz 4 !",
              81 : "Falsches Modul auf Steckplatz A !",
              82 : "Unbekanntes Modul auf Steckplatz 1 !",
              83 : "Unbekanntes Modul auf Steckplatz 2 !",
              84 : "Unbekanntes Modul auf Steckplatz 3 !",
              85 : "Unbekanntes Modul auf Steckplatz 4 !",
              86 : "Unbekanntes Modul auf Steckplatz A !",
              87 : "Rücklauffühler defekt !",
              88 : "Ext. Störeingang (Inertanode) WW !",
              89 : "Ext. Störeingang (Pumpe) WW !",
              90 : "Konfig. Rücklauf bei Strategie!",
              91 : "Konfig. Vorlauf bei Strategie !",
              92 : "RESET !",
              93 : "Handschalter Heizkreis 1 !",
              94 : "Handschalter Heizkreis 2 !",
              95 : "Handschalter Heizkreis 3 !",
              96 : "Handschalter Heizkreis 4 !",
              97 : "Handschalter Heizkreis 5 !",
              98 : "Handschalter Heizkreis 6 !",
              99 : "Handschalter Heizkreis 7 !",
              100 : "Handschalter Heizkreis 8 !",
              101 : "Handschalter Warmwasser !",
              102 : "Handschalter Brenner !",
              103 : "Handschalter Kesselkreis !",
              104 : "Strategiemodul fehlt !",
              105 : "Handschalter LAP Primärpumpe !",
              106 : "Handschalter LAP Sekundärpumpe !",
              107 : "Wärmetauscherfühler LAP defekt !",
              108 : "Speicher unten Fühler LAP defekt !",
              109 : "Warmwasser Solarfühler defekt !",
              110 : "Kollektorfühler defekt !",
              111 : "Störung Brenner 5",
              112 : "Störung Brenner 6",
              113 : "Störung Brenner 7",
              114 : "Störung Brenner 8",
              115 : "keine Verbindung mit Brennerautomat 1",
              116 : "keine Verbindung mit Brennerautomat 2",
              117 : "keine Verbindung mit Brennerautomat 3",
              118 : "keine Verbindung mit Brennerautomat 4",
              119 : "keine Verbindung mit Brennerautomat 5",
              120 : "keine Verbindung mit Brennerautomat 6",
              121 : "keine Verbindung mit Brennerautomat 7",
              122 : "keine Verbindung mit Brennerautomat 8",
              123 : "Flaschenvorlauffühler defekt",
              124 : "3-Wegeumschaltventil defekt",
              125 : "Füllstand: Grenze unterschritten",
              126 : "Unterstation Wärme Unterversorgung !",
              127 : "Unterstation Vorlauffühler defekt !",
              128 : "Kollektorfühler defekt !",
              129 : "Bypass-Rücklauffühler defekt !",
              130 : "Bypass-Vorlauffühler defekt !",
              131 : "Wärmemengenzähler Vorlauf defekt !",
              132 : "Wärmemengenzähler Rücklauf defekt !",
              133 : "Speicher 1 Fühler unten defekt !",
              134 : "Speicher 2 Fühler unten defekt !",
              135 : "Wärmemengenzähler Volumenstrommesser !",
              136 : "Fehlerhafte Einstellung Solarmodul !",
              137 : "Heizkreis 1 EIB-Fehler !",
              138 : "Heizkreis 2 EIB-Fehler !",
              139 : "Heizkreis 3 EIB-Fehler !",
              140 : "Heizkreis 4 EIB-Fehler !",
              141 : "Heizkreis 5 EIB-Fehler !",
              142 : "Heizkreis 6 EIB-Fehler !",
              143 : "Heizkreis 7 EIB-Fehler !",
              144 : "Heizkreis 8 EIB-Fehler !",
              145 : "Heizkreis 9 EIB-Fehler !",
              146 : "allgemeiner EIB - Fehler !",
              147 : "Blockierender Fehler UBA !",
              148 : "Verriegelnder Fehler UBA !",
              149 : "Handbetrieb Solar Speicher 1 !",
              150 : "Handbetrieb Solar Speicher 2 !",
              151 : "Handbetrieb Heizkreis 0 !",
              152 : "Wartung erforderlich Betriebsstunden !",
              153 : "Wartung erforderlich Datum !",
              154 : "Warmwasser ist kalt !",
              155 : "Handbetrieb Zubringerpumpe (PZB)!",
              156 : "Handbetrieb EMS - Kessel 1 !",
              157 : "Handbetrieb EMS - Kessel 2 !",
              158 : "Handbetrieb EMS - Kessel 3 !",
              159 : "Handbetrieb EMS - Kessel 4 !",
              160 : "Handbetrieb EMS - Kessel 5 !",
              161 : "Handbetrieb EMS - Kessel 6 !",
              162 : "Handbetrieb EMS - Kessel 7 !",
              163 : "Handbetrieb EMS - Kessel 8 !",
              164 : "Störung EMS - Kessel 1 !",
              165 : "Störung EMS - Kessel 2 !",
              166 : "Störung EMS - Kessel 3 !",
              167 : "Störung EMS - Kessel 4 !",
              168 : "Störung EMS - Kessel 5 !",
              169 : "Störung EMS - Kessel 6 !",
              170 : "Störung EMS - Kessel 7 !",
              171 : "Störung EMS - Kessel 8 !",
              172 : "Störung EMS - Warmwasser !",
              173 : "Wartung erforderlich EMS - Kessel 1 !",
              174 : "Wartung erforderlich EMS - Kessel 2 !",
              175 : "Wartung erforderlich EMS - Kessel 3 !",
              176 : "Wartung erforderlich EMS - Kessel 4 !",
              177 : "Wartung erforderlich EMS - Kessel 5 !",
              178 : "Wartung erforderlich EMS - Kessel 6 !",
              179 : "Wartung erforderlich EMS - Kessel 7 !",
              180 : "Wartung erforderlich EMS - Kessel 8 !",
              181 : "Alternativer WE Pumpe im Handbetrieb !",
              182 : "Alternativer WE im Handbetrieb !",
              183 : "Alternativer WE Rücklauffühler defekt !",
              184 : "Alternativer WE Vorlauffühler defekt !",
              185 : "Alternativer WE Fühler Puffer mitte !",
              186 : "Alternativer WE Fühler Puffer unten !",
              187 : "Alternativer WE Fühler Puffer oben !",
              188 : "Alternativer WE Anl. Rücklauffühler !",
              189 : "Alternativer WE Abgasfühler defekt !",
              190 : "Alternativer WE Kommunikation Brennerautomat !",
              191 : "Alternativer WE Brennerautomat verriegelt !",
              192 : "Alternativer WE Notkühlung ausgelöst !",
              193 : "FM458 Zuordnung Kessel 1 !",
              194 : "FM458 Zuordnung Kessel 2 !",
              195 : "FM458 Zuordnung Kessel 3 !",
              196 : "FM458 Zuordnung Kessel 4 !",
              197 : "FM458 Zuordnung Kessel 5 !",
              198 : "FM458 Zuordnung Kessel 6 !",
              199 : "FM458 Zuordnung Kessel 7 !",
              200 : "FM458 Zuordnung Kessel 8 !",
              201 : "FM458 Keine Verbindung zu Kessel 1 !",
              202 : "FM458 Keine Verbindung zu Kessel 2 !",
              203 : "FM458 Keine Verbindung zu Kessel 3 !",
              204 : "FM458 Keine Verbindung zu Kessel 4 !",
              205 : "FM458 Keine Verbindung zu Kess",
              206 : "FM458 Keine Verbindung zu Kessel 6 !",
              207 : "FM458 Keine Verbindung zu Kessel 7 !",
              208 : "FM458 Keine Verbindung zu Kessel 8 !",
              209 : "FM458 Fühler Vorlauf Strategie !",
              210 : "FM458 Fühler Rücklauf Strategie !",
              211 : "FM458 Konfiguration Rücklauf Strategie!",
              212 : "FM458 Konfiguration Vorlauf Strategie !",
              213 : "FM458 Leistungsangabe für Kessel fehlt !",
          }
          
          self.active_errors = []
          
          self.found_devices = []
          
          self.payload_regex = re.compile("(?P<id>AB|A7)(?P<busnr>[0-9a-fA-F]{2})(?P<type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{2})+)")
          self.error_regex = re.compile("AE(?P<busnr>[0-9a-fA-F]{2})(?P<slot1>[0-9a-fA-F]{2})(?P<slot2>[0-9a-fA-F]{2})(?P<slot3>[0-9a-fA-F]{2})(?P<slot4>[0-9a-fA-F]{2})")
          
          self._thread = None
          self.sock = None
          self._buderus_data_lock = threading.RLock()

          self._hs_message_queue = Queue()
          self._buderus_message_queue = Queue()

          self.readconfig(EN[2])
          
          self.hs_queue_thread = threading.Thread(target=self._send_to_hs_consumer,name='buderus_hs_consumer')
          self.hs_queue_thread.start()

          self.buderus_queue_thread = threading.Thread(target=self._send_to_buderus_consumer,name='hs_buderus_consumer')
          self.buderus_queue_thread.start()

          self.connect()

      def readconfig(self,configstring):
          import re
          for (option,value) in re.findall("(\w+)=(.*?)(?:\*|$)", configstring ):
              option = option.lower()
              _configoption = self.config.get(option)
              _configtype = type(_configoption)
              if _configtype == type(None):
                  self.log("unbekannte Konfig Option %s=%s" % (option,value) )
                  continue
              try:
                  _val = _configtype(value)
                  self.config[option] = _val
              except ValueError:
                  self.log("falscher Wert bei Konfig Option %s=%s (erwartet %r)" % (option,value, _configtype ) )
                  pass


      def debug(self,msg,lvl=5):
          if self.config.get("debug") < lvl:
              return
          import time
          #self.log(msg,severity='debug')
          print "%s DEBUG: %r" % (time.strftime("%H:%M:%S"),msg,)

      def connect(self):
          from hs_queue import hs_threading as threading
          self._thread = threading.Thread(target=self._connect,name='Buderus-Moxa-Connect')
          self._thread.start()

      def _send_to_buderus_consumer(self):
          import select,time
          while True:
              if not self.sock:
                  self.debug("Socket nicht bereit ... warten")
                  time.sleep(1)
                  continue
              msg = self._buderus_message_queue.get()
              self._buderus_data_lock.acquire()
              self.debug("sende Queue exklusiv lock erhalten")
              try:
                  try:
                      if self.wait_for_dle():
                          self.debug("jetzt payload %r senden" % (msg,) )
                          self.send_payload(msg)
                      else:
                          self.debug("payload %r verworfen" % (msg,) )
                  
                  except:
                      self.MC.Debug.setErr(sys.exc_info(),"%r" % msg)
              finally:
                  self._buderus_data_lock.release()
                  self.debug("sende Queue exklusiv lock released")

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
              ## leerzeciehn entfernen 
              _msg = _msg.replace(' ','')
              self._buderus_message_queue.put( _msg )

      def to_hex(self,list_of_dec):
          try:
              if not type(list_of_dec) == list:
                  list_of_dec = [list_of_dec]
              return " ".join( ["%.2x".upper() % x for x in list_of_dec] )
          except:
              return list_of_dec

      def parse_device_type(self,payload):
          _payload = self.payload_regex.search(payload)
          if _payload:
              _type = _payload.group("type")
              if _type not in self.found_devices:
                  self.found_devices.append( _type )
                  (_devicename, _datalen) = self.device_types.get( _type, ("unbekanntes Gerät (%s)" % _type, 0) )
                  self.debug("Gerät %r an ECOCAN %s gefunden" % ( _devicename, _payload.group("busnr") ) )
              return
          _error = self.error_regex.search( payload )
          if _error:
              _busnr = _error.group("busnr")
              # nur fehlerstatus > 0
              _error_slots = filter(lambda x: int(x,16) > 0,[ _error.group("slot1"), _error.group("slot2"), _error.group("slot3"), _error.group("slot4") ])
              _active_errors = filter(lambda x,busnr=_busnr: x[0] == busnr, self.active_errors)
              for _err in _error_slots:
                  _err = int(_err,16)
                  if (_busnr,_err) not in self.active_errors:
                      self.active_errors.append( (_busnr,_err) )
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      self.log( "%s an Bus %s" % (_err_message,_busnr), severity='error' )
              for (busnr,_err) in _active_errors:
                  if _err not in _error_slots:
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      self.log( "%s an Bus %s (behoben)" % (_err_message,_busnr), severity='info' )
                      self.active_errors.remove( (busnr,_err) )

      def wait_for_dle(self):
          ## 3 versuche
          for _loop in xrange(3):
              ## STX senden
              self.debug("STX senden")
              self.sock.send( self._constants['STX'] )
              self.debug("STX gesendet / warten auf DLE")
              ## auf daten warten, timeout ist QVZ
              _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['QVZ'] )
              if self.sock in _r:
                  data = self.sock.recv(1)
                  if data == self._constants['DLE']:
                      self.debug("DLE empfangen")
                      return True
                  elif data == self._constants['DLE']:
                      ## FIXME
                      self.debug("STX empfangen Initialisierungskonflikt")
                      self.sock.send( self._constants['DLE'] )
                      self.debug("DLE gesendet")
                      self.read_payload()
                      
          self.debug("Nach 3x STX senden innerhalb QVZ kein DLE")
          return False
        

      ## Verbindung zum Moxa (gethreadet)
      def _connect(self):
          import time,socket,sys,select
          try:
              self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              _ip,_port = self.device_connector.split(":")
              self.sock.connect( ( _ip, int(_port) ) )
              self.debug("connect zu moxa an %s:%s" % (_ip,_port))
              
              ## ecocan-c modem mode
              if self.config.get("ecocanmode"):
                  self.set_transparent_mode()
              while True:
                  ## wir warten einfach nur auf Daten beim timeout überprüfen wir die send queue
                  if not self.sock:
                      break
                  _r,_w,_e = select.select( [ self.sock ],[],[], 10 )
                  if not self._buderus_data_lock.acquire(blocking=False):
                      continue
                  self.debug("empfang exklusiv lock erhalten")
                  try:
                      if self.sock in _r:
                          ## wenn Daten da sind, ein zeichen lesen
                          data = self.sock.recv(1)
                          if not data:
                              self.debug("Verbindung abgebrochen")
                              break
                          if data == self._constants['STX']:
                              self.debug("STX empfangen sende DLE")
                              self.sock.send( self._constants['DLE'] )
                              self.debug("DLE gesendet")
                              
                              self.read_payload()
                          else:
                              self.debug("ungültiges Zeichen %r empfangen" % (data,) ,lvl=4)
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

      def set_transparent_mode(self):
          self.sock.send(  self._constants['ECOCANTRANSMODE'] )

      def send_payload(self,payload):
          import select,binascii
          ## 6 versuche
          for _loop in xrange(6):
              self.debug("exklusiv senden / versuch %d" % _loop)
              _bcc = 0
              for _byte in binascii.unhexlify(payload):
                  self.sock.send( _byte )
                  self.debug("Byte %r versendet" % binascii.hexlify(_byte))
                  _bcc ^= ord(_byte)
                  if _byte == self._constants['DLE']:
                      ## wenn DLE dann in der payload verdoppeln
                      self.debug("Payload enthällt DLE, ersetzt mit DLE DLE" ) 
                      self.sock.send( _byte )
                      _bcc ^= ord(_byte)
              self.debug("Alle Daten gesendet, jetzt DLE und ETX")
              self.sock.send( self._constants['DLE'] )
              _bcc ^= ord( self._constants['DLE'] )
              self.sock.send( self._constants['ETX'] )
              _bcc ^= ord( self._constants['ETX'] )
              
              self.debug("jetzt checksumme %r senden" % (_bcc) )
              self.sock.send( chr(_bcc) )

              ## auf daten warten, timeout ist QVZ
              self.debug("warten auf DLE")
              _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['QVZ'] )
              if self.sock in _r:
                  data = self.sock.recv(1)
                  if data == self._constants['DLE']:
                      self.debug("DLE erhalten")
                      self.debug("Daten %r erfolgreich gesendet" % (payload,),lvl=2)
                      return True
              self.debug("Kein DLE erhalten loop")
          self.debug("Nach 6x STX senden innerhalb QVZ kein DLE",lvl=1)


      def read_payload(self):
          import select,binascii,time
          ## 6 versuche sind erlaubt
          for _loop in xrange(6):
              self.debug("exklusiv lesen / versuch %d" % _loop)
              _lastchar = ""
              _bcc = 0
              _payload = []
              _wait_for_checksum = False
              _bwz_timer = time.time() + self._constants['BWZ']
              while True:
                  _r,_w,_e = select.select( [ self.sock ],[],[], self._constants['ZVZ'] )
                  if not self.sock in _r:
                      ## wenn schon Daten da nur zeichenverzugszeit/ wenn keine Daten dann Blockwartezeit
                      if len(_payload) > 0 or _bwz_timer <= time.time():
                          ## kein zeichen innerhalb ZVZ bzw BWZ
                          self.debug("abbruch ZVZ oder BWZ",lvl=1)
                          self.send( self._constants['NAK'] )
                          ## gegenseite zeit geben
                          time.sleep( self._constants['ZVZ'] )
                          break
                      ## wenn noch keine daten und blockwartezeit nicht überschritten
                      else:
                          self.debug("weiter warten auf daten noch kein ZVZ/BWZ timeout")
                          continue
                  ## ein Zeichen lesen
                  data = self.sock.recv(1)
                  if not data:
                      self.debug("Keine Daten / verbindung verloren")
                      return
                  ## wenn checksumme erwartet wird
                  if _wait_for_checksum:
                      _bcc_recv = ord(data)
                      self.debug("berechnete checksumme = %.2x empfange checksumme = %.2x" % ( _bcc,_bcc_recv) )
                      if _bcc == _bcc_recv:
                          _hexpayload = "".join( _payload ).upper()
                          self.debug("Payload %r erfolgreich empfangen" % (_hexpayload),lvl=2)
                          
                          self.parse_device_type( _hexpayload )
                          
                          self.send_to_output(1, _hexpayload)
                          self.sock.send( self._constants['DLE'] )
                          return
                      else:
                          self.debug("Checksum nicht korrekt %r != %r" % (_bcc, _bcc_recv) ,lvl=1)
                          self.sock.send( self._constants['NAK'] )
                          ## FIXME BREAK heißt nochmal in die 6 versuche oder return wäre zurück zum mainloop warten auf STX
                          break
                  
                  ## checksum von jedem packet berechnen
                  _bcc ^= ord(data)

                  ## wenn 2mal DLE hintereinander bcc berechnen aber nur eins zum packet
                  if data == _lastchar == self._constants['DLE']:
                      self.debug("entferne doppeltes DLE")
                      _lastchar = ""
                      continue
                  
                  ## WENN DLE ETX dann Ende
                  if _lastchar == self._constants['DLE'] and data ==  self._constants['ETX']:
                      self.debug("DLE/ETX empfangen warte auf checksumme")
                      _wait_for_checksum = True
                      ## letztes DLE entfernen
                      _payload = _payload[:-1]
                      continue
                      
                  ## daten zum packet hinzu
                  self.debug("Daten %r empfangen" % (binascii.hexlify(data)),lvl=3)
                  _payload.append( binascii.hexlify(data) )
                  ## letztes zeichen speichern
                  _lastchar = data


      def direct_read_request(self):
          ## Mit dem Kommando "0xA2 <ECOCAN-BUS-Adresse>" können die Monitordaten des ausgewählten 
          ## ECOCAN-BUS-Gerätes von der Kommunikationskarte ausgelesen werden. 
          pass
      
      def direct_read_answer(self):
          ## Die Kommunikationskarte antwortet mit : 
          ## 0xAB <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <6 Daten-Byte> 
          ## 0xAB = Kennung für Monitordaten 
          ## ECOCAN-BUS-Adresse = die abgefragte Adresse zur Bestätigung 
          ## TYP = Typ der gesendeten Monitordaten

          ## Daten unter dem entsprechenden Typ werden nur gesendet wenn auch die entsprechende Funktionalität 
          ## im Regelgerät eingebaut ist. 
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s

          ## Als Endekennung für das abgefragte Regelgerät oder falls keine Daten vorhanden sind, wird der 
          ## nachfolgende String 
          ## 0xAC <ECOCAN-BUS-Adresse> gesendet          

          ## Die Abfrage der gesamten Monitordaten braucht nur zu Beginn oder nach einem Reset zu erfolgen. 
          ## Nach erfolgter Abfrage der Monitordaten sollte wieder mit dem Kommando 0xDC in den "Normal-Modus" 
          ## zurückgeschaltet werden. 

          pass


      def normal_read(self):
          ## Im "Normal-Modus" werden die Monitordaten nach folgendem Muster übertragen: 
          ## 0xA7 <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <DATUM> 
          ## 0xA7 = Kennung für einzelne Monitordaten 
          ## ECOCAN-BUS-Adresse = Herkunft´s Adresse des Monitordatum´s (hier Regelgeräteadresse) 
          ## TYP = Typ der empfangenen Monitordaten       
          ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s 
          ## DATUM = eigentlicher Messwert 
          pass
          

## STX = 0x02
## DLE = 0x10
## ETX = 0x03
## NAK = 0x15

## Die Steuerzeichen für die Prozedur 3964R sind der Norm DIN 66003 für den 7-Bit-Code entnommen. Sie
## werden allerdings mit der Zeichenlänge 8 Bit übertragen (Bit I7 = 0). Am Ende jedes Datenblocks wird zur
## Datensicherung ein Prüfzeichen(BCC) gesendet.


## Das Blockprüfzeichen wird durch eine exklusiv-oder-Verknüpfung über alle Datenbytes der
## Nutzinformation, inclusive der Endekennung DLE, ETX gebildet.



## Bei dem Kommunikationsmodul wird zwischen einem "Normal-Modus" und einem "Direkt-Modus"
## unterschieden. 
## "Normal-Modus" Bei diesem Modus werden laufend alle sich ändernden Monitorwerte 
## sowie Fehlermeldungen übertragen. 
## "Direkt-Modus" Bei diesem Modus kann der aktuelle Stand aller bisher vom Regelgerät 
## generierten Monitordaten en Block abgefragt und ausgelesen werden. 
## Mittels des Kommandos 0xDD kann von "Normal-Modus" in den "Direkt-Modus" umgeschaltet werden. 
## In diesem Modus kann auf alle am ECOCAN-BUS angeschlossenen Geräte zugegriffen und es können 
## geräteweise die Monitorwerte ausgelesen werden. 
## Der "Direkt-Modus" kann durch das Kommando 0xDC wieder verlassen werden. 
## Außerdem wird vom "Direkt-Modus" automatisch in den "Normal-Modus" zurückgeschaltet, wenn für die 
## Zeit von 60 sec kein Protokoll des "Direkt-Modus" mehr gesendet wird. 

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

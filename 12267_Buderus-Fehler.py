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
LOGIKNAME="Buderus-Fehler"
## Logik ID
LOGIKID="12267"

## Ordner im GLE
LOGIKCAT="www.knx-user-forum.de"


## Beschreibung
LOGIKDESC="""

"""
VERSION="V0.1"


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

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''_'''+VERSION+'''"|0|2|"E1 Payload IN"|"E2 Config"|3|"A1 SystemLog"|"A2 Störung"|"A2 Störstatus XML"

5001|2|3|0|1|1

# EN[x]
5002|1|""|1 #* Payload IN
5002|2|""|1 #* config

# Speicher
5003|1||0 #* logic

# Ausgänge
5004|1|""|0|1|1 #* SystemLog
5004|2|0|1|1|0 #* SystemLog
5004|3|""|0|1|1 #* SystemLog

#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
  class buderus_fehler(object):
      def __init__(self,localvars):
          import re

          self.logik = localvars["pItem"]
          self.MC = self.logik.MC

          EN = localvars['EN']

          self.id = "buderus_fehler"

          self.localvars = localvars

          self.config = {
              'debug': 2,
              'errormsg' : 'Störmeldung an Regelgerät %(bus)s: %(msg)s',
              'errorclearmsg' : 'Störmeldung an Regelgerät %(bus)s: %(msg)s (behoben)',
              'emerg'    : '',
              'alert'    : '',
              'crit'     : '',
              'error'    : '',
              'warn'     : '',
              'info'     : '',
              'none'     : '',
              'default'  : 'error',
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
          
          self.output_bus_error_status = {}
          
          self.readconfig(EN[2])
          
          self.build_severitydict()
          
          self.log_queue = ""

          self.error_regex = re.compile("AE(?P<busnr>[0-9a-fA-F]{2})(?P<slot1>[0-9a-fA-F]{2})(?P<slot2>[0-9a-fA-F]{2})(?P<slot3>[0-9a-fA-F]{2})(?P<slot4>[0-9a-fA-F]{2})")

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

      def get_status_xml(self):
          import time
          _xml = []
          for _busnr,_errno_status_dict in self.output_bus_error_status.iteritems():
              _bus_xml = []
              for _errno,_val in _errno_status_dict.iteritems():
                  _bus_xml.append("<errno_%s>%s</errno_%s>" % (_errno, int(_val <> 0), _errno) )
              _xml.append( "<busnr_%s>%s</busnr_%s>" % (_busnr, "".join(_bus_xml) ,_busnr) )
          
          self.send_to_output( 3, "".join(_xml) )

      def set_error_status(self,busnr,errno, val):
          if not self.output_bus_error_status.get(busnr):
              self.output_bus_error_status[busnr] = {}
          self.output_bus_error_status[busnr][errno] = val

      def build_severitydict(self):
          self.severitydict = {}
          for _errno in self.config.get("none").split(","):
              if _errno:
                  self.severitydict[_errno] = None
          for _sev in ['emerg','alert','crit','error','warn','info']:
              for _errno in self.config.get(_sev).split(","):
                  if _errno:
                      self.severitydict[_errno] = _sev
          if self.config.get("default") not in ['emerg','alert','crit','error','warn','info','notice','debug']:
              self.config['default'] = None
      
      def get_severity(self,errno):
          print "get %r" % errno
          return self.severitydict.get( str(errno), self.config.get("default") )

      def debug(self,msg,lvl=5):
          if self.config.get("debug") < lvl:
              return
          import time
          #self.log(msg,severity='debug')
          print "%s DEBUG: %r" % (time.strftime("%H:%M:%S"),msg,)

      def send_to_output(self,out,msg):
          ## werte fangen bei 0 an also AN[1] == Ausgang[0]#
          self.localvars["AN"][out] = msg
          self.localvars["AC"][out] = 1

      def log(self,msg,severity='info'):
          import time
          try:
              from hashlib import md5
          except ImportError:
              import md5 as md5old
              md5 = lambda x,md5old=md5old: md5old.md5(x)
          
          _msg_uid = md5( "%s%s" % ( self.id, time.time() ) ).hexdigest()
          _msg = '<log><id>%s</id><facility>buderus</facility><severity>%s</severity><message>%s</message></log>' % (_msg_uid,severity,msg)
          self.log_queue += _msg 

      def parse(self,payload):
          import time
          _error = self.error_regex.search( payload )
          if _error:
              _busnr = int(_error.group("busnr"),16)
              # nur fehlerstatus > 0
              _error_slots = filter(lambda x: x > 0,[ int(_error.group("slot1"),16), int(_error.group("slot2"),16), int(_error.group("slot3"),16), int(_error.group("slot4"),16) ])
              _active_errors = filter(lambda x,busnr=_busnr: x[0] == busnr, self.active_errors)
              for _err in _error_slots:
                  if (_busnr,_err) not in self.active_errors:
                      self.active_errors.append( (_busnr,_err) )
                      self.set_error_status(_busnr,_err, time.time())
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      _errdict = {
                          'nr'  : _err,
                          'msg' : _err_message,
                          'bus' : _busnr,
                       }
                      _severity = self.get_severity(_err)
                      if _severity:
                          self.log( self.config.get("errormsg") % (_errdict), severity=_severity )
              for (busnr,_err) in _active_errors:
                  if _err not in _error_slots:
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      _errdict = {
                          'nr'  : _err,
                          'msg' : _err_message,
                          'bus' : _busnr,
                       }
                      _severity = self.get_severity(_err)
                      if _severity:
                          self.log( self.config.get("errorclearmsg") % (_errdict), severity='info' )
                      self.active_errors.remove( (busnr,_err) )
                      self.set_error_status( _busnr,_err, 0 )
    
      def incomming(self, payload, localvars):
          self.localvars = localvars
          self.log_queue = ""
          self.debug("incomming message %r" % payload)
          self.parse(payload)
          if self.log_queue:
              self.send_to_output( 1,self.log_queue)
          self.get_status_xml()



"""])

debugcode = """

"""
postlogik=[0,"",r"""

5012|0|"EI"|"buderus_fehler(locals())"|""|0|0|1|0
5012|0|"EC[1]"|"SN[1].incomming(EN[1],locals())"|""|0|0|0|0

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

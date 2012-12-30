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
LOGIKNAME="Buderus-Solar"
## Logik ID
LOGIKID="12282"

## Ordner im GLE
LOGIKCAT="www.knx-user-forum.de"


## Beschreibung
LOGIKDESC="""

"""
VERSION="V0.4"


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

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''_'''+VERSION+'''"|0|8|"E1 Payload IN"|"E2 ECOCAN Bus"|"E3 Betriebsart Stellbereich"|"E4 Umschaltung für Verbraucher"|"E5 Maximaltemperatur SP1"|"E6 Minimaltemperatur SP1"|"E7 Maximaltemperatur SP2"|"E8 Glykolanteil"|59|"A1 Payload OUT"|"A2 SystemLog"|"A3 Fehler Einstellung Hysterese"|"A4 SP2 auf max Temp"|"A5 SP1 auf max Temp"|"A6 Kollektor auf max Temp"|"A7 Fehler Fühler Anlagenrücklauf Bypass"|"A8 Fehler Fühler Speichermitte Bypass"|"A9 Fehler Volumenstromzähler WZ"|"A10 Fehler Fühler Rücklauf"|"A11 Fehler Fühler Vorlauf"|"A12 Fehler Fühler SP2 unten"|"A13 Fehler Fühler SP1 unten"|"A14 Fehler Fühler Kollektor"|"A15 Umschaltventil SP2 zu"|"Umschaltventil SP2 auf/Speicherladepumpe2"|"A17 Umschaltventil Bypass zu"|"A18 Umschaltventil Bypass auf"|"A19 Sekundärpumpe SP2 Betrieb"|"A20 Kollektortemperatur Byte2 0.1°C"|"A21 Kollektortemperatur Byte1 0.1°C"|"A22 SP Modulation 1%"|"A23 Warmwassertemperatur unten 1°C"|"A24 SP1 gesperrt"|"A25 SP1 zu wenig solarer Ertrag"|"A26 SP1 Low Flow"|"A27 SP1 High Flow"|"A28 SP1 Hand ein"|"A29 SP1 Umschalt-Check"|"A30 SP2 Warmwassertemperatur unten"|"A31 SP2 gesperrt"|"A32 SP2 zu wenig solarer Ertrag"|"A33 SP2 Low Flow"|"A34 SP2 High Flow"|"A35 SP2 Hand ein"|"A36 SP2 Umschalt-Check"|"A37 Warmwassertemperatur Speicher mitte"|"A38 Anlagenrücklauf"|"A39 Vorlauftemperatur Wärmemengenzähler"|"A40 Rücklauftemperatur Wärmemengenzähler"|"A41 Anlagen Volumenstrom Byte2 l/h"|"A42 Anlagen Volumenstrom Byte1 l/h"|"A43 Momentan Leistung Solar Byte2 W"|"A44 Momentan Leistung Solar Byte1 W"|"A45 SP1 eingebrachte Wärmemenge Byte3"|"A46 SP1 eingebrachte Wärmemenge Byte2"|"A47 SP1 eingebrachte Wärmemenge Byte1"|"A48 SP2 eingebrachte Wärmemenge Byte3"|"A49 SP2 eingebrachte Wärmemenge Byte2"|"A50 SP2 eingebrachte Wärmemenge Byte1"|"A51 SP1 Betriebsstunden Byte3"|"A52 SP1 Betriebsstunden Byte2"|"A53 SP1 Betriebsstunden Byte1"|"A54 Warmwassersolltemperaturabsenkung Solarertrag 1K"|"A55 Warmwassersolltemperaturabsenkung Wärmekapazität 1K"|"A56 Kollektortemperatur"|"A57 SP2 Betriebsstunden Byte3"|"A58 SP2 Betriebsstunden Byte2"|"A59 SP2 Betriebsstunden Byte1"

5001|8|59|0|1|1

# EN[x]
5002|1|""|1 #* Payload IN
5002|2|1|0 #* ECOCAN Bus ID
5002|3|1|0 #* Betriebsart Stellbereich: 0 – 2 / 0 = Aus / 1 = Auto / 2 = EIN
5002|4|2|0 #* Umschaltung für Verbraucher Stellbereich: 0 - 2 / 0 = Auto / 1 = nur SP1 / 2 = nur SP2
5002|5|60|0 #* Maximaltemperatur SP1 1° genau Stellbereich: 30 - 90 °C
5002|6|55|0 #* Minimaltemperatur SP1 1° genau Stellbereich: 30 - 55 °C
5002|7|60|0 #* Maximaltemperatur SP2 1° genau Stellbereich: 20 - 90 °C
5002|8|5|0 #* Glykolanteil 10% genau Stellbereich:  20 - 50% (2-5)


# Speicher
5003|1||0 #* logic

# Ausgänge
5004|1|""|0|1|1 #* Payload OUT
5004|2|""|0|1|1 #* SystemLog
##Betriebswerte 1
5004|3|0|1|1|0 #* Fehler Einstellung Hysterese
5004|4|0|1|1|0 #* Speicher 2 auf max. Temperatur
5004|5|0|1|1|0 #* Speicher 1 auf max. Temperatur
5004|6|0|1|1|0 #* Kollektor auf max. Temperatur
##Betriebswerte 2
5004|7|0|1|1|0 #* Fehler Fühler Anlagenrücklauf Bypass defekt
5004|8|0|1|1|0 #* Fehler Fühler Speichermitte Bypass defekt
5004|9|0|1|1|0 #* Fehler Volumenstromzähler WZ defekt
5004|10|0|1|1|0 #* Fehler Fühler Rücklauf WZ defekt
5004|11|0|1|1|0 #* Fehler Fühler Vorlauf WZ defekt
5004|12|0|1|1|0 #* Fehler Fühler Speicher-unten 2 defekt
5004|13|0|1|1|0 #* Fehler Fühler Speicher-unten 1 defekt
5004|14|0|1|1|0 #* Fehler Fühler Kollektor defekt
##Betriebswerte 3
5004|15|0|1|1|0 #* Umschaltventil Speicher 2 zu.
5004|16|0|1|1|0 #* Umschaltventil Speicher 2 auf/Speicherladepumpe2.
5004|17|0|1|1|0 #* Umschaltventil Bypass zu
5004|18|0|1|1|0 #* Umschaltventil Bypass auf
5004|19|0|0|1|0 #* Sekundärpumpe Speicher 2 Betrieb
##Kollektortemperatur Byte 2 + Byte 1
5004|20|0|0|1|0 #* Kollektortemperatur Byte2 0,1°C
5004|21|0|0|1|0 #* Kollektortemperatur Byte1 0,1°C
##
5004|22|0|0|1|0 #* SP Modulation Pumpe 1%
##
5004|23|0|0|1|0 #* SP1 Warmwassertemperatur unten 1°C
##Betriebsstatus Speicher 1
5004|24|0|1|1|0 #* SP1 Gesperrt
5004|25|0|1|1|0 #* SP1 zu wenig solarer Ertrag
5004|26|0|1|1|0 #* SP1 Low Flow
5004|27|0|1|1|0 #* SP1 High Flow
5004|28|0|1|1|0 #* SP1 HAND ein
5004|29|0|1|1|0 #* SP1 Umschalt-Check
##
5004|30|0|0|1|0 #* SP2 Warmwassertemperatur unten 1 °C
##Betriebsstatus Speicher 2
5004|31|0|1|1|0 #* SP2 Gesperrt
5004|32|0|1|1|0 #* SP2 zu wenig solarer Ertrag
5004|33|0|1|1|0 #* SP2 Low Flow
5004|34|0|1|1|0 #* SP2 High Flow
5004|35|0|1|1|0 #* SP2 HAND ein
5004|36|0|1|1|0 #* SP2 Umschalt-Check
##
5004|37|0|0|1|0 #* Warmwassertemperatur Speichermitte (Bypass) 1°C
5004|38|0|0|1|0 #* Anlagenrücklauftemperatur (Bypass)
5004|39|0|0|1|0 #* Vorlauftemperatur Wärmemengenzähler 1 °C
5004|40|0|0|1|0 #* Rücklauftemperatur Wärmemengenzähler 1 °C
##Anlagen-Volumenstrom (Byte2 * 256) + Byte1
5004|41|0|0|1|0 #* Anlagen-Volumenstrom Byte2 l/h
5004|42|0|0|1|0 #* Anlagen-Volumenstrom Byte1 l/h
##Momentan-Leistung Solar (Byte2 * 256) + Byte1
5004|43|0|0|1|0 #* Momentan-Leistung Solar Byte2 W
5004|44|0|0|1|0 #* Momentan-Leistung Solar Byte1 W
##eingebrachte Wärmemenge Speicher 1 (Byte3 * 65536) + (Byte2 * 256) + Byte1
5004|45|0|0|1|0 #* SP1 eingebrachte Wärmemenge Byte3
5004|46|0|0|1|0 #* SP1 eingebrachte Wärmemenge Byte2
5004|47|0|0|1|0 #* SP1 eingebrachte Wärmemenge Byte1
##eingebrachte Wärmemenge Speicher 2 (Byte3 * 65536) + (Byte2 * 256) + Byte1
5004|48|0|0|1|0 #* SP2 eingebrachte Wärmemenge Byte3
5004|49|0|0|1|0 #* SP2 eingebrachte Wärmemenge Byte2
5004|50|0|0|1|0 #* SP2 eingebrachte Wärmemenge Byte1
##Betriebsstunden Speicher 1 Byte 3 (Byte3 * 65536) + (Byte2 * 256) + Byte1
5004|51|0|0|1|0 #* SP1 Betriebsstunden Byte3
5004|52|0|0|1|0 #* SP1 Betriebsstunden Byte2
5004|53|0|0|1|0 #* SP1 Betriebsstunden Byte1
##
5004|54|0|0|1|0 #* Warmwassersolltemperaturabsenkung Solarertrag 1 K
##
5004|55|0|0|1|0 #* Warmwassersolltemperaturabsenkung Wärmekapazität 1 K
##
5004|56|0|0|1|0 #* Kollektortemperatur
##Betriebsstunden Speicher 2 Byte 3 (Byte3 * 65536) + (Byte2 * 256) + Byte1
5004|57|0|0|1|0 #* SP2 Betriebsstunden Byte3
5004|58|0|0|1|0 #* SP2 Betriebsstunden Byte2
5004|59|0|0|1|0 #* SP2 Betriebsstunden Byte1
#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
  class buderus_solar(object):
      def __init__(self,localvars):
          import re
		  
          self.logik = localvars["pItem"]
          self.MC = self.logik.MC

          EN = localvars['EN']
          
          self.localvars = localvars
          
          self.current_status = [ ]
          self.status_length = 54
          
          self.bus_id = "%.2X" % int(EN[2])
          self.id = "Solarfunktion"
          self.send_prefix = "B0%.2x24" % (int(EN[2]))

          self.payload_regex = re.compile( "(?P<mode>AB|A7)%s9E(?P<offset>[0-9A-F]{2})(?P<data>(?:[0-9A-F]{2})+)" % ( self.bus_id ) )

          ## Offset Name Auflösung
          ## 0 Betriebswerte 1 
          ##	1. Bit = Fehler Einstellung Hysterese
          ## 	2. Bit = Speicher 2 auf max. Temperatur
          ## 	3. Bit = Speicher 1 auf max. Temperatur
          ## 	4. Bit = Kollektor auf max. Temperatur
          ## 1 Betriebswerte 2 
          ##	1. Bit = Fehler Fühler Anlagenrücklauf Bypass defekt
          ##	2. Bit = Fehler Fühler Speichermitte Bypass defekt
          ##	3. Bit = Fehler Volumenstromzähler WZ defekt
          ## 	4. Bit = Fehler Fühler Rücklauf WZ defekt
          ## 	5. Bit = Fehler Fühler Vorlauf WZ defekt
          ##	6. Bit = Fehler Fühler Speicher-unten 2 defekt
          ##	7. Bit = Fehler Fühler Speicher-unten 1 defekt
          ## 	8. Bit = Fehler Fühler Kollektor defekt
          ## 2 Betriebswerte 3 
          ##	1. Bit = Umschaltventil Speicher 2 zu.
          ## 	2. Bit = Umschaltventil Speicher 2 auf/Speicherladepumpe2.
          ##	3. Bit = Umschaltventil Bypass zu
          ## 	4. Bit = Umschaltventil Bypass auf
          ## 	5. Bit = Sekundärpumpe Speicher 2 Betrieb
          ## 3 Kollektortemperatur Byte2 0,1 °C
          ## 4 Kollektortemperatur Byte1 0,1 °C
          ## 5 Modulation Pumpe Speicher 1 %
          ## 6 Warmwassertemperatur Speicher 1 unten 1 °C
          ## 7 Betriebsstatus Speicher 1
          ## 	Wert = 0: Gesperrt
          ##	Wert = 1: zu wenig solarer Ertrag
          ## 	Wert = 2: Low Flow
          ##	Wert = 3: High Flow
          ##	Wert = 4: HAND ein
          ## 	Wert = 5: Umschalt-Check
          ## 8 Warmwassertemperatur Speicher 2 unten 1 °C
          ## 9 Betriebsstatus Speicher 2 Wert = 0: Gesperrt
          ##	Wert = 1: zu wenig solarer Ertrag
          ##	Wert = 2: Low Flow
          ##	Wert = 3: High Flow
          ## 	Wert = 4: HAND ein
          ##	Wert = 5: Umschalt-Check
          ## 10 Warmwassertemperatur Speichermitte (Bypass) 1 °C
          ## 11 Anlagenrücklauftemperatur (Bypass) 1 °C
          ## 12 Vorlauftemperatur Wärmemengenzähler 1 °C
          ## 13 Rücklauftemperatur Wärmemengenzähler 1 °C
          ## 14 Anlagen-Volumenstrom Byte 2 (Byte2 * 256) + Byte1
          ## 15 Anlagen-Volumenstrom Byte 1 l/h
          ## 16 Momentan-Leistung Solar Byte 2 (Byte2 * 256) + Byte1
          ## 17 Momentan-Leistung Solar Byte 1 W
          ## 18 eingebrachte Wärmemenge (Byte3 * 65536) + (Byte2 * 256) + Byte1 Solar in Speicher 1 Byte 3
          ## 19 eingeb. Wärmem. Sp. 1 Byte 2
          ## 20 eingeb. Wärmem. Sp. 1 Byte 1 100 Wh
          ## 21 eingebrachte Wärmemenge (Byte3 * 65536) + (Byte2 * 256) + Byte1 Solar in Speicher 2 Byte 3
          ## 22 eingeb. Wärmem. Sp. 2 Byte 2
          ## 23 eingeb. Wärmem. Sp. 2 Byte 1 100 Wh
          ## 24 Betriebsstunden Speicher 1 Byte 3 (Byte3 * 65536) + (Byte2 * 256) + Byte1 (Pumpenlaufzeit)
          ## 25 Betriebsstunden Speicher 1 Byte 2
          ## 26 Betriebsstunden Speicher 1 Byte 1 min
          ## 27 Warmwassersolltemperaturabsenkung 1 K durch solaren Ertrag
          ## 28 Warmwassersolltemperaturabsenkung 1 K durch Wärmekapazität (Speicher unten Temperatur)
          ## 29 Kollektortemperatur 1 °C
          ## 30 Betriebsstunden Speicher 2 Byte 3 (Byte3 * 65536) + (Byte2 * 256) + Byte1 (Pumpenlaufzeit)
          ## 31 Betriebsstunden Speicher 2 Byte 2
          ## 32 Betriebsstunden Speicher 2 Byte 1 min
          ## Die mit * gekennzeichneten Werte können nur im "Direkt-Modus" empfangen werden.
 
          self.output_functions = [
              (self.to_bits,[3,4,5,6,0,0,0,0]),
              (self.to_bits,[7,8,9,10,11,12,13,14]),
              (self.to_bits,[15,16,17,18,19,0,0,0]),
              (lambda x: [(float(x)/10)],[20]),
              (lambda x: [(float(x)/10)],[21]),
              (lambda x: [x],[22]),
              (lambda x: [x],[23]),
              (self.to_bits,[24,25,26,27,28,29,0,0]),
              (lambda x: [x],[30]),
              (self.to_bits,[31,32,33,34,35,36,0,0]),
              (lambda x: [x],[37]),
              (lambda x: [x],[38]),
              (lambda x: [x],[39]),
              (lambda x: [x],[40]),
              (lambda x: [x],[41]),
              (lambda x: [x],[42]),			  
              (lambda x: [x],[43]),
              (lambda x: [x],[44]),
              (lambda x: [x],[45]),
              (lambda x: [x],[46]),
              (lambda x: [x],[47]),
              (lambda x: [x],[48]),
              (lambda x: [x],[49]),
              (lambda x: [x],[50]),
              (lambda x: [x],[51]),
              (lambda x: [x],[52]),
              (lambda x: [x],[53]),
              (lambda x: [x],[54]),
              (lambda x: [x],[55]),
              (lambda x: [x],[56]),
              (lambda x: [x],[57]),
              (lambda x: [x],[58]),
              (lambda x: [x],[59]),
          ]

          self.get_monitor_data()

      def get_monitor_data(self):
          self.send_to_output(1,"A2%s" % self.bus_id)

      def debug(self,msg):
          #self.log(msg,severity='debug')
          print "DEBUG: %r" % (msg,)

      def send_to_output(self,out,msg,sbc=False):
          if sbc and msg == self.localvars["AN"]:
              return
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
          self.send_to_output( 2, _msg )

      def parse(self,offset, data):
          offset = int(offset,16)
          #if offset > len(self.current_status):
          #    self.debug("Daten offset größer als vorhandene Daten")
          #    return
          _len = len(data)
          #self.current_status = self.current_status[:offset] + [ _x for _x in data ] + self.current_status[offset + _len:]
          for _x in xrange(_len):
              _offset = offset + _x
              _func, _out = self.output_functions[_offset]
              _ret = _func( ord(data[_x]) )
              for _xx in xrange(len(_ret)):
                  self.send_to_output(_out[_xx] , _ret[_xx], sbc=True)
              
          #self.debug("Zustand: %r" % (self.current_status,) )

      def to_bits(self,byte):
          return [(byte >> i) & 1 for i in xrange(8)]

      def incomming(self,msg, localvars):
          import binascii
          self.localvars = localvars
          self.debug("incomming message %r" % msg)
          msg = msg.replace(' ','')
          _data = self.payload_regex.search(msg)
          if _data:
              self.parse( _data.group("offset"), binascii.unhexlify(_data.group("data")) )

      def set_value(self, val, offset, byte,localvars, min=-99999, max=99999, resolution=1):
          self.localvars = localvars
          if val < min or val > max:
              self.log("ungültiger Wert %r (%s-%s)" % (val,min,max) )
          _val = val * resolution
          if _val < 0:
              (_val * -1) + 128
          _6bytes = [ "65","65","65","65","65","65" ]
          _6bytes[byte - 1] = "%.2x" % round(_val)
          self.send_to_output(1,"%s%s%s" % (self.send_prefix, offset.upper(), "".join(_6bytes).upper() ) )


"""])


debugcode = """

"""
postlogik=[0,"",r"""
5012|0|"EI"|"buderus_solar(locals())"|""|0|0|1|0
5012|0|"EC[1]"|"SN[1].incomming(EN[1],locals())"|""|0|0|0|0

#* Betriebsart Stellbereich: 0 – 2 / 0 = Aus / 1 = Auto / 2 = EIN
5012|0|"EC[3]"|"SN[1].set_value(EN[3], offset='00', byte=5, min=0, max=2, resolution=1, localvars=locals())"|""|0|0|0|0

#* Umschaltung für Verbraucher Stellbereich: 0 - 2 / 0 = Auto / 1 = nur SP1 / 2 = nur SP2
5012|0|"EC[4]"|"SN[1].set_value(EN[4], offset='00', byte=6, min=0, max=2, resolution=1, localvars=locals())"|""|0|0|0|0

#* Maximaltemperatur SP1 1° genau Stellbereich: 30 - 90 °C
5012|0|"EC[5]"|"SN[1].set_value(EN[5], offset='07', byte=1, min=30, max=90, resolution=1, localvars=locals())"|""|0|0|0|0

#* Minimaltemperatur SP1 1° genau Stellbereich: 30 - 55 °C
5012|0|"EC[6]"|"SN[1].set_value(EN[6], offset='07', byte=2, min=30, max=55, resolution=1, localvars=locals())"|""|0|0|0|0

#* Maximaltemperatur SP2 1° genau Stellbereich: 20 - 90 °C
5012|0|"EC[7]"|"SN[1].set_value(EN[7], offset='0E', byte=5, min=20, max=90, resolution=1, localvars=locals())"|""|0|0|0|0

#* Glykolanteil 10% genau Stellbereich:  20 - 50% (0-5)
5012|0|"EC[8]"|"SN[1].set_value(EN[8], offset='1C', byte=1, min=0, max=5, resolution=10, localvars=locals())"|""|0|0|0|0
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

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
LOGIKNAME="Buderus-Konfiguration"
## Logik ID
LOGIKID="12284"

## Ordner im GLE
LOGIKCAT="www.knx-user-forum.de\Buderus"


## Beschreibung
LOGIKDESC="""
Dieser Baustein wertet alle Daten für den Datentyp 0x89 Konfiguration, die vom Buderus Baustein 12264 kommen, aus und gibt
 die Zustände auf die entsprechenden Ausgänge aus. 
 <div class="hinw">
 Wichtig: Eingang 1 und Ausgang 1 dürfen NIE direkt mit dem Buderus Baustein 12264 verbunden werden. Bitte immer die 
 Verbindung indirekt über ein iKO herstellen !!!! 
</div>
 Auf Eingang 1 werden die Daten vom Buderus Baustein empfangen. Auf dem Eingang 2 stellt man die Adresse 
 des Regelgerätes ein. 
 
 Hier ein Tip: Man kann im SystemLog des Buderus Bausteines sehen, an welchen Regelgeräten welche DatenTypen
 erkannt wurden.  Hier ist der DatenTyp Solar relevant. Ist dieser am Regelgerät 2 erkannt worden, ist hier 
 eine 2 einzugeben. 
 
 Damit werden nunmehr aus dem gesamten Datenstrom des ECOCAN Bus nur noch genau diese Daten gefilter und auf 
 den Ausgängen ausgegeben.
 <div class="hinw">
 Allgemeines: Ein Istwert von 110 °C beschreibt für den betroffenen Fühler einen Fühler defekt. Es kann auch sein,
 das hier einfach kein Fühler angeschlossen wurde. Messwerte in diesem Bereich hören bei 109 auf und gehen bei 111 weiter. 
</div>

Für die eigentliche Kommunikation sind zwingend folgende Beschreibungen von Buderus zu beachten:
7747004149 – 01/2009 DE - Technische Information - Monitordaten - System 4000
7747004150 – 05/2009 DE - Technische Information - Einstellbare Parameter - Logamatic 4000

D
"""
VERSION="V1.0"


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

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''_'''+VERSION+'''"|0|2|"E1 Payload IN"|"E2 ECOCAN Bus ID"|20|"A1 SystemLog"|"A2 Außentemperatur"|"A3 gedämpfte Außentemperatur"|"A4 Version"|"A5 Modul in Slot 1"|"A6 Modul in Slot 2"|"A7 Modul in Slot 3"|"A8 Modul in Slot 4"|"A9 Modul in Slot A"|"A10 Fehler bei Slot 1"|"A11 Fehler bei Slot 2"|"A12 Fehler bei Slot 3"|"A13 Fehler bei Slot 4"|"A14 Fehler bei Slot A"|"A15 Anlagenvorlaufsolltemperatur"|"A16 Anlagenvorlaufisttemperatur"|"A17 Betriebsflags der Anlage"|"A18 Max. Anst. Heizkreispumpe"|"A19 Max. Anst. Stellglied"|"A20 Regelg. Vorlaufisttemp."

5001|2|20|0|3|1

# EN[x]
5002|1|""|1 #* Payload IN
5002|2|1|0 #* ECOCAN Bus ID des Regelgerätes

# Speicher
5003|1||0 #* logic
5003|2||0 #* Version (Vorkomma)
5003|3||0 #* Version (Nachkomma)

# Ausgänge
5004|1|""|0|1|1 #* SystemLog
5004|2|0|0|1|0 #* Außentemperatur (in °C) 
5004|3|0|0|1|0 #* gedämpfte Außentemperatur (in °C)
5004|4|""|0|1|1 #* Version des Bus (Vorkomma.Nachkomma) 
5004|5|""|0|1|1 #* Modul in Slot 1  
5004|6|""|0|1|1 #* Modul in Slot 2  
5004|7|""|0|1|1 #* Modul in Slot 3  
5004|8|""|0|1|1 #* Modul in Slot 4  
5004|9|""|0|1|1 #* Modul in Slot A 
5004|10|""|0|1|1 #* Fehler bei Slot 1 
5004|11|""|0|1|1 #* Fehler bei Slot 2 
5004|12|""|0|1|1 #* Fehler bei Slot 3 
5004|13|""|0|1|1 #* Fehler bei Slot 4 
5004|14|""|0|1|1 #* Fehler bei Slot A 
5004|15|0|0|1|0 #* Anlagenvorlaufsolltemperatur (in °C) 
5004|16|0|0|1|0 #* Anlagenvorlaufisttemperatur (in °C) 
5004|17|0|0|1|0 #* Betriebsflags der Anlage 
5004|18|0|0|1|0 #* Max. Ansteuerung für Heizkreispumpe (in %) 
5004|19|0|0|1|0 #* Max. Ansteuerung für Stellglied (in %) 
5004|20|0|0|1|0 #* Regelgerätevorlaufisttemperatur (in °C) 

#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
  class buderus_konfiguration(object):
      def __init__(self,localvars):
          import re

          self.logik = localvars["pItem"]
          self.MC = self.logik.MC

          EN = localvars['EN']
          
          self.localvars = localvars
          
          self.current_status = [ ]
          self.status_length = 18
          
          self.bus_id = "%.2X" % int(EN[2])
          self.id = "Konfiguration"
          self.send_prefix = "B0%.2x0C" % (int(EN[2]))

          self.payload_regex = re.compile( "(?P<mode>AB|A7)%s89(?P<offset>[0-9A-F]{2})(?P<data>(?:[0-9A-F]{2})+)" % ( self.bus_id ) )

          ## Offset   Name    Auflösung
          ##  0 Außentemperatur 1 °C (Werte größer 128 = negativ)                ## Ausgang 3
          ##  1 gedämpfte Außentemperatur 1 °C (Werte größer 128 = negativ)        ## Ausgang 4
          ##  2 Version Vorkomma *                                                ## Ausgang 5
          ##  3 Version Nachkomma *                                                ## Ausgang 5
          ##  4 FREI *
          ##  5 FREI *
          ##  6 Modul in Slot 1   Die Bedeutung der Werte :                        ## Ausgang 6
          ##                      0 = defekt
          ##                      1 = frei
          ##                      2 = ZM432 (Kessel für 4311)
          ##                      3 = FM442 (2x Heizkreis)
          ##                      4 = FM441 (1x Heizkreis + 1x Warmwasser)
          ##                      5 = FM447 (Strategie)
          ##                      6 = ZM432 (Kessel für 4211, Warmwasser +
          ##                                 1x ungemischter Heizkreis)
          ##                      7 = FM445 (LAP – Modul)
          ##                      8 = FM451 (KSE1)
          ##                      9 = FM454 (KSE4)
          ##                      10 = ZM424 (Kessel für 4111,Heizkreise,WW)
          ##                      11 = UBA
          ##                      12 = FM452 (KSE2)
          ##                      13 = FM448 (Störmeldemodul)
          ##                      14 = ZM433 (Unterstation mit Pumpe und
          ##                                 1 x gemischter Heizkreis)
          ##                      15 = FM446 EIB – Modul
          ##                      16 = FM443 Solarmodul
          ##                      21 = FM444 Alternativer Wärmeerzeuger - Modul
          ##  7 Modul in Slot 2                                                    ## Ausgang 7
          ##  8 Modul in Slot 3                                                    ## Ausgang 8
          ##  9 Modul in Slot 4                                                    ## Ausgang 9
          ##  10 Modul in Slot A                                                   ## Ausgang 10
          ##  11 FREI
          ##  12 Fehler bei Slot 1 *   Bedeutung der Werte:                        ## Ausgang 11
          ##                           0 = kein Fehler 
          ##                           1 = unbekanntes Modul
          ##                           2 = Fehler bei CAN – Adresse
          ##                           3 = SOLL // IST – Fehler
          ##                           4 = keine Antwort
          ##                           5 = Handbetrieb
          ##  13 Fehler bei Slot 2 *                                            ## Ausgang 12
          ##  14 Fehler bei Slot 3 *                                            ## Ausgang 13
          ##  15 Fehler bei Slot 4 *                                            ## Ausgang 14
          ##  16 Fehler bei Slot A *                                            ## Ausgang 15
          ##  17 FREI *
          ##  18 Anlagenvorlaufsolltemperatur 1 °C                              ## Ausgang 16
          ##  19 Anlagenvorlaufisttemperatur 1 °C                               ## Ausgang 17
          ##  20 Betriebsflags der Anlage     Bedeutung der Werte               ## Ausgang 18
          ##                                  1 = Pufferspeicher bleibt kalt        
          ##                                  2 = Fühler UST-FK defekt
          ##                                  3 = Wartezeit läuft
          ##  21 Max. Ansteuerung für Heizkreispumpe 1 %                        ## Ausgang 19
          ##  22 max. Ansteuerung für Stellglied 1 %                            ## Ausgang 20
          ##  23 Regelgerätevorlaufisttemperatur 1 °C                           ## Ausgang 21

          ## Buderus Fehlermeldungen
          self.slot_module = {
              0 : "defekt",
              1 : "frei",
              2 : "ZM432", #(Kessel für 4311)",
              3 : "FM442", #(2x Heizkreis)",
              4 : "FM441", #(1x Heizkreis + 1x Warmwasser)",
              5 : "FM447", #(Strategie)",
              6 : "ZM432", #(Kessel für 4211, WW + 1x ungem. Heizkreis)",
              7 : "FM445", #(LAP – Modul)",
              8 : "FM451", #(KSE1)",
              9 : "FM454", #(KSE4)",
             10 : "ZM424", #(Kessel für 4111,Heizkreise,WW)",
             11 : "UBA",
             12 : "FM452", #(KSE2)",
             13 : "FM448", #(Störmeldemodul)",
             14 : "ZM433", #(Unterstation m. Pumpe u. 1 x gem. Heizkreis)",
             15 : "FM446", #EIB – Modul",
             16 : "FM443", #Solarmodul",
             21 : "FM444", #Alternativer Wärmeerzeuger Modul",
          }
          
          self.slot_error = {
              0 : "kein Fehler",
              1 : "unbekanntes Modul",
              2 : "Fehler bei CAN – Adresse",
              3 : "SOLL // IST – Fehler",
              4 : "keine Antwort",
              5 : "Handbetrieb",
          }

          self.output_functions = [
              (self.to_128,[2],"AN"),
              (self.to_128,[3],"AN"),
              (lambda x: [x],[2],"SN"),
              (lambda x: [x],[3],"SN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [self.slot_module[x]],[5],"AN"),
              (lambda x: [self.slot_module[x]],[6],"AN"),
              (lambda x: [self.slot_module[x]],[7],"AN"),
              (lambda x: [self.slot_module[x]],[8],"AN"),
              (lambda x: [self.slot_module[x]],[9],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [self.slot_error[x]],[10],"AN"),
              (lambda x: [self.slot_error[x]],[11],"AN"),
              (lambda x: [self.slot_error[x]],[12],"AN"),
              (lambda x: [self.slot_error[x]],[13],"AN"),
              (lambda x: [self.slot_error[x]],[14],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[15],"AN"),
              (lambda x: [x],[16],"AN"),
              (lambda x: [x],[17],"AN"),
              (lambda x: [x],[18],"AN"),
              (lambda x: [x],[19],"AN"),
              (lambda x: [x],[20],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
              (lambda x: [x],[0],"AN"),
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
              _func, _out, _feld = self.output_functions[_offset]
              _ret = _func( ord(data[_x]) )
              for _xx in xrange(len(_ret)):
                  if _feld == "AN":
                     self.send_to_output(_out[_xx] , _ret[_xx], sbc=True)
                  else:
                     self.localvars[_feld][_out[_xx]] = _ret[_xx]
                     self.localvars["SC"][_out[_xx]] = 1
              
          #self.debug("Zustand: %r" % (self.current_status,) )

      def to_bits(self,byte):
          return [(byte >> i) & 1 for i in xrange(8)]

      def to_128(self,value):
          if (value > 128): 
             return [(value - 128) * -1]
          else:
             return [value]

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
5012|0|"EI"|"buderus_konfiguration(locals())"|""|0|0|1|0
5012|0|"EC[1]"|"SN[1].incomming(EN[1],locals())"|""|0|0|0|0

#* Version Vorkomma.Nachkomma
5012|0|"SC[2] or SC[3]"|"str(SN[2])+"."+str(SN[3])"|""|4|0|0|0

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

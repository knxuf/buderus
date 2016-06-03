# -*# -*- coding: iso8859-1 -*-
## -----------------------------------------------------
## Logik-Generator  V1.5
## -----------------------------------------------------
## Copyright � 2012, knx-user-forum e.V, All rights reserved.
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
LOGIKCAT="www.knx-user-forum.de\Buderus"


## Beschreibung
LOGIKDESC="""
Dieser Baustein wertet alle Fehler aus, die vom Buderus Baustein 12264 kommen und gibt die Fehlerinformationen
 auf die entsprechenden Ausg�nge aus. Der Baustein tut dies f�r alle angeschlossenen Regelger�te.
 Der Baustein ist also nur einmal pro ECOCAN Bus notwendig.
 <div class="acht">
 Wichtig: Der Eingang 1 darf NIE direkt mit dem Buderus Baustein verbunden werden. Bitte immer die 
 Verbindung indirekt �ber ein iKO herstellen !!!! 
</div>
Zitat aus der Buderus Beschreibung: Technische Information - Monitordaten - System 4000
<i>Ein Regelger�t am ECOCAN-BUS kann zur Zeit ca. 213 verschiedene Fehler erzeugen. Bei der Zahl von
15 Regelger�ten am ECOCAN-BUS m��ten somit ca. 1500 Fehlerquellen auf "Kommen" bzw. "Gehen"
untersucht werden. Da die Verarbeitung einer so gro�en Zahl von Fehlermeldungen unrealistisch
erscheint, werden nur die zur Zeit offenen Fehler aus dem Fehlerprotokoll (z. Zt. 4 St�ck) an die
Kommunikationskarte �bergeben.
</i>
 Auf Eingang 1 werden die Daten vom Buderus Baustein empfangen. Auf dem Eingang 2 kann man sp�ter 
 mal etwas konfigurieren. 
 <div class="hinw">
 <i>Hier ein Tip:</i> Man kann im SystemLog des Buderus Bausteines sehen, an welchen Regelger�ten welche DatenTypen
 erkannt wurden.  Wenn man es so als St�rung konfiguriert hat, kann man durch die Handschalter an der Regelung
 auch Fehler/St�rungen manuel setzten und l�schen. So kann man die Funktion leicht testen. 
 </div>
 Damit werden nunmehr aus dem gesamten Datenstrom des ECOCAN Bus nur noch die Fehler  
 gefilter und auf den Ausg�ngen ausgegeben. Der Fehlerstatus wird auf dem ECOCAN Bus, 
 au�er nach einem Reset der Kommunikationskarte, nur bei einer �nderung versendet. 

 <div class="hinw">
 <i>Allgemeines:</i> Ein Istwert von 110 �C beschreibt f�r den betroffenen F�hler einen F�hler defekt. Es kann auch sein,
 das hier einfach kein F�hler angeschlossen wurde. Messwerte in diesem Bereich h�ren bei 109 auf und gehen bei 111 weiter. 
</div>

Alle Fehlertexte und Fehlercodes/nummern sind in folgender Beschreibungen von Buderus nachzulesen:
7747004149 - 01/2009 DE - Technische Information - Monitordaten - System 4000

Ausgegeben werden die Fehler einmal auf den SystemLog Ausgang 1 sowie auf den XML Ausgang 3. Mit dem Ausgang 2 wird angezeigt,
ob es auf dem ECOCAN Bus ingesamt einen Fehler gibt. 
Auf dem Ausgang 3 gibt es f�r jedes Regelger�t so einen XML Block:

<p>&lt;busnr_1&gt;<br />
    &lt;errno_34&gt;1&lt;/errno_34&gt;<br />
    &lt;errno_35&gt;1&lt;/errno_35&gt;<br />
    &lt;slot_0&gt;<br />
        &lt;errno&gt;35&lt;/errno&gt;<br />
        &lt;errmsg&gt;Vorlauff�hler HK6 defekt !&lt;/errmsg&gt;<br />
        &lt;errtime&gt;18:09:59 10.06.2014&lt;/errtime&gt;<br />
    &lt;/slot_0&gt;<br />
    &lt;slot_1&gt;<br />
        &lt;errno&gt;34&lt;/errno&gt;<br />
        &lt;errmsg&gt;Vorlauff�hler HK5 defekt !&lt;/errmsg&gt;<br />
        &lt;errtime&gt;18:09:59 10.06.2014&lt;/errtime&gt;<br />
    &lt;/slot_1&gt;<br />
    &lt;slot_2&gt;<br />
        &lt;errno&gt;&lt;/errno&gt;<br />
        &lt;errmsg&gt;&lt;/errmsg&gt;<br />
        &lt;errtime&gt;&lt;/errtime&gt;<br />
    &lt;/slot_2&gt;<br />
    &lt;slot_3&gt;<br />
        &lt;errno&gt;&lt;/errno&gt;<br />
        &lt;errmsg&gt;&lt;/errmsg&gt;<br />
        &lt;errtime&gt;&lt;/errtime&gt;<br />
    &lt;/slot_3&gt;<br />
&lt;/busnr_1&gt;</p>

"""
VERSION="V0.10"


## Bedingung wann die kompilierte Zeile ausgef�hrt werden soll
BEDINGUNG="EI"
## Formel die in den Zeitspeicher geschrieben werden soll
ZEITFORMEL=""
## Nummer des zu verwenden Zeitspeichers
ZEITSPEICHER="0"

## AUF True setzen um Bin�ren Code zu erstellen
doByteCode=False
#doByteCode=True

## Base64Code �ber SN[x] cachen
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
## Copyright � '''+ time.strftime("%Y") + ''', knx-user-forum e.V, All rights reserved.
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

#5000|"Text"|Remanent(1/0)|Anz.Eing�nge|.n.|Anzahl Ausg�nge|.n.|.n.
#5001|Anzahl Eing�nge|Ausg�nge|Offset|Speicher|Berechnung bei Start
#5002|Index Eingang|Default Wert|0=numerisch 1=alphanummerisch
#5003|Speicher|Initwert|Remanent
#5004|ausgang|Initwert|runden bin�r (0/1)|typ (1-send/2-sbc)|0=numerisch 1=alphanummerisch
#5012|abbruch bei bed. (0/1)|bedingung|formel|zeit|pin-ausgang|pin-offset|pin-speicher|pin-neg.ausgang

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''"|0|2|"E1 Payload IN"|"E2 Config"|3|"A1 SystemLog"|"A2 St�rung"|"A2 St�rstatus XML"|"'''+VERSION+'''"

5001|2|3|0|1|1

# EN[x]
5002|1|""|1 #* Payload IN
5002|2|""|1 #* config

# Speicher
5003|1||0 #* logic

# Ausg�nge
5004|1|""|0|1|1 #* SystemLog
5004|2|0|1|1|0 #* St�rung Flag (insgesamt f�r den ECOCAN Bus)
5004|3|""|0|1|1 #* St�rstatus XML

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

          ## Speicher f�r lokale Variablen (muss eingehend immer wieder aktualisiert werden f�r AN/AC....
          self.localvars = localvars

          ## Default Konfiguration
          self.config = {
              'debug'         : 2,
              'errormsg'      : 'St�rmeldung an Regelger�t %(bus)s: %(msg)s',
              'errorclearmsg' : 'St�rmeldung an Regelger�t %(bus)s: %(msg)s (behoben)',
              'timeformat'    : '%H:%M:%S %d.%m.%Y',
              'emerg'    : '',
              'alert'    : '',
              'crit'     : '',
              'error'    : '',
              'warn'     : '',
              'info'     : '',
              'none'     : '',
              'default'  : 'error',
          }
          
          ## Ger�tetypen
          self.device_types = {
              "80" : ("Heizkreis 1", 18),
              "81" : ("Heizkreis 2", 18),
              "82" : ("Heizkreis 3", 18),
              "83" : ("Heizkreis 4", 18),
              "84" : ("Warmwasser", 12),
              "85" : ("Strategie wandh�ngend", 12),
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
              "92" : ("wandh�ngende Kessel 1", 60),
              "93" : ("wandh�ngende Kessel 2", 60),
              "94" : ("wandh�ngende Kessel 3", 60),
              "95" : ("wandh�ngende Kessel 4", 60),
              "96" : ("wandh�ngende Kessel 5", 60),
              "97" : ("wandh�ngende Kessel 6", 60),
              "98" : ("wandh�ngende Kessel 7", 60),
              "99" : ("wandh�ngende Kessel 8", 60),
              "9B" : ("W�rmemenge", 36),
              "9C" : ("St�rmeldemodul", 6),
              "9D" : ("Unterstation", 6),
              "9E" : ("Solarfunktion", 54),
          }

          ## Buderus Fehlermeldungen
          self.error_messages = {
              0 : "kein Fehler",
              1 : "Strategievorlauff�hler defekt !",
              2 : "Aussenf�hler defekt !",
              3 : "Vorlauff�hler HK1 defekt !",
              4 : "Vorlauff�hler HK2 defekt !",
              5 : "Vorlauff�hler HK3 defekt !",
              6 : "Vorlauff�hler HK4 defekt !",
              7 : "nicht belegt !",
              8 : "Warmwasserf�hler defekt !",
              9 : "Warmwasser bleibt kalt !",
              10 : "St�rung Therm. Desinfektion !",
              11 : "Fernbedienung HK 1 defekt !",
              12 : "Fernbedienung HK 2 defekt !",
              13 : "Fernbedienung HK 3 defekt !",
              14 : "Fernbedienung HK 4 defekt !",
              15 : "keine Kommun. mit Fernbed. HK 1!",
              16 : "keine Kommun. mit Fernbed. HK 2!",
              17 : "keine Kommun. mit Fernbed. HK 3!",
              18 : "keine Kommun. mit Fernbed. HK 4!",
              19 : "nicht belegt !",
              20 : "St�rung Brenner 1",
              21 : "St�rung Brenner 2",
              22 : "St�rung Brenner 3",
              23 : "St�rung Brenner 4",
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
              34 : "Vorlauff�hler HK5 defekt !",
              35 : "Vorlauff�hler HK6 defekt !",
              36 : "Vorlauff�hler HK7 defekt !",
              37 : "Vorlauff�hler HK8 defekt !",
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
              49 : "Kesselvorlauff�hler defekt !",
              50 : "Kesselzusatzf�hler defekt !",
              51 : "Kessel bleibt kalt !",
              52 : "Brennerst�rung !",
              53 : "St�rung Sicherheitskette !",
              54 : "Externe St�rung Kessel !",
              55 : "Abgasf�hler defekt !",
              56 : "Abgasgrenze �berschritten !",
              57 : "Externer St�reing. (Pumpe) HK1 !",
              58 : "Externer St�reing. (Pumpe) HK2 !",
              59 : "Externer St�reing. (Pumpe) HK3 !",
              60 : "Externer St�reing. (Pumpe) HK4 !",
              61 : "Externer St�reing. (Pumpe) HK5 !",
              62 : "Externer St�reing. (Pumpe) HK6 !",
              63 : "Externer St�reing. (Pumpe) HK7 !",
              64 : "Externer St�reing. (Pumpe) HK8 !",
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
              87 : "R�cklauff�hler defekt !",
              88 : "Ext. St�reingang (Inertanode) WW !",
              89 : "Ext. St�reingang (Pumpe) WW !",
              90 : "Konfig. R�cklauf bei Strategie!",
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
              105 : "Handschalter LAP Prim�rpumpe !",
              106 : "Handschalter LAP Sekund�rpumpe !",
              107 : "W�rmetauscherf�hler LAP defekt !",
              108 : "Speicher unten F�hler LAP defekt !",
              109 : "Warmwasser Solarf�hler defekt !",
              110 : "Kollektorf�hler defekt !",
              111 : "St�rung Brenner 5",
              112 : "St�rung Brenner 6",
              113 : "St�rung Brenner 7",
              114 : "St�rung Brenner 8",
              115 : "keine Verbindung mit Brennerautomat 1",
              116 : "keine Verbindung mit Brennerautomat 2",
              117 : "keine Verbindung mit Brennerautomat 3",
              118 : "keine Verbindung mit Brennerautomat 4",
              119 : "keine Verbindung mit Brennerautomat 5",
              120 : "keine Verbindung mit Brennerautomat 6",
              121 : "keine Verbindung mit Brennerautomat 7",
              122 : "keine Verbindung mit Brennerautomat 8",
              123 : "Flaschenvorlauff�hler defekt",
              124 : "3-Wegeumschaltventil defekt",
              125 : "F�llstand: Grenze unterschritten",
              126 : "Unterstation W�rme Unterversorgung !",
              127 : "Unterstation Vorlauff�hler defekt !",
              128 : "Kollektorf�hler defekt !",
              129 : "Bypass-R�cklauff�hler defekt !",
              130 : "Bypass-Vorlauff�hler defekt !",
              131 : "W�rmemengenz�hler Vorlauf defekt !",
              132 : "W�rmemengenz�hler R�cklauf defekt !",
              133 : "Speicher 1 F�hler unten defekt !",
              134 : "Speicher 2 F�hler unten defekt !",
              135 : "W�rmemengenz�hler Volumenstrommesser !",
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
              164 : "St�rung EMS - Kessel 1 !",
              165 : "St�rung EMS - Kessel 2 !",
              166 : "St�rung EMS - Kessel 3 !",
              167 : "St�rung EMS - Kessel 4 !",
              168 : "St�rung EMS - Kessel 5 !",
              169 : "St�rung EMS - Kessel 6 !",
              170 : "St�rung EMS - Kessel 7 !",
              171 : "St�rung EMS - Kessel 8 !",
              172 : "St�rung EMS - Warmwasser !",
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
              183 : "Alternativer WE R�cklauff�hler defekt !",
              184 : "Alternativer WE Vorlauff�hler defekt !",
              185 : "Alternativer WE F�hler Puffer mitte !",
              186 : "Alternativer WE F�hler Puffer unten !",
              187 : "Alternativer WE F�hler Puffer oben !",
              188 : "Alternativer WE Anl. R�cklauff�hler !",
              189 : "Alternativer WE Abgasf�hler defekt !",
              190 : "Alternativer WE Kommunikation Brennerautomat !",
              191 : "Alternativer WE Brennerautomat verriegelt !",
              192 : "Alternativer WE Notk�hlung ausgel�st !",
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
              209 : "FM458 F�hler Vorlauf Strategie !",
              210 : "FM458 F�hler R�cklauf Strategie !",
              211 : "FM458 Konfiguration R�cklauf Strategie!",
              212 : "FM458 Konfiguration Vorlauf Strategie !",
              213 : "FM458 Leistungsangabe f�r Kessel fehlt !",
          }
          
          ## derzeit aktive Fehler
          self.active_errors = []
          
          ## Status f�r ausgaben je Bus/Slot/Fehlernummer
          self.output_bus_error_status = {}
          
          ## Konfiguration an Eingang 2 parsen
          self.readconfig(EN[2])
          
          ## Ein Dict f�r default Severity's je Buderus Fehlermeldung erstellen
          self.build_severitydict()
          
          ## Queue um mehrere Logmeldungen auf den Ausgang zu schreiben
          self.log_queue = ""

          ## Regex f�r Fehlermeldungen
          ## <Kennung Fehlerstatus(0xAE)> <Ger�teadresse> < Fehler 1> < Fehler 2> < Fehler 3> < Fehler 4>
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
          ## leere List f�r alle Ausgaben
          _xml = []
          
          ## alle derzeitigen items des dicts durchlaufen (enthalten je busnr ein Dict mit Fehlernummern)
          for _busnr,_errno_status_dict in self.output_bus_error_status.iteritems():
              
              ## leere Liste f�r ausgaben des Bus
              _bus_xml = []
              
              ## Alle Fehler, Zeit werte des Dicts durchlaufen
              for _errno,_val in _errno_status_dict.iteritems():
                  
                  ## wenn wert(zeit des Fehlers als timestamp) <> 0 dann Fehler aktiv
                  _bus_xml.append("<errno_%s>%s</errno_%s>" % (_errno, int(_val <> 0), _errno) )
              
              ## alle derzeit aktiven Fehler f�r diesen Bus
              _active_errors = filter(lambda x,busnr=_busnr: x[0] == busnr, self.active_errors)
              
              ## Alle 4 Fehlerslots
              for _slot in xrange(4):
                  
                  ## default status ist alle wert f�r die xml2test/xml2num Bausteine l�schen
                  _status = "<errno>0</errno><errmsg></errmsg><errtime></errtime>"
                  
                  ## Wenn Slotnummer gef�llt
                  if len(_active_errors) > _slot:
                      ## nur die Fehlernummer des Slots holen
                      (_dummy, _err) = _active_errors[_slot]
                      
                      ## Fehlertext aus dem Dict dazu
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      
                      ## Fehlerzeit steht im dict
                      _err_time = self.get_error_status(_busnr,_err)
                      if _err_time > 0:
                          ## Fehlerzeit als lesbaren Wert wie in Config
                          _err_time = time.strftime(self.config.get('timeformat'),time.localtime(_err_time) )
                      else:
                          _err_time = "unbekannt"
                      
                      ## Werte ins XML f�llen
                      _status ="<errno>%s</errno><errmsg>%s</errmsg><errtime>%s</errtime>" % (_err,_err_message,_err_time) 
                  
                  ## xml zum jeweiligen Slot dazu schrieben
                  _bus_xml.append("<slot_%s>%s</slot_%s>" % (_slot,_status ,_slot) )
              
              ## List mit Text f�r den Bus zum allgemeinen xml schreiben
              _xml.append( "<busnr_%s>%s</busnr_%s>" % (_busnr, "".join(_bus_xml) ,_busnr) )
          
          ## Auf Ausgang 3 schreiben
          self.send_to_output( 3, "".join(_xml) )

      def set_error_status(self,busnr,errno, val):
          ## wenn es noch keinen Eintrag f�r das Ger�t gibt
          if not self.output_bus_error_status.get(busnr):
              ## dict f�r Bus
              self.output_bus_error_status[busnr] = {}
          
          ## Wert setzen auf Wert 
          self.output_bus_error_status[busnr][errno] = val

      def get_error_status(self,busnr,errno):
          ## Wert abfragen leeres dict zur�ck wenn nicht gefunden f�r n�chstes .get
          _bus_dict = self.output_bus_error_status.get(busnr,{})
          ## 0 oder Wert zur�ck
          return _bus_dict.get(errno,0)

      def build_severitydict(self):
          ## dict f�r severity je Buderus Fehler
          self.severitydict = {}
          
          ## alle Werte von Konfig none auslesen und zum dict
          for _errno in self.config.get("none").split(","):
              if _errno:
                  self.severitydict[_errno] = None
          
          ## f�r genannte Severity die Konfig durchsuchen
          for _sev in ['emerg','alert','crit','error','warn','info']:
              
              ## Konfig splitten mit ,
              for _errno in self.config.get(_sev).split(","):
                  ## wenn Wert
                  if _errno:
                      ## die jeweilige severity allen Werten in der config zu ordnen
                      self.severitydict[_errno] = _sev
          
          # wenn keine g�ltiger wert in default dann logging auf None
          if self.config.get("default") not in ['emerg','alert','crit','error','warn','info','notice','debug']:
              self.config['default'] = None
      
      def get_severity(self,errno):
          return self.severitydict.get( str(errno), self.config.get("default") )

      def debug(self,msg,lvl=5):
          if self.config.get("debug") < lvl:
              return
          import time
          
          self.log(msg,severity='debug')
          #print "%s DEBUG: %r" % (time.strftime("%H:%M:%S"),msg,)

      def send_to_output(self,out,msg,sbc=False):
          if sbc and msg == self.localvars["AN"][out] and not self.localvars["EI"] == 1:
              return
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
          found = 0
          
          ## Payload nach Fehlerregex ## <Kennung Fehlerstatus(0xAE)> <Ger�teadresse> < Fehler 1> < Fehler 2> < Fehler 3> < Fehler 4> durchsuchen
          _error = self.error_regex.search( payload )
          if _error:
              # 0xAE gefunden
              found = 1
              ## Busnr ist Hex wandeln in Int Base 10
              _busnr = int(_error.group("busnr"),16)

              # Slots auch in Int Base 10 wandeln und nur die mit Fehlerstatus > 0 in die Fehlerliste
              _error_slots = filter(lambda x: x > 0,[ int(_error.group("slot1"),16), int(_error.group("slot2"),16), int(_error.group("slot3"),16), int(_error.group("slot4"),16) ])
              
              ## Derzeit schon bekannte Fehler
              _active_errors = filter(lambda x,busnr=_busnr: x[0] == busnr, self.active_errors)
              
              ## alle Fehler >0 in den Slots durchgehen
              for _err in _error_slots:
                  ## wenn jetziger Fehler noch nicht bekannt
                  if (_busnr,_err) not in self.active_errors:
                      ## Severity f�r die Fehlernummer holen
                      _severity = self.get_severity(_err)
                        
                      if not _severity:
                        continue

                      ## Fehler zur Liste bereits bekannter Fehler hinzu
                      self.active_errors.append( (_busnr,_err) )
                      
                      ## Die Uhrzeit des Fehlers setzen
                      self.set_error_status(_busnr,_err, time.time())
                      
                      ## Fehlertext suchen
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      
                      ## dict f�r die Textausgabe erstellen im %(nr)s in der Konfig verwenden zu k�nnen
                      _errdict = {
                          'nr'  : _err,
                          'msg' : _err_message,
                          'bus' : _busnr,
                       }
                      
                      ## Wenn diese nicht None ist
                      if _severity:
                          ## Auf den Log schreiben
                          self.log( self.config.get("errormsg") % (_errdict), severity=_severity )
              
              ## in den aktiven Fehlern nach Clears suchen
              for (busnr,_err) in _active_errors:
                  ## wenn der Fehler nicht mehr im Slot ist
                  if _err not in _error_slots:
                      ## Fehlertext holen
                      _err_message = self.error_messages.get(_err,"unbekannter Fehler %r" % _err)
                      ## dict f�r Textausgabe erstellen
                      _errdict = {
                          'nr'  : _err,
                          'msg' : _err_message,
                          'bus' : _busnr,
                       }
                      ## Severity holen um zu gucken ob �berhaupt geloggt werden soll
                      _severity = self.get_severity(_err)
                      ## Wenn nicht None
                      if _severity:
                          ## Fehler Clear loggen
                          self.log( self.config.get("errorclearmsg") % (_errdict), severity='info' )
                      
                      ## Fehler von der Liste aktiver Fehler entfernen
                      self.active_errors.remove( (busnr,_err) )
                      
                      ## Fehlerstatus auf 0 setzen
                      self.set_error_status( _busnr,_err, 0 )
          return found
    
      def incomming(self, payload, localvars):
          ## 3. Auswerten von Fehlerprotokollen des "Normal-Modus"
          ## Ein Regelger�t am ECOCAN-BUS kann zur Zeit ca. 213 verschiedene Fehler erzeugen. Bei der Zahl von
          ## 15 Regelger�ten am ECOCAN-BUS m��ten somit ca. 1500 Fehlerquellen auf "Kommen" bzw. "Gehen"
          ## untersucht werden. Da die Verarbeitung einer so gro�en Zahl von Fehlermeldungen unrealistisch
          ## erscheint, werden nur die zur Zeit offenen Fehler aus dem Fehlerprotokoll (z. Zt. 4 St�ck) an die
          ## Kommunikationskarte �bergeben. Das Protokoll hat folgendes Format:
          ## <Kennung Fehlerstatus(0xAE)> <Ger�teadresse> < Fehler 1> < Fehler 2> < Fehler 3> < Fehler 4>
          ## Ist der Inhalt von "Fehler 1" bis "Fehler 4" ungleich 0x00, dann ist der entsprechende Fehler offen. (Fehler aktiv)
          
          ## locals() der Logik neu �bergeben um auf AN/AC zugreifen zu k�nnen
          self.localvars = localvars
          
          self.log_queue = ""
          
          self.debug("incomming message %r" % payload)
          
          ## Die Payload parsen
          found = self.parse(payload)
          
          ## Wenn es Meldungen im log_queue gibt 
          if self.log_queue:
              ## log auf AUsgang 1
              self.send_to_output( 1,self.log_queue)
          
          ## Wenn es aktive Fehler gibt dann Ausgang 2 auf 1
          self.send_to_output( 2, int(len(self.active_errors) >0), sbc=True)
          
          ## Status XML f�r Ausgang 3
          if found:
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
          ## �berpr�ft auch die alternativen Varianten
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
    #    commentcode.append("#"+codepart[2].split("\n")[1]+"\n################################\n## Quelltext nicht �ffentlich ##\n################################")


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
### !!!ACHTUNG: sehr lange Ausf�rungszeit!! ###
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
    ## Das ausl�sen �ber den Debug verhindern
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
Anzahl Eing�nge: """+str(ANZIN)+"""   """+repr(EN)+"""
Anzahl Ausg�nge: """+str(ANZOUT)+"""  """+repr(AN)+"""
Interne Speicher: """+str(ANZSP)+"""  """+repr(SN)+"""
"""

#print chksums

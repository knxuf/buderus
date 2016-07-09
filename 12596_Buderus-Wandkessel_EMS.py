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
LOGIKNAME="Buderus-Wandkessel-EMS"
## Logik ID
LOGIKID="12596"

## Ordner im GLE
LOGIKCAT="Buderus"


## Beschreibung
LOGIKDESC="""
Dieser Baustein wertet alle Daten für den Datentyp Wandhängender Kessel (nur EMS, für UBA den anderen nehmen), die vom Buderus 
 Baustein 12264 kommen aus und gibt
 die Zustände auf die entsprechenden Ausgänge aus. Da es mehrere Wandhängender Kessel an einem Regelgerät geben kann, muss 
 neben dem Regelgerät auch die Nummer des Wandhängender Kessel angegeben werden. Dann filtert der Baustein genau auf diese Werte
 und gibt sie aus. 
 <div class="acht">
 Wichtig: Eingang 1 und Ausgang 1 dürfen NIE direkt mit dem Buderus Baustein verbunden werden. Bitte immer die 
 Verbindung indirekt über ein iKO herstellen !!!! 
</div>
 Auf Eingang 1 werden die Daten vom Buderus Baustein empfangen. Auf dem Eingang 2 stellt man die Adresse 
 des Regelgerätes ein. Auf dem Eingang 3 die Nummer des Wandhängender Kessel mit UBA an diesem Regelgerät.
 <div class="hinw">
 Hier ein Tip: Man kann im SystemLog des Buderus Bausteines sehen, an welchen Regelgeräten welche DatenTypen
 erkannt wurden.  Hier ist der DatenTyp Wandhängender Kessel (UBA) relevant. Ist dieser am Regelgerät 2 erkannt worden, ist hier 
 eine 2 einzugeben. Auch ist hier zu sehen, welche Nummer der Wandhängender Kessel (UBA) an dem Regelgerät hat.
 </div>
 Damit werden nunmehr aus dem gesamten Datenstrom des ECOCAN Bus nur noch genau diese Daten gefilter und auf 
 den Ausgängen ausgegeben.
 <div class="hinw">
 Allgemeines: Ein Istwert von 110 °C beschreibt für den betroffenen Fühler einen Fühler defekt. Es kann auch sein,
 das hier einfach kein Fühler angeschlossen wurde. Messwerte in diesem Bereich hören bei 109 auf und gehen bei 111 weiter. 
</div>

Für die eigentliche Kommunikation sind zwingend folgende Beschreibungen von Buderus zu beachten:
7747004149 - 01/2009 DE - Technische Information - Monitordaten - System 4000
7747004150 - 05/2009 DE - Technische Information - Einstellbare Parameter - Logamatic 4000

Die Monitorwerte für wandhängende Kessel (UBA) setzen sich zur Zeit aus insgesamt 60 Werten zusammen 
und gehören zu einem der nachfolgenden Typen: 
(0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99) 
(Je nach dem welche Nummer der Kessel hat.)
<div class="acht">
Es werden hier nur die ersten 21 Werte verwendet, da bei UBA Kesseln nur diese versorgt werden.
Wert ab 22 beziehen sich auf EMS Kessel an der Logamatic 4000. Ist nur ein UBA Kessel angeschlossen
bleiben diese Wert bei 0. Aus diesem Grund werde die hier ignoriert.
Soll ein EMS Kessel ausgewertet werden, ist ein neuer Baustein zu schreiben. 
</div>
"""
VERSION="V0.20"


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

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''"|0|3|"E1 Payload IN"|"E2 Regelgerät Adresse"|"E3 Wandhängender Kessel Nr"|68|"A1 Payload OUT"|"A2 SystemLog"|"A3 Fehler: Luftfühler Feuerungsautomat defekt"|"A4 Fehler: Betriebstemperatur wird nicht erreicht"|"A5 Fehler: Ölvorwärmer Dauersignal"|"A6 Fehler: Ölvorwärmer ohne Signal"|"A7 Fehler: 1.Wasserfühler Feuerungsautomat defekt"|"A8 Fehler: 2.Wasserfühler Feuerungsautomat defekt"|"A9 Fehler: Warmwasser bleibt kalt"|"A10 Fehler: Desinfektion misslungen"|"A11 Betriebscode EMS-System ASCII"|"A12 Fehlernummer Feuerungsautomat"|"A13 Kesseltyp: Stufen des Brenners"|"A14 Kesseltyp: Stufen des Brenners"|"A15  Kesseltyp: Stufen des Brenners"|"A16 Kesseltyp: Gasbrenner"|"A17 Kesseltyp: ölbrenner"|"A18 max. Leistung des Brenners (in kW)"|"A19 min. Leistung des Brenners (in %)"|"A20 Flammenstrom müA (255=Fühler defekt)"|"A21 Abgastemperatur über Feuerungsautomat °C (255=Fühler defekt)"|"A22 Temperatur Ansaugluft °C (255=Fühler defekt)"|"A23 Wasserdruck in der Anlage bar (255=Fühler defekt)"|"A24 Zustand Brennerautomat: Heizanforderung liegt an"|"A25 Zustand Brennerautomat: Warmwasseranforderung liegt vor"|"A26 Zustand Brennerautomat: 11kW Jumper wurde entfernt"|"A27 Zustand Brennerautomat: Kessel wird mit Betriebstemperatur betrieben"|"A28 Zustand Brennerautomat: Kesselschutz zwecks Taupunktüberschreitung"|"A29 Zustand Brennerautomat: Feuerungsautomat ist verrriegelt (Serviceeinsatz)"|"A30 Zustand Brennerautomat: Feuerungsautomat ist blockiert"|"A31 Zustand Brennerautomat: Servicemeldung vom Feuerungsautomat"|"A32 Relais Brennerautomat: Magnetventil für 1. Stufe"|"A33 Relais Brennerautomat: Magnetventil für 2. Stufe"|"A34 Relais Brennerautomat: Gebläserelais"|"A35 Relais Brennerautomat: Zündungsrelais"|"A36 Relais Brennerautomat: ölvorwärmung/ Abgassperrklappe"|"A37 Relais Brennerautomat: Kesselkreispumpe/ Heizkreisumwälzpumpe"|"A38 Relais Brennerautomat: 3-Wegeventil"|"A39 Relais Brennerautomat: Warmwasser Zirkulationspumpe"|"A40 Relais Brennerautomat: Warmwasserladepumpe"|"A41 Relais Brennerautomat: Flüssiggasventil"|"A42 Relais Brennerautomat: QWP Umwälzpumpe"|"A43 angestrebte Vorlaufsolltemperatur °C"|"A44 Warmwasserladeprinzip"|"A45 Fehleinstellungen: 11kW Jumper in Kaskade gezogen"|"A46 Fehleinstellungen: Kessel über BC10 im Notbetrieb"|"A47 Fehleinstellungen: WW- Poti nicht auf Stellung AUT"|"A48 Fehleinstellungen: Kesselpoti nicht auf AUT/ 90°C"|"A49 Fehleinstellungen: Anforderung über Klemme WA"|"A50 Fehleinstellungen: Kommunikation vorhanden (nur mit FM458)"|"A51 Fehleinstellungen: keine Kommunikation (nur mit FM458)"|"A52 EMS-Servicemeldung: es steht keine Meldung an"|"A53 EMS-Servicemeldung: Abgastemperatur zu hoch"|"A54 EMS-Servicemeldung: Gebläse schwergängig"|"A55 EMS-Servicemeldung: Flammstrom ist niedrig"|"A56 EMS-Servicemeldung: Flammenverzugszeit ist hoch"|"A57 EMS-Servicemeldung: häufiger Flammenabriss"|"A58 EMS-Servicemeldung: Wasserdruck der Anlage ist niedrig"|"A59 EMS-Servicemeldung: vorgegebenes Datum überschritten"|"A60 Betriebszeit 2.Stufe (in Std.)"|"A61 Kennzeichnung EMS-Masters"|"A62 Version des EMS-Master"|"A63 Kennung des SAFe (z.Zt. 75)"|"A64 Version des Feuerungsautomaten (SAFe)"|"A65 BCM/ BIM- Nummer"|"A66 Versions-Nr. des BCM/BIM"|"A67 Betriebstemperatur des Kessel °C"|"A68 Betriebscode Text"|"'''+VERSION+'''"

5001|3|68|0|16|1

# EN[x]
5002|1|""|1 #* Payload IN
5002|2|1|0  #* Regelgerät Adresse
5002|3|1|0  #* Wandhängender Kessel Nr


# Speicher
5003|1||0   #* logic
5003|2|0|0  #* 1.Buchstabe Betriebscode EMS-System  ASCII
5003|3|0|0  #* 2.Buchstabe Betriebscode EMS-System  ASCII
5003|4|0|0  #* Fehlernummer Feuerungsautomat 1.Byte 200-499_UBA-Fehler;500-799_SAFE-Fehler;800-999_EMS-Anlagen-Fehler
5003|5|0|0  #* Fehlernummer Feuerungsautomat 2.Byte 200-499_UBA-Fehler;500-799_SAFE-Fehler;800-999_EMS-Anlagen-Fehler
5003|6|0|0  #* Max. Leistung des Brenners   (Low-Byte) in kW, High-Byte befindet sich im Offset 54
5003|7|0|0  #* Max. Leistung Kessels        (High-Byte)    1kW
5003|8|0|0  #* Betriebszeit 2.Stufe Byte3  Brennerstunden Byte 3       Version Vorkommastelle des Feuerungsautomaten SAFe
5003|9|0|0  #* Betriebszeit 2.Stufe Byte2  Brennerstunden Byte 2       Version Nachkommastelle des Feuerungsautomaten SAFe
5003|10|0|0 #* Betriebszeit 2.Stufe Byte1  Brennerstunden Byte 1       BCM/ BIM- Nummer Byte 1
5003|11|0|0 #* Version Vorkommastelle des EMS-Master
5003|12|0|0 #* Version Nachkommastelle des EMS-Masters
5003|13|0|0 #* Version Vorkommastelle des Feuerungsautomaten (SAFe)
5003|14|0|0 #* Version Nachkommastelle des Feuerungsautomaten (SAFe)
5003|15|0|0 #* BCM/ BIM- Nummer Byte2 
5003|16|0|0 #* BCM/ BIM- Nummer Byte1               0-255= UBA1; 1000-4999= UBA3; 5000-9999

# Ausgänge
5004|1|""|0|1|1  #* Payload OUT
5004|2|""|0|1|1  #* SystemLog
5004|3|0|1|1|0   #* Offset_22,1.Bit, Anlagenfehler eines EMS- Kessel, Luftfühler Feuerungsautomat defekt
5004|4|0|1|1|0   #* Offset_22,2.Bit, Anlagenfehler eines EMS- Kessel, Betriebstemperatur wird nicht erreicht
5004|5|0|1|1|0   #* Offset_22,3.Bit, Anlagenfehler eines EMS- Kessel, Ölvorwärmer Dauersignal
5004|6|0|1|1|0   #* Offset_22,4.Bit, Anlagenfehler eines EMS- Kessel, Ölvorwärmer ohne Signal
5004|7|0|1|1|0   #* Offset_23,1.Bit, Anlagenfehler von EMS- Warmwasser, 1.Wasserfühler Feuerungsautomat defekt
5004|8|0|1|1|0   #* Offset_23,2.Bit, Anlagenfehler von EMS- Warmwasser, 2.Wasserfühler Feuerungsautomat defekt 
5004|9|0|1|1|0   #* Offset_23,3.Bit, Anlagenfehler von EMS- Warmwasser, Warmwasser bleibt kalt
5004|10|0|1|1|0  #* Offset_23,4.Bit, Anlagenfehler von EMS- Warmwasser, Desinfektion misslungen
5004|11|""|0|1|1 #* Offset_24,25     Betriebscode EMS-System ASCII
5004|12|0|0|1|0  #* Offset_26,27     Fehlernummer Feuerungsautomat  (200-499: UBA-Fehler; 500-799: SAFE-Fehler; 800-999: EMS-Anlagen-Fehler)
5004|13|0|1|1|0  #* Offset_28,1.Bit, Brennertyp des Kessel, Stufen des Brenners (wenn 0, dann mod.Brenner)
5004|14|0|1|1|0  #* Offset_28,2.Bit, Brennertyp des Kessel, Stufen des Brenners (wenn 0, dann mod.Brenner)
5004|15|0|1|1|0  #* Offset_28,3.Bit, Brennertyp des Kessel, Stufen des Brenners (wenn 0, dann mod.Brenner)
5004|16|0|1|1|0  #* Offset_28,7.Bit, Brennertyp des Kessel, Gasbrenner
5004|17|0|1|1|0  #* Offset_28,8.Bit, Brennertyp des Kessel, Ölbrenner
5004|18|0|0|1|0  #* Speicher 6+7,    max. Leistung des Brenners (Low- Byte) (in kW)
5004|19|0|0|1|0  #* Offset_30,       min. Leistung des Brenners (in %)
5004|20|0|0|1|0  #* Offset_31,       Flammenstrom müA (255=Fühler defekt)
5004|21|0|0|1|0  #* Offset_32,       Abgastemperatur über Feuerungsautomat °C (255=Fühler defekt)
5004|22|0|0|1|0  #* Offset_33,       Temperatur Ansaugluft °C (255=Fühler defekt)
5004|23|0|0|1|0  #* Offset_34,       Wasserdruck in der Anlage bar (255=Fühler defekt)
5004|24|0|1|1|0  #* Offset_35,1.Bit, Betriebszustände des Brennerautomaten, Heizanforderung liegt an
5004|25|0|1|1|0  #* Offset_35,2.Bit, Betriebszustände des Brennerautomaten, Warmwasseranforderung liegt vor
5004|26|0|1|1|0  #* Offset_35,3.Bit, Betriebszustände des Brennerautomaten, 11kW Jumper wurde entfernt
5004|27|0|1|1|0  #* Offset_35,4.Bit, Betriebszustände des Brennerautomaten, Kessel wird mit Betriebstemperatur betrieben
5004|28|0|1|1|0  #* Offset_35,5.Bit, Betriebszustände des Brennerautomaten, Kesselschutz zwecks Taupunktüberschreitung
5004|29|0|1|1|0  #* Offset_35,6.Bit, Betriebszustände des Brennerautomaten, Feuerungsautomat ist verrriegelt (Serviceeinsatz)
5004|30|0|1|1|0  #* Offset_35,7.Bit, Betriebszustände des Brennerautomaten, Feuerungsautomat ist blockiert
5004|31|0|1|1|0  #* Offset_35,8.Bit, Betriebszustände des Brennerautomaten, Servicemeldung vom Feuerungsautomat
5004|32|0|1|1|0  #* Offset_36,1.Bit, Relaiszustände 1 des Brennerautomaten, Magnetventil für 1. Stufe
5004|33|0|1|1|0  #* Offset_36,2.Bit, Relaiszustände 1 des Brennerautomaten, Magnetventil für 2. Stufe
5004|34|0|1|1|0  #* Offset_36,3.Bit, Relaiszustände 1 des Brennerautomaten, Gebläserelais
5004|35|0|1|1|0  #* Offset_36,4.Bit, Relaiszustände 1 des Brennerautomaten, Zündungsrelais
5004|36|0|1|1|0  #* Offset_36,5.Bit, Relaiszustände 1 des Brennerautomaten, Ölvorwärmung/ Abgassperrklappe
5004|37|0|1|1|0  #* Offset_36,6.Bit, Relaiszustände 1 des Brennerautomaten, Kesselkreispumpe/ Heizkreisumwälzpumpe
5004|38|0|1|1|0  #* Offset_36,7.Bit, Relaiszustände 1 des Brennerautomaten, 3-Wegeventil
5004|39|0|1|1|0  #* Offset_36,8.Bit, Relaiszustände 1 des Brennerautomaten, Warmwasser Zirkulationspumpe
5004|40|0|1|1|0  #* Offset_37,1.Bit, Relaiszustände 2 des Brennerautomaten, Warmwasserladepumpe
5004|41|0|1|1|0  #* Offset_37,2.Bit, Relaiszustände 2 des Brennerautomaten, Flüssiggasventil
5004|42|0|1|1|0  #* Offset_37,3.Bit, Relaiszustände 2 des Brennerautomaten, QWP Umwälzpumpe
5004|43|0|0|1|0  #* Offset_38,       Vorlaufsolltemperatur die vom Feuerungsautomat angestrebt wird °C
5004|44|0|0|1|0  #* Offset_39,       Wie wird Warmwasser geladen (0=kein Warmwasser; 1=nach Durchlaufprinzip; 2=Durchlaufprinzip mit kleinem Speicher; 3=Speicherprinzip)
5004|45|0|1|1|0  #* Offset_40,1.Bit  mögliche Fehleinstellungen am EMS-Kessel, 11kW Jumper in Kaskade gezogen
5004|46|0|1|1|0  #* Offset_40,2.Bit  mögliche Fehleinstellungen am EMS-Kessel, Kessel über BC10 im Notbetrieb
5004|47|0|1|1|0  #* Offset_40,3.Bit  mögliche Fehleinstellungen am EMS-Kessel, WW- Poti nicht auf Stellung AUT
5004|48|0|1|1|0  #* Offset_40,4.Bit  mögliche Fehleinstellungen am EMS-Kessel, Kesselpoti nicht auf AUT/ 90°C
5004|49|0|1|1|0  #* Offset_40,5.Bit  mögliche Fehleinstellungen am EMS-Kessel, Anforderung über Klemme WA
5004|50|0|1|1|0  #* Offset_40,7.Bit  mögliche Fehleinstellungen am EMS-Kessel, Kommunikation vorhanden (nur mit FM458)
5004|51|0|1|1|0  #* Offset_40,8.Bit  mögliche Fehleinstellungen am EMS-Kessel, keine Kommunikation (nur mit FM458)
5004|52|0|1|1|0  #* Offset_41,1.Bit  EMS-Servicemeldungen, es steht keine Meldung an
5004|53|0|1|1|0  #* Offset_41,2.Bit  EMS-Servicemeldungen, Abgastemperatur zu hoch
5004|54|0|1|1|0  #* Offset_41,3.Bit  EMS-Servicemeldungen, Gebläse schwergängig
5004|55|0|1|1|0  #* Offset_41,4.Bit  EMS-Servicemeldungen, Flammstrom ist niedrig
5004|56|0|1|1|0  #* Offset_41,5.Bit  EMS-Servicemeldungen, Flammenverzugszeit ist hoch
5004|57|0|1|1|0  #* Offset_41,6.Bit  EMS-Servicemeldungen, häufiger Flammenabriss
5004|58|0|1|1|0  #* Offset_41,7.Bit  EMS-Servicemeldungen, Wasserdruck der Anlage ist niedrig
5004|59|0|1|1|0  #* Offset_41,8.Bit  EMS-Servicemeldungen, vorgegebenes Datum überschritten
5004|60|0|0|1|0  #* Offset_42,43,44, Betriebszeit 2.Stufe (in Std.)
5004|61|0|0|1|0  #* Offset_45,       Kennzeichnung/ Identifizierung des EMS-Masters (64=Feuerungsautomat UBA3, Master; 65=RC10; 66=RC20, 67=RC30; 68=BC10; 69=MM10; 70=Gaswärmepumpe; 71=Weichenmodul; 72=MC10; 73=Solar; 74=EED; 75=SAFE; 76=ES73; 77=M300; 78=M400; 79=M100; 80=M200; 81=Kaskade; 82=LPG)
5004|62|""|0|1|1  #* Offset_46/47    Version Vor- Nachkommastelle des EMS-Master
5004|63|0|0|1|0   #* Offset_48,      Kennung des SAFe (z.Zt. 75)
5004|64|""|0|1|1  #* Offset_49/50    Version Vor- Nachkommastelle des Feuerungsautomaten (SAFe)
5004|65|0|0|1|1   #* Offset_51/52    BCM/ BIM- Nummer (0-255= UBA1; 1000-4999= UBA3; 5000-9999=SAFe)
5004|66|0|0|1|0   #* Offset_53,      Versions-Nr. des BCM/BIM
5004|67|0|0|1|1   #* Offset_55,      Betriebstemperatur des Kessel °C
5004|68|""|0|1|1  #* Betriebscode Text
#################################################
'''
#####################
#### Python Code ####
#####################
code=[]

code.append([3,"EI",r"""
if EI == 1:
    class buderus_wandkessel_EMS(object):
        def __init__(self,localvars):
            import re

            self.logik = localvars["pItem"]
            self.MC = self.logik.MC

            EN = localvars['EN']
            
            self.localvars = localvars
            
            self.current_status = [ ]
            self.status_length = 18

            ## 2.3.8 Monitorwerte für wandhängende Kessel (UBA)
            ## Die Monitorwerte für wandhängende Kessel (UBA) setzen sich zur Zeit 
            ## aus insgesamt 60 Werten zusammen und gehören zu einem der 
            ## nachfolgenden Typen: (0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99)
            ## Es werden hier nur die ersten 21 Werte verwendet, da bei UBA Kessel nur diese versorgt werden.
            ## Wert ab 22 beziehen sich auf EMS Kessel an der Logamatic. Ist nur ein UBA Kessel angeschlossen
            ## bleiben diese Wert bei 0. Aus diesem Grund werde diese hier ignoriert.

            self.device_types = {
                "XX" : "kein wandhängender Kessel",
                "92" : "Kessel 1 wandhängend",
                "93" : "Kessel 2 wandhängend",
                "94" : "Kessel 3 wandhängend",
                "95" : "Kessel 4 wandhängend",
                "96" : "Kessel 5 wandhängend",
                "97" : "Kessel 6 wandhängend",
                "98" : "Kessel 7 wandhängend",
                "99" : "Kessel 8 wandhängend",
            }

            self.recv_selector = ["XX","92","93","94","95","96","97","98","99"]  
            self.send_selector = ["16","07","08","09","0A","16","18","1A"] 
            
            #self.debug("Kessel %d wandhängend" % EN[3])
            if EN[3] < 1 or EN[3] > 8:
                self.debug("Ungültiger Kessel %d wandhängend" % EN[3])
                _id = "XX"
                self.send_prefix = None
            else:
                _id = self.recv_selector[ int(EN[3]) ]
                #self.debug("suche nach %r" % repr(_id))
                self.send_prefix = "B0%.2x%s" % (int(EN[2]),self.send_selector [ int(EN[3]) ])
            
            self.bus_id = "%.2X" % int(EN[2])
            self.id = self.device_types.get(_id)

            self.payload_regex = re.compile( "(?P<mode>AB|A7)%s%s(?P<offset>[0-9A-F]{2})(?P<data>(?:[0-9A-F]{2})+)" % ( self.bus_id ,_id) )

              ## Offset Name_______________________________  Auflösung________________________________________________________ Ausgang_____
              ## 22     Anlagenfehler eines EMS- Kessel      1.Bit = Luftfuehler Feuerungsautomat defekt                      ## Ausgang 3
              ##                                             2.Bit = Betriebstemperatur wird nicht erreicht                   ## Ausgang 4
              ##                                             3.Bit = Oelvorwaermer Dauersignal                                ## Ausgang 5
              ##                                             4.Bit = Oelvorwaermer ohne Signal                                ## Ausgang 6
              ##                                             5.Bit = frei
              ##                                             6.Bit = frei
              ##                                             7.Bit = frei
              ##                                             8.Bit = frei
              ## 23      Anlagenfehler von EMS- Warmwasser    1.Bit = 1.Wasserfühler Feuerungsautomat defekt                  ## Ausgang 7
              ##                                              2.Bit = 2.Wasserfühler Feuerungsautomat defekt                  ## Ausgang 8
              ##                                              3.Bit = Warmwasser bleibt kalt                                  ## Ausgang 9
              ##                                              4.Bit = Desinfektion misslungen                                 ## Ausgang 10
              ##                                              5.Bit = frei
              ##                                              6.Bit = frei
              ##                                              7.Bit = frei
              ##                                              8.Bit = frei
              ## 24     1.Buchstabe Betriebscode EMS-System  ASCII                                                            ## speicher 2
              ## 25     2.Buchstabe Betriebscode EMS-System  ASCII                                                            ## speicher 3 -> zusammen Ausgang 11
              ## 26     Fehlernummer Feuerungsautomat 1.Byte 200-499_UBA-Fehler;500-799_SAFE-Fehler;800-999_EMS-Anlagen-Fehler ## Speicher 4 * 256 +
              ## 27     Fehlernummer Feuerungsautomat 2.Byte 200-499_UBA-Fehler;500-799_SAFE-Fehler;800-999_EMS-Anlagen-Fehler ## Speicher 5  -> Ausgang 12
              ## 28     Brennertyp des Kessel                1.Bit = Stufen des Brenners (wenn 0, dann mod. Brenner)             ## Ausgang 13
              ##                                             2.Bit = Stufen des Brenners (wenn 0, dann mod. Brenner)             ## Ausgang 14
              ##                                             3.Bit = Stufen des Brenners (wenn 0, dann mod. Brenner)             ## Ausgang 15
              ##                                             4.Bit = frei
              ##                                             5.Bit = frei
              ##                                             6.Bit = frei
              ##                                             7.Bit = Gasbrenner                                                 ## Ausgang 16
              ##                                             8.Bit = Oelbrenner                                                 ## Ausgang 17
              ## 29      max. Leistung des Brenners           (Low-Byte) in kW, High-Byte befindet sich im Offset 54            ## Speicher 6 + 7-> Ausgang 18
              ## 30     max- Leistung des Brenners           in %                                                               ## Ausgang 19
              ## 31     Flammenstrom                         in müA (255=Fühler defekt)                                         ## Ausgang 20
              ## 32     Abgastemperatur über Feuerungsautomat°C (255=Fühler defekt)                                             ## Ausgang 21
              ## 33     Temperatur Ansaugluft                °C (255=Fühler defekt)                                             ## Ausgang 22
              ## 34     Wasserdruck in der Anlage            bar (255=Fühler defekt)                                            ## Ausgang 23
              ## 35      Betriebszustände Brennerautomaten    1.Bit = Heizanforderung liegt an                                  ## Ausgang 24
              ##                                               2.Bit = Warmwasseranforderung liegt vor                          ## Ausgang 25
              ##                                               3.Bit = 11kW Jumper wurde entfernt                               ## Ausgang 26
              ##                                               4.Bit = Kessel wird mit Betriebstemperatur betrieben             ## Ausgang 27
              ##                                               5.Bit = Kesselschutz zwecks Taupunktüberschreitung               ## Ausgang 28
              ##                                               6.Bit = Feuerungsautomat ist verrriegelt (Serviceeinsatz)        ## Ausgang 29
              ##                                               7.Bit = Feuerungsautomat ist blockiert                           ## Ausgang 30
              ##                                               8.Bit = Servicemeldung vom Feuerungsautomat                      ## Ausgang 31
              ## 36      Relaiszustände 1 Brennerautomaten     1.Bit = Magnetventil für 1. Stufe                                ## Ausgang 32
              ##                                               2.Bit = Magnetventil für 2. Stufe                                ## Ausgang 33
              ##                                               3.Bit = Gebläserelais                                            ## Ausgang 34
              ##                                               4.Bit = Zündungsrelais                                           ## Ausgang 35
              ##                                               5.Bit = Ölvorwärmung/ Abgassperrklappe                           ## Ausgang 36
              ##                                               6.Bit = Kesselkreispumpe/ Heizkreisumwälzpumpe                   ## Ausgang 37
              ##                                               7.Bit = 3-Wegeventil                                             ## Ausgang 38
              ##                                               8.Bit = Warmwasser Zirkulationspumpe                             ## Ausgang 39
              ## 37      Relaiszustände 2 Brennerautomaten    1.Bit = Warmwasserladepumpe                                       ## Ausgang 40
              ##                                               2.Bit = Flüssiggasventil                                         ## Ausgang 41
              ##                                               3.Bit = QWP Umwälzpumpe                                          ## Ausgang 42
              ##                                               4.Bit = frei
              ##                                               5.Bit = frei
              ##                                               6.Bit = frei
              ##                                               7.Bit = frei
              ##                                               8.Bit = frei
              ## 38     Vorlaufsolltemp. Feuerungsauto ange. °C                                                                 ## Ausgang 43
              ## 39     Wie wird Warmwasser geladen          0=keinWarmwa.;1=nach Durchlaufpr;2=Durchlaufpr.kleinem Spei; 3=Speicherpr ## Ausgang 44
              ## 40     mögli. Fehleinstellu. am EMS-Kessel  1.Bit = 11kW Jumper in Kaskade gezogen                             ## Ausgang 45
              ##                                               2.Bit = Kessel über BC10 im Notbetrieb                           ## Ausgang 46
              ##                                               3.Bit = WW- Poti nicht auf Stellung AUT                          ## Ausgang 47
              ##                                               4.Bit = Kesselpoti nicht auf AUT/ 90°C                           ## Ausgang 48
              ##                                               5.Bit = Anforderung über Klemme WA                               ## Ausgang 49
              ##                                               6.Bit = frei
              ##                                               7.Bit = Kommunikation vorhanden (nur mit FM458)                  ## Ausgang 50
              ##                                               8.Bit = keine Kommunikation (nur mit FM458)                      ## Ausgang 51
              ## 41     EMS-Servicemeldungen                   1.Bit = es steht keine Meldung an                                ## Ausgang 52
              ##                                               2.Bit = Abgastemperatur zu hoch                                  ## Ausgang 53
              ##                                               3.Bit = Gebläse schwergängig                                     ## Ausgang 54
              ##                                               4.Bit = Flammstrom ist niedrig                                   ## Ausgang 55
              ##                                               5.Bit = Flammenverzugszeit ist hoch                              ## Ausgang 56
              ##                                               6.Bit = häufiger Flammenabriss                                   ## Ausgang 57
              ##                                               7.Bit = Wasserdruck der Anlage ist niedrig                       ## Ausgang 58
              ##                                               8.Bit = vorgegebenes Datum überschritten                         ## Ausgang 59
              ## 42     Betriebszeit 2.Stufe Byte3           (Byte3*65536)+(Byte2*256)+Byte1                                    ## interner Speicher 8
              ## 43     Betriebszeit 2.Stufe Byte2                                                                              ## interner Speicher 9
              ## 44     Betriebszeit 2.Stufe Byte1                                                                              ## interner Speicher 10 -> Ausgang 60
              ## 45     Kennzeich./Identifizi. EMS-Masters   64=Feuerungsautomat...usw.                                         ## Ausgang 61
              ## 46     Ver. Vorkommastelle des EMS-Master                                                                      ## Speicher 11
              ## 47     Ver. Nachkommastelle des EMS-Master                                                                     ## Speicher 12 ## Ausgang 62
              ## 48     Kennung des SAFe                       z.Zt. 75                                                         ## Ausgang 63
              ## 49     Ver. Vorkommastelle Feuerungsautoma  SAFe                                                               ## interner Speicher 13
              ## 50     Ver. Nachkommastelle Feuerungsautoma SAFe                                                               ## interner Speicher 14  ## Ausgang 64
              ## 51     BCM/ BIM- Nummer Byte2                                                                                  ## interner Speicher 15 
              ## 52     BCM/ BIM- Nummer Byte1               0-255= UBA1; 1000-4999= UBA3; 5000-9999                            ## interner Speicher 16 ## Ausgang 65
              ## 53     Versions-Nr. des BCM/BIM                                                                                ## Ausgang 66
              ## 54     Max. Leistung Kessels (High-Byte)    1kW                                                                ## Speicher 7 + 6 -> Ausgang 18
              ## 55     Betriebstemperatur des Kessel           °C                                                              ## Ausgang 67
              ## 56     frei
              ## 57     frei
              ## 58     frei
              ## 59     frei







            self.output_functions = [
                (self.to_bits,[3,4,5,6,0,0,0,0],"AN"),
                (self.to_bits,[7,8,9,10,0,0,0,0],"AN"),
                (lambda x: [x],[2],"SN"),
                (lambda x: [x],[3],"SN"),
                (lambda x: [x],[4],"SN"),
                (lambda x: [x],[5],"SN"),
                (self.to_bits,[13,14,15,0,0,0,16,17],"AN"),
                (lambda x: [x],[6],"SN"),
                (lambda x: [x],[19],"AN"),
                (lambda x: [x],[20],"AN"),
                (lambda x: [x],[21],"AN"),
                (lambda x: [x],[22],"AN"),
                (lambda x: x==255 and -1 or [float(x)/10],[23],"AN"),
                (self.to_bits,[24,25,26,27,28,29,30,31],"AN"),
                (self.to_bits,[32,33,34,35,36,37,38,39],"AN"),
                (self.to_bits,[40,41,42,0,0,0,0,0],"AN"),
                (lambda x: [x],[43],"AN"),
                (lambda x: [x],[44],"AN"),
                (self.to_bits,[45,46,47,48,49,0,50,51],"AN"),
                (self.to_bits,[52,53,54,55,56,57,58,59],"AN"),
                (lambda x: [x],[8],"SN"),
                (lambda x: [x],[9],"SN"),
                (lambda x: [x],[10],"SN"),
                (lambda x: [x],[61],"AN"),
                (lambda x: [x],[11],"SN"),
                (lambda x: [x],[12],"SN"),
                (lambda x: [x],[63],"AN"),
                (lambda x: [x],[13],"SN"),
                (lambda x: [x],[14],"SN"),
                (lambda x: [x],[15],"SN"),
                (lambda x: [x],[16],"SN"),
                (lambda x: [x],[66],"AN"),
                (lambda x: [x],[7],"SN"),
                (lambda x: [x],[67],"AN"),
                (lambda x: [x],[0],"AN"),
                (lambda x: [x],[0],"AN"),
                (lambda x: [x],[0],"AN"),
                (lambda x: [x],[0],"AN"),
            ]

            self.get_monitor_data()

        def get_monitor_data(self):
            self.send_to_output(1,"A2%s" % self.bus_id)


        def debug(self,msg):
            self.log(msg,severity='debug')
            #print "DEBUG-12596: %r" % (msg,)

        def send_to_output(self,out,msg,sbc=False):
            if sbc and msg == self.localvars["AN"][out] and not self.localvars["EI"] == 1:
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
            #if offset < 22:
            #    self.debug("Daten offset: %d kleiner 22" % offset )
            #    return
            _len = len(data)
            #self.current_status = self.current_status[:offset] + [ _x for _x in data ] + self.current_status[offset + _len:]
            for _x in xrange(_len):
                _offset = offset - 22 + _x
                if (_offset < 0):
                   #self.debug("Daten offset: %d " % _offset )
                   continue
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

        def incomming(self,msg, localvars):
            import binascii
            self.localvars = localvars
            #self.debug("incomming message %r" % msg)
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
            
        def get_fehler_statustext(self,errno):
            return {
                0 : "Rücklauftemperaturfühler defekt (Kabelbruch)",   
                1 : "Störung Warmwassertemperaturfühler",   
                2 : "Speichertemperaturfühler defekt",   
                3 : "Störung Außentemperaturfühler",   
                9 : "Speichertemperaturfühler 2 defekt",   
                10 : "Störung Speicherlade-Temperaturfühler 2",   
                15 : "Externer Vorlauftemperaturfühler hydraulische Weiche defekt",   
                16 : "Kaltwassereinlauftemperaturfühler defekt",   
                17 : "Abgastemperaturfühler an der Strömungssicherung defekt",   
                18 : "Gebläse bleibt stehen oder Differenzdruckschalter öffnet während Brennerbetrieb",   
                19 : "Brenner vorübergehend ausgeschaltet (Vorlauftemperatur steigt zu schnell)",   
                20 : "Gebläse läuft nicht an, oder Differenzdruckschalter schließt nicht bei Gebläseanlauf",   
                21 : "Vorlauftemperaturfühler im Wärmeerzeuger defekt",   
                22 : "Externer Wächter ausgelöst, kein Heizbetrieb möglich",   
                23 : "Differenzdruckschalter öffnet nicht bei stehendem Gebläse",   
                24 : "Abgasaustritt aus Strömungssicherung",   
                26 : "Abgastemperaturfühler in der Brennkammer defekt",   
                27 : "Abgasaustritt aus der Brennkammer",   
                28 : "Temperaturfühler am Brenner defekt",   
                29 : "Brenner vorübergehend ausgeschaltet, auf Grund zu hoher Temperatur am Brenner",   
                31 : "Kodierstecker defekt oder ungültig",   
                32 : "Kodierstecker defekt oder ungültig",   
                33 : "Heizung wegen Trockenlauf der Pumpe ausgeschaltet",   
                37 : "Rücklauftemperaturfühler defekt",   
                43 : "Regelventil öffnet nicht im Betrieb",   
                45 : "Keine Kommunikation mit vorhandenem CAN-BUS-Modul",   
                46 : "Falsche BUS-Konfiguration",   
                50 : "Abgasaustritt aus der Brennkammer, Heizgerät verriegelt",   
                51 : "Interne Störung Wärmeerzeuger",   
                52 : "Flammensignal erkannt, obwohl keine Gasfreigabe erfolgt ist, Wärmeerzeuger verriegelt",   
                53 : "Undichtigkeit an Sicherheitsventilen erkannt, Wärmeerzeuger verriegelt",   
                54 : "Entstörtaste gedrückt oder interne Störung, Wärmeerzeuger verriegelt",   
                55 : "Sicherheitsabschaltung Brenner durch Sicherheitstemperaturbegrenzer",   
                57 : "Abgasaustritt aus Strömungssicherung",   
                61 : "Störung der Buskommunikation",   
                65 : "Außentemperaturfühler defekt",   
                66 : "Schichtladespeicher-Temperaturfühler 3 Störung",   
                67 : "Interner Fehler",   
                68 : "Unzulässiger Anschluss Außentemperaturfühler",   
                69 : "Zusätzlicher Gradient-Fühler defekt",   
                70 : "Vorlauftemperaturfühler gemischter Heizkreis defekt",   
                71 : "Gebläse läuft nicht an",   
                73 : "Mischer defekt",   
                74 : "Temperaturfühler Bufferspeicher defekt",   
                76 : "Geregelte Pumpe wurde nicht erkannt",   
                84 : "Rücklauftemperaturfühler defekt (Kabelbruch)",   
                85 : "Rücklauftemperaturfühler defekt (Kurzschluss)",   
                86 : "Vorlauftemperaturfühler defekt (Kabelbruch)",   
                87 : "Vorlauftemperaturfühler defekt (Kurzschluss)",   
                88 : "Höhere Rücklauftemperatur als Vorlauftemperatur",   
                89 : "Vorlauf- oder Rücklauftemperatur außerhalb zulässigen Bereichs",   
                90 : "Außentemperaturfühler defekt",   
                91 : "Störung Außeneinheit / Wasserdurchfluss gestört",   
                200 : "Wärmeerzeuger im Heizbetrieb",   
                201 : "Wärmeerzeuger im Warmwasserbetrieb",   
                202 : "Wärmeerzeuger im Schaltoptimierungsprogramm",   
                203 : "Wärmeerzeuger befindet sich in Betriebsbereitschaft, keine Wärmeanforderung",   
                204 : "Die aktuelle Heizwassertemperatur des Wärmeerzeugers ist höher als der Sollwert",   
                205 : "Wärmeerzeuger wartet auf Luftströmung",   
                207 : "Betriebsdruck zu niedrig",   
                208 : "Abgastest wird durchgeführt",   
                209 : "Wärmeerzeuger in Betrieb und im Servicemode",   
                210 : "Das Abgasthermostat hat angesprochen",   
                211 : "Installation Geräteelektronik fehlerhaft",   
                212 : "Temperaturanstieg Sicherheits- Vorlaufsensor",   
                213 : "Temperaturdifferenz zwischen Vorlauf und Rücklauf",   
                214 : "Das Gebläse wird während der Sicherheitszeit abgeschaltet",   
                215 : "Das Gebläse dreht zu schnell",   
                216 : "Das Gebläse dreht nicht schnell genug",   
                217 : "Kein Lufttransport nach mehreren Minuten",   
                218 : "Temperatur am Kesselvorlaufsensor ist größer als 105°C",   
                219 : "Temperatur am Sicherheitssensor größer als 95°C",   
                220 : "Sicherheitsensor Kurzschluss, oder wärmer als 130°C",   
                221 : "Sicherheitsensor loser Kontakt oder defekt",   
                222 : "Vorlaufsensor Kurzschluss",   
                223 : "Vorlaufsensor loser Kontakt oder defekt",   
                224 : "Systemfehler - UBA keine Verbindung zu Kontakten 22 und 50",   
                225 : "Temperatur zwischen Vorlauf- und Sicherheitsensor zu groß",   
                226 : "Kennzeichnung für Handterminal",   
                227 : "Kein Flammensignal nach Zündung",   
                228 : "Flammensignal trotz nicht vorhandener Flamme",   
                229 : "Flamme während des Brennerbetriebes ausgefallen",   
                230 : "Fehler Regelventil",   
                231 : "Fehler Netzspannung",   
                232 : "Wärmeerzeuger durch externen Schaltkontakt verriegelt",   
                233 : "KIM oder UBA defekt",   
                234 : "Elektrische Störung der Gasarmatur",   
                235 : "Versionskonflikt Geräteelektronik (UBA/KIM)",   
                237 : "Systemstörung - Geräteelektronik defekt (UBA/KIM)",   
                238 : "Geräteelektronik UBA ist defekt",   
                239 : "Systemstörung Geräteelektronik defekt (KIM/UBA3)",   
                240 : "Rücklaufsensor defekt (Kurzschluss)",   
                241 : "Rücklaufsensor defekt (Drahtbruch)",   
                242 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                243 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                244 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                245 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                246 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                247 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                248 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                249 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                250 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                251 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                252 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                253 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                254 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                255 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                256 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                257 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                258 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                259 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                260 : "Kein Temperaturanstieg nach Brennerstart",   
                261 : "Zeitfehler bei erster Sicherheitszeit",   
                262 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                263 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                264 : "Der Lufttransport ist während der Betriebsphase ausgefallen",   
                265 : "Der Heizkessel befindet sich in Betriebsbereitschaft, Wärmebedarf ist vorhanden, es wird jedoch zuviel Energie geliefert",   
                266 : "Pumpendruckerhöhung zu niedrig",   
                267 : "Systemstörung - UBA defekt",   
                268 : "Der Relaistest wurde aktiviert",   
                269 : "Flammenüberwachung - Glühzünder zu lange eingeschaltet",   
                270 : "Wärmeerzeuger wird hochgefahren",   
                271 : "Temperaturunterschied zwischen Vorlaufsensor und Sicherheitssensor",   
                272 : "Systemstörung - UBA defekt",   
                273 : "Betriebsunterbrechnung - Brenner und Gebläse",   
                275 : "Geräteelektronik im Testmode",   
                276 : "Die Temperatur am Vorlauf ist höher als 95°C",   
                277 : "Die Temperatur am Sicherheitssensor ist größer als 95°C",   
                278 : "Sensortest fehlgeschlagen",   
                279 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                280 : "Zeitfehler bei Wiederanlaufversuch",   
                281 : "Pumpendruckerhöhung zu niedrig",   
                282 : "Keine Drehzahlrückmeldung der Kesselpumpe",   
                283 : "Der Brenner wird gestartet",   
                284 : "Die Gasarmatur wird geöffnet, 1. Sicherheitszeit",   
                285 : "Die Temperatur am Rücklaufsensor ist größer als 95°C",   
                286 : "Temperatur Rücklaufsensor zu hoch",   
                287 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                288 : "Wasserdrucksensor defekt (Drahtbruch)",   
                289 : "Wasserdrucksensordefekt (Kurzschluss)",   
                290 : "Systemstörung Geräteelektronik (KIM/UBA)",   
                305 : "Der Kessel kann vorübergehend nach Warmwasser-Vorrang nicht starten",   
                306 : "Flammensignal nach Schließen der Brennstoffversorgung",   
                307 : "Die Kesselpumpe ist blockiert",   
                308 : "Die Kesselpumpe dreht ohne Widerstand",   
                309 : "Heiz- und Wärmebetrieb parallel",   
                310 : "Keine Kommunikation mit dem EMS-Wärmeerzeuger",   
                311 : "Alle Wärmeerzeuger verriegelt",   
                312 : "Alle Wärmeerzeuger blockiert",   
                313 : "Wärmeerzeuger gesperrt oder blockiert",   
                323 : "Störung BUS-Konfiguration",   
                328 : "Unterbrechnung der Spannungsversorgung",   
                329 : "Pumpendruckerhöhung zu niedrig",   
                332 : "Temperatur am Kesselvorlaufsensor über 110°C",   
                333 : "Der Kessel hat wegen kurzzeitg zu geringem Wasserdruck abgeschaltet",   
                338 : "Zuviele erfolglose Brennerstartversuche",   
                341 : "Temperaturanstieg Wärmeerzeugertemperatur zu schnell",   
                342 : "Temperaturanstieg Warmwasserbetrieb zu schnell",   
                350 : "Vorlauftemperaturfühler defekt (Kurzschluss)",   
                351 : "Vorlauftemperaturfühler defekt (Drahtbruch)",   
                357 : "Entlüftungsprogramm",   
                358 : "Entlüftungsprogramm",   
                359 : "Temperatur am Warmwasser-Temperaturfühler zu hoch",   
                364 : "Magnetventil EV2 undicht",   
                365 : "Magnetventil EV1 undicht",   
                470 : "Keine Kommunikation mit dem Systemregler",   
                471 : "Vorlaufphase Pumpe in der Inneneinheit",   
                472 : "Vorheizphase der Wärmepumpe",   
                473 : "Wärmepumpe in Betrieb",   
                474 : "Pumpe Hybrid-Manager: Nachlaufphase",   
                475 : "Wärmepumpe im Enteisungsmodus / Abtaumodus",   
                476 : "Wärmepumpe im Störungsmodus",   
                477 : "Nur EMS-Wärmeerzeuger in Betrieb",   
                478 : "Wärmepumpe blokiert, mehr als 4 Starts pro Stunde",   
                479 : "Störung Strömungsschalter Wärmepumpe während Selbsttest",   
                480 : "Differenztemperatur außerhalb des zulässigen Bereichs",   
                481 : "Wärmepumpe läuft bei blockiertem Heizkessel",   
                482 : "Wärmepumpe arbeitet im Servicemodus",   
                500 : "Keine Spannung Sicherheitsrelais",   
                501 : "Sicherheitsrelais hängt",   
                502 : "Keine Spannungsversorgung Brennstoffrelais 1",   
                503 : "Brennstoffrelais 1 hängt",   
                504 : "Brennerstörung Nicht-EMS-Brenner",   
                505 : "Innerhalb von 30 min wurde am STB kein Temperaturanstieg festgestellt",   
                506 : "Temperaturanstieg am STB zu schnell",   
                507 : "STB-Test erfolgreich durchgeführt",   
                508 : "Zu hoher Flammfühler-Strom",   
                509 : "Eingang Flammenfühler defekt",   
                510 : "Fremdlicht Vorbelüftung",   
                511 : "Keine Flamme innerhalb der Sicherheitszeit",   
                512 : "Flammenabriss innerhalb der Sicherheitszeit",   
                513 : "Flammenabriss innerhalb der Nachzündzeit",   
                514 : "Flammenabriss innerhalb der Stabilisierungszeit",   
                515 : "Flammenabriss in Betrieb 1. + 2. Stufe",   
                516 : "Flammenabriss Umschaltung 1. Stufe",   
                517 : "Flammenabriss in Betrieb 1. Stufe",   
                518 : "Flammenabriss Umschaltung 1. + 2. Stufe",   
                519 : "Flammensignal nach Brennerabschaltung",   
                520 : "Vorlauftemperatur hat den maximal zulässigen Wert überschritten (STB)",   
                521 : "Temperaturdifferenz zwischen den Kesselvorlauffühlern zu groß",   
                522 : "Kesselvorlauffühler defekt",   
                523 : "Kesselvorlauffühler defekt (Kabelbruch)",   
                524 : "Kesselvorlauffühler defekt (Kurzschluss)",   
                525 : "Abgastemperatur zu hoch",   
                526 : "Temperaturdifferenz im Abgastemperaturfühler zu groß",   
                527 : "Abgastemperaturfühler defekt",   
                528 : "Abgastemperaturfühler defekt (Kabelbruch)",   
                529 : "Abgastemperaturfühler defekt (Kurzschluss)",   
                530 : "Abgastemperatur zu hoch (STB)",   
                531 : "Wassermangel im Wärmeerzeuger",   
                532 : "Netzspannung zeitweilig zu gering",   
                533 : "Regelung des Wärmeerzeugers hat wasserseitig falsche Durchströmung erkannt",   
                534 : "Kein Gasdruck, oder Abgasdruckbegrenzer hat geschaltet",   
                535 : "Lufttemperatur zu hoch",   
                536 : "Falsche Anbringung Lufttemperatur-/Abgastemperaturfühler",   
                537 : "Keine Drehzahlrückmeldung vom Gebläse",   
                538 : "Gebläse zu langsam",   
                539 : "Gebläsedrehzahl außerhalb des zulässigen Bereichs",   
                540 : "Gebläse zu schnell",   
                542 : "Kommunikation mit Geräteelektronik (SAFe) unvollständig",   
                543 : "Keine Kommunikation mit Geräteelektronik (SAFe)",   
                547 : "Systemstörung Kodierstecker",   
                548 : "Zuviele Wiederholungen (Brennerstarts)",   
                549 : "Sicherheitskette hat geöffnet",   
                550 : "Unterspannung",   
                551 : "Spannungsunterbrechung",   
                552 : "Zu viele Entstörungen über Schnittstelle",   
                553 : "Zu viele Flammenabrisse",   
                554 : "Systemstörung Geräteelektronik (Fehler EEPROM)",   
                555 : "Flammenabriss innerhalb Stabilisierung Zündgas",   
                556 : "Hauptflamme zu früh",   
                557 : "Flammenabriss bei Hauptgas ein",   
                558 : "Keine Bildung der Hauptflamme",   
                559 : "Luftdruckschalter hängt",   
                560 : "Luftdruckschalter offen",   
                561 : "Spannungsunterbrechung während Brennerstart",   
                562 : "Abgasaustrittssicherung zu hohe Temperatur",   
                563 : "Abgasaustrittssicherung zu häufig",   
                564 : "Temperaturanstieg Wärmeerzeugertemperatur zu schnell",   
                565 : "Differenz Vorlauf zu Rücklauf zu groß",   
                566 : "Rücklauftemperatur kleiner -5°C (Unterbrechnung)",   
                567 : "Rücklauftemperatur größer 150°C (Kurzschluss)",   
                568 : "Wasserdrucksensor defekt (Kabelbruch)",   
                569 : "Wasserdrucksensor defekt (Kurzschluss)",   
                570 : "Zuviele Entriegelungen über Schnittstelle",   
                571 : "Zuviele Wiederanläufe trotz Entriegelung",   
                572 : "externe Sperrung aktiv (Klemme EV)",   
                573 : "SAFe unzulässige Werte vom Vorlauftemperaturfühler",   
                574 : "SAFe unzulässige Werte vom Rücklauftemperaturfühler",   
                575 : "Kesselvorlauftemperatur hat maximal zulässigen Wert überschritten (Vorlauf-ISTB)",   
                576 : "Flammensignal während der Vorbelüftung",   
                577 : "Keine Flamme innerhalb der Sicherheitszeit",   
                579 : "kein Gasruck",   
                580 : "Magnetventil 1 undicht",   
                581 : "Magnetventil 2 undicht",   
                582 : "Keine Kommunikation mit Umschaltmodul",   
                583 : "Umschaltmodul externe Verriegelung aktiv",   
                584 : "Umschaltmodul keine Rückmeldung",   
                585 : "Umschaltmodul nicht vorhanden",   
                586 : "Geräteelektronik alter Softwarestand",   
                587 : "Flammenabriss, Stabilisierung Teillast",   
                588 : "Mehr als ein Umschaltmodul im System",   
                589 : "Wärmeerzeuger durch externen Kontakt verriegelt (Klemme 15/16 am BRM10)",   
                590 : "Druckschalter hat während des Betriebes geöffnet",   
                591 : "Abgasklappe öffnet nicht innerhalb von 30 sec",   
                592 : "Abgasklappe dauerhaft geöffnet",   
                593 : "Brücke am Eingang Küchenlüfter (Dunstabzugshaube) fehlt",   
                594 : "Temperaturfühler anstelle Kodierbrücken angeschlossen",   
                601 : "Zu hohe Abweichung Kesselwasser/STB-Fühler",   
                602 : "Zu hohe Unterschiede Abgastemperaturmessung",   
                603 : "Systemstörung: A/D Wandler arbeitet nicht schnell genug",   
                604 : "Systemstörung: Referenzspannung des 2. µC innerhalb ungültiger Grenzen",   
                605 : "Systemstörung: Referenzspannung des 1. µC innerhalb ungültiger Grenzen",   
                606 : "Systemstörung: Fühlertest 2. µC fehlgeschlagen",   
                607 : "Systemstörung: 1. µC hat in 10s keinen Fühlertest durchgeführt",   
                608 : "Systemstörung: 1. µC und 2. µC unterschiedlichen Vorlauftemperaturen",   
                609 : "Systemstörung: 1. µC und 2. µC unterschiedlichen Abgastemperaturen",   
                610 : "Systemstörung: der 2. µC hat verriegelt",   
                611 : "Systemstörung: der 2. µC hat einen anderen Zustand als der 1. µC",   
                612 : "Systemstörung: zu hohe Abweichungen Rücklauftemperatur",   
                613 : "Systemstörung: zu hohe Abweichungen Vorlauftemperatur",   
                620 : "Systemstörung: der 2. µC kommuniziert nicht mit dem 1. µC",   
                621 : "Systemstörung: bei der Kommunikation mit dem 2. µC treten CRC-Fehler auf",   
                622 : "Systemstörung: der 2. µC arbeitet in einem anderen Zeitschlitz als der 1 µC",   
                623 : "Systemstörung: nach einem Power-Up kommuniziert der 2. µC nicht mit dem 1. µC",   
                625 : "Systemstörung: schwankendes Flammensignal",   
                626 : "Systemstörung: Elektrodenspannung falsch",   
                627 : "Systemstörung: Eingang Ionisationsstrom defekt",   
                630 : "Systemstörung: Interner Fehler SAFe",   
                631 : "Systemstörung: Interner Fehler SAFe",   
                640 : "Systemstörung: Interner Fehler SAFe",   
                641 : "Systemstörung: Interner Fehler SAFe",   
                650 : "Systemstörung: Statezahl zu hoch",   
                651 : "Systemstörung: Falsches BIM",   
                652 : "Systemstörung: BIM CRC-Fehler erkannt",   
                653 : "Systemstörung: Verriegelung kann sich nicht gemerkt werden",   
                654 : "Systemstörung: kein EEPROM",   
                655 : "Systemstörung: Verriegelung nicht lesbar",   
                656 : "Systemstörung: Verriegelung nicht schreibbar",   
                657 : "Systemstörung: Verriegelungskennung ungültig",   
                658 : "Systemstörung: Verriegelung CRC-Fehler",   
                659 : "Systemstörung: EEPROM defekt",   
                660 : "Systemstörung: Kodierstecker Kommunikation gestört",   
                661 : "Systemstörung: Kodierstecker",   
                662 : "Systemstörung: Kodierstecker kann nicht gelesen werden",   
                690 : "Relais im Umschaltmodul schaltet nicht nach Vorgabe",   
                691 : "Rückmeldung vom Umschaltmodul, obwohl das Relais nicht angesteuert wird",   
                692 : "Systemstörung",   
                693 : "Systemstörung",   
                694 : "Systemstörung",   
                695 : "Systemstörung",   
                696 : "Systemstörung",   
                697 : "Systemstörung",   
                698 : "Systemstörung",   
                699 : "Systemstörung",   
                700 : "Werksauslieferungszustand",   
                1011 : "Abgastemperatur zu hoch",   
                1012 : "Gebläse läuft nicht korrekt",   
                1013 : "Betriebsstunden abgelaufen",   
                1014 : "Niedriger Flammenfühler-Strom",   
                1015 : "Hoher Zündverzug",   
                1016 : "Häufiger Flammenabriss",   
                1017 : "Wasserdruck zu niedrig",   
                1018 : "Eingestelltes Wartungsdatum wurde erreicht",   
                1019 : "Falscher Pumpentyp erkannt",   
                1020 : "Hoher Flammenstrom",   
                1021 : "Temperaturfühler des Schichtladespeichers defekt",   
                1022 : "Speichertemperaturfüher defekt",   
                1023 : "Maximale Betriebsdauer einschließlich Standby-Zeit ist erreicht",   
                1024 : "Keine Kommunikation zwischen Wärmeerzeuger und Fernbedienung",   
                1025 : "Rücklauftemperaturfühler defekt",   
                1026 : "Speichertemperaturfühler Korrektur zu hoch",   
                1027 : "Speichertemperaturfühler defekt (Solarmodul)",   
                1028 : "Temperaturfühler 3-Wege-Mischer defekt",   
                1029 : "3-Wege-Ventil Mischer defekt",   
                1060 : "Zu viele Startversuche des Kompressors, Wärmepumpe deaktiviert",   
                1061 : "Zu viele Betriebsabbrüche ausgelöst durch Kältemitteldruck, Wärmepumpe deaktiviert",   
                1062 : "Zu viele Startversuche des Gebläses, Wärmepumpe deaktiviert",   
                1063 : "Zu viele Betriebsabrüche, ausgelöst durch Probleme in der Luftzufuhr",   
                1064 : "Wärmepumpentemperaturfühler defekt",   
                1065 : "Wasserdruckfühler defekt",   
                1066 : "Verbrennung (öL-Luft-Verhältnis) nicht optimal",   
                2000 : "keine Spannung Zündtraforelais",   
                2001 : "keine Spannung Zündtraforelais",   
                2002 : "keine Spannung Heizpatronenrelais",   
                2003 : "keine Spannung Heizpatronenrelais",   
                2004 : "Interner Fehler SAFe",   
                2005 : "Mischraumtemperaturfühler defekt (Drahbruch)",   
                2006 : "Mischraumtemperaturfühler defekt (Kurzschluss)",   
                2007 : "Interner Fehler SAFe/BCI",   
                2008 : "Interner Fehler SAFe/BCI",   
                2009 : "Differenz zwischen Mischraumtemperaturfühler 1 und 2 zu groß",   
                2011 : "Interner Fehler SAFe/BCI",   
                2012 : "Interner Fehler SAFe/BCI",   
                2013 : "Interner Fehler SAFe",   
                2014 : "Interner Fehler SAFe/BCI",   
                2015 : "Interner Fehler SAFe/BCI",   
                2016 : "Interner Fehler SAFe/BCI",   
                2017 : "Interner Fehler SAFe",   
                2018 : "Interner Fehler SAFe",   
                2019 : "Interner Fehler SAFe",   
                2020 : "Interner Fehler SAFe",   
                2021 : "Interner Fehler SAFe",   
                2022 : "Interner Fehler SAFe",   
                2023 : "Fühler Heizpatrone defekt (Kurzschluss)",   
                2024 : "Interner Fehler SAFe",   
                2025 : "Interner Fehler SAFe",   
                2026 : "Interner Fehler SAFe",   
                2027 : "Interner Fehler SAFe",   
                2028 : "Interner Fehler SAFe",   
                2029 : "Interner Fehler SAFe",   
                2030 : "Interner Fehler SAFe",   
                2031 : "Interner Fehler SAFe",   
                2032 : "Interner Fehler SAFe",   
                2033 : "Interner Fehler SAFe",   
                2034 : "Interner Fehler SAFe",   
                2035 : "Luftklappenstellung entspricht nicht dem Sollwert",   
                2036 : "Gebläsedrehzahl entspricht nicht dem Sollwert",   
                2037 : "Startdrehzahl am Gebläse nicht erreicht",   
                2038 : "Solltemperatur im Mischraum nicht erreicht",   
                2039 : "Fremdlicht im Feuerraum während Vorbelüftung erkannt",   
                2040 : "Interner Fehler SAFe",   
                2041 : "Fremdlicht im Feuerraum während Nachbelüftung erkannt",   
                2042 : "Heizpatronentemperatur zu hoch",   
                2043 : "Mischraumtemperatur zu niedrig oder zu hoch",   
                2044 : "Interner Fehler SAFe",   
                2045 : "Interner Fehler SAFe/BCI",   
                2046 : "Mindestdrehzahl Gebläse unterschritten",   
                2047 : "Interner Fehler SAFe/BCI",   
                2048 : "Interner Fehler SAFe",   
                2049 : "Interner Fehler SAFe",   
                2050 : "Falschdurchströmung des Kessels",   
                2051 : "Interner Fehler",   
                2052 : "Maximale Einschaltdauer Zündtrafo überschritten",   
                2053 : "Interner Fehler SAFe/BCI",   
                2054 : "Interner Fehler SAFe",   
                2055 : "Interner Fehler SAFe/BCI",   
                2056 : "Interner Fehler SAFe/BCI",   
                2057 : "Interner Fehler SAFe/BCI",   
                2058 : "Interner Fehler SAFe",   
                2059 : "Interner Fehler SAFe",   
                2060 : "Interner Fehler SAFe",   
                2061 : "Interner Fehler SAFe",   
                2062 : "Interner Fehler SAFe",   
                2063 : "Interner Fehler SAFe",   
                2064 : "Interner Fehler SAFe",   
                2065 : "Interner Fehler SAFe",   
                2066 : "Interner Fehler SAFe",   
                2067 : "Interner Fehler SAFe",   
                2068 : "Interner Fehler SAFe",   
                2069 : "Interner Fehler SAFe",   
                2070 : "Interner Fehler SAFe",   
                2071 : "Interner Fehler SAFe",   
                2072 : "Interner Fehler SAFe",   
                2073 : "Interner Fehler SAFe",   
                2074 : "Interner Fehler SAFe",   
                2075 : "Interner Fehler SAFe",   
                2076 : "Interner Fehler SAFe",   
                2077 : "Interner Fehler SAFe",   
                2078 : "Interner Fehler SAFe",   
                2079 : "Interner Fehler SAFe",   
                2080 : "Interner Fehler SAFe",   
                2081 : "Interner Fehler SAFe",   
                2082 : "Interner Fehler SAFe",   
                2083 : "Positionskalibrierung Luftklappe fehlgeschlagen",   
                2084 : "Interner Fehler SAFe",   
                2085 : "Interner Fehler SAFe",   
                2086 : "Interner Fehler SAFe",   
                2087 : "Interner Fehler SAFe",   
                2088 : "Interner Fehler SAFe",   
                2089 : "Interner Fehler SAFe",   
                2090 : "Temperaturanstieg der Heizpatrone zu gering",   
                2091 : "Stellklappe schließt schwergängig",   
                2092 : "Interner Fehler SAFe",   
                2093 : "Interner Fehler SAFe",   
                2094 : "Interner Fehler SAFe",   
                2095 : "Interner Fehler SAFe",   
                2096 : "Interner Fehler SAFe",   
                2097 : "Interner Fehler SAFe",   
                2098 : "Interner Fehler SAFe",   
                2099 : "Interner Fehler SAFe",   
                2100 : "Kurzschluss Mischraumtemperaturfühler",   
                2101 : "Interner Fehler SAFe",   
                2102 : "Interner Fehler SAFe",   
                2103 : "Interner Fehler SAFe",   
                2104 : "Interner Fehler SAFe",   
                2105 : "Interner Fehler SAFe",   
                2106 : "Interner Fehler SAFe",   
                2107 : "Interner Fehler SAFe",   
                2108 : "Interner Fehler SAFe",   
                2109 : "Interner Fehler SAFe",   
                2110 : "Interner Fehler SAFe",   
                2111 : "Interner Fehler SAFe",   
                2112 : "Heizpatrone kühlt nach Abschaltung nicht ab",   
                2113 : "Interner Fehler",   
                2114 : "Schwergängiges Gebläse",   
                2115 : "Interner Fehler SAFe",   
                2116 : "Interner Fehler SAFe",   
                2117 : "Interner Fehler SAFe",   
                2118 : "Interner Fehler SAFe",   
                2119 : "Interner Fehler SAFe",   
                2120 : "Interner Fehler SAFe",   
                2121 : "Interner Fehler SAFe",   
                2122 : "Interner Fehler SAFe",   
                2123 : "Interner Fehler SAFe",   
                2124 : "Interner Fehler SAFe",   
                2500 : "keine Wärmeanforderung",   
                2501 : "Wärmeanforderung wegen Frostschutz",   
                2502 : "Wärmeanforderung wegen Notbetrieb",   
                2503 : "Wärmeanforderung wegen Abgastest",   
                2504 : "Wärmeanforderung wegen Relaistest",   
                2505 : "Wärmeanforderung blockiert wegen Antipendel",   
                2506 : "Wärmeanforderung wegen Heizbetrieb",   
                2507 : "Wärmeanforderung wegen Warmwasserbetrieb",   
                2508 : "Wärmeanforderung wegen Warmwasser/Heizbetrieb",   
                2509 : "Interner Status",   
                2510 : "Wärmeanforderung blockiert weil 24h vorbei",   
                2511 : "Wärmeanforderung blockiert weil GPA nicht kalibriert",   
                2512 : "Wärmeanforderung blockiert auf Grund einer Leistungsbegrenzung",   
                2513 : "Wärmeanforderung blockiert auf Grund von Temperaturdifferenz",   
                2514 : "Wärmeanforderung blockiert wegen Umschaltmodul",   
                2515 : "Wärmeanforderung blockiert weil Kessel warm genug",   
                2517 : "Vorbelüftung",   
                2518 : "Warten Mischraumtemperatur",   
                2519 : "Flamme bilden",   
                2520 : "Flamme stabilisieren",   
                2521 : "Stabilisieren Wärmetauscher",   
                2522 : "Warten Aufheizung Wärmetauscher",   
                2523 : "Umschaltphase (von Start auf Stationär)",   
                2524 : "Nachfackelkontrolle aus Startphase",   
                2525 : "Nachfackelkontrolle aus Stationärbetrieb",   
                2526 : "Nachbelüftung aus Startphase",   
                2527 : "Nachbelüftung aus Stationärbetrieb",   
                2528 : "Gebläse aus",   
                2529 : "Sicherheitsrelais aus",   
                2530 : "Interner Status",   
                2531 : "Wärmeanforderung blockiert weil Mischraum zu kalt",   
            }.get(int(errno),"unbekannt")

"""])
debugcode = """
"""
postlogik=[0,"",r"""
5012|0|"EI"|"buderus_wandkessel_EMS(locals())"|""|0|0|1|0
5012|0|"EC[1]"|"SN[1].incomming(EN[1],locals())"|""|0|0|0|0

#* 1. + 2. Buchstabe Betriebscode EMS-System
5012|0|"SC[2] or SC[3]"|"chr(SN[2])+chr(SN[3])"|""|11|0|0|0

#* Fehlernummer Feuerungsautomat 1.Byte * 256 + 2.Byte  
5012|0|"SC[4] or SC[5]"|"(int(SN[4])*256+int(SN[5]))"|""|12|0|0|0

#* max. Leistung des Brenners 1kW
5012|0|"SC[6] or SC[7]"|"(int(SN[7])*256+int(SN[6]))"|""|18|0|0|0

* Betriebszeit 2.Stufe
5012|0|"SC[8] or SC[9] or SC[10]"|"(int(SN[8])*65536+int(SN[9])*256+int(SN[10]))"|""|60|0|0|0

#* Version des EMS-Master
5012|0|"SC[11] or SC[12]"|"str(SN[11])+"."+str(SN[12])"|""|62|0|0|0

#* Version: Vorkomma-/ Nachkommastelle des Feuerungsautomaten SAFe
5012|0|"SC[13] or SC[14]"|"str(SN[13])+"."+str(SN[14])"|""|64|0|0|0

#* BCM/ BIM- Nummer Byte 1/ Byte2
#5012|0|"SC[15] or SC[16]"|"(int(SN[15])*256+int(SN[16]))"|""|65|0|0|0

5012|0|"AC[12]"|"SN[1].get_fehler_statustext(AN[12])"|""|68|0|0|0

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

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
LOGIKCAT="Buderus"


## Beschreibung
LOGIKDESC="""
<P>Der Baustein stellt die zentrale Kommunikation zwischen einem &quot;Logamatic Gateway RS232&quot; 
von Buderus her, wenn an dieses ein RS232 nach IP Umsetzter wie zum Beispiel ein Moxa angeschlossen ist. Dies stellt die Anwendung 1 dar

Zitat von der Buderus Produkt Seite:
Anwendung 1: Kommunikationsschnittstelle Logamatic 4000 / EMS zu übergeordneten DDC-/GLT- Anlagen z. B. Betriebsartenumschaltung, 
Sollwerte ändern, Istwerte anzeigen, Weiterleitung von Betriebs- und Störmeldungen. 
(Offenlegung Kommunikationsprotokoll zu Logamatic auf Anfrage)

Auf der einen Seite des &quot;Logamatic Gateway RS232&quot; ist der ECO-CAN Bus der Logamatic 4000 Heizungsanlage angeschlossen.
NICHT EMS !!! Dies ist ein anderes Protokoll. Die LED ECO-BUS muß blinken !!!
An der RS232 Schnittstelle des &quot;Logamatic Gateway RS232&quot; ist der Moxa (also RS232 &lt;-&gt; IP Umsetzter)
angeschlossen. Die IP Verbindung ist eine TCP Verbindung, wobei der Moxa der TCP Server ist und der Baustein im HS der TCP Client.
Im Moxa sind folgende Einstellungen zu tätigen (ggf. können einzelne Werte auch anders sein, diese wurden beim Test verwendet):

Für die RS232 Seite (Serial Settings):
Baudrate: 9600
Data Bits: 8
Stop Bits: 1
Parity: Keine
Flow Control: None !!!!
FIFO: Ja
Interface: RS232

Auf der IP Seite (Operational Setting):
- Operation Mode: TCP Server
- TCP alive check time: 7 min
- Inactivity time: 0 ms
- Max Connection: 1 (das kann nur eine sein !!! Der ECO-CAN Bus ist so aufgebaut)
- Local TCP Port:  5508 (Hier muß ein freier Port verwendet werden. Dieser muß dann im Baustein eingetragen werden.)
- Command Port: ist hier nicht relevant, kann irgend ein freier port sein.
Data packaging:
- Packing length: 0
- Delimiter 1: keiner
- Delimiter 2: keiner
- Delimiter process: keiner
- Force transmit: Nein
  
Der Moxa hat auch eine IP Adresse: z.B. 192.168.2.17 zusammen mit dem Local Port: hier z.B. 5208 stellt man das im Baustein 
dann so dar: 192.168.2.17:5208
Der Baustein öffnet also eine Verbindung zu diesem Port und erhält sie kontinuierlich aufrecht. Diese Kommunikation ist noch mit dem
 R3964R Protokoll geschützt. Dies macht der Baustein aber alles intern und nur die ausgepackten Informationen werden weitergegeben.
 </P>
<P>Diese Schnittstelle bietet viele Möglichkeiten Monitordaten der Heizung mitzulesen und aber auch 
Konfigurationen der Heizungsanlage zu verändern. Das Verändern sollte man aber dem Heizungfachmann
 überlassen. Weiter ist jeder Schreiben Zugriff, ein Schreiben auf den Flash Speicher. Laut Buderus geht das pro Wert nur 1.000.000 Mal.
 </P>
 <P>Also, aus diesem Grund gibt es hier die sehr ernst gemeinte Empfehlung nur lesend diesem Baustein zu verwenden.<BR>
 Die Config Option &quot;readonly=1&quot; sollte deshalb immer gesetzt bleiben. </P>
<P>Für die eigentlich Kommunikation sind zwingend folgende Beschreibungen von Buderus zu beachten:<BR>
7747004149 – 01/2009 DE - Technische Information - Monitordaten - System 4000<BR>
7747004150 – 05/2009 DE - Technische Information - Einstellbare Parameter - Logamatic 4000<BR>
Weiter ist folgende Beschreibung sehr Wertvoll:<BR>
 Funktionsbeschreibung - KM471- RS232-Schnittstelle (3964R) - Für Programmversion 1.07<BR>
Die Kommunikationskarte KM471 ist das Modul, was auf der Buderus Seite den Datenaustauch abwickelt.<BR>
Zumindest ist in dem heutigen Easycom RS232 Gateway etwas vergleichbares drin.</P>
<P>Der Baustein kapselt für den Benutzer komplett die 3964R Procedure. Auch schaltet er automatisch in den Direkt Mode um, bei Kommandos 
die den &quot;Direktmode&quot; benötigen. Er erkennt automatisch das Ende und schalten automatisch wieder in den Normal Mode zurück.
Ein Warten (und damit blockierend), dass in den Normal-Mode erst nach einem Timeout zurück geschaltet wird, kann somit vermieden werden. 
Man kann sagen der Benutzer braucht sich um Normal-Mode und Direkt-Mode gar nicht kümmern. Dies geschieht alles automatisch.   </P>
Für die Auswertung der Daten, die auf dem Ausgang 1 ausgegeben werden, gibt es für jeden DatenType dann einen eigenen Baustein. Dieser ist dann immer
über ein iKO vom Type 14Byte dann dort an zu schliessen. NIE DIREKT !!! Als erster wird der Solar DatenTyp veröffentlicht, weitere werden folgen.

Welche DatenTypen an welchen Regelgeräten angeschlossen sind kann man im SystemLog sehen. Die Regelgeräte haben meist die Nummer 0 wenn nur eins angeschlossen ist. 
Sonst dann 1, 2 , wenn es mehrere sind.

Wenn man nun nach dem SystemStart=1 des HS zum Beispiel mit A100 alle Monitordaten des Regelgerätes 0 abfragt, werden alle Monitordaten einmal ausgelesen.
Ändern sich dann später ein Wert, werden diese im Normal-Mode automatisch gesendet und im HS dann auch aktualisiert. 

<P>Folgende Kommandos sind getestet:<BR>
# Zeit abfragen mit &quot;B1&quot;: ok<BR>
EN[3]:&quot;B1&quot;   <BR>
# Zeit setzen mit &quot;B2&lt;Zeit beschrieben in Dokument Technische Information - Einstellbare Parameter&gt; : ok <BR>
EN[3]:&quot;B2121D941FD572&quot;<BR>
# Anfordern des ECO-BUS Geräte Status, Endekennung: 0xA8 0x80+adr &lt; Seriennummer &gt; &lt;version vorkomma&gt; &lt;version nachkomma&gt;<BR>
EN[3]:&quot;A000&quot;<BR>
#  'A8010948849F40E4'   A8: Antwort , 01: Gerätestatus von Gerät #1 , 0948849F40E4: &lt;6Byte Seriennummer&gt; Codierung unklar<BR>
#  'A8020930032FC00C'   A8: Antwort , 02: Gerätestatus von Gerät #2 , 0930032FC00C: &lt;6Byte Seriennummer&gt; Codierung unklar<BR>
#  'A8940102030405060F17'   0xA8 0x80+0x14 &lt; Seriennummer '010203040506'&gt; &lt;version vorkomma 0x0F -&gt; dez. 15&gt; &lt;version nachkomma 0x17 -&gt; dez. 23&gt;<BR>
#                           Endekennung muß also 0x08 0x[89abcdef]? sein. ; Das ist die Version des EasyCom: 15.23 Sieht man nur über die ECO-SOFT.<BR>
Mit diesem Kommando &quot;A000&quot; kann man zum Beispiel nach dem System Start erstmal den Bus abfragen welche Geräte existieren. Hier sind auf dem ECOCAN Bus<BR>
 die Adressen 1 und 2 vergeben. </P>
<P>Nun kann man mit A1 gefolgt von der Adresse des Regelgeräts alle einstellbaren Parameter abfragen: <BR>
##Anfordern aller einstellbaren Parameter eines Gerätes <BR>
#EN[3]:&quot;A101&quot;<BR>
#EN[3]:&quot;A102&quot;<BR>
## Endekennung &quot;AA&lt;busnr&gt;  hier also AA01 bzw. AA02 ## beides Ok</P>
<P>##Anfordern aller einstellbaren Parameter eines Gerätes im Block mode<BR>
EN[3]:&quot;B301&quot;<BR>
EN[3]:&quot;B302&quot;<BR>
## Endekennung &quot;AA&lt;busnr&gt;  hier also AA01 bzw. AA02 ## beides Ok</P>
<P>## Einzelabfrage A3 eines einstellbaren Parameter eines Gerätes, nur Beispiel<BR>
EN[3]:&quot;A3010704&quot;</P>
<P>## Einzelabfrage von Monitordaten eines Gerätes, nur Beispiel<BR>
EN[3]:&quot;A3018004&quot;<BR>
## ok<BR>
Das, was die meisten machen sollte ist nach dem Systemstart alle Monitor Daten einmal abzufragen.<BR>
##Anfordern aller Monitordaten eines Gerätes <BR>
#EN[3]:&quot;A201&quot;<BR>
#EN[3]:&quot;A202&quot;<BR>
## Endekennung &quot;AC&lt;busnr&gt;  hier also AC01 bzw AC02 ## beides Ok</P>
<P>##Anfordern aller Monitordaten eines Gerätes im Blockmode<BR>
EN[3]:&quot;B401&quot;<BR>
EN[3]:&quot;B402&quot;<BR>
## Endekennung &quot;AC&lt;busnr&gt;  hier also AC01 oder AC02 ## beides Ok</P>

Kommandos können auch durch ein &quot;*&quot; Zeichen getrennt gebündelt gesendet werden (z.B. &quot;A101*A102&quot;). Der Baustein 
sendet sie dann nacheinander weiter. 

Rechtliche Hinweise:
Die Produkte &quot;Logamatic 4000&quot;,  &quot;Logamatic Gateway RS232&quot; sind Produkte der Buderus Heiztechnik GmbH. - www.Buderus.de
Die Benutzung dieses Bausteins geschieht auf eigene Gefahr. 

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

5000|"'''+LOGIKCAT+'''\\'''+LOGIKNAME+'''"|0|3|"E1 IP-Adresse:Port"|"E2 config"|"E3 senden"|2|"A1 Daten"|"A2 SystemLog"|"'''+VERSION+'''"

5001|3|2|0|1|1

# EN[x]
5002|1|"192.168.2.17:5208"|1 #* IP-Adresse:Port <BR>des Moxa
5002|2|""|1 #* config <BR>(mit debug=5 wird diese Konfiguration auf SystemLog ausgegeben, readonly=1 weist schreibende Kommandos ab, und writetime=1 erlaubt die BUS Zeit zu setzen) Der * ist das Trennzeichen.
5002|3|""|1 #* Senden <BR>(Hier werden die Kommandos an den ECOCAN Bus gesendet)

# Speicher
5003|1||0 #* logic

# Ausgänge
5004|1|""|0|1|1 #* Daten <BR>(Hier werden alle Antworten vom ECOCAN ausgegeben, hier müssen die Auswerte Bausteine immer über ein iKO angeschlossen werden)
5004|2|""|0|1|1 #* SystemLog <BR>(Ausgang an den SystemLog)

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
                'debug': 0,                 # debug level (> 5) macht debug prints
                'readonly' : 1,             # wenn readyonly=1 , werden schreibende Befehle nicht zugelassen
                'writetime' : 0,            # wenn writetime=1 , wird das schreiben der Zeit zugelassen
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
            self.data_types = {
                "07" : ("Heizkreis 1", 18),
                "08" : ("Heizkreis 2", 18),
                "09" : ("Heizkreis 3", 18),
                "0A" : ("Heizkreis 4", 18),
                "0B" : ("Außenparameter", 12),
                "0C" : ("Warmwasser", 12),
                "0D" : ("Konfiguration (Modulauswahl)", 18),
                "0E" : ("Strategie wandhängend(UBA)", 18),
                "10" : ("Kessel bodenstehend", 18),
                "11" : ("Schaltuhr pro Woche Kanal 1", 18),
                "12" : ("Schaltuhr pro Woche Kanal 2", 18),
                "13" : ("Schaltuhr pro Woche Kanal 3", 18),
                "14" : ("Schaltuhr pro Woche Kanal 4", 18),
                "15" : ("Schaltuhr pro Woche Kanal 5", 18),
                "16" : ("Heizkreis 5", 18),
                "17" : ("Schaltuhr pro Woche Kanal 6", 18),
                "18" : ("Heizkreis 6", 18),
                "19" : ("Schaltuhr pro Woche Kanal 7", 18),
                "1A" : ("Heizkreis 7", 18),
                "1B" : ("Schaltuhr pro Woche Kanal 8", 18),
                "1C" : ("Heizkreis 8", 18),
                "1D" : ("Schaltuhr pro Woche Kanal 9", 18),
                "1F" : ("Schaltuhr pro Woche Kanal 10", 18),
                "20" : ("Strategie bodenstehend", 12),
                "24" : ("Solar", 12),
                "26" : ("Strategie (FM458)", 12),
                "80" : ("Heizkreis 1", 18),
                "81" : ("Heizkreis 2", 18),
                "82" : ("Heizkreis 3", 18),
                "83" : ("Heizkreis 4", 18),
                "84" : ("Warmwasser", 12),
                "85" : ("Strategie wandhängend", 12),
                "87" : ("Fehlerprotokoll", 42),
                "88" : ("Kessel bodenstehend", 42),
                "89" : ("Konfiguration", 24),
                "8A" : ("Heizkreis 5", 18),
                "8B" : ("Heizkreis 6", 18),
                "8C" : ("Heizkreis 7", 18),
                "8D" : ("Heizkreis 8", 18),
                "8E" : ("Heizkreis 9", 18),
                "8F" : ("Strategie bodenstehend", 30),
                "90" : ("LAP", 18),
                "92" : ("Kessel 1 wandhängend", 60),
                "93" : ("Kessel 2 wandhängend", 60),
                "94" : ("Kessel 3 wandhängend", 60),
                "95" : ("Kessel 4 wandhängend", 60),
                "96" : ("Kessel 5 wandhängend", 60),
                "97" : ("Kessel 6 wandhängend", 60),
                "98" : ("Kessel 7 wandhängend", 60),
                "99" : ("Kessel 8 wandhängend", 60),
                "9A" : ("KNX FM446",60),
                "9B" : ("Wärmemenge", 36),
                "9C" : ("Störmeldemodul", 6),
                "9D" : ("Unterstation", 6),
                "9E" : ("Solarfunktion", 54),
                "9F" : ("alternativer Wärmeerzeuger", 42),
            }

            ## List für gefundene Geräte
            self.found_devices = []

            ## List die Geräte IDs enthällt bei denen Antworten ausstehen
            self.waiting_direct_bus = []

            ## threading Lock um _is_directmode und waiting_direct_bus zu beschreiben
            self.directmode_lock = threading.RLock()

            ## Derzeitiger Direct-mode status
            self._is_directmode = False

            self._moxa_thread = None

            ## Socket zum MOXA
            self.sock = None

            ## threading Lock für exklusives schreiben von entweder der Empfangs- oder Sende- Funktion
            self._buderus_data_lock = threading.RLock()
  
            ## Queue für Nachrichten zum Logamtik
            self._buderus_message_queue = Queue()
  
            ## Konfig an Eingang 2 parsen
            self.readconfig(EN[2])

            ## Mit dem Kommando "0xA2 <ECOCAN-BUS-Adresse>" können die Monitordaten des ausgewählten 
            ## ECOCAN-BUS-Gerätes von der Kommunikationskarte ausgelesen werden. 
            ## Mit Hilfe des Kommandos "0xB0 <ECOCAN-BUS-Adresse>" gefolgt von einem entsprechenden 
            ## Datenblock können im Direkt-Modus einstellbare Parameter die für ein Regelgerät bestimmt sind an die 
            ## Schnittstelle geschickt werden. Die Schnittstelle schickt diese Daten dann weiter an das entsprechende 
            ## Regelgerät. 

            self.directmode_regex = re.compile("(?P<id>A0|A1|A2|B3|B4)(?P<busnr>[0-9a-fA-F]{2})")

            self.directmode_regexes = {
                "A3" : re.compile("(?P<id>A3)(?P<busnr>[0-9a-fA-F]{2})(?P<Data_type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})"),
                "B0" : re.compile("(?P<id>B0)(?P<busnr>[0-9a-fA-F]{2})(?P<Data_type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})[0-9a-fA-F]{12}"),
                "B1" : re.compile("(?P<id>B1)"), ## Datum/Uhrzeit vom ECOBUS anfordern
                "B2" : re.compile("(?P<id>B2)[0-9a-fA-F]{12}"), ## Datum/Uhrzeit auf ECOBUS schreiben
            }

            ## Im "Normal-Modus" werden die Monitordaten nach folgendem Muster übertragen: 
            ## 0xA7 <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <DATUM> 
            ## 0xA7 = Kennung für einzelne Monitordaten 
            ## ECOCAN-BUS-Adresse = Herkunft´s Adresse des Monitordatum´s (hier Regelgeräteadresse) 
            ## TYP = Typ der empfangenen Monitordaten       
            ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s 
            ## DATUM = eigentlicher Messwert 

            ## Im "Direct-Modus" werden alle Monitordaten nach folgendem Muster übertragen: 
            ## 0xAB <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <6 Daten-Byte> 
            ## 0xAB = Kennung für Monitordaten 
            ## ECOCAN-BUS-Adresse = die abgefragte Adresse zur Bestätigung 
            ## TYP = Typ der gesendeten Monitordaten
            ## Daten unter dem entsprechenden Typ werden nur gesendet wenn auch die entsprechende Funktionalität 
            ## im Regelgerät eingebaut ist. 
            ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s

            ## Im "Direct-Modus" werden alle Einstellbaren Parameter nach folgendem Muster übertragen: 
            ## 0xA9 <ECOCAN-BUS-Adresse> <TYP> <OFFSET> <6 Daten-Byte> 
            ## 0xA9 = Kennung für Monitordaten 
            ## ECOCAN-BUS-Adresse = die abgefragte Adresse zur Bestätigung 
            ## TYP = Typ der gesendeten Monitordaten
            ## Daten unter dem entsprechenden Typ werden nur gesendet wenn auch die entsprechende Funktionalität 
            ## im Regelgerät eingebaut ist. 
            ## OFFSET = Offset zur Einsortierung der Daten eines Typ´s

            self.payload_regex = re.compile("(?P<id>B8|B9|A9|AB|B7)(?P<busnr>[0-9a-fA-F]{2})(?P<data_type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{12})+)")
            
            self.payload_regexes = {
                "A7" : re.compile("(?P<id>A7)(?P<busnr>[0-9a-fA-F]{2})(?P<data_type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{2}))"),
                "A8" : re.compile("(?P<id>A8)(?:(?P<busnr>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{12}))$|[8-9a-fA-F][0-9a-fA-F]{13}(?P<version_vk>[0-9a-fA-F]{2})(?P<version_nk>[0-9a-fA-F]{2}))"),
                "AE" : re.compile("(?P<id>AE)(?P<busnr>[0-9a-fA-F]{2})(?P<data>[0-9A-F]{8})"), ## Fehlerstatus
                "AF" : re.compile("AF(?P<bustime>[0-9a-fA-F]{12}|FF)") ## Uhrzeit Datum
            }

            ## Als Endekennung für das abgefragte Regelgerät oder falls keine Daten vorhanden sind, wird der 
            ## nachfolgende String 
            ## 0xAC <ECOCAN-BUS-Adresse> gesendet  Endekennung bei A2<busnr> und bei B4<busnr>
            ## 0xAA <ECOCAN-BUS-Adresse> gesendet  Endekennung bei A1<busnr>
            ## 0xA8 0x80+adr < Seriennummer > <version vorkomma> <version nachkomma> Endekennung bei A100 
            ##  Da A8 auch als normale Antwort kommt, muß auf A8[89a-fA-F]? abgefragt werden
            self.directmode_finish_regex = re.compile("(AC|AA|AD)(?P<busnr>[0-9a-fA-F]{2})")
            #self.directmode_finish_AD_regex = re.compile("AD(?P<busnr>[0-9a-fA-F]{2})(?P<data_type>[0-9a-fA-F]{2})(?P<offset>[0-9a-fA-F]{2})(?P<data>(?:[0-9A-F]{12}))")
            
            ## 
            ## 1.Byte Sekunden (0-59)
            ## 2.Byte Minuten (0-59)
            ## 3.Byte Stunden / Sommerzeit
            ##      Bit 1-5 Stunden
            ##      Bit 6 intern
            ##      Bit 7 Sommerzeit (1=Sommerzeit)
            ##      Bit 8 Funkuhr (1=ist Funkuhrzeit)
            ## 4.Byte Tag (1-31)
            ## 5.Byte Monat / Wochentag
            ##      Bit 1-4 Monat
            ##      Bit 5-7 Wochentag
            ##      Bit 8 Funkuhrempfang zugelassen
            ## 6.Byte Jahr (89-188) > 100 20xx sonst 19xx
            ##

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
                    self.log("unbekannte Konfig Option %s=%s" % (option,value), severity="error" )
                    continue
                ## versuchen Wert im config string zum richtigen Type zu machen
                try:
                    _val = _configtype(value)
                    self.config[option] = _val
                    #self.debug("Konfig Option %s=%s empfangen" % (option,value ), 5 )
                except ValueError:
                    self.log("falscher Wert bei Konfig Option %s=%s (erwartet %r)" % (option,value, _configtype ), severity="error" )
                    pass

        def time_to_bustime(self,set_time,funkuhr=0):
            return ("{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}".format(
                set_time[5], ## Sekunden
                set_time[4], ## Minuten
                set_time[3] + (set_time[8] << 6) + (funkuhr << 7) , ## Stunden + Bit 7 Sommerzeit + Bit 8 Funkuhr
                set_time[2], ## Tag
                set_time[1] + ((set_time[6] + 1) << 4), ## Bit 1-4 Monat + Bit 5-7 (Wochentag +1)
                set_time[0] - 1900 ## Jahr -1900
            )).upper()

        def bustime_to_time(self,bustime):
            import binascii
            bustime = bustime.lstrip("AF")
            _bustime = [ ord(x) for x in binascii.unhexlify(bustime) ]
            return [
                (_bustime[5] + 1900), ## Jahr
                (_bustime[4] & 0xf), ## Monat
                _bustime[3], ## Tag
                _bustime[2] & 0x1f, # Stunden
                _bustime[1], ## Minuten
                _bustime[0], ## Sekunden
                (_bustime[4] >> 4 & 0x7) -1 , ## Wochentag
                0,
                -1 ##_bustime[2] >> 6 & 0x1 ## Sommerzeit ##FIXME## Time unknown
            ]

        def device_addresses(self,msg):
            _ret = []
            _addresses = map(lambda x: x=="1",bin(int(msg,16))[2:][::-1])
            for _addr in xrange(len(_addresses)):
                if _addresses[_addr]:
                    _ret.append(_addr)
            return _ret

        def debug(self,msg,lvl=8):
            ## wenn debuglevel zu klein gleich zurück
            if self.config.get("debug") == 0:
                return
            import time

            ## FIXME sollte später gesetzt werden
            if lvl < 10 and lvl <= (self.config.get("debug")):
              self.log(msg,severity='debug')
            if (self.config.get("debug") == 10):
              print "%s DEBUG-12264: %r" % (time.strftime("%H:%M:%S"),msg,)

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

                ## solange noch ein direkt mode Befehlt austeht, darf kein neuer geschickt werden.
                if self.get_direct_waiting():
                    continue

                ## nächste payload aus der Queue holen
                msg = self._buderus_message_queue.get()
                ## nach gültigen zu sendener payload suchen

                _cmdid = msg[:2]
                _direct_mode_regex = self.directmode_regexes.get(_cmdid,self.directmode_regex)
                _direct_mode = _direct_mode_regex.search(msg)

                ## wenn keine gültige SENDE payload
                if not _direct_mode:
                    self.log("ungültige sende Nachricht %r" % (msg,) )
                    continue

                if _cmdid in [ "B1","B2"]:
                    _busnr = _cmdid
                else:
                    _busnr = _direct_mode.group("busnr")

                if self.config.get("readonly"):
                    if _cmdid == "B0":
                        self.log("schreiben auf den Bus deaktiviert, Payload verworfen",severity="warn")
                        continue
                    if _cmdid == "B2" and not self.config.get("writetime"):
                        self.log("schreiben der Uhrzeit deaktiviert, Payload verworfen",severity="warn")
                        continue

                ## Wenn eine direct-mode anfrage
                if _cmdid in ["A0","A1","A2","A3","B3","B4"]:
                    if _busnr not in self.waiting_direct_bus:
                        ## busnr zur liste auf Antwort wartender hinzu
                        self.add_direct_waiting(_busnr)
                    else:
                        ## Bus wird schon abgefragt
                        continue

                self._buderus_data_lock.acquire()
                self.debug("sende Queue exklusiv lock erhalten")
                try:
                    ## wenn wir nicht schon im directmode sind oder nicht auf den directmode schalten konnten 
                    if not self.is_directmode():
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
            self.debug("check Directmode",lvl=7)
            ## wenn direct mode nicht an ist, dann gleich zurück
            if not self.is_directmode():
                self.debug("kein Directmode",lvl=7)
                return

            ## wenn die Sendewarteschlange leer ist und keine Antworten(AC<busnr>) mehr von einem A2<busnr> erwartet werden,
            ## dann directmode ausschalten
            if (self._buderus_message_queue.empty() and not self.get_direct_waiting()):
                self.debug("deaktiviere Directmode",lvl=7)
                self.set_directmode(False)
            else:
                self.debug("check nicht Directmode",lvl=7)

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
                    self.debug("jetzt payload %r senden" % (payload,) ,lvl=5)
                    self.send_payload(payload)

                    ## returnwert auf True
                    _ret = True
                else:
                    ## wenn kein DLE auf unser STX kam dann payload verwerfen
                    self.debug("payload %r verworfen" % (payload,) ,lvl=4)

            except:
                ## Fehler auf die HS Debugseite
                self.MC.Debug.setErr(sys.exc_info(),"%r" % (payload,))
            return _ret

        ## send_out: Wert auf einen Ausgang senden
        ## Parameter out: Ausgang auf den gesendet werden soll analog zu AN[x]
        ## Parameter value: Wert der an den Ausgang gesendet werden soll
        def send_to_output(self,out,value):
            import time
            out -= 1 ## Intern starten die Ausgänge bei 0 und nicht bei 1
            ## Sendeintervall wird beachtet
            if self.logik.SendIntervall == 0 or time.time() >= self.logik.Ausgang[out][0]:

                ## Wert an allen iKOs an den Ausgängen setzen
                for iko in self.logik.Ausgang[out][1]:
                    self.logik.MC.TagList.setWert(FLAG_EIB_LOGIK,iko, value)

                ## Wenn value nicht 0 / "" / None etc ist dann die Befehle ausführen
                if value:
                    for cmd in self.logik.Ausgang[out][2]:
                        cmd.execBefehl()

                ## Direkte Verbindungen und Connectoren
                for con in self.logik.Ausgang[out][3]:
                    self.logik.MC.LogikList.ConnectList.append(con + [ value ])

                ## Wenn Sendeintervall gesetzt, nächste mögliche Ausführungszeit setzen
                if self.logik.SendIntervall > 0:
                    self.logik.Ausgang[out][0] = time.time() + self.logik.SendIntervall

                ## Ausgangswert auch in der Logik setzen
                self.logik.OutWert[out] = value

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
            self.debug("incomming message %r" % (msg), lvl=5)
            ## mit * getrennte messages hinzufügen
            for _msg in msg.split("*"):

                ## leerzeichen entfernen 
                _msg = _msg.replace(' ','')

                ## _msg in die sende Warteschlange
                self._buderus_message_queue.put( _msg )

        def busnr_4byte_to_list(self,bytes):
            return (lambda addr: [x for x in xrange(len(addr)) if addr[x] ])(map(lambda x: x=="1",bin(int(bytes,16))[2:])[::-1])

        def parse_payload(self,payload):
            import time,binascii
            
            _cmdid = payload[:2]
            
            if _cmdid in ["A5","A6"]:
                self.debug("%s in Busgeräte: %r" % (_cmdid,self.busnr_4byte_to_list(payload[2:10])),lvl=6)
                return True
                
            _payload_regex = self.payload_regexes.get(_cmdid,self.payload_regex)

            ## nach gültiger payload suchen
            _payload = _payload_regex.search(payload)

            ## wenn normal-mode oder direct mode antwort 
            if _payload:
                if _cmdid == "A5":
                    pass
                    
                if _cmdid == "A6":
                    pass
                    
                ## wenn einen normal mode antwort mit Typ A7 kommt und der direktmode gerade an ist, 
                ## dann ist der 60 Sekunden Timeout abgelaufen ohne die Daten rechtzeitig erhalten zu haben
                if _cmdid in ["A7", "B7"] and self.is_directmode():
                    self.remove_direct_waiting()
                    ## Der "Direkt-Modus" kann durch das Kommando 0xDC wieder verlassen werden. 
                    ## Außerdem wird vom "Direkt-Modus" automatisch in den "Normal-Modus" zurückgeschaltet, wenn für die 
                    ## Zeit von 60 sec kein Protokoll des "Direkt-Modus" mehr gesendet wird. 
                    self.log("Directmode timeout")

                if _cmdid == "A8" and self.is_directmode():
                    if _payload.groupdict().get("busnr"):
                        self.log("Regelgerät %s an ECOCAN BUS gefunden" % (  _payload.group("busnr") ) , severity="info")
                    else:
                        self.log("ECOCAN BUS Version %r.%r gefunden" % ( ord(binascii.unhexlify(_payload.group("version_vk"))), ord(binascii.unhexlify(_payload.group("version_nk"))) ) ,severity="info")
                        self.remove_direct_waiting("00") # da mit "A000" eingeleitet ist, dann ist die Busnr "00", diese muß nun wieder gelöscht werden
                        time.sleep( self.config.get('delaydirectendtime') )
                        self.check_directmode_needed()
                
                if _cmdid == "AF":
                    _bustime = _payload.group("bustime")
                    if _bustime == "FF":
                        self.log("Keine ECOBUS-Uhrzeit vorhanden")
                    else:
                        _time = self.bustime_to_time(_bustime)
                        _diff = time.mktime(_time) - time.time()
                        self.log("ECOBUS-Uhrzeit empfangen: {0} (Differenz {1:.1f}sec)".format(time.strftime("%a %d.%m.%Y %H:%M:%S",_time),_diff))
                
                if _cmdid in ["A7","A9","AB","B7","B8","B9"]:
                    ## Datentype
                    _type = _payload.group("data_type")

                    ## wenn wir das Gerät noch nicht gefunden hatten kurze Info über den Fund loggen
                    if _type not in self.found_devices:
                        self.found_devices.append( _type )
                        (_devicename, _datalen) = self.data_types.get( _type, ("unbekannter Datentyp (%s)" % _type, 0) )
                        self.log("Datentyp '%s' an Regelgerät %d gefunden" % ( _devicename, int(_payload.group("busnr")) ) , severity="info")

                return True
            else:
                ## wenn eine Endekennung AC|AA|AD<busnr> empfangen wurde, dann die busnr aus der liste für direct Daten entfernen und evtl direct_mode beenden
                _direct = self.directmode_finish_regex.search(payload)
                if _direct:
                    _busnr = _direct.group("busnr")
                    ## bus von der liste auf antwort wartender im direct mode entfernen
                    self.remove_direct_waiting(_busnr)
                    #self.log("BusNr %s gelöscht" % ( repr(_busnr) ) ,severity="info")
                    ## Wenn ein AC<busnr> gekommen ist, wird ggf. die Sende Richtung geändert, was zu Initialisierungskonflikten führen kann
                    time.sleep( self.config.get('delaydirectendtime') )
                    self.check_directmode_needed()
                    if _cmdid == "AD":
                        return True
                else:
                    self.debug("NO Payload found",lvl=5)

            return False

        def wait_for_ready_to_receive(self):
            import select,time
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
                        self.debug("STX empfangen Initialisierungskonflikt",lvl=5)
                        time.sleep(self._constants['ZVZ'])

                        ## DLE senden, dass wir Daten vom anderen Gerät akzeptieren senden
                        self.sock.send( self._constants['DLE'] )
                        self.debug("DLE gesendet")

                        ## eigentlich Funktion aus dem connect zum lesen der payload hier ausführen
                        self.read_payload()

                        ### danach loop und erneuter sende Versuch
                    else:
                        self.debug("%r empfangen" % (data,),lvl=9 )

            self.debug("Nach 3x STX senden innerhalb QVZ kein DLE",lvl=5)
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
                    self.log("Verbindung zu Netzwerkschnittstelle %s:%s hergestellt" % (_ip,_port))
                except (TypeError,ValueError):
                    self.log("ungültige IP:Port Kombination %r an Eingang 1" % self.device_connector, severity="error")
                    return
                except socket.error as error:
                    self.log("Verbindung zu Netzwerkschnittstelle %s:%s fehlgeschlagen" % (_ip,_port),severity="error")
                    raise

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
                                self.debug("Verbindung abgebrochen",lvl=3)
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
            
            ## Ungültige Payload abfangen um exception zu verhindern
            if len(payload) % 2:
                self.debug("ungültige Payloadlänge",lvl=1)
                return
                
            for _loop in xrange(6):
                self.debug("exklusiv senden / versuch %d" % (_loop),lvl=6)

                ## checksumme
                _bcc = 0
                for _byte in binascii.unhexlify(payload):

                    ## Byte an Gerät schicken
                    self.sock.send( _byte )
                    self.debug("Byte %r versendet" % (binascii.hexlify(_byte)),lvl=8 )

                    ## Checksumme berechnen
                    _bcc ^= ord(_byte)

                    ## Wenn payload ein DLE ist
                    if _byte == self._constants['DLE']:

                        ## dann in der payload verdoppeln
                        self.sock.send( _byte )
                        self.debug("Payload enthällt DLE, ersetzt mit DLE DLE",lvl=7 ) 

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
                self.debug("Kein DLE erhalten loop",lvl=6)
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
                self.debug("exklusiv lesen / versuch %d" % (_loop),lvl=8)

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
                        self.debug("Keine Daten / verbindung verloren",lvl=3)
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
                            if self.parse_payload( _hexpayload ):
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
                    self.debug("Daten %r empfangen" % (binascii.hexlify(data)),lvl=7)

                    ## letztes zeichen speichern
                    _lastchar = data

"""])

debugcode = """

"""
postlogik=[0,"",r"""

5012|0|"EI"|"buderus_connect(locals())"|""|0|0|1|0
5012|0|"EC[2]"|"SN[1].readconfig(EN[2])"|""|0|0|0|0
5012|0|"EC[3]"|"SN[1].incomming(EN[3].upper())"|""|0|0|0|0

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

#!/usr/bin/env python
# #
# APRS Symbol Tables and Symbols
#
from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)

from pymongo import MongoClient

u"""/$ XYZ BASIC SYMBOL TABLE"""
BASIC_SYMBOL_TABLE = dict()
BASIC_SYMBOL_TABLE["/!"] = "BB  Police, Sheriff"
BASIC_SYMBOL_TABLE["/\""] = "BC  reserved (was rain)"
BASIC_SYMBOL_TABLE["/#"] = "BD  DIGI (white center)"
BASIC_SYMBOL_TABLE["/$"] = "BE  PHONE"
BASIC_SYMBOL_TABLE["/%"] = "BF  DX CLUSTER"
BASIC_SYMBOL_TABLE["/&"] = "BG  HF GATEway"
BASIC_SYMBOL_TABLE["/'"] = "BH  Small AIRCRAFT (SSID-11)"
BASIC_SYMBOL_TABLE["/("] = "BI  Mobile Satellite Station"
BASIC_SYMBOL_TABLE["/)"] = "BJ  Wheelchair (handicapped)"
BASIC_SYMBOL_TABLE["/*"] = "BK  SnowMobile"
BASIC_SYMBOL_TABLE["/+"] = "BL  Red Cross"
BASIC_SYMBOL_TABLE["/,"] = "BM  Boy Scouts"
BASIC_SYMBOL_TABLE["/-"] = "BN  House QTH (VHF)"
BASIC_SYMBOL_TABLE["/."] = "BO  X"
BASIC_SYMBOL_TABLE["//"] = "BP  Red Dot"


u""""/$ XYZ ALTERNATE SYMBOL TABLE"""
ALTERNATE_SYMBOL_TABLE  = dict()
ALTERNATE_SYMBOL_TABLE["\\$"] = "XYZ ALTERNATE SYMBOL TABLE (\)"
ALTERNATE_SYMBOL_TABLE["\\0"] = "A0# CIRCLE (IRLP/Echolink/WIRES)"
ALTERNATE_SYMBOL_TABLE["\\1"] = "A1  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\2"] = "A2  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\3"] = "A3  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\4"] = "A4  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\5"] = "A5  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\6"] = "A6  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\7"] = "A7  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\8"] = "A8O 802.11 or other network node"
ALTERNATE_SYMBOL_TABLE["\\9"] = "A9  Gas Station (blue pump)"
ALTERNATE_SYMBOL_TABLE["\\:"] = "NR  AVAIL (Hail ==> ` ovly H)"
ALTERNATE_SYMBOL_TABLE["\\;"] = "NSO Park/Picnic + overlay events"
ALTERNATE_SYMBOL_TABLE["\\<"] = "NTO ADVISORY (one WX flag)"
ALTERNATE_SYMBOL_TABLE["\\="] = "NUO avail. symbol overlay group"
ALTERNATE_SYMBOL_TABLE["\\>"] = "NV# OVERLAYED CARs & Vehicles"
ALTERNATE_SYMBOL_TABLE["\\?"] = "NW  INFO Kiosk  (Blue box with ?)"
ALTERNATE_SYMBOL_TABLE["\\@"] = "NX  HURICANE/Trop-Storm"
ALTERNATE_SYMBOL_TABLE["\\A"] = "AA# overlayBOX DTMF & RFID & XO"
ALTERNATE_SYMBOL_TABLE["\\B"] = "AB  AVAIL (BlwngSnow ==> E ovly B"
ALTERNATE_SYMBOL_TABLE["\\C"] = "AC  Coast Guard"
ALTERNATE_SYMBOL_TABLE["\\D"] = "ADO  DEPOTS (Drizzle ==> ' ovly D)"
ALTERNATE_SYMBOL_TABLE["\\E"] = "AE  Smoke (& other vis codes)"
ALTERNATE_SYMBOL_TABLE["\\F"] = "AF  AVAIL (FrzngRain ==> `F)"
ALTERNATE_SYMBOL_TABLE["\\G"] = "AG  AVAIL (Snow Shwr ==> I ovly S)"
ALTERNATE_SYMBOL_TABLE["\\H"] = "AHO \Haze (& Overlay Hazards)"
ALTERNATE_SYMBOL_TABLE["\\I"] = "AI  Rain Shower"
ALTERNATE_SYMBOL_TABLE["\\J"] = "AJ  AVAIL (Lightening ==> I ovly L)"
ALTERNATE_SYMBOL_TABLE["\\K"] = "AK  Kenwood HT (W)"
ALTERNATE_SYMBOL_TABLE["\\L"] = "AL  Lighthouse"
ALTERNATE_SYMBOL_TABLE["\\M"] = "AMO MARS (A=Army,N=Navy,F=AF)"
ALTERNATE_SYMBOL_TABLE["\\N"] = "AN  Navigation Buoy"
ALTERNATE_SYMBOL_TABLE["\\O"] = "AO  Overlay Balloon (Rocket = \O)"
ALTERNATE_SYMBOL_TABLE["\\P"] = "AP  Parking"
ALTERNATE_SYMBOL_TABLE["\\Q"] = "AQ  QUAKE"
ALTERNATE_SYMBOL_TABLE["\\R"] = "ARO Restaurant"
ALTERNATE_SYMBOL_TABLE["\\S"] = "AS  Satellite/Pacsat"
ALTERNATE_SYMBOL_TABLE["\\T"] = "AT  Thunderstorm"
ALTERNATE_SYMBOL_TABLE["\\U"] = "AU  SUNNY"
ALTERNATE_SYMBOL_TABLE["\\V"] = "AV  VORTAC Nav Aid"
ALTERNATE_SYMBOL_TABLE["\\W"] = "AW# # NWS site (NWS options)"
ALTERNATE_SYMBOL_TABLE["\\X"] = "AX  Pharmacy Rx (Apothicary)"
ALTERNATE_SYMBOL_TABLE["\\Y"] = "AYO Radios and devices"
ALTERNATE_SYMBOL_TABLE["\\Z"] = "AZ  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\["] = "DSO W.Cloud (& humans w Ovrly)"
ALTERNATE_SYMBOL_TABLE["\\\\"] = "DTO New overlayable GPS symbol"
ALTERNATE_SYMBOL_TABLE["\\]"] = "DU  AVAIL"
ALTERNATE_SYMBOL_TABLE["\\^"] = "DV# other Aircraft ovrlys (2014)"
ALTERNATE_SYMBOL_TABLE["\\_"] = "DW# # WX site (green digi)"
ALTERNATE_SYMBOL_TABLE["\\`"] = "DX  Rain (all types w ovrly)"


u""""/$ XYZ PRIMARY SYMBOL TABLE"""
PRIMARY_SYMBOL_TABLE = dict()
PRIMARY_SYMBOL_TABLE["/0"] = "P0  # circle (obsolete)"
PRIMARY_SYMBOL_TABLE["/1"] = "P1  TBD (these were numbered)"
PRIMARY_SYMBOL_TABLE["/2"] = "P2  TBD (circles like pool)"
PRIMARY_SYMBOL_TABLE["/3"] = "P3  TBD (balls.  But with)"
PRIMARY_SYMBOL_TABLE["/4"] = "P4  TBD (overlays, we can)"
PRIMARY_SYMBOL_TABLE["/5"] = "P5  TBD (put all #'s on one)"
PRIMARY_SYMBOL_TABLE["/6"] = "P6  TBD (So 1-9 are available)"
PRIMARY_SYMBOL_TABLE["/7"] = "P7  TBD (for new uses?)"
PRIMARY_SYMBOL_TABLE["/8"] = "P8  TBD (They are often used)"
PRIMARY_SYMBOL_TABLE["/9"] = "P9  TBD (as mobiles at events)"
PRIMARY_SYMBOL_TABLE["/:"] = "MR  FIRE"
PRIMARY_SYMBOL_TABLE["/;"] = "MS  Campground (Portable ops)"
PRIMARY_SYMBOL_TABLE["/<"] = "MT  Motorcycle     (SSID-10)"
PRIMARY_SYMBOL_TABLE["/="] = "MU  RAILROAD ENGINE"
PRIMARY_SYMBOL_TABLE["/>"] = "MV  CAR            (SSID-9)"
PRIMARY_SYMBOL_TABLE["/?"] = "MW  SERVER for Files"
PRIMARY_SYMBOL_TABLE["/@"] = "MX  HC FUTURE predict (dot)"
PRIMARY_SYMBOL_TABLE["/A"] = "PA  Aid Station"
PRIMARY_SYMBOL_TABLE["/B"] = "PB  BBS or PBBS"
PRIMARY_SYMBOL_TABLE["/C"] = "PC  Canoe"
PRIMARY_SYMBOL_TABLE["/D"] = "PD"
PRIMARY_SYMBOL_TABLE["/E"] = "PE  EYEBALL (Events, etc!)"
PRIMARY_SYMBOL_TABLE["/F"] = "PF  Farm Vehicle (tractor)"
PRIMARY_SYMBOL_TABLE["/G"] = "PG  Grid Square (6 digit)"
PRIMARY_SYMBOL_TABLE["/H"] = "PH  HOTEL (blue bed symbol)"
PRIMARY_SYMBOL_TABLE["/I"] = "PI  TcpIp on air network stn"
PRIMARY_SYMBOL_TABLE["/J"] = "PJ"
PRIMARY_SYMBOL_TABLE["/K"] = "PK  School"
PRIMARY_SYMBOL_TABLE["/L"] = "PL  PC user (Jan 03)"
PRIMARY_SYMBOL_TABLE["/M"] = "PM  MacAPRS"
PRIMARY_SYMBOL_TABLE["/N"] = "PN  NTS Station"
PRIMARY_SYMBOL_TABLE["/O"] = "PO  BALLOON        (SSID-11)"
PRIMARY_SYMBOL_TABLE["/P"] = "PP  Police"
PRIMARY_SYMBOL_TABLE["/Q"] = "PQ  TBD"
PRIMARY_SYMBOL_TABLE["/R"] = "PR  REC. VEHICLE   (SSID-13)"
PRIMARY_SYMBOL_TABLE["/S"] = "PS  SHUTTLE"
PRIMARY_SYMBOL_TABLE["/T"] = "PT  SSTV"
PRIMARY_SYMBOL_TABLE["/U"] = "PU  BUS            (SSID-2)"
PRIMARY_SYMBOL_TABLE["/V"] = "PV  ATV"
PRIMARY_SYMBOL_TABLE["/W"] = "PW  National WX Service Site"
PRIMARY_SYMBOL_TABLE["/X"] = "PX  HELO           (SSID-6)"
PRIMARY_SYMBOL_TABLE["/Y"] = "PY  YACHT (sail)   (SSID-5)"
PRIMARY_SYMBOL_TABLE["/Z"] = "PZ  WinAPRS"
PRIMARY_SYMBOL_TABLE["/["] = "HS  Human/Person   (SSID-7)"
PRIMARY_SYMBOL_TABLE["/\""] = "HT  TRIANGLE(DF station)"
PRIMARY_SYMBOL_TABLE["/]"] = "HU  MAIL/PostOffice(was PBBS)"
PRIMARY_SYMBOL_TABLE["/^"] = "HV  LARGE AIRCRAFT"
PRIMARY_SYMBOL_TABLE["/_"] = "HW  WEATHER Station (blue)"
PRIMARY_SYMBOL_TABLE["/`"] = "HX  Dish Antenna"

u"""\$  XYZ OTHER SYMBOL TABLE (\)"""
OTHER_SYMBOL_TABLE = dict()
OTHER_SYMBOL_TABLE["\!"] = "OBO EMERGENCY (and overlays)"
OTHER_SYMBOL_TABLE["\\\""] = "OC  reserved"
OTHER_SYMBOL_TABLE["\\#"] = "OD# OVERLAY DIGI (green star)"
OTHER_SYMBOL_TABLE["\\$"] = "OEO Bank or ATM  (green box)"
OTHER_SYMBOL_TABLE["\\%"] = "OFO Power Plant with overlay"
OTHER_SYMBOL_TABLE["\\&"] = "OG# I=Igte R=RX T=1hopTX 2=2hopTX"
OTHER_SYMBOL_TABLE["\\'"] = "OHO Crash (& now Incident sites)"
OTHER_SYMBOL_TABLE["\\("] = "OIO CLOUDY (other clouds w ovrly)"
OTHER_SYMBOL_TABLE["\\)"] = "OJO Firenet MEO, MODIS Earth Obs."
OTHER_SYMBOL_TABLE["\\*"] = "OK  AVAIL (SNOW moved to ` ovly S)"
OTHER_SYMBOL_TABLE["\\+"] = "OL  Church"
OTHER_SYMBOL_TABLE["\\,"] = "OM  Girl Scouts"
OTHER_SYMBOL_TABLE["\\-"] = "ONO House (H=HF) (O = Op Present)"
OTHER_SYMBOL_TABLE["\\."] = "OO  Ambiguous (Big Question mark)"
OTHER_SYMBOL_TABLE["\\/"] = "OP  Waypoint Destination"

u"""\$  XYZ SECONDARY SYMBOL TABLE (\)"""
SECONDARY_SYMBOL_TABLE = dict()
SECONDARY_SYMBOL_TABLE ["\\a"] = "SA#O ARRL,ARES,WinLINK,Dstar, etc"
SECONDARY_SYMBOL_TABLE ["\\b"] = "SB  AVAIL(Blwng Dst/Snd => E ovly)"
SECONDARY_SYMBOL_TABLE ["\\c"] = "SC#O CD triangle RACES/SATERN/etc"
SECONDARY_SYMBOL_TABLE ["\\d"] = "SD  DX spot by callsign"
SECONDARY_SYMBOL_TABLE ["\\e"] = "SE  Sleet (& future ovrly codes)"
SECONDARY_SYMBOL_TABLE ["\\f"] = "SF  Funnel Cloud"
SECONDARY_SYMBOL_TABLE ["\\g"] = "SG  Gale Flags"
SECONDARY_SYMBOL_TABLE ["\\h"] = "SHO Store. or HAMFST Hh=HAM store"
SECONDARY_SYMBOL_TABLE ["\\i"] = "SI# BOX or points of Interest"
SECONDARY_SYMBOL_TABLE ["\\j"] = "SJ  WorkZone (Steam Shovel)"
SECONDARY_SYMBOL_TABLE ["\\k"] = "SKO Special Vehicle SUV,ATV,4x4"
SECONDARY_SYMBOL_TABLE ["\\l"] = "SL  Areas      (box,circles,etc)"
SECONDARY_SYMBOL_TABLE ["\\m"] = "SM  Value Sign (3 digit display)"
SECONDARY_SYMBOL_TABLE ["\\n"] = "SN# OVERLAY TRIANGLE"
SECONDARY_SYMBOL_TABLE ["\\o"] = "SO  small circle"
SECONDARY_SYMBOL_TABLE ["\\p"] = "SP  AVAIL (PrtlyCldy => ( ovly P"
SECONDARY_SYMBOL_TABLE ["\\q"] = "SQ  AVAIL"
SECONDARY_SYMBOL_TABLE ["\\r"] = "SR  Restrooms"
SECONDARY_SYMBOL_TABLE ["\\s"] = "SS# OVERLAY SHIP/boats"
SECONDARY_SYMBOL_TABLE ["\\t"] = "ST  Tornado"
SECONDARY_SYMBOL_TABLE ["\\u"] = "SU# OVERLAYED TRUCK"
SECONDARY_SYMBOL_TABLE ["\\v"] = "SV# OVERLAYED Van"
SECONDARY_SYMBOL_TABLE ["\\w"] = "SWO Flooding (Avalanches/Slides)"
SECONDARY_SYMBOL_TABLE ["\\x"] = "SX  Wreck or Obstruction ->X<-"
SECONDARY_SYMBOL_TABLE ["\\y"] = "SY  Skywarn"
SECONDARY_SYMBOL_TABLE ["\\z"] = "SZ# OVERLAYED Shelter"
SECONDARY_SYMBOL_TABLE ["\\{"] = "Q1  AVAIL? (Fog ==> E ovly F)"
SECONDARY_SYMBOL_TABLE ["\\|"] = "Q2  TNC Stream Switch"
SECONDARY_SYMBOL_TABLE ["\\}"] = "Q3  AVAIL? (maybe)"
SECONDARY_SYMBOL_TABLE ["\\~"] = "Q4  TNC Stream Switch"


u"""/$ XYZ LOWER CASE SYMBOL TABLE"""
LOWER_CASE_SYMBOL_TABLE = dict()
LOWER_CASE_SYMBOL_TABLE["/a"] = "LA  AMBULANCE     (SSID-1)"
LOWER_CASE_SYMBOL_TABLE["/b"] = "LB  BIKE          (SSID-4)"
LOWER_CASE_SYMBOL_TABLE["/c"] = "LC  Incident Command Post"
LOWER_CASE_SYMBOL_TABLE["/d"] = "LD  Fire dept"
LOWER_CASE_SYMBOL_TABLE["/e"] = "LE  HORSE (equestrian)"
LOWER_CASE_SYMBOL_TABLE["/f"] = "LF  FIRE TRUCK    (SSID-3)"
LOWER_CASE_SYMBOL_TABLE["/g"] = "LG  Glider"
LOWER_CASE_SYMBOL_TABLE["/h"] = "LH  HOSPITAL"
LOWER_CASE_SYMBOL_TABLE["/i"] = "LI  IOTA (islands on the air)"
LOWER_CASE_SYMBOL_TABLE["/j"] = "LJ  JEEP          (SSID-12)"
LOWER_CASE_SYMBOL_TABLE["/k"] = "LK  TRUCK         (SSID-14)"
LOWER_CASE_SYMBOL_TABLE["/l"] = "LL  Laptop (Jan 03)  (Feb 07)"
LOWER_CASE_SYMBOL_TABLE["/m"] = "LM  Mic-E Repeater"
LOWER_CASE_SYMBOL_TABLE["/n"] = "LN  Node (black bulls-eye)"
LOWER_CASE_SYMBOL_TABLE["/o"] = "LO  EOC"
LOWER_CASE_SYMBOL_TABLE["/p"] = "LP  ROVER (puppy, or dog)"
LOWER_CASE_SYMBOL_TABLE["/q"] = "LQ  GRID SQ shown above 128 m"
LOWER_CASE_SYMBOL_TABLE["/r"] = "LR  Repeater         (Feb 07)"
LOWER_CASE_SYMBOL_TABLE["/s"] = "S  SHIP (pwr boat)  (SSID-8)"
LOWER_CASE_SYMBOL_TABLE["/t"] = "LT  TRUCK STOP"
LOWER_CASE_SYMBOL_TABLE["/u"] = "LU  TRUCK (18 wheeler)"
LOWER_CASE_SYMBOL_TABLE["/v"] = "LV  VAN           (SSID-15)"
LOWER_CASE_SYMBOL_TABLE["/w"] = "LW  WATER station"
LOWER_CASE_SYMBOL_TABLE["/x"] = "LX  xAPRS (Unix)"
LOWER_CASE_SYMBOL_TABLE["/y"] = "LY  YAGI @ QTH"
LOWER_CASE_SYMBOL_TABLE["/z"] = "LZ  TBD"
LOWER_CASE_SYMBOL_TABLE["/{"] = "J1"
LOWER_CASE_SYMBOL_TABLE["/|"] = "J2  TNC Stream Switch"
LOWER_CASE_SYMBOL_TABLE["/}"] = "J3"
LOWER_CASE_SYMBOL_TABLE["/~"] = "J4  TNC Stream Switch"


u"""
/$ XYZ BASIC SYMBOL TABLE
/$ XYZ PRIMARY SYMBOL TABLE

\$  XYZ OTHER SYMBOL TABLE (\)
\$  XYZ ALTERNATE SYMBOL TABLE (\)
\$  XYZ SECONDARY SYMBOL TABLE (\)

/$ XYZ LOWER CASE SYMBOL TABLE
"""

SYMBOL_TABLES = dict()
SYMBOL_TABLES.update(BASIC_SYMBOL_TABLE)
SYMBOL_TABLES.update(PRIMARY_SYMBOL_TABLE)
SYMBOL_TABLES.update(LOWER_CASE_SYMBOL_TABLE)
SYMBOL_TABLES.update(OTHER_SYMBOL_TABLE)
SYMBOL_TABLES.update(ALTERNATE_SYMBOL_TABLE)
SYMBOL_TABLES.update(SECONDARY_SYMBOL_TABLE)


symbols = dict()
symbols[u"G"] = u"Glider"
symbols[u"H"] = u"Hospital"
symbols[u"I"] = u"IOTA (Island on the Air)"
symbols[u"J"] = u"Jeep"
symbols[u"K"] = u"Truck"
symbols[u"M"] = u"Repeater"
symbols[u"N"] = u"Node"
symbols[u"O"] = u"Emergency Operations Center"
symbols[u"P"] = u"Rover"
symbols[u"Q"] = u"Grid Square"
symbols[u"R"] = u"Antenna"
symbols[u"S"] = u"Ship"
symbols[u"T"] = u"Truck"
symbols[u"U"] = u"!8 Wheeler"
symbols[u"V"] = u"Van"
symbols[u"W"] = u"Water Station"
symbols[u"X"] = u"X-APRS"

message_types = dict()
message_types[u"U"] = u"Ultimeter 2000"
message_types[u"!"] = u"Raw Weather Report"
message_types[u"_"] = u"Positionless Weather Report"
message_types[u"="] = u"Complete Weather Report"
message_types[u"@"] = u"Complete Weather Format"
message_types[u"/"] = u"Complete Weather - Compressed"
message_types[u";"] = u"Object Report Format"
message_types[u">"] = u"Snafu"
message_types[u":"] = u"Object Report Format"
message_types[u"`"] = u"MicE Format"

def findSymbolName(symbol_table, symbol):
    vl = None
    try:
        vl = SYMBOL_TABLES[symbol_table + symbol]
        logger.debug(u"%s%s : %s" % (symbol_table, symbol, vl))

    except Exception, msg:
        logger.debug(u"%s" % msg)
        return None

    return vl

if __name__ == u"__main__":
    client = MongoClient(u'mongodb://localhost:27017/')
    db = client[u"local"]
    collection = db[u'Weather']

    for post in collection.find({"symbol": {"$exists": "True"}}):
        symbol_table = post['symbol_table']
        symbol = post['symbol']
        vl = findSymbolName(symbol_table, symbol)

        if vl is not None:
            logger.info("%s%s : %s" % (symbol_table, symbol_table, vl))









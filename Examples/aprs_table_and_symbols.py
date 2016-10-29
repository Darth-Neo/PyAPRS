u"""
The character after the latitude "N/S" in an APRS position report is a TABLE character
The character following the longitude "E/W" is the APRS symbol character.

The TABLE character selects one of two symbol
tables or may be used as an alphanumeric overlay over some symbols:
"""

APRS_Table = dict()
APRS_Table["&"] = "RESERVED for possible AUXILLIARY tables (Aug 09)"
APRS_Table["/"] = "Primary   symbol Table  (Mostly stations)"
APRS_Table["\\"] = "Alternate symbol table  (Mostly Objects)"
APRS_Table["0-9"] = "Alternate OVERLAY symbols with 0-9 overlayed"
APRS_Table["A-Z"] = "Alternate OVERLAY symbols with A-Z overlayed"

"""
/$ XYZ BASIC SYMBOL TABLE        \$  XYZ OTHER SYMBOL TABLE (\)
-- --- ------------------------  --  --- ----------------------
/! BB  Police, Sheriff           \!  OBO EMERGENCY (and overlays)
/" BC  reserved  (was rain)      \"  OC  reserved
/# BD  DIGI (white center)       \#  OD# OVERLAY DIGI (green star)
/$ BE  PHONE                     \$  OEO Bank or ATM  (green box)
/% BF  DX CLUSTER                \%  OFO Power Plant with overlay
/& BG  HF GATEway                \&  OG# I=Igte R=RX T=1hopTX 2=2hopTX
/' BH  Small AIRCRAFT (SSID-11)  \'  OHO Crash (& now Incident sites)
/( BI  Mobile Satellite Station  \(  OIO CLOUDY (other clouds w ovrly)
/) BJ  Wheelchair (handicapped)  \)  OJO Firenet MEO, MODIS Earth Obs.
/* BK  SnowMobile                \*  OK  AVAIL (SNOW moved to ` ovly S)
/+ BL  Red Cross                 \+  OL  Church
/, BM  Boy Scouts                \,  OM  Girl Scouts
/- BN  House QTH (VHF)           \-  ONO House (H=HF) (O = Op Present)
/. BO  X                         \.  OO  Ambiguous (Big Question mark)
// BP  Red Dot                   \/  OP  Waypoint Destination
                                          See APRSdos MOBILE.txt

/$ XYZ PRIMARY SYMBOL TABLE      \$  XYZ ALTERNATE SYMBOL TABLE (\)
-- --- ------------------------  --  --- --------------------------
/0 P0  # circle (obsolete)       \0  A0# CIRCLE (IRLP/Echolink/WIRES)
/1 P1  TBD (these were numbered) \1  A1  AVAIL
/2 P2  TBD (circles like pool)   \2  A2  AVAIL
/3 P3  TBD (balls.  But with)    \3  A3  AVAIL
/4 P4  TBD (overlays, we can)    \4  A4  AVAIL
/5 P5  TBD (put all #'s on one)  \5  A5  AVAIL
/6 P6  TBD (So 1-9 are available)\6  A6  AVAIL
/7 P7  TBD (for new uses?)       \7  A7  AVAIL
/8 P8  TBD (They are often used) \8  A8O 802.11 or other network node
/9 P9  TBD (as mobiles at events)\9  A9  Gas Station (blue pump)
/: MR  FIRE                      \:  NR  AVAIL (Hail ==> ` ovly H)
/; MS  Campground (Portable ops) \;  NSO Park/Picnic + overlay events
/< MT  Motorcycle     (SSID-10)  \<  NTO ADVISORY (one WX flag)
/= MU  RAILROAD ENGINE           \=  NUO avail. symbol overlay group
/> MV  CAR            (SSID-9)   \>  NV# OVERLAYED CARs & Vehicles
/? MW  SERVER for Files          \?  NW  INFO Kiosk  (Blue box with ?)
/@ MX  HC FUTURE predict (dot)   \@  NX  HURICANE/Trop-Storm
/A PA  Aid Station               \A  AA# overlayBOX DTMF & RFID & XO
/B PB  BBS or PBBS               \B  AB  AVAIL (BlwngSnow ==> E ovly B
/C PC  Canoe                     \C  AC  Coast Guard
/D PD                            \D ADO  DEPOTS (Drizzle ==> ' ovly D)
/E PE  EYEBALL (Events, etc!)    \E  AE  Smoke (& other vis codes)
/F PF  Farm Vehicle (tractor)    \F  AF  AVAIL (FrzngRain ==> `F)
/G PG  Grid Square (6 digit)     \G  AG  AVAIL (Snow Shwr ==> I ovly S)
/H PH  HOTEL (blue bed symbol)   \H  AHO \Haze (& Overlay Hazards)
/I PI  TcpIp on air network stn  \I  AI  Rain Shower
/J PJ                            \J  AJ  AVAIL (Lightening ==> I ovly L)
/K PK  School                    \K  AK  Kenwood HT (W)
/L PL  PC user (Jan 03)          \L  AL  Lighthouse
/M PM  MacAPRS                   \M  AMO MARS (A=Army,N=Navy,F=AF)
/N PN  NTS Station               \N  AN  Navigation Buoy
/O PO  BALLOON        (SSID-11)  \O  AO  Overlay Balloon (Rocket = \O)
/P PP  Police                    \P  AP  Parking
/Q PQ  TBD                       \Q  AQ  QUAKE
/R PR  REC. VEHICLE   (SSID-13)  \R  ARO Restaurant
/S PS  SHUTTLE                   \S  AS  Satellite/Pacsat
/T PT  SSTV                      \T  AT  Thunderstorm
/U PU  BUS            (SSID-2)   \U  AU  SUNNY
/V PV  ATV                       \V  AV  VORTAC Nav Aid
/W PW  National WX Service Site  \W  AW# # NWS site (NWS options)
/X PX  HELO           (SSID-6)   \X  AX  Pharmacy Rx (Apothicary)
/Y PY  YACHT (sail)   (SSID-5)   \Y  AYO Radios and devices
/Z PZ  WinAPRS                   \Z  AZ  AVAIL
/[ HS  Human/Person   (SSID-7)   \[  DSO W.Cloud (& humans w Ovrly)
/\ HT  TRIANGLE(DF station)      \\  DTO New overlayable GPS symbol
/] HU  MAIL/PostOffice(was PBBS) \]  DU  AVAIL
/^ HV  LARGE AIRCRAFT            \^  DV# other Aircraft ovrlys (2014)
/_ HW  WEATHER Station (blue)    \_  DW# # WX site (green digi)
/` HX  Dish Antenna              \`  DX  Rain (all types w ovrly)

/$ XYZ LOWER CASE SYMBOL TABLE   \$  XYZ SECONDARY SYMBOL TABLE (\)
-- --- ------------------------  --  --- --------------------------
/a LA  AMBULANCE     (SSID-1)    \a  SA#O ARRL,ARES,WinLINK,Dstar, etc
/b LB  BIKE          (SSID-4)    \b  SB  AVAIL(Blwng Dst/Snd => E ovly)
/c LC  Incident Command Post     \c  SC#O CD triangle RACES/SATERN/etc
/d LD  Fire dept                 \d  SD  DX spot by callsign
/e LE  HORSE (equestrian)        \e  SE  Sleet (& future ovrly codes)
/f LF  FIRE TRUCK    (SSID-3)    \f  SF  Funnel Cloud
/g LG  Glider                    \g  SG  Gale Flags
/h LH  HOSPITAL                  \h  SHO Store. or HAMFST Hh=HAM store
/i LI  IOTA (islands on the air) \i  SI# BOX or points of Interest
/j LJ  JEEP          (SSID-12)   \j  SJ  WorkZone (Steam Shovel)
/k LK  TRUCK         (SSID-14)   \k  SKO Special Vehicle SUV,ATV,4x4
/l LL  Laptop (Jan 03)  (Feb 07) \l  SL  Areas      (box,circles,etc)
/m LM  Mic-E Repeater            \m  SM  Value Sign (3 digit display)
/n LN  Node (black bulls-eye)    \n  SN# OVERLAY TRIANGLE
/o LO  EOC                       \o  SO  small circle
/p LP  ROVER (puppy, or dog)     \p  SP  AVAIL (PrtlyCldy => ( ovly P
/q LQ  GRID SQ shown above 128 m \q  SQ  AVAIL
/r LR  Repeater         (Feb 07) \r  SR  Restrooms
/s LS  SHIP (pwr boat)  (SSID-8) \s  SS# OVERLAY SHIP/boats
/t LT  TRUCK STOP                \t  ST  Tornado
/u LU  TRUCK (18 wheeler)        \u  SU# OVERLAYED TRUCK
/v LV  VAN           (SSID-15)   \v  SV# OVERLAYED Van
/w LW  WATER station             \w  SWO Flooding (Avalanches/Slides)
/x LX  xAPRS (Unix)              \x  SX  Wreck or Obstruction ->X<-
/y LY  YAGI @ QTH                \y  SY  Skywarn
/z LZ  TBD                       \z  SZ# OVERLAYED Shelter
/{ J1                            \{  Q1  AVAIL? (Fog ==> E ovly F)
/| J2  TNC Stream Switch         \|  Q2  TNC Stream Switch
/} J3                            \}  Q3  AVAIL? (maybe)
/~ J4  TNC Stream Switch         \~  Q4  TNC Stream Switch

HEADING SYMBOLS:  Although all symbols are supposed to have a heading
line showing the direction of movement with a length proportional to
the log of speed, some symbols were desiged as top-down views so that
they could be displayed actually always POINTING in the direction of
movement.  Now All symbols should be oriented (if practical).  These
original special symbols were:

\> OVERLAYED CAR
\s Overlayed Ship
\^ Overlayed Aircraft
/^ Aircraft
/g Glider
\n Overlayed Triangle

"""
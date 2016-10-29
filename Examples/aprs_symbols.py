u"""
Modified these Alternate Symbol codes for expanded Overlays.
Prior to this, each Alternate Table basic symbol had a unique defini-
tion, but this was every restrictive.

So the following alternate base symbols were redefined so that the
basic symbol could take on dozens of unique overlay definitions:

\= - Had been undefined
\0 - Several overlays for the numbered Circle
\A - (BOX symbol) APRStt(DTMF), RFID users, XO (OLPC)
\' - Was Crash Site.  Now expanded to be INCIDENT sites
\% - is an overlayed Powerplant.  See definitions below
\H - \H is HAZE but other H overlays are HAZARDs. WH is "H.Waste"
\Y - Overlays for Radios and other APRS devices
\k - Overlay Special vehicles.  A = ATV for example
\u - Overlay Trucks.  "Tu" is a tanker. "Gu" is a gas truck, etc
\< - Advisories may now have overlays
\8 - Nodes with overlays. "G8" would be 802.11G
\[ - \[ is wall cloud, but overlays are humans. S[ is a skier.
\h - Buildings. \h is a Ham store, "Hh" is Home Depot, etc.

ADVISORIES: #<  (new expansion possibilities)
/< = motorcycle
\< = Advisory (single gale flag)

AIRCRAFT
/^ = LARGE Aircraft
\^ = top-view originally intended to point in direction of flight
A^ = Autonomous (2015)
D^ = Drone   (new may 2014)
E^ = Electric aircraft (2015)
H^ = Hovercraft    (new may 2014)
J^ = JET     (new may 2014)
M^ = Missle   (new may 2014)
P^ = Prop (new Aug 2014)
R^ = Remotely Piloted (new 2015)
S^ = Solar Powered  (new 2015)
V^ = Vertical takeoff   (new may 2014)
X^ = Experimental (new Aug 2014)

ATM Machine or CURRENCY:  #$
/$ = original primary Phone
\$ = Bank or ATM (generic)
U$ = US dollars
L$ = Brittish Pound
Y$ = Japanese Yen

ARRL or DIAMOND: #a
/a = Ambulance
Aa = ARES
Da = DSTAR (had been ARES Dutch)
Ga = RSGB Radio Society of Great Brittan
Ra = RACES
Sa = SATERN Salvation Army
Wa = WinLink
Ya = C4FM Yaesu repeaters

BALLOONS and lighter than air #O (All new Oct 2015)
/O = Original Balloon (think Ham balloon)
\O = ROCKET (amateur)(2007)
BO = Blimp           (2015)
MO = Manned Balloon  (2015)
TO = Teathered       (2015)
CO = Constant Pressure - Long duration (2015)
RO = Rocket bearing Balloon (Rockoon)  (2015)

BOX SYMBOL: #A (and other system inputted symbols)
/A = Aid station
\A = numbered box
9A = Mobile DTMF user
7A = HT DTMF user
HA = House DTMF user
EA = Echolink DTMF report
IA = IRLP DTMF report
RA = RFID report
AA = AllStar DTMF report
DA = D-Star report
XA = OLPC Laptop XO
etc

BUILDINGS: #h
/h = Hospital
\h = Ham Store       ** <= now used for HAMFESTS
Fh = HamFest (new Aug 2014)
Hh = Home Dept etc..

CARS: #> (Vehicles)
/> = normal car (side view)
\> = Top view and symbol POINTS in direction of travel
#> = Reserve overlays 1-9 for numbered cars (new Aug 2014)
E> = Electric
H> = Hybrid
S> = Solar powered
V> = GM Volt

CIVIL DEFENSE or TRIANGLE: #c
/c = Incident Command Post
\c = Civil Defense
Dc = Decontamination (new Aug 2014)
Rc = RACES
Sc = SATERN mobile canteen

DEPOT
/D = was originally undefined
\D = was drizzle (moved to ' ovlyD)
AD = Airport  (new Aug 2014)
FD = Ferry Landing (new Aug 2014)
HD = Heloport (new Aug 2014)
RD = Rail Depot  (new Aug 2014)
BD = Bus Depot (new Aug 2014)
LD = LIght Rail or Subway (new Aug 2014)
SD = Seaport Depot (new Aug 2014)

EMERGENCY: #!
/! = Police/Sheriff, etc
\! = Emergency!
E! = ELT or EPIRB  (new Aug 2014)
V! = Volcanic Eruption or Lava  (new Aug 2014)

EYEBALL (EVENT) and VISIBILITY  #E
/E = Eyeball for special live events
\E = (existing smoke) the symbol with no overlay
HE = (H overlay) Haze
SE = (S overlay) Smoke
BE = (B overlay) Blowing Snow         was \B
DE = (D overlay) blowing Dust or sand was \b
FE = (F overlay) Fog                  was \{

GATEWAYS: #&
/& = HF Gateway  <= the original primary table definition
I& = Igate Generic (please use more specific overlay)
R& = Receive only IGate (do not send msgs back to RF)
P& = PSKmail node
T& = TX igate with path set to 1 hop only)
W& = WIRES-X as opposed to W0 for WiresII
2& = TX igate with path set to 2 hops (not generally good idea)

GPS devices: #\
/\ = Triangle DF primary symbol
\\ = was undefined alternate symbol
A\ = Avmap G5      * <= Recommend special symbol

HAZARDS: #H
/H = hotel
\H = Haze
RH = Radiation detector (new mar 2011)
WH = Hazardous Waste
XH = Skull&Crossbones

HUMAN SYMBOL: #[
/[ = Human
\[ = Wall Cloud (the original definition)
B[ = Baby on board (stroller, pram etc)
S[ = Skier      * <= Recommend Special Symbol
R[ = Runner
H[ = Hiker

HOUSE: #-
/- = House
\- = (was HF)
5- = 50 Hz mains power
6- = 60 Hz mains power
B- = Backup Battery Power
C- = Club, as in Ham club
E- = Emergency power
G- = Geothermal
H- = Hydro powered
O- = Operator Present
S- = Solar Powered
W- = Wind powered

INCIDENT SITES: #'
/' = Small Aircraft (original primary symbol)
\' = Airplane Crash Site  <= the original alternate deifinition
A' = Automobile crash site
H' = Hazardous incident
M' = Multi-Vehicle crash site
P' = Pileup
T' = Truck wreck

NUMBERED CIRCLES: #0
A0 = Allstar Node (A0)
E0 = Echolink Node (E0)
I0 = IRLP repeater (I0)
S0 = Staging Area  (S0)
V0 = Echolink and IRLP (VOIP)
W0 = WIRES (Yaesu VOIP)

NETWORK NODES: #8
88 = 802.11 network node (88)
G8 = 802.11G  (G8)

PORTABLE SYMBOL: #;
/; = Portable operation (tent)
\; = Park or Picnic
F; = Field Day
I; = Islands on the air
S; = Summits on the air
W; = WOTA

POWER or ENERGY: #%
/% = DX cluster  <= the original primary table definition
C% = Coal
E% = Emergency  (new Aug 2014)
G% = Geothermal
H% = Hydroelectric
N% = Nuclear
P% = Portable (new Aug 2014)
S% = Solar
T% = Turbine
W% = Wind

RESTAURANTS: #R
\R = Restaurant (generic)
7R = 7/11
KR = KFC
MR = McDonalds
TR = Taco Bell

RADIOS and APRS DEVICES: #Y
/Y = Yacht  <= the original primary symbol
\Y =        <= the original alternate was undefined
AY = Alinco
BY = Byonics
IY = Icom
KY = Kenwood       * <= Recommend special symbol
YY = Yaesu/Standard* <= Recommend special symbol


SPECIAL VEHICLES: #k
/k = truck
\k = SUV
4k = 4x4
Ak = ATV (all terrain vehicle)

SHELTERS: #z
/z = was available
\z = overlayed shelter
Cz = Clinic (new Aug 2014)
Gz = Government building  (new Aug 2014)
Mz = Morgue (new Aug 2014)
Tz = Triage (new Aug 2014)

SHIPS: #s
/s = Power boat (ship) side view
\s = Overlay Boat (Top view)
6s = Shipwreck ("deep6") (new Aug 2014)
Bs = Pleasure Boat
Cs = Cargo
Ds = Diving
Es = Emergency or Medical transport
Fs = Fishing
Hs = High-speed Craft
Js = Jet Ski
Ls = Law enforcement
Ms = Miltary
Os = Oil Rig
Ps = Pilot Boat (new Aug 2014)
Qs = Torpedo
Ss = Search and Rescue
Ts = Tug (new Aug 2014)
Us = Underwater ops or submarine
Ws = Wing-in-Ground effect (or Hovercraft)
Xs = Passenger (paX)(ferry)
Ys = Sailing (large ship)

TRUCKS: #u
/u = Truck (18 wheeler)
\u = truck with overlay
Bu = Buldozer/construction/Backhoe  (new Aug 2014)
Gu = Gas
Pu = Plow or SnowPlow (new Aug 2014)
Tu = Tanker
Cu = Chlorine Tanker
Hu = Hazardous

First, consolidate all of the visibility symbols into the old
SMOKE symbol and change its meaning to "VISIBILITY", and then
differentiate them with the overlay characters.

"\E"  (existing smoke) the symbol with no overlay
"HE"  (an H overlay) will mean Haze
"SE"  (an S overlay) will mean Smoke
"BE"  (a  B overlay) will mean Blowing Snow         was \B
"DE"  (a  D overlay) will mean blowing Dust or sand was \b
"FE"  (an F overlay) will mean Fog                  was \{

Another category is to expand the RAIN symbol to make it kinda
like lots of angled dots coming from the sky, but with an open
center so that we can use overlays for a number of common
PRECIPITATIONS.  The consolidations would be:

"\`" (existing Rain) would be the symbol with no overlay
"R`" (an R overlay) would mean Rain
"F`" (an F overlay) would mean Freezing Rain  was \F
"H`" (an H overlay) would mean Hail           was\:
"D`" (an D overlay) would mean Drizzle        was \D
"E`" (an E overlay) would mean slEEt          was \e
"S`" (an S overlay) would mean Snow           was \*
Etc. and other particulates coming from the sky

Next, I propose expanding the existing RAIN SHOWER "\I" symbol
to look like some kind of cloud symbol with specks in it that
can be overlayed. (It needs to look different from the next
CLOUD symbol). It can then consolidate these symbols:

"RI" (an R overlay) would mean Rain Shower
"SI" (an S overlay) would mean Snow shower    was \G
"LI" (an L overlay) would mean Lightening     was \J
Etc. and other things related to clouds

Next, I propose expanding the existing CLOUD symbol to allow
definition of any number of different types of cloud.  This
needs to also look like a cloud but a different shape and allow
for overlays  (Maybe this cloud is clear):

"\(" is the existing cloud symbol (would have no overlay)
"P(" with P overlay would mean partly cloudy        was \p
"W(" with W overlay would be a wall cloud           was \[
"F(" would be Funnel cloud, but the original "\f" will also be
retained for now

All of these initiative will free up a lot of overlayable symbol
GROUPS each of which can suport up to 36 different overlays in
each group for the future:

#H for 36 new Hazards (was only Hail)
#[ for 36 new human symbols (was only Wall Cloud)
#\ for 36 new GPS or navigation equipment
#B TBD. \B was only blowing snow         now is BE
#b TBD. \b was only blowing dust/sand    now is DE
#{ TBD. \{ was only fog                  now is FE
#* TBD. \* was snow only                 now is S`
#: TBD. \: was hail only                 now is H`
#D TBD. \D was drizzle only              now is D`
#F TBD. \F was freezing rain only        now is F`
#e TBD. \e was sleet only                now is E`
#G TBD. \G was only Snow shower          now is SI
#J TBD. \J was only Lightening           now is LI
#p TBD. \p was only partly cloudy        now is P(

Of course future code can fully draw each of these overlays as
distinct special symbols in any way they want.

I especially want to hear from Dale Hugley who
is a resource for weather, and Stephen Smith who will have to
draw them for Uiview. And others with a stake in this...

Bob Bruninga, WB4APR
"""
import aprslib

if __name__ == u"__main__":

    a = """17:31:31$ fm W4KBW-9 to R8SU7P-0 via W4MCO-10,WC4PEM-14,WIDE2-0 UIv PID=F0
          `m0xmJ_k/`"47}Just truckin'_%"""

    message0 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    `m0xmJ_k/`\"47}Just truckin'_%"
    message1 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    'n/Ql .#/]146.520MHz Citrus Digi  ="
    message2 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    /021746z2757.15N/08147.20W_111/012g020t090r000p000P000h54b10173"
    message3 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    =2830.06N/08116.63W-PHG2060/WinAPRS 2.4.7 -FLORAORLANDO -247-<630>"
    message4 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    !2831.06N/08142.91W_ Wx @ Clermont"
    message5 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    @022149z2815.27N/08139.28W_094/003g009t088r000p000P000h60b10170U2k"
    message6 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    =2835.63NS08118.08W#PHG8250/DIGI_NED: OCCA Digi,www.w4mco.org,N2KIQ@arrl.net"
    message7 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    !2811.79NS08147.14W_PHG73676/W3,FLn POLK CITY, FLORIDA"
    message8 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    @022244z2815.27N/08139.28W_094/001g006t088r000p000P000h58b10172U2k"
    message9 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:    2643.77NP08054.82W#PHG6530/11,22,21,33 Clewiston, Fl. On the Web pbpg.org"

    messageNotSupported0 = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:_08031759c166s000g000t082r009p000P018h00b10156tU2k"

    message = "M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:/021852z2757.15N/08147.20W_143/011g016t087r000p000P000h62b10180"




    result = aprslib.parse(message)

    "FROM:  M0XER-4"
    "       > "
    "TO:    APRS64,"
    "PATH:  TF3RPF,WIDE2*,qAR, VIA:TF3SUT-2"
    ":!/.(M4I^C,O `DXa/A=040849|#B>@\"v90!+|"

    """
    comment[Xa]
    via[TF3SUT-2]
    from[M0XER-4]
    to[APRS64]
    messagecapable[False]
    symbol[O]
    format[compressed]
    telemetry[{'vals': [2670, 176, 2199, 10, 0], 'bits': '00000000', 'seq': 215}]
    longitude[-19.0706541428]
    gpsfixstatus[1]
    raw[M0XER-4>APRS64,TF3RPF,WIDE2*,qAR,TF3SUT-2:!/.(M4I^C,O `DXa/A=040849|#B>@"v90!+|]
    symbol_table[/]
    latitude[64.1198736763]
    path[[u'TF3RPF', u'WIDE2*', u'qAR', u'TF3SUT-2']]
    altitude[12450.7752]
    """

    for n, field in enumerate(result):
        if field == "raw":
            continue
        print(u"%s[%s]" % (field, result[field]))

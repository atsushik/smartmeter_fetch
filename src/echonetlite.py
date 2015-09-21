import serial
import io
import sys
import time
from binascii import unhexlify
import array
import signal
from optparse import OptionParser

def func(num, frame):
    ser.setTimeout(0.5)
    ser.write("\n\r\n\rSKTERM\n\r")      # write a string
    sio.flush()

parser = OptionParser()
parser.add_option("--pwd",  dest="passwd", help="password")
parser.add_option("--rbid", dest="rbid",   help="rbid")
(options, args) = parser.parse_args()

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=5)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

signal.signal(signal.SIGINT, func)

try:

    #print ser.name          # check which port was really used
    #print ser

    ser.setTimeout(0.5)
    sio.write(unicode("WOPT 1\n\r"))
    sio.flush()
    lines = sio.readlines()
    #print lines
    
    lines = sio.readlines()
    sio.write(unicode("SKVER\n\r"))
    sio.flush()
    lines = sio.readlines()
    #print lines
    version = None
    if lines[1].startswith("EVER "):
        version = lines[1].split(" ")[1]
    #print u"VERSION:%s" % (version)

    sio.write(unicode("SKSETPWD C " + options.passwd + "\n\r"))
    sio.flush()
    lines = sio.readlines()
    #print lines
    
    sio.write(unicode("SKSETRBID " + options.rbid + "\n\r"))
    sio.flush()
    lines = sio.readlines()
    #print lines
    
    ser.setTimeout(0.1)
    sio.write(unicode("SKSCAN 2 FFFFFFFF 6\n\r"))
    sio.flush()
    channel  = None
    panID    = None
    addr     = None
    myv6addr = None
    while (True):
        line = sio.readline().rstrip()
        if line == "":
            continue
        if line.startswith("EVENT 22 "):
            print "SCAN FAILED"
            ser.setTimeout(2)
            ser.write("\n\r\n\rSKTERM\n\r")      # write a string
            sio.flush()
            lines = sio.readlines()
            #print lines
            ser.close()             # close port
            sys.exit()
        if line.startswith("  Channel:"):
            channel=line.split(":")[1]
            #print "CHANNEL=\"" , channel , "\""
        if line.startswith("  Pan ID:"):
            panID=line.split(":")[1]
            #print "PAN ID =\"" , panID , "\""
        if line.startswith("  Addr:"):
            addr=line.split(":")[1]
            #print "ADDR   =\"" , addr , "\""
        if not channel == None and not panID == None and not addr == None:
            break
    sio.flush()
    lines = sio.readlines()
    #print lines

    while True:
        sio.write(unicode("SKSREG S2 " + channel + "\n\r"))
        sio.flush()
        lines = sio.readlines()
        #print lines
        
        sio.write(unicode("SKSREG S3 " + panID + "\n\r"))
        sio.flush()
        lines = sio.readlines()
        #print lines
        
        sio.write(unicode("SKLL64 " + addr + "\n\r"))
        sio.flush()
        lines = sio.readlines()
        v6addr=lines[1].rstrip()
        #print "V6_ADDR   =\"" , v6addr , "\""
        #print lines
        sys.stdout.flush() 
        
        ser.setTimeout(0.1)
        sio.write(unicode("SKJOIN " + v6addr + "\n\r"))
        sio.flush()
        while (True):
            line = sio.readline().rstrip()
            if line == "":
                continue
            #print "\"", line, "\""
            if line.startswith("EVENT 22 "):
                myv6addr = line.rstrip().split(" ")[2]
                #print "MY_V6ADDR =", myv6addr
            if line.startswith("EVENT 25 "):
                #print "JOIN SUCCEEDED"
                break

        sio.write(unicode("\n\r"))
        sio.flush()
        lines = sio.readlines()
        #print lines

        ser.setTimeout(0.5)
        sio.write(unicode("SKSENDTO 1 " + v6addr + " 0E1A 1 000E "))
        sio.flush()
        cmd = '1081000105FF010288016201E700'
        ser.write(cmd.decode("hex"))
        ser.flush()
        sio.write(unicode("\n\r"))
        sio.flush()
        while (True):
            #line = ser.read(200)
            line = sio.readline()
            if line == "":
                continue
            #print "\"", line, "\""
            if line.startswith("ERXUDP "):
                buf = line.split(" ")
                #print "BUF,", buf
                myaddr = buf[2]
                #print "myaddr =", myaddr
                #print "        ", myv6addr
                if myaddr == myv6addr:
                    from datetime import datetime
                    import json
                    cur = datetime.now()
                    dtStr = cur.strftime('%Y/%m/%dT%H:%M:%S')
                    timestamp = cur.strftime('%s')
                    watt = int(buf[8].rstrip()[-8:], 16)
                    #print "Watt = " , watt
                    print json.dumps({'timestamp':timestamp, 'datetime':dtStr, 'watt':watt})
                    break
            else:
                next

        ser.setTimeout(0.5)
        ser.write("\n\r\n\rSKTERM\n\r")      # write a string
        sio.flush()
        lines = sio.readlines()
        #print lines
        
        time.sleep(1)
        #break
        
finally:
    ser.setTimeout(2)
    ser.write("\n\r\n\rSKTERM\n\r")      # write a string
    sio.flush()
    lines = sio.readlines()
    #print lines
    ser.close()             # close port

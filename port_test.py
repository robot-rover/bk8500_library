import serial

def cmd8500(cmd , ser):
    print("Command: ", hex(cmd[2]))
    printbuff(cmd)
    ser.write(cmd)
    resp = ser.read(26)
    print("Resp: ")
    printbuff(resp)

def printbuff(b):
    r=""
    for s in range(len(b)):
        r+=" "
        #r+=str(s)
        #r+="-"
        r+=hex(b[s]).replace('0x','')
    print(r)

def csum(thing):
    sum = 0
    for i in range(len(thing)):
        sum+=thing[i]
    return 0xFF&sum

def test_serial(port='/dev/ttyUSB0'):
    ser = serial.Serial(port=port, baudrate=9600)
    print(ser)
    cmd8500([0xaa,00,0x6A,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,(0x6A+0xAA)&0xFF], ser)


if __name__ == '__main__':
    test_serial()

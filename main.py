import machine
import network
import utime
from machine import UART
from machine import Pin
import sds011
import ntptime
import dht

# config
WIFIssid = "ENGIOT"
WIFIpsw = "coeai123"

room = 'Test'

device_ID1 = 'Test'
## In case multi
# device_ID2 = 'ACWU-Co2'
# device_ID3 = 'ACWU-Co3'

## In case multi outdoor for multiCurrentwithOutdoorOnly, singleCurrentwithOutdoorOnly
# DeviceOutdoor2 = ''

# CT30A = 80, CT10A = 30
# currentCalibration1 = 55
# currentCalibration2 = 80
# currentCalibration3 = 80

# URL = 'https://smart-air-care-default-rtdb.asia-southeast1.firebasedatabase.app'

# create a current object refering to the sensor’s data pin

## MultiCurrent Board ### White board swaps between indoor and outdoor
sensor = dht.DHT22(machine.Pin(27))

## Choose dust sensor
dust_ss = "SDS011"
uart = UART(1, baudrate=9600, tx=18, rx=4)

if dust_ss == "SDS011":
    # Dust sensor: SDS011
    dust_sensor = sds011.SDS011(uart)
    print('sleeping for 30 seconds...')
    dust_sensor.wake()
    utime.sleep(30)

SUPPLY_VOLTAGE = 220

led_pin = machine.Pin(2, Pin.OUT) #built-in LED pin
led_pin.value(1)

inTemps, inHums, exTemps, exHums, pm10s, pm25s = [], [], [], [], [], []

now = ""

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...', WIFIssid)
        sta_if.active(True)
        sta_if.connect(WIFIssid, WIFIpsw)
        count = 0
        while not sta_if.isconnected():
             if(count > 60):
               print('Cannot connect to network...')
               utime.sleep(180)
               machine.reset()
             else: 
               print('.', end = '')
               utime.sleep(1)
               count = count + 1
               pass
    print()
    print('network config: {}'.format(sta_if.ifconfig()))

def set_time():
    ntptime.settime()
    tm = utime.localtime()
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    machine.RTC().datetime(tm)
    print('current time: {}'.format(utime.localtime()))

def mean(arr):
    sum = 0.00
    for x in arr:
        sum = sum + x
    avg = sum / len(arr)
    return avg

def indoorDust(now, minute):
    
    global inTemps, inHums, pm10s, pm25s

    it = 0
    ih = 0
    pm10 = 0
    pm25 = 0

    ### Indoor Environment Senser ###
    try:
        sensor.measure()
        it = sensor.temperature()
        ih = sensor.humidity()
        inTemps.append(it)
        inHums.append(ih)
    except:
        inTemps.append(1.00)
        inHums.append(1.00)
    
     # For Dust
    try:
        if dust_ss == "SDS011":
            dust_sensor.read()
            dust_sensor.packet_status
            pm25 = dust_sensor.pm25
            pm10 = dust_sensor.pm10

        pm25s.append(pm25)
        pm10s.append(pm10)
    except:
        pm25s.append(0.00)
        pm10s.append(0.00)

    print(now, it, ih, pm10, pm25)
    utime.sleep(2)

    '''
    if(minute % 2 == 0):
        inTemp = mean(inTemps)
        inHum = mean(inHums)
        pm10 = mean(pm10s)
        pm25 = mean(pm25s)

        print()
        line = now + ", " + str(inTemp) + ", "+str(inHum)  + ", "+ str(pm10) + ", " + str(pm25) +  "\n"
        print(line)

        
        message1 = {
            "Timestamp": now,
            "IndoorTemperature": inTemp,
            "IndoorHumidity": inHum,
            "PM 10": pm10,
            "PM 25": pm25,
        }

        utime.sleep(1)
        
        try:
            led_pin.value(1)

            # Publish to Firebase Realtime Database
            path1 = "SAC/RAWdata/" + room + "/" + device_ID1 + "/" + now +  "/"
            firebase.put(path1, message1, bg=0)

            inTemps = []
            inHums = []
            pm10s = []
            pm25s = []

            led_pin.value(0)

            utime.sleep(60)

        except Exception as e:               
            print('Cannot Publish to Google Cloud ...', e)
            utime.sleep(30)
            machine.reset()
    '''

def main():

    while(True):

        t = rtc.datetime()
        now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])            
        
        try:
            led_pin.value(1)

            ## For a room with multiple ACs with indoor DHT, and outdoor DHT
            # multiCurrentwithIndoorOutdoor(now, t[5])

            ## For a room with an AC with indoor DHT, and outdoor DHT
            # singleCurrentwithIndoorOutdoor(now, t[5])

            ## For a room with an multiple ACs with indoor DHT
            # multiCurrentwithIndoorOnly(now, t[5])

            ## For a room with an multiple ACs with outdoor DHT (edit in fuction for outdoor DHT for another room, edit room2, DeviceOutdoor2)
            # multiCurrentwithOutdoorOnly(now, t[5])

            ## For a room with an AC with indoor DHT
            # singleCurrentwithIndoorOnly(now, t[5])

            ## For a room with an AC with outdoor DHT (edit in fuction for outdoor DHT for another room, edit room2, DeviceOutdoor2)
            # singleCurrentwithOutdoorOnly(now, t[5])

            ## For a room with an AC only, no DHT
            # singleCurrentOnly(now, t[5])

            ## For a room with an multiple ACs only, no DHT
            # multiCurrentOnly(now, t[5])

            ## For outdoor DHT, no AC (edit in fuction for another room, edit room2, device_ID2)
            # outdoorDHTBoardOnly(now, t[5])

            ## For indoor DHT, no AC
            # indoorDHTBoardOnly(now, t[5])

            ## For indoor and outdoor board, no AC
            # indoorAndOutdoor(now, t[5])

            ## For a room with an AC with indoor DHT, outdoor DHT, and Dust sensor
            # singleCurrentwithIndoorOutdoorDust(now, t[5])

            ## For a room with indoor DHT, and Dust sensor
            indoorDust(now, t[5])

            led_pin.value(0)

        except Exception as e:               
            print('Main ...', e)
            utime.sleep(30)
            machine.reset()
        
        utime.sleep(1)  # Delay for 1 seconds.

try:
    print()
    print('starting...', room)

    connect()

    #Need to be connected to the internet before setting the local RTC.
    set_time()
    rtc = machine.RTC()
    utc_shift = 7
    (year, month, mday, week_of_year, hour, minute, second, milisecond) = rtc.datetime()
    rtc.init((year, month, mday, week_of_year, hour + utc_shift, minute, second, milisecond))
    t = rtc.datetime()
    now = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(t[0], t[1], t[2], t[4], t[5], t[6])

    # firebase.setURL(URL)

    main()

except Exception as e:
    print('Failed ...', e)

    utime.sleep(30)
    machine.reset()

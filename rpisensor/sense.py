# This example is a hello world example
# for using a keypad with the Raspberry Pi
 
import RPi.GPIO as GPIO
import requests
import time
import sys
 

# Code from https://github.com/tatobari/hx711py/blob/master/example.py

EMULATE_HX711=False
 
# referenceUnit = 1
referenceUnit = 21.7
 
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711
 
def cleanAndExit():
    print("Cleaning...")
 
    if not EMULATE_HX711:
        GPIO.cleanup()
 
    print("Bye!")
    sys.exit()
 
hx = HX711(17, 27)
 
# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")
 
# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)
 
hx.reset()
 
hx.tare()
 
print("Tare done! Add weight now...")
 
# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()
 
# Code for 16 button keypad
 
L1 = 5
L2 = 6
L3 = 13
L4 = 19
 
C1 = 12
C2 = 16
C3 = 20
C4 = 21
 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
 
GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)
 
GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
def readLine(line, characters):
    column = None
    GPIO.output(line, GPIO.HIGH)
    if(GPIO.input(C1) == 1):
        column = characters[0]
    if(GPIO.input(C2) == 1):
        column = characters[1]
    if(GPIO.input(C3) == 1):
        column = characters[2]
    if(GPIO.input(C4) == 1):
        column = characters[3]
    GPIO.output(line, GPIO.LOW)
    return column
 
def get_current_weight():
    w = 0
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
 
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
 
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        w = hx.get_weight(5)
 
        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s  B: %s" % ( val_A, val_B )
 
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
    return w
 
def send_current_weight():
    w = get_current_weight()
    url = '<LAMBDA_URL>'
    item_data = dict(weight=w, device="RPI")
    r = requests.post(url, json=item_data)
    print(f'sending {w}')
    print(r.json())
 
 
counter = 0
sending = False
try:
    while True:
        col = readLine(L1, ["1","2","3","A"])
        if col and not sending:
            if col == '3':
                sending = True
                send_current_weight()
        counter += 1
        if counter % 20 == 0:
            counter = 0
            sending = False
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nApplication stopped!")
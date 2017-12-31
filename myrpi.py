# Import packages
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import ssl
import json
import time

#-------------------------------------------------------------------------------
# MQTT Setup
#-------------------------------------------------------------------------------

#
# MQTT connection variables
#

MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_HOST = "awo55dh8tplny.iot.us-east-1.amazonaws.com"
CA_ROOT_CERT_FILE = "./root-CA.crt"
THING_CERT_FILE = "./MyRPi.cert.pem"
THING_PRIVATE_KEY = "./MyRPi.private.key"

MQTT_TOPIC_SUB = "$aws/things/MyRPi/shadow/update/delta"
MQTT_TOPIC_PUB = "$aws/things/MyRPi/shadow/update"
INIT_PAYLOAD = "{\"state\":{\"reported\":{\"power\":\"off\",\"color\":\"red\"}}}"
UPDATE_POWER_OFF = "{\"state\":{\"reported\":{\"power\":\"off\"}}}"
UPDATE_POWER_ON = "{\"state\":{\"reported\":{\"power\":\"on\"}}}"
UPDATE_COLOR_RED = "{\"state\":{\"reported\":{\"color\":\"red\"}}}"
UPDATE_COLOR_WHITE = "{\"state\":{\"reported\":{\"color\":\"white\"}}}"
UPDATE_COLOR_BLUE = "{\"state\":{\"reported\":{\"color\":\"blue\"}}}"

#
# MQTT callback functions
#

def on_connect(client, userdata, flags, rc):
    #print "on_connect: rc = " + str(rc)
    mqttc.subscribe(MQTT_TOPIC_SUB, 0)

def on_message(client, userdata, msg):
	#print "Topic: " + str(msg.topic)
	#print "Payload: " + str(msg.payload)
	handle_led(str(msg.payload))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to Topic: " + 
	MQTT_TOPIC_SUB + " with QoS: " + str(granted_qos))

def on_publish(client, userdata, mid):
    #print "on publish:"
    print ""

#
# Shadow update functions
#

def report_update_power(power) :
    if power == 0 :
        mqttc.publish(MQTT_TOPIC_PUB, UPDATE_POWER_OFF, qos=1)
    elif power == 1 :
        mqttc.publish(MQTT_TOPIC_PUB, UPDATE_POWER_ON, qos=1)

def report_update_color(color) :
    if color == LED_RED :
        mqttc.publish(MQTT_TOPIC_PUB, UPDATE_COLOR_RED, qos=1)
    elif color == LED_WHITE :
        mqttc.publish(MQTT_TOPIC_PUB, UPDATE_COLOR_WHITE, qos=1)
    elif color == LED_BLUE :
        mqttc.publish(MQTT_TOPIC_PUB, UPDATE_COLOR_BLUE, qos=1)

#-------------------------------------------------------------------------------
# LED Setup
#-------------------------------------------------------------------------------

#
# State variables
#

LED_RED = 22 
LED_WHITE = 27
LED_BLUE = 17 

#
# LED handling when subscription topic is received
#

def handle_led(payload):
    global statePower, stateLED

    # Translate msg into state variables
    payloadDict = json.loads(payload)
    desiredPower = payloadDict["state"].get("power","") 
    desiredColor = payloadDict["state"].get("color","")
    str = "Delta: "
    if desiredPower != "" :
       str += "power = " + desiredPower + " "
    if desiredColor != "" :
       str += "color = " + desiredColor 
    print str
    
    newPower = -1   # Not specified
    if desiredPower == "off" :
        newPower = 0
    elif desiredPower == "on" :
        newPower = 1

    newLED = -1     # Not specified
    if desiredColor == "red":
        newLED = LED_RED
    elif desiredColor == "white" :
        newLED = LED_WHITE
    elif desiredColor == "blue" :
        newLED = LED_BLUE

    # Turn LED on/off and change color
    if newPower != -1 :    # Power state changed: turn off/on the old LED
        if newPower == 1 :
            GPIO.output(stateLED, GPIO.HIGH)
        else :
            GPIO.output(stateLED, GPIO.LOW)
        statePower = newPower
        report_update_power(newPower)
    elif newLED != -1 :           
        # if currently powered on >> turn off old and turn on new; 
        if statePower == 1 :
            GPIO.output(stateLED, GPIO.LOW)
            GPIO.output(newLED, GPIO.HIGH)
        stateLED = newLED   
        report_update_color(newLED)
    else  :
        print("Error: Wrong Msg or problem in parsing")

    str = "State: power = %d " % statePower + "and color = " 
    if stateLED == LED_RED :
        str += "red"
    elif stateLED == LED_WHITE :
        str += "white" 
    elif stateLED == LED_BLUE :
        str += "blue"
    print str

#-------------------------------------------------------------------------------
# Main Program
#-------------------------------------------------------------------------------

statePower = 0         # (0 - off; 1 - on)
stateLED   = LED_RED   # (Red, White, & Blue)

#
# Setup & test LEDs on RPi
#

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(LED_WHITE, GPIO.OUT)
GPIO.setup(LED_BLUE, GPIO.OUT)

# Turn led's on and off to indicate readiness
GPIO.output(LED_RED, GPIO.HIGH)
GPIO.output(LED_WHITE, GPIO.HIGH)
GPIO.output(LED_BLUE, GPIO.HIGH)
time.sleep(2)
GPIO.output(LED_RED, GPIO.LOW)
GPIO.output(LED_WHITE, GPIO.LOW)
GPIO.output(LED_BLUE, GPIO.LOW)

#
# Setup connction with AWS IoT and wait for delta messages
#

# Initiate MQTT Client
mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_publish = on_publish

# Configure TLS Set
mqttc.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, 
    keyfile=THING_PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, 
    tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect with MQTT Broker
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

# Initialize shadow state and wait for updates
mqttc.publish(MQTT_TOPIC_PUB, UPDATE_POWER_OFF, qos=1)
mqttc.publish(MQTT_TOPIC_PUB, UPDATE_COLOR_RED, qos=1)
mqttc.loop_forever()
GPIO.cleanup()
print "Exiting myrpi program..."


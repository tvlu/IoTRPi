# Import packages
import time
import paho.mqtt.client as mqtt
import ssl

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

MQTT_TOPIC      = "$aws/things/MyRPi/shadow/update"
MSG_POWER_ON    = "{\"state\":{\"reported\":{\"power\":\"on\"}}}"
MSG_POWER_OFF   = "{\"state\":{\"reported\":{\"power\":\"off\"}}}"
MSG_COLOR_RED   = "{\"state\":{\"reported\":{\"color\":\"red\"}}}"
MSG_COLOR_WHITE = "{\"state\":{\"reported\":{\"color\":\"white\"}}}"
MSG_COLOR_BLUE  = "{\"state\":{\"reported\":{\"color\":\"blue\"}}}"
DELAY           = 10

#
# MQTT callback functions
#

def on_connect(client, userdata, flags, rc):
    print "on_connect: rc = " + str(rc)

def on_publish(client, userdata, mid):
    print "Message published.. "

#-------------------------------------------------------------------------------
# Main Program
#-------------------------------------------------------------------------------

#
# Setup connction with AWS IoT and wait for delta messages
#

# Initiate MQTT Client
mqttc = mqtt.Client()

# Assign event callbacks
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish

# Configure TLS Set
mqttc.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, 
    keyfile=THING_PRIVATE_KEY, cert_reqs=ssl.CERT_REQUIRED, 
    tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

# Connect with MQTT Broker
mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
mqttc.loop_start()

# Keep publishing messages
while True:
	mqttc.publish(MQTT_TOPIC, MSG_POWER_ON, qos=1)
	time.sleep(DELAY)
	mqttc.publish(MQTT_TOPIC, MSG_COLOR_WHITE, qos=1)
	time.sleep(DELAY)
	mqttc.publish(MQTT_TOPIC, MSG_COLOR_BLUE, qos=1)
	time.sleep(DELAY)
	mqttc.publish(MQTT_TOPIC, MSG_COLOR_RED, qos=1)
	time.sleep(DELAY)
	mqttc.publish(MQTT_TOPIC, MSG_POWER_OFF, qos=1)
	time.sleep(DELAY)

mqttc.disconnect()


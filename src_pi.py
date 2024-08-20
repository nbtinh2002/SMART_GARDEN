import adafruit_dht
import board
import time
import paho.mqtt.client as mqtt
import ssl
import RPi.GPIO as GPIO
from gpiozero import MCP3008

# GPIO configuration
GPIO.setmode(GPIO.BCM)  
GPIO.setup(21, GPIO.OUT)  # Pump control
GPIO.setup(20, GPIO.OUT)  # Light control

# MQTT broker configuration
MQTT_BROKER = 'c63b78190c984836a0307fe0cbc37128.s1.eu.hivemq.cloud'
MQTT_PORT = 8883
SUB_TOPIC = 'IoT_spkt/Control'
PUB_TOPIC = 'IoT_spkt/Temp_Humid'
MQTT_USERNAME = 'hatuan1102'
MQTT_PASSWORD = 'Choghe123'
CA_CERTS_FILE = '/etc/ssl/certs/ca-certificates.crt'

# Initialize the DHT11 sensor and soil sensor
dht_device = adafruit_dht.DHT11(board.D4)
soil_sensor = MCP3008(channel=0, device=0)

# Initialize the MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set(ca_certs=CA_CERTS_FILE, tls_version=ssl.PROTOCOL_TLS)

#Threshold for auto mode
TEMP_THRESHOLD = 30.0
HUMIDITY_THRESHOLD = 60.0
SOIL_THRESHOLD = 50.0
mode_control = 0
pump_control = 0
light_control = 0
# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(SUB_TOPIC)

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

def on_message(client, userdata, msg):
    global mode_control, pump_control, light_control
    try:
        control_message = msg.payload.decode().split()
        print(f"Received control message: {control_message}")
        pump_control = int(control_message[1])
        light_control = int(control_message[2])
        mode_control = int(control_message[3])

    except (ValueError, IndexError) as e:
        print(f"Error processing control message: {e}")

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def average_soil_moisture(sensor):
    total = 0
    for _ in range(10):
        total += (1 - sensor.value) *200
        time.sleep(0.1)
    return total / 10
try:
    while True:
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            soil_percen = average_soil_moisture(soil_sensor)
            
            if mode_control == 1:
                
                if humidity < HUMIDITY_THRESHOLD or soil_percen < SOIL_THRESHOLD:
                    pump_control = 1
                    GPIO.output(21, GPIO.HIGH)
                else:
                    GPIO.output(21,GPIO.LOW)
                    pump_control = 0
                    
                if soil_percen < SOIL_THRESHOLD:
                    light_control = 1
                    GPIO.output(20, GPIO.HIGH)
                else:
                    GPIO.output(20,GPIO.LOW)
                    light_control = 0
                        
                message = f"Temperature: {temperature_c:.1f} C, Humidity: {humidity:.1f}%, Soil Moisture: {soil_percen:.1f}%, Status: {pump_control}"
                client.publish(PUB_TOPIC, message)
                print(f"Message published: {message}")
            else:
                GPIO.output(21, GPIO.HIGH if pump_control else GPIO.LOW) 
                GPIO.output(20, GPIO.HIGH if light_control else GPIO.LOW) 
                message = f"Temperature: {temperature_c:.1f} C, Humidity: {humidity:.1f}%, Soil Moisture: {soil_percen:.1f}%"
                client.publish(PUB_TOPIC, message)
                print(f"Message published: {message}")
            print("Mode: Auto" if mode_control else "Mode: Manual")    
            print("Pump ON" if pump_control else "Pump OFF")
            print("Light ON" if light_control else "Light OFF")
        except Exception as e:
            print(f"Sensor read or MQTT publish error: {e}")
        time.sleep(3)

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    client.loop_stop()
    client.disconnect()
    GPIO.cleanup()

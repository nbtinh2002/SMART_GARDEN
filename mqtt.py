import paho.mqtt.client as mqtt
import mysql.connector
import json
import time
import re
# Thông tin kết nối MySQL
MYSQL_HOST = "localhost"
MYSQL_USER = "tuan"
MYSQL_PASSWORD = "100902"
MYSQL_DATABASE = "SIC_IOT_FINAL"

# Thông tin kết nối MQTT
BROKER = "c63b78190c984836a0307fe0cbc37128.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "hatuan1102"
PASSWORD = "Choghe123"
SUB_TOPIC = "IoT_spkt/Temp_Humid"
PUB_TOPIC = "IoT_spkt/Control"

# Kết nối MySQL
def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Callback khi nhận được tin nhắn
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Received message: {payload} on topic {msg.topic}")

        # Sử dụng regex để phân tích dữ liệu
        temp_match = re.search(r"Temperature:\s*(\d+\.\d+)", payload)
        humid_match = re.search(r"Humidity:\s*(\d+\.\d+)", payload)
        humid_soil_match = re.search(r"Soil Moisture:\s*(\d+\.\d+)", payload)
        status_match = re.search(r"Status:\s*(\d+)", payload)
	
        if temp_match and humid_match:
            # Trích xuất giá trị nhiệt độ và độ ẩm
            temp = float(temp_match.group(1))
            humid = float(humid_match.group(1))
            humid_soil = float(humid_soil_match.group(1))
            status = int(status_match.group(1))
	
            # Kết nối đến MySQL và gửi dữ liệu
            connection = connect_mysql()
            if connection:
                cursor = connection.cursor()
                
                # Chèn dữ liệu vào bảng "data"
                cursor.execute("""
                    INSERT INTO DATA (Humid_dht11, Temp_dht11, Humid_soil) 
                    VALUES (%s, %s, %s)
                """, (humid, temp, humid_soil))
                
                # Cập nhật dữ liệu vào bảng "CONTROL"
                cursor.execute("""
                    UPDATE CONTROL 
                    SET Pump = %s 
                    WHERE ID = 1
                """, (status,))
                
                # Xoá các bản ghi cũ để chỉ giữ lại 10 bản ghi mới nhất
                cursor.execute("""
                    DELETE FROM DATA 
                    WHERE ID NOT IN (
                        SELECT ID FROM (
                            SELECT ID FROM DATA 
                            ORDER BY ID DESC 
                            LIMIT 10
                        ) AS temp_table
                    )
                """)
                connection.commit()
                cursor.close()
                connection.close()
                print("Data inserted and old records removed from MySQL")
            else:
                print("Failed to connect to MySQL")
        else:
            print("Failed to parse temperature or humidity from payload")

    except Exception as e:
        print(f"Error: {e}")

# Lấy dữ liệu từ cơ sở dữ liệu
def retrieve_data():
    connection = connect_mysql()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CONTROL")
        rows = cursor.fetchall()
        retrive = " ".join(str(value) for row in rows for value in row.values())
        cursor.close()
        connection.close()
        return retrive.strip()
    else:
        return ""

# Callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(SUB_TOPIC)

# Gửi dữ liệu lên MQTT
def publish_data(client):
    data = retrieve_data()
    if data:
        client.publish(PUB_TOPIC, data)
        print(f"Published message: {data}")
    else:
        print("No data to publish")

# Tạo đối tượng client MQTT
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

# Kết nối đến broker
client.connect(BROKER, PORT, 60)

# Bắt đầu vòng lặp lắng nghe tin nhắn
client.loop_start()

# Nghe tin nhắn và gửi dữ liệu định kỳ
try:
    while True:
        publish_data(client)
        time.sleep(1)  # Chờ 1 giây trước khi gửi dữ liệu tiếp theo
except KeyboardInterrupt:
    print("Program interrupted by user")

# Ngắt kết nối và dừng vòng lặp
client.loop_stop()
client.disconnect()


import paho.mqtt.client as mqtt
import datetime
import collections
import pandas as pd
import os
import json
import psycopg2
import time
import prophet
from prophet.serialize import model_to_json, model_from_json

FORECASTED_FEATURE = "meteo_TdegC"

def init_db():
    print("Initializing DB...", flush=True)

    max_retries = 10
    retry_delay = 3  # seconds

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host='db',
                database="measurements_db",
                user="user",
                password="password",
                port=5432
            )
            print("Connected to DB!", flush=True)

            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    time TIMESTAMP,
                    tenant VARCHAR(255),
                    device VARCHAR(255),
                    measurements_true FLOAT,
                    measurements_predicted FLOAT,
                    measurements_predicted_upper_bound FLOAT,
                    measurements_predicted_lower_bound FLOAT
                );
            """)
            conn.commit()
            cur.close()
            conn.close()

            print("DB initialized successfully")
            return

        except psycopg2.OperationalError as e:
            print(f"DB not ready yet (attempt {attempt+1}/{max_retries})", flush=True)
            time.sleep(retry_delay)

    raise Exception("Could not connect to DB after retries")

def on_message(client, userdata, msg):
    print("Received MQTT message on topic", flush=True)
    # 1. Parse the incoming JSON
    data = json.loads(msg.payload.decode())
    
    # Topic format: tenant/device/things/...
    topic_parts = msg.topic.split('/')
    tenant = topic_parts[0]
    device = topic_parts[1]
    time = datetime.datetime.strptime(data['timestamp'], "%Y-%m-%d %H:%M:%S")
    measurements_true = pd.json_normalize(data['value'], sep='_')[FORECASTED_FEATURE].tolist()[0]
    
    # 3. Predict using the prhpnet model
    with open('serialized_model.json', 'r') as fin:
        model = model_from_json(fin.read())
    
    datetimes_df = pd.DataFrame({
        'ds': [time]
    })  
    
    predictions = model.predict(datetimes_df)
    measurements_predicted = predictions['yhat'].tolist()[0]
    measurements_predicted_lower_bound = predictions['yhat_lower'].tolist()[0]
    measurements_predicted_upper_bound = predictions['yhat_upper'].tolist()[0]
    
    # 4. Insert into PostgreSQL/TimescaleDB
    conn = psycopg2.connect(host='db', database="measurements_db", user="user", password="password", port=5432)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sensor_data (time, tenant, device, measurements_true, measurements_predicted, measurements_predicted_upper_bound, measurements_predicted_lower_bound)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (time, tenant, device, measurements_true, measurements_predicted, measurements_predicted_upper_bound, measurements_predicted_lower_bound))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("mqtt_broker", 1883, 60)
    client.subscribe("sensors/temp/live")
    client.loop_forever()
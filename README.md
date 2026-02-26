# WattWatch

A Docker-based IoT data pipeline that:

- Receives sensor data via MQTT
- Performs prediction and stores true and predicted data in PostgreSQL
- Visualizes data in Grafana with outliers indication 

demonstration_mqtt.ipynb notebbok deomstrates training of prophet and how to send data via mqqt. 

---

## Architecture

This project uses:

- Eclipse Mosquitto (MQTT broker)
- PostgreSQL (relational database)
- Python writer service (MQTT subscriber + DB writer)
- Grafana (analytics and visualization platform)

Data Flow:

MQTT Devices
      ↓
Mosquitto (Broker)
      ↓
Writer Service (Python)
      ↓
PostgreSQL
      ↓
Grafana Dashboard

---

## Project Structure
```
project/
│
├── docker-compose.yml
├── mosquitto/
│   └── config/
├── writer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── writer.py
└── dashboard/ (optional if using Dash instead of Grafana)
```

---

## Getting Started

Start the stack:

   docker compose up --build

Services:

- MQTT Broker: port 1883
- PostgreSQL: port 5432
- Grafana: http://localhost:3000

---

## Default Credentials
```
PostgreSQL:
- Database: measurements_db
- User: user
- Password: password
- Host (inside Docker): db
- Port: 5432

Grafana:
- URL: http://localhost:3000
- User: admin
- Password: admin
```

---

## Configuring Grafana

1. Open http://localhost:3000
2. Go to Settings → Data Sources → Add Data Source
3. Choose PostgreSQL
4. Use:
```
   Host: db:5432
   Database: measurements_db
   User: user
   Password: password
   SSL Mode: disable
```

Click "Save & Test"

Create a  new time-series dashboard with the following query:
```
SELECT
  time as "time",
  measurements_true,
  measurements_predicted_upper_bound,
  measurements_predicted_lower_bound 

FROM sensor_data
ORDER BY time;
```

Then, configure fill below property of dash to visualize confidence interval between lower and upper bounds. 

---

## Database Schema
```
CREATE TABLE sensor_data (
    time TIMESTAMP,
    tenant VARCHAR(255),
    device VARCHAR(255),
    measurements_true FLOAT,
    measurements_predicted FLOAT,
    measurements_predicted_upper_bound FLOAT,
    measurements_predicted_lower_bound FLOAT
);
```
---

## Environment Variables (Writer Service)
```
DB_HOST=db
DB_NAME=measurements_db
DB_USER=user
DB_PASSWORD=password
MQTT_BROKER=mosquitto
```
---

## Development Notes

- Docker service names are used as hostnames inside the network (db, mosquitto)
- Writer implements retry logic for DB startup
- Grafana refresh interval can be configured per dashboard
- Output buffering disabled via PYTHONUNBUFFERED=1
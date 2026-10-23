Full-stack IoT environment monitoring system featuring an asynchronous FastAPI backend, Jinja2 server-side rendering (SSR), MQTT data pipeline, and PostgreSQL database, containerized via Docker.

### Testing with Hardware Emulator

The project includes an IoT hardware emulator (`emulator.py`) that simulates a physical weather station. It generates random temperature, humidity, and atmospheric pressure data and publishes it to the Mosquitto MQTT broker.

To test the system locally outside of Docker:
1. Make sure the Docker container infrastructure is running (`docker-compose up -d`).
2. Install the required dependency for the script (e.g., `pip install paho-mqtt` or `gmqtt` depending on your emulator stack).
3. Run the emulator script from your terminal:
   ```bash
   python emulator.py
   ```
4. Open the web interface at `http://localhost:8085/` to watch the charts update dynamically as the database receives new entries from the emulator.

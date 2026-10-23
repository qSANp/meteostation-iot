import time
import json
import random
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1884
TOPIC = "weather/sensors"

# Инициализируем клиент
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(BROKER, PORT, 60)
except Exception as e:
    print(f"❌ Ошибка подключения к брокеру: {e}")
    exit(1)

# Запускаем сетевой цикл в отдельном потоке (это критично для стабильности!)
client.loop_start()

print("🚀 Эмулятор датчика запущен. Отправка данных... (Ctrl+C для выхода)")

try:
    while True:
        payload = {
            "temperature": round(random.uniform(18.0, 26.0), 1),
            "humidity": round(random.uniform(45.0, 75.0), 1),
            "pressure": round(random.uniform(745.0, 760.0), 1)
        }

        # Отправляем сообщение
        msg_info = client.publish(TOPIC, json.dumps(payload))

        # Ждем подтверждения доставки от брокера (не более 1 секунды)
        msg_info.wait_for_publish(timeout=1.0)

        print(f"[Датчик] Успешно отправлено: {payload}")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nОстановка эмулятора...")
finally:
    client.loop_stop()
    client.disconnect()

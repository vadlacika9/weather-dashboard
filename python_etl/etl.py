import os
import time
import requests
from influxdb import InfluxDBClient

INFLUX_HOST = os.getenv("INFLUX_HOST", "localhost")
INFLUX_PORT = int(os.getenv("INFLUX_PORT", "8086"))
INFLUX_DB = os.getenv("INFLUX_DB", "weatherdb")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CITY = "Cluj-Napoca,RO"

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": float(data["main"]["temp"]),
                "humidity": float(data["main"]["humidity"]),
                "pressure": float(data["main"]["pressure"]),
                "wind_speed": float(data["wind"]["speed"]),
            }
        else:
            print(f"Failed to get weather data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def main():
    client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
    client.switch_database(INFLUX_DB)

    try:
        while True:
            weather = get_weather()
            if weather:
                json_body = [
                    {
                        "measurement": "weather",
                        "tags": {
                            "location": CITY
                        },
                        "fields": weather
                    }
                ]
                client.write_points(json_body)
                print(f"Written data: {weather}")
            else:
                print("No data to write.")
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        client.close()

if __name__ == "__main__":
    main()

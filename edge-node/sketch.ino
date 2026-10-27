#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "fog/edge01/sensors";

#define DHTPIN 15
#define DHTTYPE DHT22
#define PIR_PIN 13
#define LDR_PIN 34

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void connectWiFi() {

  Serial.print("Connecting to WiFi");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void connectMQTT() {

  client.setServer(mqtt_server, mqtt_port);

  while (!client.connected()) {

    Serial.print("Connecting to MQTT broker...");

    if (client.connect("edge01")) {

      Serial.println("connected");

    } else {

      Serial.print("failed, retrying...");
      delay(2000);

    }
  }
}

void initSensors() {

  pinMode(PIR_PIN, INPUT);
  dht.begin();
}

void readSensors(float &temperature,
                 float &humidity,
                 int &motion,
                 int &light) {

  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  motion = digitalRead(PIR_PIN);
  light = analogRead(LDR_PIN);
}

String createPacket(float temperature,
                    float humidity,
                    int motion,
                    int light) {

  StaticJsonDocument<200> doc;

  doc["device_id"] = "edge01";
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["motion"] = motion;
  doc["light"] = light;

  String payload;
  serializeJson(doc, payload);

  return payload;
}

void publishSensorData() {

  float temperature, humidity;
  int motion, light;

  readSensors(temperature, humidity, motion, light);

  String payload = createPacket(temperature, humidity, motion, light);

  Serial.println("\nPublishing packet:");
  Serial.println(payload);

  client.publish(mqtt_topic, payload.c_str());
}

void setup() {

  Serial.begin(115200);

  connectWiFi();
  initSensors();
  connectMQTT();
}

void loop() {

  if (!client.connected()) {
    connectMQTT();
  }

  client.loop();

  publishSensorData();

  delay(2000);
}
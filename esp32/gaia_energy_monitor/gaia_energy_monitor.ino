/*
  Gaia – ESP32 Energy Monitor
  ------------------------------------
  - Lê corrente/energia (simulado no pino 34)
  - Detecta anomalias localmente
  - Envia dados para a API do HUM.A.N OPS
  - Loga no Serial Plotter
*/

#include <WiFi.h>
#include <HTTPClient.h>

// ========================
// CONFIG WIFI
// ========================
const char* WIFI_SSID     = "WIFI_SSID_AQUI";
const char* WIFI_PASSWORD = "WIFI_PASSWORD_AQUI";

// ========================
// CONFIG API
// ========================
String API_URL = "http://servidor/energia/register";  
// Ex: http://192.168.0.15:8000/energia/register

// ========================
// PINAGEM
// ========================
int SENSOR_PIN = 34;     // Entrada analógica do ESP32

// ========================
// ANOMALIA (REGRAS LOCÁIS)
// Mesmo conceito do backend: pico > 2.0 kWh
// ========================
float ANOMALY_THRESHOLD = 2.0;

// ========================
// FUNÇÃO: Conectar WiFi
// ========================
void connectWiFi() {
  Serial.print("Conectando ao WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retry++;
    if (retry > 20) {
      Serial.println("Falha no WiFi. Reiniciando...");
      ESP.restart();
    }
  }

  Serial.println("\nConectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// ========================
// FUNÇÃO: Ler Energia
// (Simulação simples)
// ========================
float readEnergy() {
  int raw = analogRead(SENSOR_PIN);

  // Normaliza (0–4095) para ~0.3 a 2.5 kWh
  float kwh = map(raw, 0, 4095, 30, 250) / 100.0;

  return kwh;
}

// ========================
// FUNÇÃO: Enviar para API
// ========================
void sendToAPI(float kwh, bool anomaly) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{ \"kwh\": " + String(kwh, 3) +
                   ", \"anomaly\": " + String(anomaly ? "true" : "false") + 
                   " }";

  int code = http.POST(payload);

  Serial.print("Enviando dados... code=");
  Serial.println(code);

  http.end();
}

// ========================
// SETUP
// ========================
void setup() {
  Serial.begin(115200);
  delay(2000);

  connectWiFi();
  pinMode(SENSOR_PIN, INPUT);
}

// ========================
// LOOP
// ========================
void loop() {
  float kwh = readEnergy();
  bool anomaly = (kwh > ANOMALY_THRESHOLD);

  // Log no Serial Plotter
  Serial.print("kWh: ");
  Serial.print(kwh, 3);
  Serial.print(" | Anomaly: ");
  Serial.println(anomaly ? "1" : "0");

  // Envia para API
  sendToAPI(kwh, anomaly);

  delay(5000); // Leitura a cada 5 segundos
}

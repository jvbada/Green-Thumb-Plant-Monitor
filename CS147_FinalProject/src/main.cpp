#include <Arduino.h>
#include <WiFi.h>
#include <TFT_eSPI.h>
#include <DFRobot_DHT20.h>
#include <HttpClient.h>

#include <string.h>


// WI-FI AND CLOUD SERVER INFO
char ssid[] = "UCInet Mobile Access"; // your network SSID (name) UCInet Mobile Access / CDS-Resident
char pass[] = ""; // your network password (use for WPA, or use as key for WEP) / AC86fm!6
const int kNetworkTimeout = 30*1000; // Number of milliseconds to wait without receiving any data before we give up
const int kNetworkDelay = 1000; // Number of milliseconds to wait if no data is available before trying again

const char kHostname[] = "54.241.144.204"; // Name of the server we want to connect to
const char kPath[] = "/?var=10"; // Path to download
uint16_t aServerPort = 5000;

// SENSOR INFO
DFRobot_DHT20 tempSensor; // Temperature and humidity sensor

#define MOISTURE_PIN 38
#define PHOTOCELL_PIN 32

// #define BUTTON 36

const int dry = 2500;
const int wet = 1000;


void startWiFi() {
  // Connect to Wi-Fi
  Serial.println();
  Serial.println("-- Connecting to Wi-Fi Network --");
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC address: ");
  Serial.println(WiFi.macAddress());
}


void initSensors() {
  // Initialize all sensors
  Serial.println();
  Serial.println("-- Initializing Sensors --");
  
  // Temperature/humidity sensor
  while(tempSensor.begin()){
    Serial.println("Initializing temperature/humidity sensor failed");
    delay(1000);
  }
  Serial.println("Temperature/humidity sensor initialized");
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); 
  sleep(5);
  Serial.println("==== GREEN THUMB PLANT MONITOR ====");
  
  // Connect to Wi-Fi
  startWiFi();
  
  // Initialize sensors
  initSensors();
  pinMode(MOISTURE_PIN, INPUT);
  pinMode(PHOTOCELL_PIN,INPUT);

}

void sendData(char* dataPath) {
  int err =0;
  
  WiFiClient c;
  HttpClient http(c);
  
  err = http.get(kHostname, aServerPort, dataPath);

  char URL[100];
  strcat(URL, "http://127.0.0.1:5000");
  strcat(URL, dataPath);
  Serial.println(URL);
  Serial.println();


  if (err == 0)
  {
    Serial.println();
    Serial.println("startedRequest ok");

    err = http.responseStatusCode();
    if (err >= 0)
    {
      Serial.print("Got status code: ");
      Serial.println(err);

      // Usually you'd check that the response code is 200 or a
      // similar "success" code (200-299) before carrying on,
      // but we'll print out whatever response we get

      err = http.skipResponseHeaders();
      if (err >= 0)
      {
        int bodyLen = http.contentLength();
        Serial.print("Content length is: "); Serial.print(bodyLen);
        
        Serial.println();
        Serial.println("Body returned follows:");
      
        // Now we've got to the body, so we can print it out
        unsigned long timeoutStart = millis();
        // char c;
        // Whilst we haven't timed out & haven't reached the end of the body
        while ( (http.connected() || http.available()) &&
               ((millis() - timeoutStart) < kNetworkTimeout) )
        {
            if (http.available())
            {
                c = http.read();
                // Print out this character
                // Serial.print(c);
               
                bodyLen--;
                // We read something, reset the timeout counter
                timeoutStart = millis();
            }
            else
            {
                // We haven't got any data, so let's pause to allow some to arrive
                delay(kNetworkDelay);
            }
        }
      }
      else
      {
        Serial.print("Failed to skip response headers: ");
        Serial.println(err);
      }
    }
    else
    {    
      Serial.print("Getting response failed: ");
      Serial.println(err);
    }
  }
  else
  {
    Serial.print("Connect failed: ");
    Serial.println(err);
  }

  http.stop();
}


void loop() {
  // put your main code here, to run repeatedly:

  // Button test
  // int buttonState = digitalRead(BUTTON);
  // if (buttonState) {
  //   Serial.println("Button!");
  // }
  // delay(100);

 
  // Get data from sensors
  float temperature = tempSensor.getTemperature(); // Temperature/humidity sensor
  float humidity = tempSensor.getHumidity()*100;
  Serial.print("Temperature: ");
  Serial.println(temperature);
  Serial.print("Humidity: ");
  Serial.println(humidity);

  // HERE
  Serial.println("---------------------");
  // Light sensor
  float lightRead;
  lightRead = analogRead(PHOTOCELL_PIN);
  Serial.print("photocell reading = ");
  Serial.print(lightRead);
  Serial.println("");
  

  // Moisture sensor;
  float MoistureSensorRaw = analogRead(MOISTURE_PIN); // range of 2530(dry) to 3100(wet)
  float HumidityPercentage = map(MoistureSensorRaw, wet, dry, 100.0, 0.0); // range of 0%(dry) to 100%(wet)

  Serial.print("moisture raw = ");
  Serial.print(MoistureSensorRaw);
  Serial.println("");
  Serial.print("Humidity Percentage = ");
  Serial.print(HumidityPercentage);
  Serial.println(" %");

  char dataPath[100];
  sprintf(dataPath, "/?light=%f&soilMoisture=%f&temp=%f&humid=%f", lightRead, MoistureSensorRaw, temperature, humidity);
  // sprintf(dataPath, "/?number=%d", i);
  // i++;
  sendData(dataPath);
  delay(1000);

}
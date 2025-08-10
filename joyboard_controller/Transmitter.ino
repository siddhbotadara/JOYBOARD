// This code includes optional LCD+I2C display support alongside NRF24L01 transceiver functionality.
// If you're not using an LCD+I2C, you can safely remove the related LCD code. The transmitter will still function properly.

// Recommendation: If you're not very familiar with Arduino or its coding conventions,
// feel free to upload this code as-is. It is optimized to run reliably, and the latency will remain minimal.

#include <SPI.h>
#include <Wire.h>
#include <RF24.h>
#include <LiquidCrystal_I2C.h>

// === NRF24L01 Configuration ===
#define CE_PIN  9
#define CSN_PIN 10
RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";

// === LCD I2C Setup ===
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Adjust address according to your lcd dislay

// === Pin Definitions ===
#define JOY2_X A0
#define JOY2_Y A1
#define JOY1_X A3
#define JOY1_Y A2
#define POT1   A7
#define POT2   A6
#define BTN1   2
#define BTN2   3
#define TOGGLE1_UP    7
#define TOGGLE1_DOWN  8
#define TOGGLE2_UP    4
#define TOGGLE2_DOWN  5

// === Data Structure to Send ===
struct DataPacket {
  int joy1X, joy1Y;
  int joy2X, joy2Y;
  int pot1, pot2;
  bool btn1, btn2;
  int toggle1, toggle2; // -1, 0, 1
};

int lcdMode = 0;         
int lastMode = -1;       
unsigned long modeSwitchTime = 0;
bool showModeName = false;

int lastToggle2 = -1;    

void setup() {
  Serial.begin(9600);

  // Set pin modes
  pinMode(BTN1, INPUT_PULLUP);
  pinMode(BTN2, INPUT_PULLUP);
  pinMode(TOGGLE1_UP, INPUT_PULLUP);
  pinMode(TOGGLE1_DOWN, INPUT_PULLUP);
  pinMode(TOGGLE2_UP, INPUT_PULLUP);
  pinMode(TOGGLE2_DOWN, INPUT_PULLUP);

  // LCD setup
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Transmitter ON");

  // NRF24L01 setup - **MATCH RECEIVER SETTINGS**
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_HIGH);
  radio.setChannel(100);
  radio.setDataRate(RF24_250KBPS);      // Match receiver's side too
  radio.setAutoAck(true);
  radio.stopListening();                // Transmitter mode

  Serial.println("Transmitter started");
}

void loop() {
  DataPacket data;

  // === Read all inputs ===
  data.joy1X = analogRead(JOY1_X);
  data.joy1Y = 1023 - analogRead(JOY1_Y);  
  data.joy2X = analogRead(JOY2_X);
  data.joy2Y = 1023 - analogRead(JOY2_Y);
  data.pot1  = analogRead(POT1);
  data.pot2  = analogRead(POT2);
  data.btn1  = !digitalRead(BTN1); 
  data.btn2  = !digitalRead(BTN2);
  data.toggle1 = readToggle(TOGGLE1_UP, TOGGLE1_DOWN);
  data.toggle2 = readToggle(TOGGLE2_UP, TOGGLE2_DOWN);

  // === Send data and check status ===
  bool success = radio.write(&data, sizeof(data));
  if (success) {
    Serial.println("Data sent successfully");
  } else {
    Serial.println("Data send FAILED");
  }

  // === LCD mode switching ===
  int currentToggle2 = data.toggle2;

  if (currentToggle2 == 1) {
    lcdMode = 0;  // Mode A
  } else if (currentToggle2 == -1) {
    lcdMode = 1;  // Mode B
  }

  if (currentToggle2 == 0) {
    // Toggle in middle - show default message
    if (lastToggle2 != 0) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Transmitter ON");
      lcd.setCursor(0, 1);
      lcd.print("Toggle For Modes");
    }
    lastToggle2 = 0;
  } else {
    lastToggle2 = currentToggle2;

    // Show mode name for 2 seconds when mode changes
    if (lcdMode != lastMode) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("MODE ");
      lcd.print(lcdMode == 0 ? "JOYSTICK" : "POTS");
      lcd.setCursor(0, 1);
      lcd.print("Toggle to switch");
      modeSwitchTime = millis();
      showModeName = true;
      lastMode = lcdMode;
    }

    // After 2 seconds, display normal info
    if (showModeName) {
      if (millis() - modeSwitchTime > 2000) {
        showModeName = false;
        lcd.clear();
      } else {
        delay(20);
        return; 
      }
    }

    // === Scale analog values 0-10 for display ===
    int j1x = map(data.joy1X, 0, 1023, 0, 10);
    int j1y = map(data.joy1Y, 0, 1023, 0, 10);
    int j2x = map(data.joy2X, 0, 1023, 0, 10);
    int j2y = map(data.joy2Y, 0, 1023, 0, 10);
    int p1  = map(data.pot1, 0, 1023, 0, 10);
    int p2  = map(data.pot2, 0, 1023, 0, 10);

    if (lcdMode == 0) {
      // Mode A: Joysticks + Toggles + Buttons
      lcd.setCursor(0, 0);
      lcd.print("J1:");
      lcd.print(j1x);
      lcd.print(",");
      lcd.print(j1y);
      lcd.print(" J2:");
      lcd.print(j2x);
      lcd.print(",");
      lcd.print(j2y);

      lcd.setCursor(0, 1);
      lcd.print("T1:");
      lcd.print(data.toggle1);
      lcd.print(" T2:");
      lcd.print(data.toggle2);
      lcd.print(" B:");
      lcd.print(data.btn1);
      lcd.print(data.btn2);
      lcd.print("   ");  // Clear any leftover chars
    } else {
      // Mode B: Pots + Buttons + Toggles
      lcd.setCursor(0, 0);
      lcd.print("P1:");
      lcd.print(p1);
      lcd.print(" P2:");
      lcd.print(p2);
      lcd.print("   ");

      lcd.setCursor(0, 1);
      lcd.print("B1:");
      lcd.print(data.btn1);
      lcd.print(" B2:");
      lcd.print(data.btn2);
      lcd.print("    "); 
    }
  }

  delay(50);
}

// Read toggle switches
int readToggle(int upPin, int downPin) {
  bool up = !digitalRead(upPin);
  bool down = !digitalRead(downPin);

  if (up && !down) return 1;
  else if (!up && down) return -1;
  else return 0;
}
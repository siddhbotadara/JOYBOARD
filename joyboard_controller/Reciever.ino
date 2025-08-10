#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Store joystick data from transmitter
int joystick1x;
int joystick1y;
int joystick2x;
int joystick2y;
int pot1,pot2;
int button1,button2;
int toggle1, toggle2;

// === NRF24L01 Setup ===
#define CE_PIN 9
#define CSN_PIN 10
RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";  // Must match transmitter

// === Data Structure ===
struct DataPacket {
  int joy1X, joy1Y;
  int joy2X, joy2Y;
  int pot1, pot2;
  bool btn1, btn2;
  int toggle1, toggle2;
};

DataPacket data;

void setup() {
  Serial.begin(9600);

  // Initialize radio
  if (!radio.begin()) {
    Serial.println("NRF24 not detected!");
    while (1); 
  }

  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_HIGH);         // Match with transmitter
  radio.setChannel(100);                  // Must match transmitter
  radio.setDataRate(RF24_250KBPS);        // Match transmitter
  radio.setAutoAck(true);
  radio.startListening();

}

void loop() {
  if (radio.available()) {
    radio.read(&data, sizeof(data));      // Read the full struct

    joystick1x = data.joy1X;               // Read joystick x (1st stick)
    joystick1y = data.joy1Y;               // Read joystick y (1st stick)

    joystick2x = data.joy2X;               // Read joystick X (2nd stick)
    joystick2y = data.joy2Y;               // Read joystick Y (2nd stick)

    pot1 = data.pot1;                     // Read potentiometer - 1 (left)
    pot2 = data.pot2;                     // Read potentiometer - 2 (right)

    button1 = data.btn1;                  // Read Button - 1 (left)
    button2 = data.btn2;                  // Read Button - 2 (right)

    toggle1 = data.toggle2;               // Read Toggle Switch (left)
    toggle2 = data.toggle1;               // Read Toggle Switch (right)


    // Print (Essential for python to read values)
    Serial.print(joystick1x);
    Serial.print(", ");
    Serial.print(joystick1y);
    Serial.print(", ");
    Serial.print(joystick2x);
    Serial.print(", ");
    Serial.print(joystick2y);
    Serial.print(", ");
    Serial.print(pot1);
    Serial.print(", ");
    Serial.print(pot2);
    Serial.print(", ");
    Serial.print(button1);
    Serial.print(", ");
    Serial.print(button2);
    Serial.print(", ");
    Serial.print(toggle1);
    Serial.print(", ");
    Serial.println(toggle2);
  }

  delay(25); // Small delay for smoother output
}
#include <util/delay.h>
#include <EEPROM.h>
// ISR (PCINT0_vect) pin change interrupt for D8 to D13
// ISR (PCINT2_vect) pin change interrupt for D0 to D7
// EEPROM.read(add);
// EEPROM.write(add, val);
// EEPROM.length();
//if (Serial.available() > 0) {
//    // get incoming byte:
//    inByte = Serial.read();
//    // read first analog input, divide by 4 to make the range 0-255:
//    firstSensor = analogRead(A0) / 4;
//    // delay 10ms to let the ADC recover:
//    delay(10);
//    // read second analog input, divide by 4 to make the range 0-255:
//    secondSensor = analogRead(1) / 4;
//    // read switch, map it to 0 or 255L
//    thirdSensor = map(digitalRead(2), 0, 1, 0, 255);
//    // send sensor values:
//    Serial.write(firstSensor);
//    Serial.write(secondSensor);
//    Serial.write(thirdSensor);
//  }

#define DEBUG
#define CHANNEL1 0x90

volatile bool activeH = false;
volatile bool activeL = false;
volatile bool previousState[10] = {false};
volatile bool currentState[10] = {false};
enum DRUM_POSITION { KICK = 0, SNARE, HIHAT_OPEN, HIHAT_CLOSE, RIDE, CYMBAL1, CYMBAL2, TOM_HIGH, TOM_MID, TOM_LOW };

uint8_t drumNotes[10] = {0};
uint8_t drumVelocities[10] = {0};
uint8_t drumPins[10] = {0};

#ifdef DEBUG
  const uint8_t DRUM_NOTES[10] = { 35, 39, 123, 122, 51, 55, 57, 47, 48, 41 };
  const uint8_t DRUM_VELOCITIES[10] = { 100, 100, 100, 100, 100, 100, 100, 100, 100, 100 };
  const uint8_t DRUM_PINS[10] = { 8, 6, 4, 7, 3, 11, 9, 5, 10, 2 };
#endif
/* TODO:
 * - Support for hihat pedal: if pressed: closed, else open
 * - proper enumeration for DRUM_POSITION - make experience first
 * - EEPROM Fields for customizable IO:
 *   |0x0%| - IOs for defined enum
 *   |0x1%| - Notes  
 *   |0x2%| - Velocities
 *
 */

void loadEepromValues() {
  #ifndef DEBUG
    memcpy(drumNotes, DRUM_NOTES, 10);
    memcpy(drumVelocities, DRUM_VELOCITIES, 10);
    memcpy(drumPins, DRUM_PINS, 10);
  #endif 
}

void storeEepromValue(uint8_t io, uint8_t type, uint8_t note, uint8_t velocity) {
 
}
void pinChangeConfiguration(byte pin) {
    *digitalPinToPCMSK(pin) |= bit (digitalPinToPCMSKbit(pin));  // enable pin
    PCIFR  |= bit (digitalPinToPCICRbit(pin)); // clear any outstanding interrupt
    PCICR  |= bit (digitalPinToPCICRbit(pin)); // enable interrupt for the group
}

uint8_t getDrumPin(uint8_t pinPtr) {
  volatile uint8_t inPtr;
  for(inPtr = 1; inPtr < 11; inPtr++) {
    if (DRUM_PINS[inPtr] == pinPtr) break;
  }
  return inPtr;
}
 
ISR(PCINT0_vect) { // 8-11  
  volatile uint8_t drumPin = 0;
    for(uint8_t iPtr = 8; iPtr <= 11; iPtr++) {
        drumPin = drumPins[iPtr];
        currentState[iPtr] = digitalRead(iPtr);
        if (!currentState[iPtr] && previousState[iPtr]) {
          noteOn(CHANNEL1, drumNotes[drumPin], drumVelocities[drumPin]);
          _delay_us(10);
          noteOn(CHANNEL1, drumNotes[drumPin], 0);
        }
        previousState[iPtr] = currentState[iPtr];
    }
    activeH = false;
}
 
ISR(PCINT2_vect) { // 1 - 7
  volatile uint8_t drumPin = 0;
  if (!activeL) {
    activeL = true;
    for(uint8_t iPtr = 1; iPtr <= 7; iPtr++) {
        drumPin = getDrumPin(iPtr);
        currentState[iPtr] = digitalRead(iPtr);
        if (!currentState[iPtr] && previousState[iPtr]) {
          noteOn(CHANNEL1, drumNotes[drumPin], drumVelocities[drumPin]);
          _delay_us(10);
          noteOn(CHANNEL1, drumNotes[drumPin], 0);
        }
        previousState[iPtr] = currentState[iPtr];
    }
    activeL = false;
  }
}  

void setup() {
  Serial.begin(115200);
  for (uint8_t iPtr = 1; iPtr <= 11; iPtr++) {
    pinMode(iPtr, INPUT);
    // pinChangeConfiguration(iPtr);
    loadEepromValues();
  }
}

void loop() {
  volatile uint8_t drumPin = 0;
    for(uint8_t iPtr = 0; iPtr < 10; iPtr++) {
        drumPin = getDrumPin(iPtr);
        if (!digitalRead(drumPin)) {
        while(!digitalRead(drumPin));
          noteOn(CHANNEL1, drumNotes[iPtr], drumVelocities[iPtr]);
          _delay_us(10);
          noteOn(CHANNEL1, drumNotes[iPtr], 0);
        }
        previousState[iPtr] = currentState[iPtr];
    }
}

// plays a MIDI note. Doesn't check to see that cmd is greater than 127, or that
// data values are less than 127:
void noteOn(uint8_t cmd, uint8_t pitch, uint8_t velocity) {
  Serial.write(cmd);
  Serial.write(pitch);
  Serial.write(velocity);
}

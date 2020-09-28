#include <Debouncer.h>
#include <EEPROM.h>

/* KhomDrums Arduino Project V1.2.1
   April 2020 */

/* Developer Switches: Uncomment desired mode for debugging or initializing */
//#define LOAD_DEFAULT_VALUES // Load constant values instead of EEPROM
//#define PRINT_PADS_PIN_NUMBERS // Print pin number that is connected to a pad that was hit via serial port 

/* Drum type enumeration */
enum DRUM_POSITION { KICK = 0, SNARE, HIHAT, RIDE, CYMBAL1, CYMBAL2, TOM_HIGH, TOM_MID, TOM_LO, HIHAT_PEDAL };

/* Default values */
const uint8_t DRUM_NOTES[10] = { 36, 40, 42, 51, 49, 55, 47, 45, 43, 48};
const uint8_t DRUM_VELOCITIES[10] = { 110, 100, 100, 110, 110,110,110,110,110,110};
const uint8_t DRUM_PINS[10] = { 8, 6, 4, 3, 11, 9, 5, 10, 2, 7 };

/* Kick drum debounce duration */
const uint8_t KICK_DB_DURATION = 0;

/* EEPROM Addresses mapping 
Notes:      |0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09|
Pins:       |0x0A,0x0B,0x0C,0x0D,0x0E,0x0F,0x10,0x11,0x12,0x13|
Velocities  |0x14,0x15,0x16,0x17,0x18,0x19,0x20,0x21,0x22,0x23| */
const uint8_t NOTES_ADDR = 0x00; 
const uint8_t VELOCITIES_ADDR = 0x14;
const uint8_t PINS_ADDR = 0x0A;
/*                */

/* Global Variables */
uint8_t drumNotes[10], drumVelocities[10], drumPins[10];  // MIDI Variables
uint8_t uartBuffer[64];                                   // UART Buffer for collecting and storing MIDI Data
Debouncer kick(DRUM_PINS[KICK], KICK_DB_DURATION);        // Debouncer object for kick drum
volatile bool previousState[9] = {0,0,0,0,0,0,0,0,0};     // Drum pad previous logic states
volatile bool currentState[9] = {0,0,0,0,0,0,0,0,0};      // Drum pad current logic states

/* Store settings in the EEPROM*/
void storeEEPROM() {
  memcpy(drumNotes, uartBuffer, 10);
  memcpy(drumPins, uartBuffer + 10, 10);
  memcpy(drumVelocities, uartBuffer + 20, 10);
  for (uint8_t i = 0; i < 10; i++) EEPROM.write(NOTES_ADDR + i, drumNotes[i]);
  for (uint8_t i = 0; i < 10; i++) EEPROM.write(PINS_ADDR + i, drumPins[i]);
  for (uint8_t i = 0; i < 10; i++) EEPROM.write(VELOCITIES_ADDR + i, drumVelocities[i]);
}

/* Load settings from the EEPROM*/
void loadEEPROM() {
  for (uint8_t i = 0; i < 10; i++) drumNotes[i] = EEPROM.read(NOTES_ADDR + i);
  for (uint8_t i = 0; i < 10; i++) drumPins[i] = EEPROM.read(PINS_ADDR + i);
  for (uint8_t i = 0; i < 10; i++) drumVelocities[i] = EEPROM.read(VELOCITIES_ADDR + i);
}

/* Enter UI programming mode */
void enterProgrammingMode() {
  bool confirmBreak = false;
  uint8_t lineCnt = 0;
  uint8_t charCnt = 0;
  char readChar = 0;
  while(!confirmBreak) {
      if (Serial.available()) {
        uartBuffer[charCnt] = Serial.read();
        if (charCnt >= 29) confirmBreak = true;
        else charCnt++;
      }
  }
  Serial.println("OK");
  storeEEPROM();
}

void initValues() {
  #ifdef LOAD_DEFAULT_VALUES
  memcpy(drumNotes, DRUM_NOTES, 10);
  memcpy(drumVelocities, DRUM_VELOCITIES, 10);
  memcpy(drumPins, DRUM_PINS, 10);
  #else
  loadEEPROM();
  #endif
}

void setup() {
  Serial.begin(115200);
  for (uint8_t i = 0; i < 10; i++) {
    pinMode(i + 2,INPUT);
  }
  #ifdef PRINT_PADS_PIN_NUMBERS
    while(true) { // Infinite debug loop
       for (uint8_t i = 0; i < 10; i++) {
        if (!digitalRead(i + 2)) {
          Serial.print("Pin No: D");
          Serial.print(i + '0'); // Convert number to ASCII character
        }
       }
    }
  #else
  initValues();
  /* Programming mode: If two pedals are pressed while booting - mode is activated */
  if (!digitalRead(drumPins[KICK]) && !digitalRead(drumPins[HIHAT_PEDAL])) enterProgrammingMode();
  #endif
}

/* Play MIDI note function */
void midiOut(enum DRUM_POSITION drumIn) {
  if (drumIn == HIHAT) { // If HI-HAT was hit, there is need to perform a check whether pedal is pressed
    if (!digitalRead(drumPins[HIHAT_PEDAL])) {
      noteOn(0x90, drumNotes[HIHAT_PEDAL], drumVelocities[HIHAT_PEDAL]);
      delay(1);
      noteOn(0x90, drumNotes[HIHAT_PEDAL], 0);
    }
    else {
      noteOn(0x90, drumNotes[HIHAT], drumVelocities[HIHAT]);
      delay(1);
      noteOn(0x90, drumNotes[HIHAT], 0);         
    }
  }
  else { // Regular drum MIDI transmission
    noteOn(0x90, drumNotes[drumIn], drumVelocities[drumIn]);
    delay(1);
    noteOn(0x90, drumNotes[drumIn], 0);
  }
}

void loop() {
    for (uint8_t i = 1; i < 9; i = i + 1) {
      currentState[i] = digitalRead(drumPins[i]);
      if (!currentState[i] && previousState[i]) midiOut(i); // Compare states and detect falling edge
      previousState[i] = currentState[i];
    }
    kick.update(); // Kick drum uses custom debounce algorithm
    if (kick.edge())  if (kick.falling()) midiOut(KICK);
    
}

void noteOn(int cmd, int pitch, int velocity) {
  Serial.write(cmd);
  Serial.write(pitch);
  Serial.write(velocity);
}

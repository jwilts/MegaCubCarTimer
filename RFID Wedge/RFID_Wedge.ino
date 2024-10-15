/*
 * -----------------------------------------------------
 * RC522 Reader Based on an Arduino Pro Micro
 * -----------------------------------------------------
 * Doug Wong 2022
 * 
 * Pin layout used:
 * ------------------------------------
 *             MFRC522      Arduino    
 *             Reader/PCD   Pro Micro  
 * Signal      Pin          Pin        
 * ------------------------------------
 * RST/Reset   RST          18         
 * SPI SS      SDA(SS)      10 
 * SPI MOSI    MOSI         16 
 * SPI MISO    MISO         14 
 * SPI SCK     SCK          15 
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Keyboard.h>

#define RST_PIN         18          // Configurable, see typical pin layout above
#define SS_PIN          10          // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance

void setup() {
	Serial.begin(9600);		        // Initialize serial communications with the PC (Commented out)
	// while (!Serial);		        // Do nothing if no serial port is opened (Removed)
	SPI.begin();			        // Init SPI bus
	mfrc522.PCD_Init();		        // Init MFRC522
	delay(4);				        // Optional delay. Some boards do need more time after init to be ready, see Readme
	Keyboard.begin();               // Init keyboard emulation
	// mfrc522.PCD_DumpVersionToSerial();	// Show details of PCD - MFRC522 Card Reader details (Commented out)
	// Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks...")); (Commented out)
}

void loop() {
	// Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	if (!mfrc522.PICC_IsNewCardPresent()) {
		return;
	}

	// Select one of the cards
	if (!mfrc522.PICC_ReadCardSerial()) {
		return;
	}

	// Now we have the UID, let's convert it to a decimal string
	String uidString = "";
	for (byte i = 0; i < mfrc522.uid.size; i++) {
		uidString += String(mfrc522.uid.uidByte[i]); // Convert each byte to decimal
		if (i < mfrc522.uid.size - 1) {
			uidString += ""; // Add a separator if needed
		}
	}

	// Send the UID string as keyboard input
	Keyboard.print(uidString);

	// Optionally, send a newline character to simulate pressing "Enter"
	Keyboard.write(KEY_RETURN);

	// Halt PICC
	mfrc522.PICC_HaltA();
}

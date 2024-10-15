This is a repository of files for building a ludicriously over engineered and over featured cubcar (Pinewood Derby) timer.

Lots of people have built projects to make the "smallest, simplest, cheapest" pinewood derby / cubcar timers.  I myself have built many of them around arduinos or pi zeros. 
However to run a full cubcar / pinewood derby rally with multiple tracks and kids who are coming and going at different times you need a different solution.

What I have been designing and building over the past few years is really a platform that can be configured for a whole bunch of different scenarios and options.
Here are a few of the features of the solution:
1) New for 2025 is the introduction of a web based registration and administration console.
  - This registration station captures the name of the youth, the car name, what pack they are part of, a picture of the car during initial setup
  - Pit crew can check out the car and record the weight, register it into different weight classes, and confirm that it has been checked out and it meets all the rules.
  - RFID ID tags are used to keep track of the individual youth and cars.  (We put RFID tags on lanyards, but could just as easily affix RFID stickers to the cars)
  - $10 USD sparkfun pro micros and $5.00 USD MFRC-522 readers can plug into any laptops that are doing registration to capture the RFIDs. (Code in the RFID Wedge directory) For a full rally a minimum of 4 laptops are ideal
  - (Primary Regisration, Pit Crew, Central Admin, Youth Lookup -- Youth can lookup for themselves how many races they have run on which track)
  - From the console you can view how many races each youth have done, can update the heat information for individual tracks, run reporting and export data to excel.
  - 
2) New for 2025 is a drag race start.  After cars are loaded on the track a Drag Race Tree counts down and youth need to hit buttons corresponding to their lanes to trigger a start. This makes the race more interactive for the youth. This can be programmed a number of different ways for the start. Timing of the races can either include or exclude the "reaction time" of the youth as well as the car "racing time"
  A) After last youth has hit their button all the lanes trigger simultaneously  (mass start)
OR B) Each lane is triggered individually as youth hit their button.
OR C) Buttons are disabled and a master button triggers all the lanes.

3) RFID Entry: For the timers there are 4 different ways that RFID data can be captured. (Things have evolved over the years)
   A) On the timer board an MFRC522 reader can be mounted directly onto the mainboard.
   OR B) MFRC522 can be wired remotely using CAT5 (Ethernet) cable up to about 45' feet.  A CAT5 connector soldered onto the mainboard of the timer allows for a remote PCB board with an MFRC522 and a single button to be used as an alternative.
   OR C) a Raspberry PICO can be connected wirelessly running sockets protocol which has a whole raft of features on it.  (I2C screen, string of addressable LEDs, Rotary encoder and MFRC522) Code and libraries for that is in RFID Pad folder.
   OR D) the same RFID Wedge that is used for registration stations can be connected via a USB cable through the raspberry Pi that powers the timer. 

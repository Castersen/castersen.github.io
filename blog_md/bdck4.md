# Making an 8 Bit Computer Kit 4 - Output and Control Logic
September 13th, 2023

Time to build the final parts and put everything together! By the end of this everything should be fully functioning!

#### Part 1 - Arduino EEPROM Programmer

We are going to use the Arduino Nano CH340 to program our EEPROM (electronically erasable programmable read-only-memory) which will make it easy to use our display in the next part. Here is the schematic:

<img src="../images/bdck4/arduino-eeprom-programmer-schematic.webp">

And here it is!

<img src="../images/bdck4/arduino-eeprom-programmer.webp" width=500>

I used a piece of paper as recommended in this [video](https://www.youtube.com/watch?v=TGueNvmNNCM) to help with moving the eeprom while not damaging it.

#### How this works and programming the eeprom

Okay, time to talk about serial data transfers and shift registers. Serial data transfer means we are sending the bits one at a time. Because we don't have enough pins on the Arduino Nano we are going to be using shift registers, and sending the bits one at a time to these shift registers. By using shift registers we can use three pins to effectively create as many outputs as we want. These will be used to store and output the address we want to write to, and then we will use the remaining pins to write the data at that address.

The shift registers we are using are the **74HC595** 8-bit shift registers with 3-state output. Which consist of a D flip-flop and several S-R flip flops arranged in such a way that as data comes in it will be shifted down on a clock pulse. This is great because we can use the Arduino Nano to send out data one bit at a time, and then every time it sends a bit it can pulse the clock to store that bit, and shift the other bits down. The Arduino libraries already have a function that does just this. The other nice feature about the 74HC595 is that it has serial-in but parallel out shift registers. So we can send the bits one at a time, and then once we have sent everything we can latch those bits and they will be stored and outputted in parallel. They can also be chained together, since the 74HC595 shift register features an output pin known as the serial output or Q7 pin. When a clock pulse is applied to the shift register the data on this output pin represents the last bit of the shifted data. This serial output can be connected to the input of another 74HC595 shift register, creating a chain of these chips.

Here is how it works: At the bottom I have a D flip-flop connected to the serial out to show how you can chain these chips together.

<img src="../images/bdck4/74hc595.gif">

Now let's take a look at the code, all credit to Ben Eater, here is the [github repository](https://github.com/beneater/eeprom-programmer/tree/master).

This is the code that is responsible for setting the address that we want to read or write to from the EEPROM. The output enable part is used for either reading or writing, if we want to read the contents of the EEPROM at a particular memory address we just set that to true and the EEPROM will output its contents, otherwise we set it to false.

As you can see in the video above we can set the bits, and then once we are done we can pulse the RClk to latch those bits, which is exactly what the last three lines are doing. As a side note the reason for output 0x00 being the result of output enable set to true is because output enable is active low, so setting it to 0 will set it to on.

```cpp
void setAddress(int address, bool outputEnable) {
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80));
  shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, address);

  digitalWrite(SHIFT_LATCH, LOW);
  digitalWrite(SHIFT_LATCH, HIGH);
  digitalWrite(SHIFT_LATCH, LOW);
}
```

From there we can build some convenience functions to read and write to the EEPROM. We first have to set the data pins to INPUT mode, as we will use them to read the outputs from the EEPROM, and then we set the address that we want to read from, and output enable to true. At this point the EEPROM is outputting the contents from that address to the data pins, so we just read and store the contents of those pins and return the data.

```cpp
byte readEEPROM(int address) {
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, INPUT);
  }
  setAddress(address, /*outputEnable*/ true);

  byte data = 0;
  for (int pin = EEPROM_D7; pin >= EEPROM_D0; pin -= 1) {
    data = (data << 1) + digitalRead(pin);
  }
  return data;
}
```

Writing is a bit more tricky. The first step is to set the address we want to write to, and turn output off. Then we set the data pins to output mode. In the second loop we write the data one bit at a time. At this point the EEPROM is pointing to the correct location, and we have the are sending the data that we want to write, now it is time to actually write that data. We set the WE pin low, and then we wait $1\mu s$,the maximum write pulse width, before setting it high. The final delay is to wait for the write cycle to complete before writing the next byte.

```cpp
void writeEEPROM(int address, byte data) {
  setAddress(address, /*outputEnable*/ false);
  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    pinMode(pin, OUTPUT);
  }

  for (int pin = EEPROM_D0; pin <= EEPROM_D7; pin += 1) {
    digitalWrite(pin, data & 1);
    data = data >> 1;
  }
  digitalWrite(WRITE_EN, LOW);
  delayMicroseconds(1);
  digitalWrite(WRITE_EN, HIGH);
  delay(10);
}
```

That's it, and after you can use these functions to write and read the EEPROM, here is a sample output.

```plaintext
Erasing EEPROM................................ done
Programming EEPROM. done
Reading EEPROM
000:  81 cf 92 86 cc a4 a0 8f   80 84 88 e0 b1 c2 b0 b8
010:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
020:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
030:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
040:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
050:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
060:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
070:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
080:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
090:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0a0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0b0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0c0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0d0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0e0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
0f0:  ff ff ff ff ff ff ff ff   ff ff ff ff ff ff ff ff
```

#### Part 2 Output Register

Time to build the output register, by the end of this we will be able to use a display for our numbers. Here is the schematic:

<img src="../images/bdck4/output-schematic.webp">

Here it is! Displaying 180.

<img src="../images/bdck4/output-180.webp">

And then the two's complement -76

<img src="../images/bdck4/output-76.webp">

#### How This Works

The idea is that we want to use a a single EEPROM to control 4 different 7-segment LED displays. The core input of the EEPROM is A0-A7, this is the number we want to output. Those inputs are connected to the **74LS273** octal d-type flip-flop. The inputs are connected to the bus, and the clock is connected to an AND gate, so when the output enable is on and we pulse the clock this will grab and store whatever is on the bus and pass it to the EEPROM.

So that covers input, but how do we select between the different displays, and write the correct data. This is where the 555 timer IC, **74LS107** dual J-K flip-flop, and **74LS139** come into play. The 74LS139 essentially works the same as the address decoder that I went over in the last part. We pass it two inputs, which can be seen as a number between 0-3 and based on those inputs it turns on one of the displays.

The key idea is that we can use the bits from the 74LS107, which we use as a counter in a very similar manner to the PC to decide which part of the input to display. For example, let's look at the number 137.

```plaintext
137
^^^
|||-> Ones place
||--> Tens place
|---> Hundreds place

137 in binary -> 1000 1001 (This is the input to A0-A7 on the EEPROM)

The next two bits A8-A9 decide whether we display the 1, 3, or 7

A8=0, A9=0 means we want to output the 7 (Ones place)
A8=0, A9=1 means we want to output the 3 (Tens place)
A8=1, A9=0 means we want to output the 1 (Hundreds place)

We will look at A8=1, A9=1 in the next part but this is the sign part
here we are only working the positive numbers so this will just mean output 0

Getting these values:

---
Ones place

137 % 10 = 7 -- We can use the modulo operator to get the remainder

---
Tens place

(137 / 10) with integer division yields 13, 13 % 10 yields 3
Which means (137 / 10) % 10 = 3

---
Hundreds place
(137 / 100) with integer division yields 1

```

So in reality we are working with 10 address inputs, or 2^10=1024 inputs. So we will have to encode each digit based on these inputs, here is the code. (The digit inputs A0-A7 are 8 bits, so we have to encode 0-255 for each place)

```cpp
  Serial.println("Programming ones place");
  for (int value = 0; value <= 255; value += 1) {
    writeEEPROM(value, digits[value % 10]);
  }
  Serial.println("Programming tens place");
  for (int value = 0; value <= 255; value += 1) {
    writeEEPROM(value + 256, digits[(value / 10) % 10]);
  }
  Serial.println("Programming hundreds place");
  for (int value = 0; value <= 255; value += 1) {
    writeEEPROM(value + 512, digits[(value / 100) % 10]);
  }
  Serial.println("Programming sign");
  for (int value = 0; value <= 255; value += 1) {
    writeEEPROM(value + 768, 0);
  }
```

Now, what about negative numbers, our ALU is able to subtract so how can we make that work. For negative numbers we use the output of a switch as another address input. If that input is a 1, then the input will be taken as the two's complement. So now if A8=1, A9=1 and A10=1 we want to output a negative sign on the last display if the number is negative. In the ALU section I went over two's complement, our inputs are 8-bits so the range is between -128 and 127. Here is the code.

```cpp
  Serial.println("Programming ones place (twos complement)");
  for (int value = -128; value <= 127; value += 1) {
    writeEEPROM((byte)value + 1024, digits[abs(value) % 10]);
  }
  Serial.println("Programming tens place (twos complement)");
  for (int value = -128; value <= 127; value += 1) {
    writeEEPROM((byte)value + 1280, digits[abs(value / 10) % 10]);
  }
  Serial.println("Programming hundreds place (twos complement)");
  for (int value = -128; value <= 127; value += 1) {
    writeEEPROM((byte)value + 1536, digits[abs(value / 100) % 10]);
  }
  Serial.println("Programming sign (twos complement)");
  for (int value = -128; value <= 127; value += 1) {
    if (value < 0) {
      writeEEPROM((byte)value + 1792, 0x01);
    } else {
      writeEEPROM((byte)value + 1792, 0);
    }
  }
```

So this is how we can decide which display to output, using the dual J-K flip flop as a counter between 0-3, the 74LS139 to take those two bits as input and produce four outputs, and those two bits combined with the switch to control which place value is outputted. The other part is that we use the 555 timer IC to make this switching happen very fast, so in reality there is only one display on at a given time, but we can't tell.

#### Part 3 Bringing it All Together

Time to connect everything to the bus! By the end of this our components will be able to communicate with each other. Here is the final schematic:

<img src="../images/bdck4/join-together-schematic.webp">

Here it is! Here the output of the ALU is being put on the bus and the A register is reading in that input, and the B register is set to 1 so it is just constantly adding 1.

<img src="../images/bdck4/bus-output.gif">

#### Part 4 Control Logic

What we have so far is a fully functioning computer, all of the components work and can communicate. However, we have to set everything manually, in this part we will add the control logic so that we can write programs instead of having to set everything manually. This is the final part of the project! As always, this is the schematic.

<img src="../images/bdck4/control-logic-schematic.webp">

Here it is! Two of the EEPROMs were faulty, so I used the Arduino Nano and shift registers to simulate the two EEPROMs instead.

<img src="../images/bdck4/final-computer.webp">

Here it is multiplying 12 and 13=156

<img src="../images/bdck4/multiply.gif">

Running a simple counter

<img src="../images/bdck4/simple-counter.gif">


#### How This Works

Let's start by taking a look at the Arduino Nano code to simulate the EEPROMs. I removed the debug prints to make it easier to see what is going on. In this first part we define the instruction set, the instructions consist of two parts; the instruction and then the step. The step dictates which microinstructions to run, let's break this down further.

If you look at the first two columns of the data array you will see they are the same, regardless of the instruction. The way to look at the data array is each row is the instruction, and each column is the microinstructions needed to execute that instruction. So the first two columns are fetches and loads. The first microinstruction is MI|CO which means MAR in, program counter out. The program counter keeps track of which instruction we are on so when we place its contents on the bus and store it in the MAR we are getting that instruction.

The next part is RO|II|CE, which is RAM out, instruction register in, counter enable. So in the previous step we selected the right address from the RAM, and now we are outputting those contents on the bus and storing them in the instruction register, or loading the contents on the instruction register. The last part is counter enable, this means we will increment the program counter which makes sense, because after this step we will have loaded the current instruction into the IR, completing this cycle.

Now we have the instruction loaded in the IR it is time to decode and execute that instruction. Let's take a look at LDA for example, the first microinstruction is IO|MI or instruction register out, memory address in. This makes sense, because the instruction is LDA [Memory Address] like 15 for example or 0b1111. The IR only outputs its value portion onto the bus, so the 0b1111 would be on the bus, and MAR would get this value on the next clock cycle, which tells the RAM to get the value in memory. So now the MAR is pointing the RAM at what we want to load in the A register so it's time to complete the cycle with the next step RO|AI. This means RAM out, A register in, or put the contents of RAM (the value we want to store) on the bus, and store those contents in the A register. That's it! So really each instruction contains multiple microinstructions that direct the hardware on what to do.

```cpp
#define NUM_ADDRESS_LINES 8
#define SHIFT_DATA 10
#define SHIFT_CLK 11
#define SHIFT_LATCH 12

#define HLT 0b1000000000000000  // Halt clock
#define MI  0b0100000000000000  // Memory address register in
#define RI  0b0010000000000000  // RAM data in
#define RO  0b0001000000000000  // RAM data out
#define IO  0b0000100000000000  // Instruction register out
#define II  0b0000010000000000  // Instruction register in
#define AI  0b0000001000000000  // A register in
#define AO  0b0000000100000000  // A register out
#define EO  0b0000000010000000  // ALU out
#define SU  0b0000000001000000  // ALU subtract
#define BI  0b0000000000100000  // B register in
#define OI  0b0000000000010000  // Output register in
#define CE  0b0000000000001000  // Program counter enable
#define CO  0b0000000000000100  // Program counter out
#define J   0b0000000000000010  // Jump (program counter in)
#define FI  0b0000000000000001  // Flags in

uint16_t data[] = {
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 0000 - NOP
  MI|CO,  RO|II|CE,  IO|MI,  RO|AI,  0,            0, 0, 0,   // 0001 - LDA
  MI|CO,  RO|II|CE,  IO|MI,  RO|BI,  EO|AI|FI,     0, 0, 0,   // 0010 - ADD
  MI|CO,  RO|II|CE,  IO|MI,  RO|BI,  EO|AI|SU|FI,  0, 0, 0,   // 0011 - SUB
  MI|CO,  RO|II|CE,  IO|MI,  AO|RI,  0,            0, 0, 0,   // 0100 - STA
  MI|CO,  RO|II|CE,  IO|AI,  0,      0,            0, 0, 0,   // 0101 - LDI
  MI|CO,  RO|II|CE,  IO|J,   0,      0,            0, 0, 0,   // 0110 - JMP
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 0111 - JC
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1000 - JZ
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1001
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1010
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1011
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1100
  MI|CO,  RO|II|CE,  0,      0,      0,            0, 0, 0,   // 1101
  MI|CO,  RO|II|CE,  AO|OI,  0,      0,            0, 0, 0,   // 1110 - OUT
  MI|CO,  RO|II|CE,  HLT,    0,      0,            0, 0, 0,   // 1111 - HLT
};
```

In this part I am just doing general setup, setting the address pins to input mode, and the pins responsible for shifting to output mode. Now what about the line previous_address = 255; the idea is that an EEPROM just constantly polls its address lines, performs a lookup and then outputs the value. Using the Arduino Nano the lookup is expensive, because you have to do all of these shift outs and reads, it also isn't necessary to perform a lookup everytime, only when the address changes.

However, when the Arduino Nano is first turned on you do want it to perform a lookup, and so you want the current address to always be different from the previous address. The way this is setup is that only 7 bits are used for the address inputs, three are for the step, and four for the instruction, the last bit is just tied low. But we are using an unsigned eight bit integer to store the address, and because the last bit (MSB) is tied low the value of the address will never be 255, because that would imply all the bits are high. So on startup the current address will never equal the micro instruction. This will make more sense in the next part.

```cpp
uint8_t current_address = 0;
uint8_t previous_address = 255; // Trick to make startup output micro instruction
uint16_t micro_instruction = 0;

void setup() {
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(8, INPUT);
  pinMode(9, INPUT);

  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);

  delay(2000); // Wait for all the pins to be set
}
```

This is the main driver, this is all that is needed to simulate the two EEPROMs. The first loop is just constantly polling the address pins, and using some bit manipulation to store the bits in the correct location. The idea with the bit manipulation is that reading a pin returns a 1 or 0, so do a left bit shift of one on the current address and then do a bitwise or to set the first bit based on the digital read and keep all the other bits the same.

Then I check if the address has changed, at first this will always be true, it also means we need to output a different microinstruction. I do a read one more time, because the pins are read in series. This means we could have an address change in the middle of a read, which means the addresses are different, but we haven't actually read the lower bits. Then I update the previous address, and grab the micro_instruction from the data array. The next two lines are for the conditional jump instructions.

When these instructions were added there were two additional pins that had to be read, which meant that the number of address inputs would have gone to 10, and most of the code would have needed to be changed. What I realized is that the only time we actually need to check the carry flag is when we have a JC instruction at step 010, and if the carry flag is a 1 then I just need to update the microinstruction to perform the jump. This also applies to the JZ instruction. Now that we have the correct microinstruction it is time to write it to the shift registers, and then latch the data to output it.

**Performance:** My main concern with using the Arduino Nano instead of an EEPROM was speed, however, this code was plenty fast and could keep up with the clock on its highest speed no problem. This was great because it meant I didn't have to interact with the port registers directly, and could use the API that is provided. However, if you did use the port registers directly you could effectively eliminate the loop that reads the address again, and significantly increase speed.

```cpp
void loop() {
  for(int i = 0; i < NUM_ADDRESS_LINES; ++i) {
    current_address = (current_address << 1) | digitalRead(2 + i);
  }

  if (current_address != previous_address) {
    // Read address pins one more time in case we were in the middle of a read
    for(int i = 0; i < NUM_ADDRESS_LINES; ++i) {
      current_address = (current_address << 1) | digitalRead(2 + i);
    }
    previous_address = current_address;
    micro_instruction = data[current_address];
    
    // JC instruction at step 010 has an extra bit that needs to be checked
    if(current_address == 58) {
      if(digitalRead(A1) == 1) { micro_instruction = IO|J; } // CF = 1
    }

    // JZ instruction at step 010 has an extra bit that needs to be checked
    if(current_address == 66) {
      if(digitalRead(A0) == 1) { micro_instruction = IO|J; } // JF = 1
    }

    shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, micro_instruction);
    shiftOut(SHIFT_DATA, SHIFT_CLK, MSBFIRST, (micro_instruction >> 8));

    digitalWrite(SHIFT_LATCH, LOW);
    digitalWrite(SHIFT_LATCH, HIGH);
    digitalWrite(SHIFT_LATCH, LOW);
  }
}
```

That completes the project! I had a ton of fun working on this and troubleshooting all of the various issues.
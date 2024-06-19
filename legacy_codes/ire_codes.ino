//these pins can not be changed 2/3 are special pins
int encoderPin1 = 2;
int encoderPin2 = 3;
int angle;

volatile int lastEncoded = 0;
volatile long encoderValue = 0;

long lastencoderValue = 0;

int lastMSB = 0;
int lastLSB = 0;

unsigned long lastMillis = 0;
float RPM = 0.0;
float Angle=0.0;

void setup() 
{
  Serial.begin (9600);

  pinMode(encoderPin1, INPUT);
  pinMode(encoderPin2, INPUT);

  digitalWrite(encoderPin1, HIGH); //turn pullup resistor on
  digitalWrite(encoderPin2, HIGH); //turn pullup resistor on

  //call updateEncoder() when any high/low changed seen
  //on interrupt 0 (pin 2), or interrupt 1 (pin 3)
  attachInterrupt(0, updateEncoder, CHANGE);
  attachInterrupt(1, updateEncoder, CHANGE);
}

void loop()
{
  //Do stuff here

  // calculate RPM every 2000ms (2s)
  if (millis() - lastMillis >= 1000) 
  {
    float rotations = (encoderValue - lastencoderValue) / 4096.0; 
    // calculate number of rotations since last update

    RPM = rotations*60.0; 
    // calculateRPM

    angle=(encoderValue*360)/(4096);
    angle=angle/44;
    angle=angle%360;

    Serial.println(RPM);
    Serial.println(angle);
    Serial.println(encoderValue);
    lastencoderValue = encoderValue;
    lastMillis = millis();
  }
}

void updateEncoder()
{
  int MSB = digitalRead(encoderPin1); 
  //MSB = most significant bit

  int LSB = digitalRead(encoderPin2); 
  //LSB = least significant bit

  int encoded = (MSB << 1) |LSB; 
  //converting the 2 pin value to single number

  int sum = (lastEncoded << 2) | encoded;
  //adding it to the previous encoded value

  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderValue ++;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderValue --;
  
  lastEncoded = encoded; 
  //store this value for next time
}
void setup() {
  Serial.begin(9600);
  
  
  // put your setup code here, to run once:

}

void loop() {
  float wind_vel = analogRead(A2);
  wind_vel = wind_vel*50/1024;
  Serial.println(wind_vel);
  //delay(200);
  
  float wind_dir = analogRead(A1);
  wind_dir = wind_dir*360/1024;
  Serial.println(wind_dir);
  delay(200);
  // put your main code here, to run repeatedly:

}
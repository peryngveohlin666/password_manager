#define notification_pin 10
#define button_pin 3

int val = 0;
int notification = 0;

void button_pressed();

void setup() {
  pinMode(notification_pin, OUTPUT);
  pinMode(button_pin, INPUT);
  
  Serial.begin(9600);

  attachInterrupt(digitalPinToInterrupt(button_pin), button_pressed, RISING);


}

void loop() {

  delay(100);

  
  // digitalWrite(notification_pin, HIGH);

  /*
  Serial.print("Value =");
  Serial.print(val);
  Serial.print("\n");
  */

}


void button_pressed(){
  Serial.print("Button Pressed");
  digitalWrite(notification_pin, LOW);
}

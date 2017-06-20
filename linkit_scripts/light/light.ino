int LED_RED = 2;
int LED_GREEN = 3;
int LED_BLUE = 4;

int R = 0;
int G = 0;
int B = 0;

void setup() {
  Serial.begin(115200);
	Serial1.begin(57600);
	pinMode(LED_RED, OUTPUT);
	pinMode(LED_GREEN, OUTPUT);
	pinMode(LED_BLUE, OUTPUT);
}


int cnt = 254;
int d = HIGH;
void loop() {
	char sIn;
	
	sIn = Serial1.read();

	if (sIn != -1){
		if(sIn == 0){
			R = 0;
			G = 255;
			B = 0;
		}
		else if(sIn == 1){
			R = 255;
			G = 255;
			B = 0;
		}
		else if(sIn == 2){
			R = 255;
			G = 0;
			B = 0;
		}
		else if(sIn == 3){
			R = 255;
			G = 0;
			B = 255;
		}
    Serial.print("R:");
    Serial.print(R);
    Serial.print(" G:");
    Serial.print(G);
    Serial.print(" B:");
    Serial.println(B);
	}
 if(d) d = LOW;
 else d = HIGH;
 digitalWrite(LED_RED, d);
	digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_BLUE, d);
    
}
// R H G L B L seven
// R L G H B L no



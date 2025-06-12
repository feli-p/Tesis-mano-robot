/*
Tesis mano robótica.
F. Castro, S. Fernández
*/
#include <AccelStepper.h>

/* Asignamos un número para referirnos a cada dedo.
  1: Pulgar
  2: Índice
  3: Medio
  4: Anular
  5: Meñique
*/

// Puertos para controlar los motores de los dedos.
// Pulsos y dirección.
#define pul1 2
#define dir1 3

#define pul2 4
#define dir2 5

#define pul3 6
#define dir3 7

#define pul4 8
#define dir4 9

#define pul5 10
#define dir5 11

// Puerto de sensores analógicos
const int flexPin1 = A0;
const int flexPin2 = A1;
const int flexPin3 = A2;

// Valor de los sensores
int valorFlex1;
int valorFlex2;
int valorFlex3;

// Construcción de objetos stepper y del arreglo de pointers para acceder a ellos
AccelStepper stepper1(DRIVER, pul1, dir1);
AccelStepper stepper2(1, pul2, dir2);
AccelStepper stepper3(1, pul3, dir3);
AccelStepper stepper4(1, pul4, dir4);
AccelStepper stepper5(1, pul5, dir5);

AccelStepper *ptrStepper1 = &stepper1;
AccelStepper *ptrStepper2 = &stepper2;
AccelStepper *ptrStepper3 = &stepper3;
AccelStepper *ptrStepper4 = &stepper4;
AccelStepper *ptrStepper5 = &stepper5;


AccelStepper* arrStepper[5] = {ptrStepper1, ptrStepper2, ptrStepper3, ptrStepper4, ptrStepper5};
int flexPin[3] = {flexPin1, flexPin2, flexPin3};

void setup() {
  // Empatar baudaje del puerto serial con el código procesador
  Serial.begin(115200);
  while (!Serial) {
    ;  // Espera a que se conecte el puerto serial.
  }

  // Velocidad angular máxima y aceleración de cada motor. (En pasos)
  stepper1.setMaxSpeed(400);
  stepper1.setAcceleration(150);

  stepper2.setMaxSpeed(400);
  stepper2.setAcceleration(150);
  stepper2.setPinsInverted(true,false,false); // Invertimos la dirección por como fueron alambrados

  stepper3.setMaxSpeed(400);
  stepper3.setAcceleration(150);
  stepper3.setPinsInverted(true,false,false);

  stepper4.setMaxSpeed(400);
  stepper4.setAcceleration(150);

  stepper5.setMaxSpeed(400);
  stepper5.setAcceleration(150);
  stepper5.setPinsInverted(true,false,false);

  //inicializar();
  //Serial.println("Ingresa un comando: →");
}

void loop() {
  if (Serial.available() > 0) {
    String str = Serial.readStringUntil('\n');
    str.trim();
    String commands[6];
    int strCount = 0;

    while (str.length() > 0) {
      int index = str.indexOf(' ');
      if (index == -1) { // No space found
        commands[strCount++] = str;
        //str = ""
        break;
      }
      else {
        commands[strCount++] = str.substring(0, index);
        str = str.substring(index+1);
      }
    }

    /*
    Imprime el arreglo de comandos 
    for (int i = 0; i < strCount; i++) {
      Serial.print(i);
      Serial.print(": \"");
      Serial.print(commands[i]);
      Serial.println("\"");
    }
    */
    
    char cmd = commands[0][0];

    switch (cmd) {
      case 'a':{
        // Terminal de arduino: para probar un motor
        int dedo = commands[1].toInt();
        int ang = commands[2].toInt();
        mueveMotor(arrStepper[dedo-1],ang);
        break;
      }

      case 'c':{
        // Calibrar
        if (commands[1] != ""){
          // Si se indica qué dedo calibrar
          int dedo = commands[1].toInt();
          int minT = commands[2].toInt();
          int maxT = commands[3].toInt();
          calibraDedo(arrStepper[dedo-1], flexPin[dedo-1], dedo, minT, maxT);
        } else {
          // Calibrar todos los dedos
          // Nota: Hasta el momento sólo los primeros tres dedos tienen sensor.
          for (int dedo=1; dedo<4; dedo++){
            calibraDedo(arrStepper[dedo-1], flexPin[dedo-1], dedo, 0.25, 2);
          }
        }
        break;
      }

      case 'm':{
        // Para mover todos los motores a alguna posición
        int a = commands[1].toInt();
        int b = commands[2].toInt();
        int c = commands[3].toInt();
        int d = commands[4].toInt();
        int e = commands[5].toInt();
        mueveTodo(a,b,c,d,e);
        break;
      }

      default:{
        Serial.println("Comando inválido.");
        break;
      }
    }


  }
  stepper1.run();
  stepper2.run();
  stepper3.run();
  stepper4.run();
  stepper5.run();
}

void inicializar(){
  for (int dedo=1; dedo<4; dedo++){
    calibraDedo(arrStepper[dedo-1], flexPin[dedo-1], dedo, 0.25, 2);
  }
}

void mueveMotor(AccelStepper* stepper, int ang){
  // Mueve el motor señalado a la posición absoluta señalada
  stepper->moveTo(ang);
}

void mueveTodo(int a, int b, int c, int d, int e){
  // Mueve todo los dedos a las posiciones señaladas
  stepper1.moveTo(a);
  stepper2.moveTo(b);
  stepper3.moveTo(c);
  stepper4.moveTo(d);
  stepper5.moveTo(e);
}

void calibraDedo(AccelStepper* stepper, int pinSensor, int dedo, float minT, float maxT){
  Serial.print("... Calibrando dedo ");
  Serial.print(dedo);
  Serial.println(" ...");

  float valOld;
  float valNew;
  float test;

  // Abrir dedo hasta que deje de cambiar el sensor
  // Utilizamos esta función para filtrar ruido del sensor
  valNew = promedioVentana(pinSensor);
  do {
    valOld = valNew;
    // Mover motor 10 pasos atrás y seguir hasta que termine
    movBloqueante(stepper,-10);
    valNew = promedioVentana(pinSensor);

  } while(abs(valOld-valNew) > minT);

  // Cerrar dedo hasta que lo empiece a detectar el sensor.
  valOld = promedioVentana(pinSensor);
  do {
    movBloqueante(stepper,5);
    valNew = promedioVentana(pinSensor);
  } while(abs(valOld-valNew) < maxT);

  // Regresamos los pasos adicionales
  movBloqueante(stepper,-5);

  stepper->setCurrentPosition(0);
  Serial.print("Listo dedo ");
  Serial.println(dedo);
}

void movBloqueante(AccelStepper* stepper, int pasos){
  // Mueve el stepper el número de pasos dado y bloquea hasta que termine.
  stepper->move(pasos);
  while(stepper->isRunning()){
    stepper->run();
  }
}

float promedioVentana(int pin){
  // Apesar de que el promedio es sensible a datos atípicos, lo utilizamos para calibrar porque es eficiente en memoria.
  // La media sería un mejor representante del valor del sensor.
  int n = 1000;
  float sum = 0;
  for(int i = 0; i<n; i++){
    sum = sum + analogRead(pin);
  }
  sum = sum/n;
  return sum;
}

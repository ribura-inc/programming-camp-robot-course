#include <Wire.h>

// 超音波センサー
const int SONIC_SENSOR_LEFT_TRIG_PIN  = 50;
const int SONIC_SENSOR_LEFT_ECHO_PIN  = 51;
const int SONIC_SENSOR_RIGHT_TRIG_PIN = 28;
const int SONIC_SENSOR_RIGHT_ECHO_PIN = 29;
const int SONIC_SENSOR_BACK_TRIG_PIN  = 26;
const int SONIC_SENSOR_BACK_ECHO_PIN  = 27;

// ラインセンサー（走行制御には用いないが，点灯のON/OFF切替に使用）
const int LINE_SENSOR_LEFT_PIN       = 10;
const int LINE_SENSOR_RIGHT_PIN      = 11;
const int LINE_SENSOR_FRONT_PIN      = 13;
const int LINE_SENSOR_BACK_LEFT_PIN  = 12;
const int LINE_SENSOR_BACK_RIGHT_PIN = 9;

// スイッチ類
const int START_BUTTON_PIN = 2;    // 起動用ボタン（押されるまで待機）
const int SWITCH_PIN       = 3;    // 切り替えスイッチ

// モータピン
const int RIGHT_MOTOR_PLUS_PIN  = 30;
const int RIGHT_MOTOR_MINUS_PIN = 31;
const int RIGHT_MOTOR_PWM_PIN   = 4;
const int LEFT_MOTOR_PLUS_PIN   = 32;
const int LEFT_MOTOR_MINUS_PIN  = 33;
const int LEFT_MOTOR_PWM_PIN    = 5;
const int BACK_MOTOR_PLUS_PIN   = 36;
const int BACK_MOTOR_MINUS_PIN  = 37;
const int BACK_MOTOR_PWM_PIN    = 6;

// 超音波センサーの測定結果（単位: cm）
volatile int distance_L = 0;
volatile int distance_R = 0;
volatile int distance_B = 0;

// LINEセンサーの値（必要なら取得可能）
bool line_L = false;
bool line_R = false;
bool line_F = false;
bool line_BL = false;
bool line_BR = false;

// ランダム移動用変数
int currentRandomDirection = -1;          // 現在のランダム方向（未設定なら-1）
unsigned long randomDirectionSetTime = 0;   // ランダム方向を設定した時刻
unsigned long randomDirectionDuration = 0;  // その方向を保持する期間（ミリ秒）

//
// setup() - 初期設定
//
void setup() {
  Serial.begin(2000000);
  randomSeed(analogRead(0));  // ランダムシードの初期化

  // モータ制御用ピンの設定
  pinMode(RIGHT_MOTOR_PLUS_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_MINUS_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_PLUS_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_MINUS_PIN, OUTPUT);
  pinMode(BACK_MOTOR_PLUS_PIN, OUTPUT);
  pinMode(BACK_MOTOR_MINUS_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PWM_PIN, OUTPUT);
  pinMode(LEFT_MOTOR_PWM_PIN, OUTPUT);
  pinMode(BACK_MOTOR_PWM_PIN, OUTPUT);

  // 超音波センサー用ピン設定
  pinMode(SONIC_SENSOR_LEFT_TRIG_PIN, OUTPUT);
  pinMode(SONIC_SENSOR_LEFT_ECHO_PIN, INPUT);
  pinMode(SONIC_SENSOR_RIGHT_TRIG_PIN, OUTPUT);
  pinMode(SONIC_SENSOR_RIGHT_ECHO_PIN, INPUT);
  pinMode(SONIC_SENSOR_BACK_TRIG_PIN, OUTPUT);
  pinMode(SONIC_SENSOR_BACK_ECHO_PIN, INPUT);

  // ラインセンサー用ピン設定（点灯用なので保持）
  // pinMode(LINE_SENSOR_LEFT_PIN, INPUT);
  // pinMode(LINE_SENSOR_RIGHT_PIN, INPUT);
  // pinMode(LINE_SENSOR_FRONT_PIN, INPUT);
  // pinMode(LINE_SENSOR_BACK_LEFT_PIN, INPUT);
  // pinMode(LINE_SENSOR_BACK_RIGHT_PIN, INPUT);

  // スイッチ用ピン設定
  pinMode(START_BUTTON_PIN, INPUT);
  pinMode(SWITCH_PIN, INPUT);

  Serial.println("Ready");

  // 起動ボタンが押されるまで待機
  while (digitalRead(START_BUTTON_PIN)) {
    updateSensors();
    printSensors();
    delay(10);
  }
}

//
// loop() - 逃げるロボットのメインループ
//
// void loop() {
//   updateSensors();
//   int command = determineSafeDirection();
//   if (command == -2) {
//     rightSpin(180);
//     delay(200);
//   } else {
//     move(command, 130);
//   }
//   delay(50);
// }

void loop() {
  int randomDir = random(0, 360);
  move(randomDir, 130);
  delay(500);j
  stop();
  delay(1000);
}


//
// determineSafeDirection() - 超音波センサーの値から進行方向を決定
//
// ・各センサーの危険閾値（cm以下なら危険と判断）を設定
// ・危険が検出された場合，そのセンサーの反対方向へ進む
//   ・後方が危険 → 前進（theta = 180）
//   ・左側が危険 → 右へ（theta = 270）※旧来の定義では90°だったが，新仕様に合わせる
//   ・右側が危険 → 左へ（theta = 90）※旧来の定義では270°だったが，新仕様に合わせる
// ・いずれも危険でなければ，ランダム方向に移動（一定期間その値を保持）
//

int determineSafeDirection() {
  const int dangerThreshold = 30;  // 危険と判断する距離（cm）
  bool danger_back  = (distance_B > 0 && distance_B < dangerThreshold);
  bool danger_left  = (distance_L > 0 && distance_L < dangerThreshold);
  bool danger_right = (distance_R > 0 && distance_R < dangerThreshold);

  if (danger_back || danger_left || danger_right) {
    int minDistance = 999;
    int safeDir = 0;
    if (danger_back && distance_B < minDistance) {
      minDistance = distance_B;
      safeDir = 180;  // 後方が危険なら前進
    }
    if (danger_left && distance_L < minDistance) {
      minDistance = distance_L;
      safeDir = 270;  // 左側が危険なら右へ
    }
    if (danger_right && distance_R < minDistance) {
      minDistance = distance_R;
      safeDir = 90;   // 右側が危険なら左へ
    }
    currentRandomDirection = -1;
    return safeDir;
  } else {
    // 一定の確率でその場スピン（特殊コード -2）を返す
    if (random(0, 20) == 0) {
      currentRandomDirection = -1;
      return -2;
    }
    if (currentRandomDirection == -1 || (millis() - randomDirectionSetTime) > randomDirectionDuration) {
      currentRandomDirection = random(0, 360);
      randomDirectionDuration = random(2000, 5000);
      randomDirectionSetTime = millis();
    } else {
      currentRandomDirection = (currentRandomDirection + random(-5, 6)) % 360;
      if (currentRandomDirection < 0)
        currentRandomDirection += 360;
    }
    return currentRandomDirection;
  }
}


//
// updateSensors() - 各センサーの値を取得
//
void updateSensors() {
  getLeftSonicSens();
  getRightSonicSens();
  getBackSonicSens();

  // LINEセンサーの値取得（必要に応じてコメント解除）  
  // line_L = digitalRead(LINE_SENSOR_LEFT_PIN);
  // line_R = digitalRead(LINE_SENSOR_RIGHT_PIN);
  // line_F = digitalRead(LINE_SENSOR_FRONT_PIN);
  // line_BL = digitalRead(LINE_SENSOR_BACK_LEFT_PIN);
  // line_BR = digitalRead(LINE_SENSOR_BACK_RIGHT_PIN);
}

//
// getLeftSonicSens() - 左側センサーから距離を取得（cm）
//
void getLeftSonicSens() {
  digitalWrite(SONIC_SENSOR_LEFT_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(SONIC_SENSOR_LEFT_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(SONIC_SENSOR_LEFT_TRIG_PIN, LOW);
  double duration = pulseIn(SONIC_SENSOR_LEFT_ECHO_PIN, HIGH);
  if (duration > 0) {
    duration = duration / 2;
    distance_L = (int)(duration * 340.0 * 100.0 / 1000000.0);
  }
}

//
// getRightSonicSens() - 右側センサーから距離を取得（cm）
//
void getRightSonicSens() {
  digitalWrite(SONIC_SENSOR_RIGHT_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(SONIC_SENSOR_RIGHT_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(SONIC_SENSOR_RIGHT_TRIG_PIN, LOW);
  double duration = pulseIn(SONIC_SENSOR_RIGHT_ECHO_PIN, HIGH);
  if (duration > 0) {
    duration = duration / 2;
    distance_R = (int)(duration * 340.0 * 100.0 / 1000000.0);
  }
}

//
// getBackSonicSens() - 後方センサーから距離を取得（cm）
//
void getBackSonicSens() {
  digitalWrite(SONIC_SENSOR_BACK_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(SONIC_SENSOR_BACK_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(SONIC_SENSOR_BACK_TRIG_PIN, LOW);
  double duration = pulseIn(SONIC_SENSOR_BACK_ECHO_PIN, HIGH);
  if (duration > 0) {
    duration = duration / 2;
    distance_B = (int)(duration * 340.0 * 100.0 / 1000000.0);
  }
}

//
// printSensors() - 各センサーの値をシリアルモニタに出力
//
void printSensors() {
  Serial.print("Distance_L: ");
  Serial.print(distance_L);
  Serial.print(" cm, Distance_R: ");
  Serial.print(distance_R);
  Serial.print(" cm, Distance_B: ");
  Serial.print(distance_B);
  Serial.print(" cm, ");
  Serial.print("Line: L=");
  Serial.print(line_L);
  Serial.print(" R=");
  Serial.print(line_R);
  Serial.print(" F=");
  Serial.print(line_F);
  Serial.print(" BL=");
  Serial.print(line_BL);
  Serial.print(" BR=");
  Serial.println(line_BR);
}

//
// move() - 指定方向(theta: 度)と速度(spd)で移動
// 0°：後退, 90°：左, 180°：前進, 270°：右
//
void move(int theta, int spd) {
  if (theta == 0) {  // 0° → 後退
    digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_MINUS_PIN, HIGH);
    digitalWrite(LEFT_MOTOR_PLUS_PIN, HIGH);
    digitalWrite(LEFT_MOTOR_MINUS_PIN, LOW);
    digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
    digitalWrite(BACK_MOTOR_MINUS_PIN, LOW);
    analogWrite(LEFT_MOTOR_PWM_PIN, spd);
    analogWrite(RIGHT_MOTOR_PWM_PIN, spd * 0.95);
    analogWrite(BACK_MOTOR_PWM_PIN, spd);
  }
  else if (theta == 90) {  // 90° → 左
    // 以前の270°ブランチ（左向き）を利用
    digitalWrite(RIGHT_MOTOR_PLUS_PIN, HIGH);
    digitalWrite(RIGHT_MOTOR_MINUS_PIN, LOW);
    digitalWrite(LEFT_MOTOR_PLUS_PIN, HIGH);
    digitalWrite(LEFT_MOTOR_MINUS_PIN, LOW);
    digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
    digitalWrite(BACK_MOTOR_MINUS_PIN, HIGH);
    analogWrite(LEFT_MOTOR_PWM_PIN, 150);
    analogWrite(RIGHT_MOTOR_PWM_PIN, 150);
    analogWrite(BACK_MOTOR_PWM_PIN, 250);
  }
  else if (theta == 270) {  // 270° → 右
    // 以前の90°ブランチ（右向き）を利用
    digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
    digitalWrite(RIGHT_MOTOR_MINUS_PIN, HIGH);
    digitalWrite(LEFT_MOTOR_PLUS_PIN, LOW);
    digitalWrite(LEFT_MOTOR_MINUS_PIN, HIGH);
    digitalWrite(BACK_MOTOR_PLUS_PIN, HIGH);
    digitalWrite(BACK_MOTOR_MINUS_PIN, LOW);
    analogWrite(LEFT_MOTOR_PWM_PIN, 150);
    analogWrite(RIGHT_MOTOR_PWM_PIN, 150);
    analogWrite(BACK_MOTOR_PWM_PIN, 250);
  }
  else {  // それ以外の角度（例：前進 180° や斜めなど）
    int internalAngle = (360 - theta) % 360;
    double x_vector = cos(radians(internalAngle - 90));
    double y_vector = sin(radians(internalAngle - 90));

    double right_motor_vector = -(x_vector / 2) + (sqrt(3) * y_vector / 2);
    double left_motor_vector  = -(x_vector / 2) - (sqrt(3) * y_vector / 2);
    double back_motor_vector  = x_vector;

    if (left_motor_vector > 0) {
      digitalWrite(LEFT_MOTOR_PLUS_PIN, HIGH);
      digitalWrite(LEFT_MOTOR_MINUS_PIN, LOW);
    } else if (left_motor_vector < 0) {
      digitalWrite(LEFT_MOTOR_PLUS_PIN, LOW);
      digitalWrite(LEFT_MOTOR_MINUS_PIN, HIGH);
    } else {
      digitalWrite(LEFT_MOTOR_PLUS_PIN, LOW);
      digitalWrite(LEFT_MOTOR_MINUS_PIN, LOW);
    }

    if (right_motor_vector > 0) {
      digitalWrite(RIGHT_MOTOR_PLUS_PIN, HIGH);
      digitalWrite(RIGHT_MOTOR_MINUS_PIN, LOW);
    } else if (right_motor_vector < 0) {
      digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
      digitalWrite(RIGHT_MOTOR_MINUS_PIN, HIGH);
    } else {
      digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
      digitalWrite(RIGHT_MOTOR_MINUS_PIN, LOW);
    }

    if (back_motor_vector > 0) {
      digitalWrite(BACK_MOTOR_PLUS_PIN, HIGH);
      digitalWrite(BACK_MOTOR_MINUS_PIN, LOW);
    } else if (back_motor_vector < 0) {
      digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
      digitalWrite(BACK_MOTOR_MINUS_PIN, HIGH);
    } else {
      digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
      digitalWrite(BACK_MOTOR_MINUS_PIN, LOW);
    }

    analogWrite(LEFT_MOTOR_PWM_PIN, spd * abs(left_motor_vector));
    analogWrite(RIGHT_MOTOR_PWM_PIN, spd * abs(right_motor_vector));
    analogWrite(BACK_MOTOR_PWM_PIN, spd * abs(back_motor_vector));
  }
}


//
// stop() - 全モータ停止
//
void stop() {
  digitalWrite(LEFT_MOTOR_PLUS_PIN, LOW);
  digitalWrite(LEFT_MOTOR_MINUS_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_MINUS_PIN, LOW);
  digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
  digitalWrite(BACK_MOTOR_MINUS_PIN, LOW);
}


//
// rightSpin() - その場で時計回りに回転（全モータを逆回転）
//
void rightSpin(int spd) {
  digitalWrite(LEFT_MOTOR_PLUS_PIN, LOW);
  digitalWrite(LEFT_MOTOR_MINUS_PIN, HIGH);
  digitalWrite(RIGHT_MOTOR_PLUS_PIN, LOW);
  digitalWrite(RIGHT_MOTOR_MINUS_PIN, HIGH);
  digitalWrite(BACK_MOTOR_PLUS_PIN, LOW);
  digitalWrite(BACK_MOTOR_MINUS_PIN, HIGH);
  analogWrite(LEFT_MOTOR_PWM_PIN, spd);
  analogWrite(RIGHT_MOTOR_PWM_PIN, spd);
  analogWrite(BACK_MOTOR_PWM_PIN, spd);
}


/*-----------------------------------------------------------
 以下、使用しないIR・ジャイロセンサー関連のコードはコメントアウトして残す
-----------------------------------------------------------
 
 // IRセンサー用（使用しないのでセットアップ不要）
 // const int KIROBO_IR_SENSOR_LEFT_PIN = 7;
 // const int KIROBO_IR_SENSOR_RIGHT_PIN = 6;
 // volatile bool kirobo_ir_left = false;
 // volatile bool kirobo_ir_right = false;
 //
 // void getLegoIrSens() {
 //   // IRセンサーからのデータ取得処理（不要のためコメントアウト）
 // }
 //
 // void getKiroboIrSens() {
 //   // キロボIRセンサーの読み取り処理（不要のためコメントアウト）
 // }
 //
 // ジャイロセンサー用（使用しないのでセットアップ不要）
 // volatile float gyro;
 // volatile float first_gyro;
 //
 // void getGyroSens() {
 //   // ジャイロセンサーから角度を取得する処理（不要のためコメントアウト）
 // }
-------------------------------------------------------------*/

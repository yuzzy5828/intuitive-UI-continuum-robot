#include <stdint.h>
#include <Wire.h>
#define AS5600_AS5601_DEV_ADDRESS 0x36
#define AS5600_AS5601_REG_RAW_ANGLE 0x0C

#define PIN A0

int bendSensorValue = 0;

// ローパスフィルタ用のパラメータ(0 < alpha < 1)
const float alpha = 0.8;

// フィルタ後の値を保持する変数を静的に定義（グローバルあるいは静的に）
static float angleFiltered = 0.0f;
static float bendAngleFiltered = 0.0f;
static float sensorValueFiltered = 0.0f;

void setup()
{
    // I2C init
    Wire.begin();
    Wire.setClock(400000); // 400kHz

    // Serial init
    Serial.begin(9600);

    // Set analog pin
    pinMode(PIN, INPUT);

    // --- 初期値を設定する ---
    // 実際に一度センサを読み取ってからフィルタ済み変数に代入しておくとよい
    float initAngle = ReadRotateAngle(); 
    float initBend = ReadBendAngle();
    angleFiltered = initAngle;
    bendAngleFiltered = initBend;
    sensorValueFiltered = float(bendSensorValue); // bendSensorValue は ReadBendAngle() 内で更新
}

void loop()
{
    // 生の値を取得
    float angleRaw = ReadRotateAngle();
    float bendAngleRaw = ReadBendAngle();
    float sensor_valueRaw = float(bendSensorValue);

    // --- ローパスフィルタをかける ---
    angleFiltered      = alpha * angleFiltered      + (1.0f - alpha) * angleRaw;
    bendAngleFiltered  = alpha * bendAngleFiltered  + (1.0f - alpha) * bendAngleRaw;
    sensorValueFiltered= alpha * sensorValueFiltered+ (1.0f - alpha) * sensor_valueRaw;

    // Send filtered angle value to PC
    // angleFiltered が “phi”、bendAngleFiltered が “rho” のイメージであれば、
    // 必要に応じて順番など変更してください。
    Serial.print(angleFiltered, 2);
    Serial.print(",");
    Serial.print(bendAngleFiltered, 2);
    Serial.print(",");
    Serial.println(sensorValueFiltered, 2);

    delay(200);
}

float ReadRotateAngle()
{
    // Read RAW_ANGLE value from encoder
    Wire.beginTransmission(AS5600_AS5601_DEV_ADDRESS);
    Wire.write(AS5600_AS5601_REG_RAW_ANGLE);
    Wire.endTransmission(false);
    Wire.requestFrom(AS5600_AS5601_DEV_ADDRESS, 2);
    uint16_t RawAngle = 0;
    RawAngle = ((uint16_t)Wire.read() << 8) & 0x0F00;
    RawAngle |= (uint16_t)Wire.read();
    // Raw angle value (0 ~ 4095) is stored in RawAngle

    // 0〜4095 を 0〜360 度に変換
    float angleDeg = (float)RawAngle * 360.0f / 4096.0f;
    return angleDeg;
}

float ReadBendAngle()
{
    // bendSensorValue を更新
    bendSensorValue = analogRead(PIN);

    // 変換
    float bend_angle = BendToCurvature(bendSensorValue);
    return bend_angle;
}

float BendToCurvature(int value_int)
{
    // if文における「範囲」は && を使う
    float value = float(value_int);
    float bend_value;

    if (value < 630.0) {
        bend_value = 90.0;
    }
    else if (value >= 610.0 && value < 670.0) {
        bend_value = 90.0 * (670.0 - value) / (670.0 - 610.0);
        bend_value = (bend_value / 90.0) * (bend_value / 90.0) * 90.0;
    }
    else if (value >= 670.0 && value < 690.0) {
        bend_value = 0.000001;
    }
    else if (value >= 690.0 && value < 750.0) {
        bend_value = - 90.0 * (690.0 - value) / (690.0 - 750.0);
        bend_value = - (bend_value / 90.0) * (bend_value / 90.0) * 90.0;
    }
    else {  // value >= 750.0
        bend_value = -90.0;
    }

    return bend_value;
}

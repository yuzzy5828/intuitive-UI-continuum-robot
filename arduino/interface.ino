// ここではrhoとphiを送信する
// rhoは曲げセンサの値と曲率半径の関係として記述し，phiはI2Cで読み取った読み取り値をそのまま送信する

#include <stdint.h>
#include <Wire.h>
#define AS5600_AS5601_DEV_ADDRESS 0x36
#define AS5600_AS5601_REG_RAW_ANGLE 0x0C

#define PIN A0

void setup()
{
    // I2C init
    Wire.begin();
    Wire.setClock(400000); // 400kHz

    // Serial init
    Serial.begin(9600);

    // Set analog pin
    pinMode(PIN, INPUT);
}

void loop()
{
    // Read angle value from encoder
    // float angle = ReadRotateAngle();
    float angle = 0;
    // Read bend sensor value
    float bend_angle = ReadBendAngle();

    // Send angle value to PC
    Serial.print(angle, 2);
    Serial.print(",");
    Serial.println(bend_angle, 2);

    delay(10);
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

    RawAngle = (float)RawAngle * 360.0f / 4096.0f;
    return RawAngle;
}

float ReadBendAngle()
{
    // Read bend sensor value
    // Read bend sensor value from analog pin
    int bendSensorValue = analogRead(PIN);

    // Convert bend sensor value to bend angle
    // using the relationships between bendsensorvalue and curvature
    float bend_angle = bendSensorValue;
    // float bend_angle = BendToCurvature();

    return bend_angle;
}

float BendToCurvature()
{
    // describe the relationships between bend and curvature
    // 670-750-830
}
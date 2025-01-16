#include <Arduino.h>

// 定数定義
static const int DIR_PIN[4] = {2, 3, 5, 6};    // DIR ピン
static const int STEP_PIN[4] = {8, 9, 11, 12}; // STEP ピン
static const int STEPS_PER_REV = 200;          // 200 ステップ / 1 回転
static const float STEPS_PER_DEG = STEPS_PER_REV / 360.0f;
static const unsigned long BAUD_RATE = 9600;

// 初期化処理
void setup()
{
    Serial.begin(BAUD_RATE);

    for (int i = 0; i < 4; i++)
    {
        pinMode(DIR_PIN[i], OUTPUT);
        pinMode(STEP_PIN[i], OUTPUT);
        digitalWrite(DIR_PIN[i], LOW);
        digitalWrite(STEP_PIN[i], LOW);
    }
}

// データ分割関数
int split(const String &data, char delimiter, String *dst, int maxCount)
{
    int index = 0;
    String temp = "";

    for (unsigned int i = 0; i < data.length(); i++)
    {
        char c = data.charAt(i);
        if (c == delimiter)
        {
            if (index < maxCount)
            {
                dst[index++] = temp;
                temp = "";
            }
            else
            {
                return -1; // 配列オーバーフロー
            }
        }
        else
        {
            temp += c;
        }
    }

    if (!temp.isEmpty() && index < maxCount)
    {
        dst[index++] = temp;
    }

    return index; // 分割数を返す
}

// コマンド処理
void processCommand(const String *str_angle)
{
    float angles[4];
    int steps[4];
    int max_step = 0;

    // 角度をステップ数に変換
    for (int i = 0; i < 4; i++)
    {
        angles[i] = str_angle[i].toFloat();
        steps[i] = abs(angles[i] * STEPS_PER_DEG);

        // 回転方向設定
        digitalWrite(DIR_PIN[i], angles[i] >= 0 ? LOW : HIGH);

        // 最大ステップ数を計算
        if (steps[i] > max_step)
        {
            max_step = steps[i];
        }
    }

    // モータ制御ループ
    for (long s = 0; s < max_step; s++)
    {
        for (int i = 0; i < 4; i++)
        {
            if (s < steps[i])
            {
                digitalWrite(STEP_PIN[i], HIGH);
                delayMicroseconds(1000); // 適宜調整
                digitalWrite(STEP_PIN[i], LOW);
                delayMicroseconds(1000);
            }
        }
    }
    delay(100); // 安定待ち
}

// メインループ
void loop()
{
    static String inputBuffer;
    static String str_angle[4];

    if (Serial.available() > 0)
    {
        inputBuffer = Serial.readStringUntil('\n');
        if (split(inputBuffer, ',', str_angle, 4) == 4)
        {
            processCommand(str_angle);
        }
        else
        {
            Serial.println("Invalid input format. Expected 4 values.");
        }
    }
}

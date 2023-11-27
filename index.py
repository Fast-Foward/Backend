import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import sqlite3

v = 0  # 속도
vmax = 0  # 최대 속도
Sigpin = 8  # GPIO.BOARD 기준으로 라즈베리 파이 14번 핀에 해당하는 번호 (물리적>인 핀 번호에 맞게 변경)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Sigpin, GPIO.IN)

def measure_speed():
    global v
    T = 0  # 주기
    f = 0.0  # 주파수

    while GPIO.input(Sigpin):
        pass    
    while not GPIO.input(Sigpin):
        pass

    t1 = time.time()
    while GPIO.input(Sigpin):
                pass
    t2 = time.time()

    T = (t2 - t1) * 1e6
    f = 1 / T
    v = int((f * 1e6) / 44.0)

    return v  # 현재 속도 반환

try:
    while True:
        current_speed = measure_speed()
        print(f"현재 속도: {current_speed} km/h")
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
    

#ID 저장
@app.route('/main', methods=['POST'])
def main():
    try:
        # POST 요청에서 'value' 필드의 값을 받음
        received_value = request.json.get('value')

        # 데이터베이스에 받은 값을 'Sports' 테이블의 'value_received' 열에 저장
        cursor.execute("INSERT INTO Sports (Id) VALUES (?)", (received_value,))
        conn.commit()

        return jsonify({"message": "ID값이 성공적으로 저장되었습니다.", "received_value": received_value})

    except Exception as e:
        return jsonify({"ID error": str(e)})



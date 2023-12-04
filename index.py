import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import sqlite3
import pymysql
import asyncio
from flask_cors import CORS

conn = pymysql.connect(host='localhost', user='yeseong', password='qwer1234', db='fastfoward')

GPIO.setwarnings(False)  
GPIO.setmode(GPIO.BOARD)
Sigpin = 8
GPIO.setup(Sigpin, GPIO.IN)

app = Flask(__name__)
CORS(app)

cursor = conn.cursor()

v = 0

# ID 저장
@app.route('/main', methods=['POST'])
def main():
    try:
        cursor = conn.cursor()
        received_value = request.json.get('value')

        # 데이터베이스에서 동일한 Id가 있는지 확인
        select_query = f"SELECT * FROM Sports WHERE Id = '{received_value}'"
        cursor.execute(select_query)
        result = cursor.fetchone()

        if result:
            # 동일한 Id가 이미 존재하는 경우
            return jsonify({"message": "이미 존재하는 Id입니다.", "received_value": received_value}), 200
        else:
            # 동일한 Id가 없는 경우, 새로운 레코드를 삽입
            insert_query = f"INSERT INTO Sports (Id) VALUES ('{received_value}')"
            cursor.execute(insert_query)
            conn.commit()

            return jsonify({"message": "Id값이 성공적으로 저장되었습니다.", "received_value": received_value}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 속도 보냄 // 원래 값과 비교해서 
@app.route('/measure', methods=['POST'])
def measure():
    try:
        cursor = conn.cursor()
        data = request.get_json()
        user_id = data.get('userId')
        sports_name = data.get('sports')
        print(user_id, sports_name)

        # 3초 동안의 최대 속도 측정
        vmax = 0
        start_time = time.time()
        end_time = start_time + 3  # 3초 동안 측정

        while time.time() < end_time:
            current_speed = measure_speed()
            if current_speed > vmax:
                vmax = current_speed
            time.sleep(0.1)
        
        print('maxspeed : ', vmax)
        if vmax > 100:
            return jsonify({"max_speed": 100})

        if (sports_name == 'baseball'):
            cursor.execute("UPDATE Sports SET Baseball = %s WHERE Id = %s and (Baseball IS NULL OR Baseball < %s)", (vmax, user_id, vmax))
        elif (sports_name == 'soccer'):
            cursor.execute("UPDATE Sports SET Soccer = %s WHERE Id = %s and (Soccer IS NULL OR Soccer < %s)", (vmax, user_id, vmax))
        elif (sports_name == 'badminton'):
            cursor.execute("UPDATE Sports SET Badminton = %s WHERE Id = %s and (Badminton IS NULL OR Badminton < %s)", (vmax, user_id, vmax))
        conn.commit()
        
        updated_rows = cursor.rowcount
        print('Number of updated rows:', updated_rows)

        # 프론트엔드에 최대 속도를 응답으로 전송
        return jsonify({"max_speed": vmax})

    except Exception as e:
        return jsonify({"MESR error": str(e)})
    
# rank
@app.route('/rank', methods=['GET'])
def rank():
    try:
        cursor = conn.cursor()
        # 프론트엔드에서 보낸 종목 이름 가져오기
        sports_name = request.args.get('sports')

        cursor.execute(f"SELECT Id, {sports_name} FROM Sports WHERE {sports_name} IS NOT NULL ORDER BY {sports_name} DESC")
        all_speed_data = cursor.fetchall()

        # cursor 객체 닫기
        cursor.close()

        high_to_low_data = [{"Id": row[0], "speed": row[1]} for row in all_speed_data]

        if high_to_low_data:
            response_data = {
                "high_to_low_data": high_to_low_data
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "No speed data available."})


    except Exception as e:
        return jsonify({"Rank error": str(e)}), 500
    
def measure_speed():
    global v
    while GPIO.input(Sigpin) == GPIO.LOW:
        pass

    start_time = time.time()
    while GPIO.input(Sigpin) == GPIO.HIGH:
        pass

    pulse_duraction = time.time() - start_time;
    if pulse_duraction != 0:
        frequency = 1 / pulse_duraction
        v = int((frequency * 1e6) / 44.0/400000000)
        v = round(v, 1)

    print('속도', v)
    return v
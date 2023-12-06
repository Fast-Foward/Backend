import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS

conn = pymysql.connect(host='localhost', user='yeseong', password='qwer1234', db='fastfoward')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
Sigpin = 8
GPIO.setup(Sigpin, GPIO.IN)

app = Flask(__name__)
CORS(app)

cursor = conn.cursor()

# Save ID
@app.route('/main', methods=['POST'])
def main():
    try:
        received_value = request.json.get('value')

        select_query = f"SELECT * FROM Sports WHERE Id = '{received_value}'"
        cursor.execute(select_query)
        result = cursor.fetchone()

        if result:
            return jsonify({"message": "이미 존재하는 Id입니다.", "received_value": received_value}), 200
        else:
            insert_query = f"INSERT INTO Sports (Id) VALUES ('{received_value}')"
            cursor.execute(insert_query)
            conn.commit()

            return jsonify({"message": "Id값이 성공적으로 저장되었습니다.", "received_value": received_value}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Measure speed
@app.route('/measure', methods=['POST'])
def measure():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        sports_name = data.get('sports')

        vmax = 0
        start_time = time.time()
        end_time = start_time + 3

        while time.time() < end_time:
            current_speed = measure_speed()
            if current_speed > vmax:
                vmax = current_speed
            time.sleep(0.1)

        if vmax > 100:
            return jsonify({"max_speed": 100})

        update_query = f"UPDATE Sports SET {sports_name} = %s WHERE Id = %s and ({sports_name} IS NULL OR {sports_name} < %s)"
        cursor.execute(update_query, (vmax, user_id, vmax))
        conn.commit()

        return jsonify({"max_speed": vmax})

    except Exception as e:
        return jsonify({"MESR error": str(e)})

# Get rank
@app.route('/rank', methods=['GET'])
def rank():
    try:
        sports_name = request.args.get('sports')

        cursor.execute(f"SELECT Id, {sports_name} FROM Sports WHERE {sports_name} IS NOT NULL ORDER BY {sports_name} DESC")
        all_speed_data = cursor.fetchall()
        cursor.close()

        high_to_low_data = [{"Id": row[0], "speed": row[1]} for row in all_speed_data]

        if high_to_low_data:
            response_data = {"high_to_low_data": high_to_low_data}
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

    pulse_duration = time.time() - start_time
    if pulse_duration != 0:
        frequency = 1 / pulse_duration
        v = int((frequency * 1e6) / 44.0 / 400000000)
        v = round(v, 1)

    return v

if __name__ == '__main__':
    app.run(host='10.129.57.184', port=5000, debug=True)

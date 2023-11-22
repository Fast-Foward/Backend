import RPi.GPIO as GPIO
import time

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
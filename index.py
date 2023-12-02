import RPi.GPIO as GPIO
import time
import pymysql
from flask import Flask
from flask_cors import CORS

conn = pymysql.connect(host='localhost', user='yeseong', password='qwer1234', db='fastfoward')

GPIO.setwarnings(False)  
GPIO.setmode(GPIO.BOARD)
Sigpin = 8
GPIO.setup(Sigpin, GPIO.IN)

app = Flask(__name__)
CORS(app)

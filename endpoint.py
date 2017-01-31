"""
    This is the endpoint script scaffolding. You need to specify all the endpoint state data you
    wish to report in the report() function. The operations need to be specified by additional
    functions. If you wish for your function to report the result to the endpoint, just return
    a string. The single string parameter that each function takes is the entirety of the string
    received besides the operation name and delimiter. To interpret this string's format is up to
    the function itself.

    After writing an operation function, add its string identifier to the operations dictionary.

    The KEY variable is the single AES key that the node will respond to.

    Calls encrypted with a key different from KEY or containing an invalid operation identifier
    will be completely ignored.
"""
import socket
import Utils as u
import json
import time
import sys

# import netifaces as ni

KEY = 'bonobo'

if sys.platform.startswith("linux"):
    import RPi.GPIO as GPIO

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)

    GPIO.output(26, False)


def blink(arg):
    if sys.platform.startswith("win"):
        return 'not available'

    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)

    GPIO.output(26, False)

    for i in range(0, int(arg)):
        GPIO.output(26, False)
        time.sleep(0.5)
        GPIO.output(26, True)
        time.sleep(0.5)
        GPIO.output(26, False)

    return "done"


def report(arg):
    prepared_data = {
        'description': 'windows dummy endpoint',
        'temperature': '15C',
        'operations': ['report']
    }

    if sys.platform.startswith("linux"):
        import Adafruit_BMP.BMP085 as BMP085
        import Adafruit_DHT
        sensor_a = BMP085.BMP085()
        sensor_b = Adafruit_DHT.DHT22
        pin = 17
        humidity, temperature = Adafruit_DHT.read_retry(sensor_b, pin)
        prepared_data = {
            'description': 'Raspberry Pi, west-side balcony',
            'operations': ['report'],
            'temp_worse': str(round(sensor_a.read_temperature(), 1)) + ' degrees centigrade',
            'pressure': str(round(sensor_a.read_pressure() / 100, 0)) + ' hPa',
            'altitude': str(round(sensor_a.read_altitude(), 0)) + ' m',
            'sealevel_pressure': str(round(sensor_a.read_sealevel_pressure(250) / 100, 0)) + ' hPa',
            'temp': str(round(temperature, 1)) + ' degrees centigrade',
            'humidity': str(round(humidity, 1)) + ' %',
        }

    jsond_data = json.dumps(prepared_data)

    return jsond_data


def do_nothing(arg):
    return None


if __name__ == '__main__':
    OWN_IP = socket.gethostbyname(socket.gethostname())
    OWN_PORT = 9320
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', OWN_PORT))

    recv_string = None

    operations = {
        'report': report,
        'blink': blink
    }

    while True:
        try:
            data, addr = sock.recvfrom(1040)
        except socket.error:
            continue
        recv_string = u.decrypt(data, KEY)
        if recv_string[:5] == 'valid':
            print "received packet: ", recv_string
            print "from: ", addr
            index = recv_string.find('_')
            action_result = operations.get(recv_string[5:index], do_nothing)(recv_string[index+1:])
            if action_result:
                time.sleep(0.5)
                sock.sendto(u.encrypt('valid' + action_result, KEY), addr)

    sock.close()
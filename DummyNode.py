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


def blink(arg):
    return 'not available'


def report(arg):
    prepared_data = {
        'description': 'dummy endpoint',
        'temperature': '15C',
        'operations': operations.keys()
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
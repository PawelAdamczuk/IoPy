"""
    This is the server script. The usage is as follows:
        main.py -k <keys> -o [operation] -h [remote hostname] -a [operation argument]

    You have to specify the AES keys that will be used trying to communicate with the endpoints.
    The keys should be in the "key1 key2 key3 key4..." format.
    The "report" operation is always called and the nodes answering are always listed.
    If no operation is specified, only the report will get called. If no hostname is specified,
    any operation given will be sent to every node. Nodes generally respond neither to unavailable
    calls, nor to packets encrypted with a key different from theirs. For the node set-up
    instructions refer to the endpoint.py description.

    For the report to list nodes with no additional data, all the endpoints need to be in the
    same transport layer broadcast domain. You can query nodes outside of your network by
    specifying their IP addresses. You will have to interpret their JSON-formatted responses by
    yourself, though.
"""

import socket
import Utils as u
import json
import time
import select
import sys
import getopt


# get local ip
if sys.platform.startswith("linux"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("gmail.com", 80))
    OWN_IP = sock.getsockname()[0][:-1]
    sock.close()
else:
    OWN_IP = socket.gethostbyname(socket.gethostname())

SEND_PORTNUM = 9320
RECV_PORT_NUMBER = 9321

# KEYS = ['aardvark', 'bonobo']
KEYS = None
OPERATION = None
OPERATION_ARGUMENT = None

endpoints = []

REMOTE_HOSTNAME = None


class EndPoint:
    def __init__(self, data, address):
        self.data = data
        self.address = address

    def __str__(self):
        result = []
        title = self.data['description'] or self.address[0]
        if title != self.address[0]:
            title += ' [' + self.address[0] + ']'
        result.append(title + '\n')

        info = []
        for key, value in self.data.iteritems():
            if key != 'description' and key != 'operations':
                info.append((key, value))
        if len(info) > 0:
            result.append('  Info:' + '\n')
            for item in info:
                result.append('    ' + item[0] + ': ' + str(item[1]) + '\n')

        result.append('  Operations:' + '\n')
        for item in self.data['operations']:
            result.append('    ' + item + '\n')

        result.append('\n')
        return ''.join(result)

    __repr__ = __str__


def send_call(call_data='report', call_ip=None, call_argument=''):

    # addressing information of the target network (sending to all if no address specified
    if call_ip is None:
        call_ip = OWN_IP[:-1] + '255'

    # initialize a socket
    # SOCK_DGRAM specifies that this is UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # bind the socket so that the source IP and port are correct
    s.bind(('', RECV_PORT_NUMBER))

    call_data_padded = 'valid' + call_data + '_' + call_argument

    # send the packets
    for key in KEYS:
        call_data_encrypted = u.encrypt(call_data_padded, key)
        s.sendto(call_data_encrypted, (call_ip, SEND_PORTNUM))

    s.setblocking(0)

    if call_data == 'report':
        wait_time = 2
    else:
        wait_time = 5

    timeout = time.time() + wait_time

    while True:
        data = ''
        try:
            ready = select.select([s], [], [], wait_time)
            if ready[0]:
                data, addr = s.recvfrom(1040)
                if not data:
                    continue
        except socket.error:
            continue

        if time.time() > timeout:
            break

        for key in KEYS:
            if data:
                recv_string = u.decrypt(data, key)
                if recv_string[0:5] == 'valid':
                    # print "received packet: ", recv_string
                    # print "from: ", addr

                    try:
                        point_data = json.loads(recv_string[5:])
                        print EndPoint(point_data, addr)
                    except ValueError:
                        print addr[0] + ': ' + recv_string[5:]

    # close the socket
    s.close()

if __name__ == '__main__':

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "k:o:h:a:")
    except getopt.GetoptError:
        print "Usage:  main.py -k <keys> -o <operation> -h <remote hostname>"
        sys.exit(2)

    if len(sys.argv) < 2:
        print "Usage:  main.py -k <keys> -o <operation> -h <remote hostname>"
        sys.exit(2)

    for opt, arg in OPTS:
        if opt == '-k':
            KEYS = str(arg).split()
        if opt == '-o':
            OPERATION = str(arg)
        if opt == '-h':
            REMOTE_HOSTNAME = str(arg)
        if opt == '-a':
            OPERATION_ARGUMENT = str(arg)

    if not OPERATION_ARGUMENT:
        OPERATION_ARGUMENT = ''

    if OPERATION:
        send_call(OPERATION, REMOTE_HOSTNAME, OPERATION_ARGUMENT)

    send_call()
    time.sleep(1)
    # if len(endpoints) > 0:
    #     for endpoint in endpoints:
    #         print endpoint
    # else:
    #     print 'No endpoints found!'

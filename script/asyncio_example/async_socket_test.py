import socket
sockets = {}
for i in range(10):
    s = socket.socket()
    sockets[s.fileno()] = s
    s.setblocking(0)
    try:
        s.connect(('www.baidu.com', 80))
    except Exception as e:
        print(e)
        pass

import select
while sockets:
    fds = select.select([], list(sockets.keys()), [])[1]
    for fd in fds:
        s = sockets.pop(fd)
        print("%d connected to %s:%d" % ((fd,) + s.getpeername()))
    print('sockets waiting...', sockets.keys())
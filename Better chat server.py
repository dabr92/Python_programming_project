import socket
import select
import re
from threading import Thread
import mysql.connector

userdict = {"Daniel":["Daniel", "123"]}
connections = []
buffer = 1024
port = 9876
sockdict = {"emptydicts":"causecrashes"}

servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servsock.bind(("192.168.1.53", port))
servsock.listen(99)

connections.append(servsock)

print("Chat server has started on port: {}".format(port))

def sqlconnect():
    global db
    global curs
    db = mysql.connector.connect(
        user="root",
        host="localhost",
        database="logininfo"
    )

    curs = db.cursor()


def broadcast(sock, msg, addr=None, key=None):
    for s in connections:
        if s != sock and s != servsock:
            try:
                s.send("{}: {}".format(addr, msg).encode())
            except:
                del sockdict[sock]
                s.close()
                connections.remove(s)
        elif s == sock:
            try:
                if key == "noyou":
                    s.send("{} {}".format(addr, msg).encode())
                else:
                    s.send("You: {}".format(msg).encode())
            except:
                del sockdict[sock]
                s.close()
                removes = s
    if key == "destroy":
        try:
            connections.remove(removes)
        except:
            pass

while True:
    readsock, writesock, errsock = select.select(connections, [], [])
    for sock in readsock:
        if sock == servsock:
            sockfd, addr = servsock.accept()
            try:
                sqlconnect()
                regorlog = sockfd.recv(1024)
                sockfd.send(regorlog)
                if regorlog.decode() == "login":
                    username = sockfd.recv(1024)
                    sockfd.send("username received".encode())
                    password = sockfd.recv(1024)
                    sql = "select * from person where name='{}' AND password='{}'".format(username.decode(), password.decode())
                    curs.execute(sql)
                    userinfo = (curs.fetchall())
                    if len(userinfo) == 1:
                        if userinfo[0][1] in sockdict.values():
                            sockfd.send("User is already logged in".encode())
                            sockfd.close()
                            db.close()
                        else:
                            sockfd.send("correct".encode())
                            connections.append(sockfd)
                            sockdict[sockfd] = userinfo[0][1]
                            print("Client {}, {} connected".format(userinfo[0][1], addr))
                            db.close()
                            broadcast(sockfd, "connected.\n", sockdict[sockfd], key="noyou")
                    else:
                        sockfd.send("Incorrect username or password".encode())
                        sockfd.close()
                        db.close()
                elif regorlog.decode() == "register":
                    print("do we get here")
                    reguser = sockfd.recv(1024)
                    sockfd.send("username received".encode())
                    regpassword = sockfd.recv(1024)
                    sql = "select * from person where name='{}'".format(reguser.decode())
                    curs.execute(sql)
                    reginfo = curs.fetchall()
                    print(reginfo)
                    if len(reginfo) > 0:
                        sockfd.send("Username is taken".encode())
                        sockfd.close()
                        db.close()
                    else:
                        sqlin = "insert into person set name='{}', password='{}'".format(reguser.decode(), regpassword.decode())
                        curs.execute(sqlin)
                        db.commit()
                        db.close()
                        sockfd.send("Registration complete".encode())
                        sockfd.close()
            except:
                sockfd.close()
                db.close()
        else:
            try:
                data = sock.recv(buffer)
                if data:
                    print("if data")
                    print(data.decode())
                    broadcast(sock, data.decode(), sockdict[sock])
                    continue
            except:
                print("THIS ONE")
                try:
                    copysock = sockdict[sock]
                    print("{} went offline".format(copysock))
                    broadcast(sock, "went offline\n", copysock, key="destroy")
                except:
                    print("WE HERE")
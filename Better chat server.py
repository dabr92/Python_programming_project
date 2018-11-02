import socket
import select
import re
from threading import Thread
import mysql.connector

userdict = {"Daniel":["Daniel", "123"]}
print(userdict["Daniel"][1])
connections = []
buffer = 1024
port = 9876
sockdict = {"emptydicts":"causecrashes"}

servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

'''

def loginprocess(loginsock):
    conn, addr = loginsock.accept()
    print("ACCEPTED")
    try:
        action = conn.recv(1024).decode()
        if action == "login":
            conn.send("login".encode())
            while True:
                try:
                    usename = conn.recv(1024)
                    if usename:
                        conn.send("got it".encode())
                        password = conn.recv(1024)
                        print(usename.decode(), password.decode())
                        sql = "select * from person where name='{}' AND password='{}'".format(usename.decode(), password.decode())
                        curs.execute(sql)
                        logininfo = (curs.fetchall())
                        print(len(logininfo))
                        if len(logininfo) == 1:
                            print("MATCH")
                            conn.send("correct".encode())
                            db.close()
                            conn.close()
                            break
                        else:
                            conn.send("Username or password is incorrect".encode())
                            print("NOT IN KEYS")
                            conn.close()
                    else:
                        print("we broke cuz no data")
                        break
                except:
                    print("we excepted")
                    conn.close()
                    break
        elif action == "register":
            print("register")
            conn.send("register".encode())
            while True:
                try:
                    regname = conn.recv(1024)
                    if regname:
                        conn.send("got it".encode())
                        regpassword = conn.recv(1024)
                        print(regname.decode(), regpassword.decode())
                        sql = "select * from person where name='{}'".format(regname.decode())
                        curs.execute(sql)
                        reginfo = curs.fetchall()
                        print(reginfo)
                        if len(reginfo) > 0:
                            conn.send("Username is taken".encode())
                            conn.close()
                            break
                        else:
                            sqlin = "insert into person set name='{}', password='{}'".format(regname.decode(), regpassword.decode())
                            curs.execute(sqlin)
                            db.commit()
                            db.close()
                            conn.send("Registration complete".encode())
                            conn.close()
                            break
                except:
                    conn.close()
                    break
        else:
            print("something fucking weird happened because we should never get here")
            conn.close()
    except:
        print("DIDNT GET DATA")
        conn.close()

def loginthreader():
    for luls in range(9999):
        loginsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        loginsock.bind(("192.168.1.53", 9877))
        loginsock.listen(99)
        sqlconnect()
        loginprocess(loginsock)


loginthreaderthread = Thread(target=loginthreader)
loginthreaderthread.start()
'''

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
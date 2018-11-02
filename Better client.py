from tkinter import *
import socket
from threading import Thread
from tkinter import ttk
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(("172.20.200.196", 9876))
window = Tk()
window.minsize(650, 440)
window.title("Sickest chat, yo")
login = Tk()
login.title("Chat login")
login.resizable(0, 0)

###CREATE MENUBAR TO RECONNECT AND LOG OUT EZPZ

window.withdraw()
login.withdraw()
isconnected = IntVar()

def showlast():
    textbox.see(END)

def receive():
    while True:
        try:
            msg = sock.recv(1024)
            textbox.config(state="normal")
            textbox.insert(END, "{}".format(msg.decode()))
            textbox.config(state="disabled")
            showlast()
        except:
            textbox.config(state="normal")
            textbox.insert(END, "\nCONNECTION TO SERVER LOST\n")
            textbox.config(state="disabled")
            showlast()
            print("Shits dead yo")
            isconnected.set(0)
            break


def connecttoserver():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.1.53", 9876))
    isconnected.set(1)


def reconnect():
    if isconnected.get() == 0:
        textbox.config(state="normal")
        textbox.insert(END, "\nTRYING TO CONNECT TO SERVER...\n")
        textbox.config(state="disabled")
        try:
            print(username)
            print(password)
            connecttoserver()
            sock.send("login".encode())
            print(sock.recv(1024))
            sock.send(username.encode())
            print(sock.recv(1024))
            sock.send(password.encode())
            sock.recv(1024)
            textbox.config(state="normal")
            textbox.insert(END, "\nCONNECTION REESTABLISHED\n\n")
            textbox.config(state="disabled")
            receivethread = Thread(target=receive, daemon=True)
            receivethread.start()
        except:
            textbox.config(state="normal")
            textbox.insert(END, "\nFAILED TO RECONNECT TO SERVER\n")
            textbox.config(state="disabled")
    else:
         print(sock)


def sendmsg(event):
    msg = entryfield.get(1.0, END)
    if len(msg.strip()) < 1:
        return "break"
    else:
        entryfield.delete(1.0, END)
        sock.send(msg.encode())
        return "break"


def showlogin(event=None):
    global loginsock
    global loginentry
    global passentry
    global loginframe
    global infolabel
    startframe.pack_forget()

    loginframe = Frame(startwindow)

    loginentry = ttk.Entry(loginframe)
    passentry = ttk.Entry(loginframe, show="*")
    uselabel = ttk.Label(loginframe, text="Username")
    passlabel = ttk.Label(loginframe, text="Password")
    padlabel = Label(loginframe)

    loginbutton = ttk.Button(loginframe, text="Login", command=sendlogin)
    quitbutton = ttk.Button(loginframe, text="Back", command=destroyloginwindow)

    padlabel.grid(row=0, column=0)
    quitbutton.grid(row=4, column=0, columnspan=2, padx=5, ipadx=5, sticky=W)
    loginbutton.grid(row=4, column=1, columnspan=2, padx=5, pady=8, ipadx=5, sticky=E)
    loginentry.grid(row=1, column=1, padx=5, pady=5)
    passentry.grid(row=2, column=1, padx=5, pady=1)
    uselabel.grid(row=1, column=0, padx=5)
    passlabel.grid(row=2, column=0, padx=5)
    loginentry.bind("<Return>", sendlogin)
    passentry.bind("<Return>", sendlogin)
    loginbutton.bind("<Return>", sendlogin)
    quitbutton.bind("<Return>", destroyloginwindow)
    loginframe.pack()
    infolabel = Label(loginframe)
    infolabel.grid(row=5, column=0, columnspan=2)


def sendlogin(event=None):
    textbox.config(state="normal")
    textbox.delete(1.0, END)
    textbox.config(state="disabled")
    global username
    global password
    username = loginentry.get()
    password = passentry.get()
    if len(username) < 1 or len(password) < 1:
        infolabel.config(text="Please enter username and password")
    else:
        try:
            connecttoserver()
            sock.send("login".encode())
            print(sock.recv(1024))
            sock.send(username.encode())
            print(sock.recv(1024))
            sock.send(password.encode())
            rightorwrong = sock.recv(1024)
            if rightorwrong.decode() == "correct":
                print("launchwindowmajong")
                window.deiconify()
                startwindow.withdraw()
                loginframe.destroy()
                receivethread = Thread(target=receive, daemon=True)
                receivethread.start()
            else:
                infolabel.config(text=rightorwrong.decode())
                sock.close()
        except:
            infolabel.config(text="Failed to connect to server")
            sock.close()


def register(event=None):
    global registerframe
    global reguserentry
    global regpassentry
    global reglabel
    startframe.pack_forget()

    registerframe = Frame(startwindow)

    reguserentry = ttk.Entry(registerframe)
    regpassentry = ttk.Entry(registerframe, show="*")
    uselabel = ttk.Label(registerframe, text="Username")
    passlabel = ttk.Label(registerframe, text="Password")
    padlabel = Label(registerframe)

    registerbutton = ttk.Button(registerframe, text="Register", command=sendregister)
    quitbutton = ttk.Button(registerframe, text="Back", command=destroyregwindow)

    padlabel.grid(row=0, column=0)
    quitbutton.grid(row=4, column=0, columnspan=2, padx=5, ipadx=5, sticky=W)
    registerbutton.grid(row=4, column=1, columnspan=2, padx=5, pady=8, ipadx=5, sticky=E)
    reguserentry.grid(row=1, column=1, padx=5, pady=5)
    regpassentry.grid(row=2, column=1, padx=5, pady=1)
    uselabel.grid(row=1, column=0, padx=5)
    passlabel.grid(row=2, column=0, padx=5)
    reguserentry.bind("<Return>", sendlogin)
    regpassentry.bind("<Return>", sendlogin)
    registerbutton.bind("<Return>", sendlogin)
    quitbutton.bind("<Return>", destroyregwindow)
    registerframe.pack()
    reglabel = Label(registerframe)
    reglabel.grid(row=5, column=0, columnspan=2)


def sendregister():
    username = reguserentry.get()
    password = regpassentry.get()
    if len(username) < 1 or len(password) < 1:
        reglabel.config(text="Please enter username and password")
    else:
        try:
            connecttoserver()
            sock.send("register".encode())
            print(sock.recv(1024))
            sock.send(username.encode())
            print(sock.recv(1024))
            sock.send(password.encode())
            response = sock.recv(1024).decode()
            reglabel.config(text=response)
            sock.close()
        except:
            reglabel.config(text="Failed to connect to server")
            sock.close()


def logout():
    window.withdraw()
    startframe.pack()
    startwindow.deiconify()
    sock.close()


def destroyloginwindow(event=None):
    loginframe.destroy()
    startframe.pack()


def destroyregwindow(event=None):
    registerframe.destroy()
    startframe.pack()


entryfield = Text(window, height=3, wrap=WORD, padx=7, pady=3)
entryfield.bind("<Return>", sendmsg)
textbox = Text(window, wrap=WORD, padx=7, pady=3)
textbox.pack(expand=TRUE, fill=BOTH)
textbox.config(state="disabled")
entryfield.pack(fill=X)
entryfield.size()

startwindow = Tk()
startwindow.title("Dannyboi's sick chat")
startwindow.resizable(0, 0)
startwindow.minsize(360, 140)
startframe = Frame(startwindow)
startlogin = ttk.Button(startframe, text="Login", command=showlogin)
startregister = ttk.Button(startframe, text="Register", command=register)
startlabel = Label(startframe, text="Welcome to the chat", font=20)
startlogin.grid(row=1, column=1, ipadx=40, ipady=20, padx=10, pady=10)
startregister.grid(row=1, column=0, ipadx=40, ipady=20, padx=10)
startlabel.grid(row=0, column=0, columnspan=2, pady=10)
startframe.pack()

startlogin.bind("<Return>",showlogin)
startregister.bind("<Return>", register)

menus = Menu(window)
connectionmenu = Menu(menus, tearoff=0)
connectionmenu.add_command(label="Reconnect", command=reconnect)
menus.add_cascade(label="Connection", menu=connectionmenu)

accountmenu = Menu(menus, tearoff=0)
accountmenu.add_command(label="Log out", command=logout)
menus.add_cascade(label="Account", menu=accountmenu)

window.config(menu=menus)


startwindow.protocol("WM_DELETE_WINDOW", quit)
window.protocol("WM_DELETE_WINDOW", quit)
window.mainloop()


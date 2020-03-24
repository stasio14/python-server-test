#version 2.4.2
#author: Stanisław Piechota

#necessary libraries
import socket, _thread, sys
#GUI library
from tkinter import *
#sending data that's not string
import json as js
#selecting random values
from random import choice

#class that displays configuration entries
class Config():
    def __init__(self):
        #default values
        self.IP, self.PORT, self.NICK = '127.0.0.1', 4444, 'guest'
        #initialzing window
        win = Tk()

        #creating widgets with canvas
        canvas = Canvas(win, width=400, height=400)
        canvas.pack()

        label1 = Label(win, text="Podaj IP serwera:")
        canvas.create_window(200, 20, window=label1)
        entry1 = Entry(win)
        canvas.create_window(200, 40, window=entry1)

        label2 = Label(win, text="Podaj port:")
        canvas.create_window(200, 60, window=label2)
        entry2 = Entry(win)
        canvas.create_window(200, 80, window=entry2)

        label3 = Label(win, text="Podaj nick:")
        canvas.create_window(200, 100, window=label3)
        entry3 = Entry(win)
        canvas.create_window(200, 120, window=entry3)

        button = Button(win, text="ENTER", bg="green", command=lambda:self.send_data \
        (entry1, entry2, entry3, win, canvas))
        canvas.create_window(200, 160, window=button)

        #main loop of window
        win.mainloop()

    #function of button
    def send_data(self, entry1, entry2, entry3, win, canvas):
        #getting necessary values from entries
        ip = entry1.get()
        #user can type port as string so it's better to make 'try' here
        try:
            port = int(entry2.get())
            nick = entry3.get()
            win.destroy()
            self.IP = ip
            self.PORT = port
            self.NICK = nick
        #in case of error display message
        except ValueError:
            err_label = Label(win, text="Wprowadz poprawny port", fg="red")
            canvas.create_window(200, 180, window=err_label)

#temporary class with configuration data
class Configuration():
    def __init__(self):
        self.IP = "127.0.0.1"
        self.PORT = 4444
        self.NICK = "guest"

#initialzing class
data = Config()
#lists that will be used to set different parameters of messages
#list for sliding messages
messages = []
#dict for settings of colors
users = {}
#setting colors of message (unmade)
colors = ["red", "green", "blue", "yellow", "orange"]

#connecting to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((data.IP, data.PORT))
    print('connected')
except socket.error as e:
    print(str(e))

#table that will be used to check if nick isn't repeating
#that could cause problem with displaying messages
s.send(bytes(data.NICK, 'utf-8'))
validate = s.recv(100).decode("utf-8")
if validate != "ok":
    data.NICK = validate

#nitlializng second window
win = Tk()

#creating blank canvas
canvas = Canvas(win, width=400, height=400)
canvas.pack()

#entry
entry = Entry(win, width=50)
canvas.create_window(160, 15, window=entry)

#example of label for messages
label = Label(win, text='')
canvas.create_window(300, 380, window=label)

#function for sending messages
def sendMsg():
    #to text from entry, there's nick appended
    msg = data.NICK + ": " + entry.get()
    #sending a table with msg and nick for setting different sides
    msg = [msg, data.NICK]
    #because this is table, it's neccessary to use json here
    s.send(bytes(js.dumps(msg), 'utf-8'))
    #after sending message we need to clear up entry
    entry.delete(0, END)

#function for going messages up
def slideMessages():
    #removing message that is on the top of canvas
    canvas.delete(messages[0])
    messages.remove(messages[0])
    #this instructions nedd to be done for every message on the screen
    for mess in messages:
        #getting actual x, y of label
        xcoord, ycoord = canvas.coords(mess)[0], canvas.coords(mess)[1]
        #settings new x, y, based on previous
        canvas.coords(mess, (xcoord, ycoord-20))

#color assgnment to user
#for every user colors won't be the same
def setColor(fr):
    global colors
    # checking if nick isnt in dictionary
    if fr not in users.keys():
        users[fr] = choice(colors)
        print(users[fr])

def getMsg(s):
    # this is dy for messages; it's incrementing for 20 points every time
    pad = -20
    while True:
        # this is situation, where messages is going of Canvas
        #that means it's time to swipe messages with function
        if pad+40 > 360:
            slideMessages()
            #in this situation we don't increment pad
        else:
            pad+=20
        #reciving table with data
        msg=js.loads(s.recv(1024).decode('utf-8'))
        #creating label with default color
        label = Label(win, text=msg[0], fg='black')
        #case when message comes from this user
        if msg[1] == data.NICK:
            messages.append(canvas.create_window(400-3.2*len(msg[0]), 40+pad, window=label))
        #case for every different user
        else:
            #checking if user is dict with colors
            setColor(msg[1])
            #changing value of color
            label['fg'] = users[msg[1]]
            #creating window for this label
            messages.append(canvas.create_window(3.2*len(msg[0]), 40+pad, window=label))

#start new thread for func getMsg
#this allows you to make two thing in one time
#because getMsg is in infinite loop it will be impossible without threading
_thread.start_new_thread(getMsg, (s , ))

# creating button, that's function is sendMsg
button = Button(win, text="ENTER", bg="green", command=sendMsg)
canvas.create_window(360, 15, window=button)

#main loop of second window
win.mainloop()

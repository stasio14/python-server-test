import socket
import threading
import json
from random import randint

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connections = []
clients = []
addNums = [0]

IP = input("Type IP to listen on: ")
PORT = int(input("Type Port: "))
try:
	s.bind((IP, PORT))
except socket.error as e:
	print(str(e))

s.listen()
print("Listening for clients on: " + IP + ":" + str(PORT))

def handler(c, a):
	while True:
		try:
			data = c.recv(1024)
			for connection in connections:
				connection.send(data)
		except:
			print(str(a[0]) + ':' + str(a[1]), 'disconnected')
			connections.remove(c)
			c.close()
			break

def validateClient(c):
	new_nick = c.recv(100).decode('utf-8')
	if new_nick not in clients:
		clients.append(new_nick)
		c.send(bytes("ok", "utf-8"))
	else:
		n = addNums[len(addNums)-1] + 1
		addNums.append(n)
		new_nick += str(n)
		c.send(bytes(new_nick, 'utf-8'))

def run():
	while True:
		c, a = s.accept()
		validateClient(c)
		connections.append(c)
		cThread = threading.Thread(target=handler, args=(c, a))
		cThread.deamon = True
		cThread.start()
		print(str(a[0]) + ':' + str(a[1]), 'connected')
run()

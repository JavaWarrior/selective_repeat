from socket import *
import consts
import util
import threading
import sender
import os
import time
def run_server(filename):
	server_port, window_size, seed, plp = read_params('input/' + filename)
	
	main_socket = socket(AF_INET, SOCK_DGRAM)
	main_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #enable socket reuse
	main_socket.bind(('', server_port))

	print('server up')
	bef_to_add = 0
	while(1):
		msg,to_add = main_socket.recvfrom(consts.pkt_size)
		if(to_add == bef_to_add):
			continue
		bef_to_add = to_add
		threading.Thread(target = connection_handler, args = (msg.decode('utf-8'), window_size, seed, plp, to_add)).start()


def connection_handler(filename, windowsize, seed, plp, to_add):
	connection = socket(AF_INET, SOCK_DGRAM)
	connection.bind(("", 0)) #bind to any available port

	cur_seqnum = 0

	sender_obj = sender.sender(connection, to_add, seed, plp, windowsize)

	if os.path.isfile("server/"+filename):
		file = open("server/"+filename, "rb")
		filesize = os.stat("server/"+filename).st_size
		print("request: " + filename + ", size: " + str(filesize))
		tic = time.time()

		sender_obj.send_buf(str(filesize).encode())
		sender_obj.send_file(file)
		file.close()
		print("Sent successfully in:", util.util_round(time.time() - tic, 1000), "sec")
	else:
		print("requested file not found: "+ filename)
		sender_obj.send_buf(b'0')



def read_params(filename):
	file = open(filename)
	server_port = int(file.readline())
	window_size = int(file.readline())
	seed = int(file.readline())
	plp = float(file.readline())
	return (server_port, window_size, seed, plp)





def read_params(filename):
	file = open(filename)
	server_port = int(file.readline())
	window_size = int(file.readline())
	seed = int(file.readline())
	plp = float(file.readline())
	return (server_port, window_size, seed, plp)


run_server('server_0.00.in')
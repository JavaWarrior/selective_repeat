from socket import *
import consts
import util
import time
import os
import threading
def client_main(filename):	
	serverip, serverport, send_file, windowsize = read_params('input/' + filename)
	client_sock = socket(AF_INET, SOCK_DGRAM)
	client_sock.settimeout(1)
	to_add = (serverip, serverport)
	fsize = 0

	while 1:
		#send request server and wait for response
		print('sending rquest to', to_add)
		client_sock.sendto(send_file.encode(), to_add)
		try:
			fsize, to_add = client_sock.recvfrom(consts.pkt_size)
		except Exception as e:
			#no response in time
			print(e)
			continue
		#response received
		if(fsize):
			break

	fsize = int(util.getdata(fsize).decode('utf-8'))
	#ack the file size
	client_sock.sendto(util.makepkt(b'', 0), to_add)
	cur_seqnum = 1

	if(fsize == 0):
		#file not found
		print(send_file, 'not found by server')
		return 0,0

	packets = {}

	delete_file_first(send_file)
	tic = time.time()

	file = open('client/'+ send_file, 'a+b')

	const_fsize = fsize

	client_sock.settimeout(None)

	while fsize:
		data, to_add = client_sock.recvfrom(consts.pkt_size + consts.header_size)

		if(not util.checkvalid(data)):
			continue #invalid packet
	
		rec_seqnum = util.getseqnum(data)

		if(rec_seqnum < cur_seqnum + windowsize):
			if(rec_seqnum < cur_seqnum):
				# already received just ack
				send_ack(client_sock, rec_seqnum, to_add)
				# client_sock.sendto(util.makepkt(b'', rec_seqnum), to_add) #send ack
				continue

			#we can buffer this file
			found_data = 0
			try:
				found_data = packets[rec_seqnum]
			except Exception as e:
				pass
			#find file in our buffer
			if(not found_data):
				#if not already saved
				packets[rec_seqnum] = util.getdata(data)
			print(cur_seqnum, rec_seqnum)
			send_ack(client_sock, rec_seqnum, to_add)
			# client_sock.sendto(util.makepkt(b'', rec_seqnum), to_add) #send ack anyway
			if(rec_seqnum != cur_seqnum):
				#desired packet didn't come yet
				continue
			found_data = 0
			try:
				found_data = packets[cur_seqnum]
			except Exception as e:
				pass
			while( found_data != 0):
				fsize = fsize - len(found_data)
				file.write(found_data)
				util.print_download_bar(cur_seqnum, const_fsize/consts.pkt_size, 
					suffix = util.util_round(time.time() - tic, 1000))
				cur_seqnum = cur_seqnum + 1
				found_data = 0
				try:
					found_data = packets[cur_seqnum]
				except Exception as e:
					pass
	print('completed in:', time.time() - tic)
	return const_fsize,time.time() - tic






def read_params(filename):
	file = open(filename)
	serverip = file.readline()
	serverport = int(file.readline())
	filename = file.readline()
	windowsize = int(file.readline())
	return (serverip[:-1], serverport, filename[:-1], windowsize)

def delete_file_first(filename):
	try:
		os.remove(filename)
	except OSError:
		pass
def send_ack(sock, seqnum, to_add):
	threading.Thread(target = send_ack_core, args = (sock, seqnum, to_add)).start()
def send_ack_core(sock, seqnum, to_add):
	sock.sendto(util.makepkt(b'', seqnum), to_add)
client_main('client1.in')
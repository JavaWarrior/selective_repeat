import threading
import util
import random
import consts
import time
import sys
class sender:
	start_timeout_val = 0.5

	timeout_val = start_timeout_val

	rtt_exp = start_timeout_val
	rtt_var = 0

	send_base = 0
	next_seqnum = 0
	ssthresh = consts.ssthresh
	cc_state = 0
	cc_ca_counter = 0
	packets = {}

	packets_data = {}
	def __init__(self, connection, to_add, seed, plp, windowsize):
		self.connection = connection
		self.to_add = to_add
		self.plp = plp
		self.windowsize = windowsize
		random.seed(seed)
		threading.Thread(target = self.receiver_kernel, args = ()).start()
		threading.Thread(target = self.sender_core, args = ()).start()

	def send_buf(self, msg):
		seqnum = self.genseqnum()
		self.fire_sender(msg,seqnum)
		while(not self.acked(seqnum)):
			#wait till the packet is acked
			pass

	def send_file(self, file):
		chunk = file.read(consts.pkt_size)
		while(chunk):
			while(self.next_seqnum - self.send_base >= self.windowsize):
				pass #don't send another packet until there's window
			#there's window
			seqnum = self.genseqnum()
			self.fire_sender(chunk, seqnum)
			chunk = file.read(consts.pkt_size)

		while(self.send_base != self.next_seqnum):
			#not all packets acked, wait
			pass

	def receiver_kernel(self):
		while 1:
			recvd, self.to_add = self.connection.recvfrom(consts.header_size + consts.pkt_size)
			if(not util.checkvalid(recvd)):
				continue
			seqnum = util.getseqnum(recvd)
			if(seqnum >= self.send_base):
				if(not self.acked(seqnum)):
					#not acked yet
					self.packets[seqnum]['acked'] = True
					self.update_timeout(time.time() - self.packets[seqnum]['time'])
					self.cc_recvd_ack()
					while(self.acked(self.send_base)):
						self.send_base = self.send_base + 1
						del self.packets_data[self.send_base - 1]

	def sender_core(self):
		while 1:
			for i in range(self.send_base, self.next_seqnum):
				if(not self.packets[i]['acked'] and self.packets[i]['time'] == -1):
					self.packets[i]['time'] = time.time()
					self.sendpkt(util.makepkt(self.packets_data[i], i))
				elif(not self.packets[i]['acked'] and
				 time.time() - self.packets[i]['time'] > self.timeout_val):
					self.packets[i]['time'] = time.time()
					self.sendpkt(util.makepkt(self.packets_data[i], i))
					self.cc_timeout()

	def fire_sender(self, msg, seqnum):
		self.packets_data[seqnum] = msg
		self.packets[seqnum] = {'time': -1, 'acked':False} #add data to send queue
		# t = threading.Timer(self.timeout_val, self.sender_kernel, (msg,seqnum))
		# self.packets[seqnum]['thread'] = t
		# t.start()

	# def sender_kernel(self, msg, seqnum):
	# 	if(not self.acked(seqnum)):
	# 		#packet not acked in time resend
	# 		t = threading.Timer(self.timeout_val, self.sender_kernel, (msg,seqnum))
	# 		self.packets[seqnum]['time'] = time.time()
	# 		self.packets[seqnum]['thread'] = t
	# 		#call for congestion control timeout
	# 		if(self.packets[seqnum]['time'] != -1):
	# 			self.cc_timeout()
	# 		self.sendpkt(util.makepkt(msg, seqnum))
	# 		t.start()

	def sendpkt(self, msg):
		if(random.random() >= self.plp):
			self.connection.sendto(msg, self.to_add)
	def acked(self, seqnum):
		if(seqnum < self.next_seqnum):
			return self.packets[seqnum]['acked']
		return False

	def update_timeout(self,new_rtt):
		# return 0.01	#used when we want to define constant rtt
		self.rtt_exp = 0.875 * self.rtt_exp + 0.125 * new_rtt
		self.rtt_var = 0.75 * self.rtt_var + 0.25 * abs(self.rtt_exp - new_rtt)
		# print('\n', new_rtt, self.rtt_exp, self.rtt_var)
		# debug = open('rtt_debug.csv', 'w')
		# debug.write(str(new_rtt) + ', ' + str(self.rtt_exp) + ', ' + str(self.rtt_var))
		# return max(self.rtt_exp + 4 * self.rtt_var, 0.003)
		self.timeout_val =  self.rtt_exp + 4 * self.rtt_var

	def genseqnum(self):
		self.next_seqnum = self.next_seqnum + 1
		return self.next_seqnum - 1

	def cc_recvd_ack(self):
		if(self.cc_state == 0):
			#slow start
			self.windowsize = self.windowsize + 1			
			if(self.windowsize > self.ssthresh):
				self.cc_state = 1 #congestion avoidance
		elif(self.cc_state == 1):
			self.cc_ca_counter = self.cc_ca_counter + 1
			if(self.cc_ca_counter >= self.windowsize):
				self.cc_ca_counter = 0
				self.windowsize = self.windowsize + 1
		self.print_cc()

	def cc_timeout(self):
		if(self.cc_state == 0):
			#slow start
			self.ssthresh = self.windowsize / 2
			self.windowsize = 1 #tcp tahoe
			# self.windowsize = self.windowsize / 2 #tcp reno
		else:
			#congestion avoidance
			self.ssthresh = self.windowsize / 2
			self.windowsize = 1
			self.cc_state = 0
		self.print_cc()

	def print_cc(self):
		return
		if(self.cc_state == 0):
			print('slow start cwnd:',self.windowsize,'ssthresh:', self.ssthresh)
			# print('slow start cwnd:', self.cc_ca_counter, )
		else:
			print('cong avoid cwnd:',self.windowsize,'ssthresh:', self.ssthresh)

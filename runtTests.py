import client
import server
import statistics
import time
import threading
def run_test(serverfilename):

	files = ['client1.in', 'client2.in', 'client3.in', 'client4.in', 'client5.in']
	thread_server = threading.Thread(target = server.run_server, args = (serverfilename,))
	thread_server.start()

	time.sleep(1)
	out = open('tests/sel_rep_'+serverfilename+'.out', 'w')

	# out.write(serverfilename)
	# out.write('\n')
	
	for file in files:
		times = [0] * 5
		for i in range(5):
			tic = time.time()
			client.client_main(file)			
			times[i] = time.time() - tic
			out.write(str(times[i]))
			out.write(',')
		out.write(str(sum(times) / len(times)))
		out.write(',')
		out.write(str(statistics.stdev(times)))
		out.write('\n')

	server.running = False #turn server off
	time.sleep(1)





run_test('server_0.in')
run_test('server_0.05.in')
run_test('server_0.1.in')
run_test('server_0.3.in')


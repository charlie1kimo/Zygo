import multiprocessing.Process as Process

def f(x):
	print x
	return x
	
if __name__ == "__main__":
	for num in range(10):
		p = Process(target=f, args=(num,))
		p.start()
		p.join()
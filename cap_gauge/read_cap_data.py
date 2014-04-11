import datetime
import numpy
import time
import traceback
from capgauge import Capgauge, CompositeCapgauge


def read_5_mins_6_channels():
	CONFIG_FILE = 'NI_xp_config.txt'
	cap0 = Capgauge(0, name='channel0', ni_config_file=CONFIG_FILE)
	cap1 = Capgauge(1, name='channel1', ni_config_file=CONFIG_FILE)
	cap2 = Capgauge(2, name='channel2', ni_config_file=CONFIG_FILE)
	cap3 = Capgauge(3, name='channel3', ni_config_file=CONFIG_FILE)
	cap4 = Capgauge(4, name='channel4', ni_config_file=CONFIG_FILE)
	cap5 = Capgauge(5, name='channel5', ni_config_file=CONFIG_FILE)

	OUTPUT_FILE = 'capgauge_reading_noise_summary.txt'
	f = open(OUTPUT_FILE, 'w')

	for i in xrange(6):
		cap = eval("cap%d" % i)
		for j in xrange(20):
			print "Running %s trial %d..." % (cap.taskName, j)
			data = cap.samples_data(1000)
			mean = numpy.mean(data)
			std = numpy.std(data)
			peak_to_valley = numpy.max(data) - numpy.min(data)

			f.write(cap.taskName+'_'+str(j)+': \n')
			f.write('Mean: '+repr(mean)+'\n')
			f.write('STD: '+repr(std)+'\n')
			f.write('P-V: '+repr(peak_to_valley)+'\n')
			f.write('\n')
			f.flush()

			time.sleep(15)

	f.close()


def read_6_channel_records_data_point():
	CONFIG_FILE = 'NI_xp_config.txt'
	cap0 = Capgauge(0, name='channel0', ni_config_file=CONFIG_FILE)
	cap1 = Capgauge(1, name='channel1', ni_config_file=CONFIG_FILE)
	cap2 = Capgauge(2, name='channel2', ni_config_file=CONFIG_FILE)
	cap3 = Capgauge(3, name='channel3', ni_config_file=CONFIG_FILE)
	cap4 = Capgauge(4, name='channel4', ni_config_file=CONFIG_FILE)
	cap5 = Capgauge(5, name='channel5', ni_config_file=CONFIG_FILE)

	DATA_POINT_FILE = 'capgauge_data_points_10000_delay_10s_5mins_'
	FILE_EXT = '.txt'
	f0 = open(DATA_POINT_FILE+cap0.taskName+FILE_EXT, 'w')
	f1 = open(DATA_POINT_FILE+cap1.taskName+FILE_EXT, 'w')
	f2 = open(DATA_POINT_FILE+cap2.taskName+FILE_EXT, 'w')
	f3 = open(DATA_POINT_FILE+cap3.taskName+FILE_EXT, 'w')
	f4 = open(DATA_POINT_FILE+cap4.taskName+FILE_EXT, 'w')
	f5 = open(DATA_POINT_FILE+cap5.taskName+FILE_EXT, 'w')
	for c in xrange(6):
		for i in xrange(30):
			print "Running: trial#%d, cap#%d" % (i, c)
			cap = eval("cap%d" % c)
			f = eval("f%d" % c)
			data = cap.samples_data(10000)
			for d in range(len(data)):
				f.write(repr(data[d]))
				if d != len(data)-1:
					f.write(',')
			f.write('\n\n\n')
			f.flush()
			time.sleep(10)

	f0.close()
	f1.close()
	f2.close()
	f3.close()
	f4.close()
	f5.close()


def read_composite_cap_data_point(num, rates):
	DATA_POINT_FILE = 'composite_cap_data_points_1000_rate_1000ss_delay_10s_5mins_'
	FILE_EXT = '.txt'
	config = "NI_composite_capgauge.config"
	cap = CompositeCapgauge(range(6), config)

	f0 = open(DATA_POINT_FILE+'chan0'+FILE_EXT, 'w')
	f1 = open(DATA_POINT_FILE+'chan1'+FILE_EXT, 'w')
	f2 = open(DATA_POINT_FILE+'chan2'+FILE_EXT, 'w')
	f3 = open(DATA_POINT_FILE+'chan3'+FILE_EXT, 'w')
	f4 = open(DATA_POINT_FILE+'chan4'+FILE_EXT, 'w')
	f5 = open(DATA_POINT_FILE+'chan5'+FILE_EXT, 'w')

	for i in xrange(30):
		print "Running: trial#%d..." % i
		data = cap.samplesData(num, rates)
		if cap.isDataInterleaved():
			for d_ind in range(len(data)):
				chan = d_ind % len(cap.channels)
				exec("f"+str(chan)+".write(str(data[d_ind])+',')")

			for chan in xrange(6):
				f = eval("f"+str(chan))
				f.write('\n\n\n')
				f.flush()
			time.sleep(10)
		else:
			raise RuntimeError("ERROR: Data collecting should be set to be interleaved!")

	for chan in xrange(6):
		f = eval("f"+str(chan))
		f.close()


def read_data_stats(intervalInSec, totalTimeInHour, saveRaw=None):
	date = datetime.datetime.now()
	FILE_HEAD = './cap_gauge_data/means_1kHz_sample_rate_%d_secs_interval_%d_hours_total_%s_' % (intervalInSec, totalTimeInHour, date.strftime('%Y.%m.%d'))
	FILE_STD_HEAD = './cap_gauge_data/stds_1kHz_sample_rate_%d_secs_interval_%d_hours_total_%s_' % (intervalInSec, totalTimeInHour, date.strftime('%Y.%m.%d'))
	FILE_PTV_HEAD = './cap_gauge_data/ptvs_1kHz_sample_rate_%d_secs_interval_%d_hours_total_%s_' % (intervalInSec, totalTimeInHour, date.strftime('%Y.%m.%d'))
	FILE_RAW = './cap_gauge_data/raw/raw_data_%s_' % date.strftime('%Y.%m.%d')
	FILE_EXT = '.txt'
	config = "NI_composite_capgauge.config"
	cap = CompositeCapgauge(range(6), config)

	totalNum = int(totalTimeInHour*3600.0 / intervalInSec + 1)
	data_avg = [numpy.zeros(totalNum) for i in xrange(6)]
	data_std = [numpy.zeros(totalNum) for i in xrange(6)]
	data_ptv = [numpy.zeros(totalNum) for i in xrange(6)]

	try:
		for i in xrange(totalNum):
			totalsecs = intervalInSec*i
			hr = int(totalsecs/3600.0)
			totalsecs -= hr*3600.0
			mins = int(totalsecs / 60.0)
			totalsecs -= mins*60.0
			secs = totalsecs
			print "Running: %d/%d...%dh:%dm:%ds..." % (i, totalNum-1, hr, mins, secs)
			(avg_array, std_array, ptv_array, raw_data) = cap.samplesStats(1000, 1000)
			for chan in range(len(avg_array)):
				data_avg[chan][i] = avg_array[chan]
				data_std[chan][i] = std_array[chan]
				data_ptv[chan][i] = ptv_array[chan]
			if saveRaw != None:
				for chan in saveRaw:
					fnameRaw = FILE_RAW + 'chan%d'%chan + '_' + str(i) + FILE_EXT
					numpy.savetxt(fnameRaw, raw_data[chan])

			time.sleep(intervalInSec)
	except Exception, e:
		traceback.print_exc()
	finally:
		for chan in range(len(data_avg)):
			 fname_mean = FILE_HEAD + "chan%d"%chan + FILE_EXT
			 numpy.savetxt(fname_mean, data_avg[chan])
			 fname_std = FILE_STD_HEAD + "chan%d"%chan + FILE_EXT
			 numpy.savetxt(fname_std, data_std[chan])
			 fname_ptv = FILE_PTV_HEAD + "chan%d"%chan + FILE_EXT
			 numpy.savetxt(fname_ptv, data_ptv[chan])


def record_outlier_data_points(monitorIntervalInSec, totalMonitorTimeInHour):
	FILE_HEAD = './cap_gauge_data/outliers_test/chan1_data_'
	FILE_EXT = '.txt'
	config = "NI_composite_capgauge.config"
	cap = CompositeCapgauge([1], config)

	totalNum = int(totalMonitorTimeInHour*3600.0 / monitorIntervalInSec + 1)

	for i in xrange(totalNum):
		totalsecs = monitorIntervalInSec*i
		hr = int(totalsecs/3600.0)
		totalsecs -= hr*3600.0
		mins = int(totalsecs / 60.0)
		totalsecs -= mins*60.0
		secs = totalsecs
		print "Running: %d/%d...%dh:%dm:%ds..." % (i, totalNum-1, hr, mins, secs)
		(avg_array, std_array, ptv_array, raw_data) = cap.samplesStats(1000, 1000)
		if ptv_array[0] / std_array[0] > 7.0:		# outlier data
			fname = FILE_HEAD + str(i) + FILE_EXT
			numpy.savetxt(fname, raw_data)
		time.sleep(monitorIntervalInSec)

		
def record_avg_positions_drift_after_move(monitorIntervalInSec, totalMonitorTimeInHour):
	FILE_HEAD = './cap_gauge_data/drift_data/chan_'
	FILE_EXT = '.txt'
	config = "NI_composite_capgauge.config"
	cap = CompositeCapgauge(range(6), config)

	totalNum = int(totalMonitorTimeInHour*3600.0 / monitorIntervalInSec + 1)

	for i in xrange(totalNum):
		totalsecs = monitorIntervalInSec*i
		hr = int(totalsecs/3600.0)
		totalsecs -= hr*3600.0
		mins = int(totalsecs / 60.0)
		totalsecs -= mins*60.0
		secs = totalsecs
		print "Running: %d/%d...%dh:%dm:%ds..." % (i, totalNum-1, hr, mins, secs)
		try:
			pos_data = cap.readPositions()
			now = time.time()
			for chan in range(len(pos_data)):
				f = open(FILE_HEAD+str(chan)+FILE_EXT, 'a')
				f.write(repr(now)+'\t'+repr(pos_data[chan])+'\n')
				f.close()
		except Exception, e:
			print "ERROR: %d/%d on %dh:%dm:%ds..." % (i, totalNum-1, hr, mins, secs)
			traceback.print_exc
		
		time.sleep(monitorIntervalInSec)
		

		
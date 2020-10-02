from enum import Enum
import re

# TODO
	#command += 'FA30KZ' # Freq Start
	#command += 'FB50KZ' # Freq Stop
	#command += 'FN10KZ'# Freq Increment
	#command += 'AN1MV' # Amplitude Increment (mV)

	#command += 'W1' # Sweep on (0-Off)



class Measurement(Enum):
	AC_VOLT = "M1"
	SINAD = "M2"
	DISTORTION = "M3"
	DC_VOLT = "S1"
	SNR = "S2"
	DISTORTION_LEVEL = "S3"

class Filters(Enum):
	HP_OFF = "H0"
	HP_400 = "H1"
	HP_PSOPH_BP = "H2"
	LP_OFF = "L0"
	LP_30KHZ = "L1"
	LP_80KHZ = "L2"

class Trigger(Enum):
	TRIG_FREERUN = "T0"
	TRIG_HOLD = "T1"
	TRIG_SETTLING = "T3"

class HP8903(Object):
	gpib = None

	def __init__(self, gpib):
		self.gpib = gpib

	def read_left(self):
		return parse_exp_notation(self.gpib.send_with_return("RL"))

	def read_right(self):
		return parse_exp_notation(self.gpib.send_with_return("RR"))

	def generic_sweep(self, init_command, start, end, steps_per_octave, conversion_function, persistor):
		self.gpib.send_command_with_return_eoi(init_command)

		increase_factor = 2**(1/steps_per_octave)

		if (end < start): # Swap parameters if provided in the wrong direction
			(start, end) = (end, start)

		current = start

		while current < end:
			self.gpib.send_with_return(conversion_function(current))

			persistor(current, self)
			current *= increase_factor

	def measure_preset_freq_level(self, start_freq, max_freq, steps_per_octave, amplitude, persistor):
		init_command = hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.AC_VOLT) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

	def measure_preset_thd_level(self, start_ampl, max_ampl, steps_per_octave, frequency, persistor):
		init_command = hp8903_freq(frequency) + hp8903_ampl(start_ampl) + hp8903_meas(Measurement.DISTORTION) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_ampl, max_ampl, steps_per_octave, hp8903_ampl, persistor)

	def measure_preset_thd_freq(self, start_freq, max_freq, steps_per_octave, amplitude, persistor):
		init_command =  hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.DISTORTION) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

	def measure_thdlv_level(self, start_ampl, max_ampl, steps_per_octave, frequency, persistor):
		init_command =  hp8903_freq(frequency) + hp8903_ampl(start_ampl) + hp8903_meas(Measurement.DISTORTION_LEVEL) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_ampl, max_ampl, steps_per_octave, hp8903_ampl, persistor)

	def measure_thdlv_freq(self, start_freq, max_freq, steps_per_octave, amplitude, persistor):
		init_command =  hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.DISTORTION_LEVEL) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

	def measure_snr_level(self, start_ampl, max_ampl, steps_per_octave, frequency, persistor):
		init_command =  hp8903_freq(frequency) + hp8903_ampl(start_ampl) + hp8903_meas(Measurement.SNR) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
		self.generic_sweep(init_command, start_ampl, max_ampl, steps_per_octave, hp8903_ampl, persistor)

def parse_exp_notation(string):
	#return string
	pattern = re.compile(r"""([+-][0-9]+)E([+-][0-9]+)""", re.VERBOSE)
	
	match = pattern.match(string)
	if match is not None:
		mantisse = float(match.group(1))
		exponent = float(match.group(2))

		return (mantisse * (10 ** exponent))
	else:
		return None

def hp8903_freq(freq_in_hz):
	# KZ for Kilohertz
	return "FR" + str(int(freq_in_hz)) + "HZ"

def hp8903_ampl(ampl_in_v):
	# MV for Millivolts
	return "AP" + str(int(ampl_in_v * 1000)) + "E-3VL"

def hp8903_meas(measurement):
	return measurement.value

def hp8903_filter(filter):
	return filter.value

def hp8903_trigger(trigger):
	return trigger.value

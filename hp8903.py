from enum import Enum


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




def parse_exp_notation(string):
	#return string.decode(ENCODING)
	pattern = re.compile(r"""([+-][0-9]+)E([+-][0-9]+)""", re.VERBOSE)
	
	match = pattern.match(string.decode(ENCODING))
	if match is not None:
		mantisse = float(match.group(1))
		exponent = float(match.group(2))

		return (mantisse * (10 ** exponent))
	else:
		return None


def hp8903_freq(freq_in_hz):
	# KZ for Kilohertz
	return f"FR{freq_in_hz}HZ"

def hp8903_ampl(ampl_in_v):
	# MV for Millivolts
	return f"AP{ampl_in_v}VL"

def hp8903_meas(measurement):
	return measurement.value

def hp8903_filter(filter):
	return filter.value

def hp8903_trigger(trigger):
	return trigger.value
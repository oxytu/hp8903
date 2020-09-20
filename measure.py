import serial
import yaml
import re

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

parity = serial.PARITY_NONE
rtscts = 1

def parse_exp_notation(string):
	#return string.decode("iso8859-1")
	pattern = re.compile(r"""([+-][0-9]+)E([+-][0-9]+)""", re.VERBOSE)
	
	match = pattern.match(string.decode("iso8859-1"))
	if match is not None:
		mantisse = float(match.group(1))
		exponent = float(match.group(2))

		return (mantisse * (10 ** exponent))
	else:
		return None

with serial.Serial('COM2', config['baudrate'], timeout=2, parity=parity, rtscts=rtscts) as gpib:

	gpib.write(b'++mode 1\n')
	gpib.write(b'++auto 1\n')
	gpib.write(b'++addr\n')
	print(gpib.read(10).decode("iso8859-1"))
	gpib.write(b'++ifc\n')
	gpib.write(b'++eoi 0\n')
	gpib.write(b'++clr\n')

	#gpib.write(b'++auto 0\n*idn?\n++read eoi\n')
	#print(gpib.read(10).decode("iso8859-1"))
	#gpib.write(b'++auto 1\n')

	#command = "AU" # Automatic Operation
	#command = "T1"
	command = ""

	command += "FR30KZ"

	#command += 'FA30KZ' # Freq Start
	#command += 'FB50KZ' # Freq Stop
	#command += 'FN10KZ'# Freq Increment

	command += 'AP1VL' # AMplitude
	#command += 'AN1MV' # Amplitude Increment (mV)

	#command += 'W1' # Sweep on (0-Off)

	command += 'M1' # Measure AC Level (M2 SINAD - M3 DIST - S1 DC - S2 SNR - S3 DIST LVL)
	command += 'H0' # Filters Off (H1 400Hz HP, H2 Psoph BP)
	command += 'L0' # Filters Off (L1 30kHz LP, L2 80kHz LP)

	#command += 'T1' # Trigger Immediate (T1 - Hold, T0 - Free Frun, T3 - Trigger with Setting)

	print(command)
	gpib.write((command + '\n').encode("iso8859-1"))
	gpib.write(b'++read eoi\n')
	gpib.readline()

	start_freq = 20
	max_freq = 40000
	steps_per_octave = 12
	increase_factor = 2**(1/steps_per_octave)

	current_freq = start_freq

	while current_freq < max_freq:
		gpib.write(("FR" + str(current_freq) + "HZ\n").encode("iso8859-1"))
		#gpib.write(b'++trg\n') # Clear Key - Trigger Measurement
		#gpib.write(b'++spoll\n')
		gpib.readline()

		gpib.write(b'RL\n')
		answerleft = parse_exp_notation(gpib.readline())

		gpib.write(b'RR\n')
		answerright = parse_exp_notation(gpib.readline())

		print(str(answerleft) + ";" + str(answerright))
		current_freq *= increase_factor
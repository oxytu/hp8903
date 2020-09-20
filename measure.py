import serial
import yaml
import argparse
from hp8903 import *

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

parity = serial.PARITY_NONE
rtscts = 1
ENCODING = "iso8859-1"
DEBUG = False

def gpib_send(gpib, string):
	if DEBUG:
		print(">>>" + string)
	gpib.write((string + "\n").encode(ENCODING))

def initialize_prologix(gpib, remote_address):
	gpib_send(gpib, "++mode 1")
	gpib_send(gpib, "++auto 1")
	#gpib_send(gpib, "++read_tmo_ms 3000")
	gpib_send(gpib, "++addr " + str(remote_address))
	gpib_send(gpib, "++ifc")
	gpib_send(gpib, "++eoi 0")
	#gpib_send(gpib, "++eos 0")
	gpib_send(gpib, "++clr")

def persist_meas_result(gpib):
	gpib_send(gpib, "RL")
	answerleft = parse_exp_notation(gpib.readline().decode(ENCODING))

	gpib_send(gpib, "RR")
	answerright = parse_exp_notation(gpib.readline().decode(ENCODING))

	print(str(answerleft) + ";" + str(answerright))

def generic_sweep_measurement(gpib, init_command, start, end, steps_per_octave, conversion_function, persistor):
	gpib_send(gpib, init_command)
	gpib_send(gpib, "++read eoi")
	gpib.readline()

	increase_factor = 2**(1/steps_per_octave)

	if (end < start): # Swap parameters if provided in the wrong direction
		(start, end) = (end, start)

	current = start

	while current < end:
		gpib_send(gpib, conversion_function(current))
		gpib.readline()

		persistor(gpib)
		current *= increase_factor

def measure_freq_level(gpib, start_freq, max_freq, steps_per_octave, amplitude, persistor):
	init_command = hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.AC_VOLT) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_HOLD)
	generic_sweep_measurement(gpib, init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

def measure_thd_level(gpib, start_ampl, max_ampl, steps_per_octave, frequency, persistor):
	init_command = hp8903_freq(frequency) + hp8903_ampl(start_ampl) + hp8903_meas(Measurement.DISTORTION) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_HOLD)
	generic_sweep_measurement(gpib, init_command, start_ampl, max_ampl, steps_per_octave, hp8903_ampl, persistor)

def init_argparse() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		usage="%(prog)s [options]",
		description="Creates a measurement via the HP8903 and outputs the results to STDOUT"
	)
	parser.add_argument(
		"-v", "--verbose",
		action='store_true',
		default=False
	)
	parser.add_argument(
		"-m", "--measure",
		action='store',
		default="LVL_FREQ",
		choices=["LVL_FREQ", "THD_LVL", "SNR_LVL"],
		help="What measurement to perform"
	)
	parser.add_argument(
		"-f1", "--start-frequency",
		action='store',
		type=int,
		default=10,
		metavar='FREQ_HZ',
		help="Start Frequency (if applicable for measurement type)"
	)
	parser.add_argument(
		"-f2", "--stop-frequency",
		action='store',
		type=int,
		default=40000,
		metavar='FREQ_HZ',
		help="Stop Frequency (if applicable for measurement type)"
	)
	parser.add_argument(
		"-st", "--steps",
		action='store',
		type=int,
		default=12,
		metavar='STP/OCT',
		help="How many measurement steps per octave"
	)
	parser.add_argument(
		"-a1", "--start-amplitude",
		action='store',
		type=int,
		default=0.001,
		metavar='VOLT',
		help="Start Amplitude (if applicable for measurement type)"
	)
	parser.add_argument(
		"-a2", "--stop-amplitude",
		action='store',
		type=int,
		default=6,
		metavar='VOLT',
		help="Stop Amplitude (if applicable for measurement type)"
	)

	return parser

def main() -> None:
	parser = init_argparse()
	args = parser.parse_args()

	if (args.verbose):
		print("<<<DEBUG MODE ACTIVE>>>")
		DEBUG = True

	with serial.Serial(config['serialdevice'], config['baudrate'], timeout=int(config['timeout']), parity=parity, rtscts=rtscts) as gpib:
		initialize_prologix(gpib, config['gpib_remote_addr'])

		if (args.measure == "LVL_FREQ"):
			measure_freq_level(gpib, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result)
		if (args.measure == "THD"):
			measure_thd_level(gpib, args.start_amplitude, args.stop_amplitude, args.steps, args.start_frequency, persist_meas_result)
		else:
			print("Not yet supported: " + args.measure)

main()
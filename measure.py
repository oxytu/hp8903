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
	gpib_send(gpib, "++read_tmo_ms 5000")
	gpib_send(gpib, "++addr " + str(remote_address))
	gpib_send(gpib, "++ifc")
	gpib_send(gpib, "++eoi 1")
	gpib_send(gpib, "++eos 1")
	gpib_send(gpib, "++clr")

def persist_meas_result(stream):
	return lambda x, y : _internal_persist_meas_result(stream, x, y)

def _internal_persist_meas_result(stream, current_output, gpib):
	gpib_send(gpib, "RL")
	answerleft = parse_exp_notation(gpib.readline().decode(ENCODING))

	gpib_send(gpib, "RR")
	answerright = parse_exp_notation(gpib.readline().decode(ENCODING))

	print(str(current_output) + ";" + str(answerleft) + ";" + str(answerright), file=stream)

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

		persistor(current, gpib)
		current *= increase_factor

def measure_freq_level(gpib, start_freq, max_freq, steps_per_octave, amplitude, persistor, stream):
	print("# FRQ_LVL Measurement, start_freq=" + str(start_freq) + ", max_freq=" + str(max_freq) + ", amplitude=" + str(amplitude) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	init_command = hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.AC_VOLT) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
	generic_sweep_measurement(gpib, init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

def measure_thd_level(gpib, start_ampl, max_ampl, steps_per_octave, frequency, persistor, stream):
	print("# THD_LVL Measurement, start_ampl=" + str(start_ampl) + ", max_ampl=" + str(max_ampl) + ", frequency=" + str(frequency) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	init_command = hp8903_freq(frequency) + hp8903_ampl(start_ampl) + hp8903_meas(Measurement.DISTORTION) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
	generic_sweep_measurement(gpib, init_command, start_ampl, max_ampl, steps_per_octave, hp8903_ampl, persistor)

def measure_thd_freq(gpib, start_freq, max_freq, steps_per_octave, amplitude, persistor, stream):
	print("# THD_FRQ Measurement, start_freq=" + str(start_freq) + ", max_freq=" + str(max_freq) + ", amplitude=" + str(amplitude) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	init_command = hp8903_freq(start_freq) + hp8903_ampl(amplitude) + hp8903_meas(Measurement.DISTORTION) + hp8903_filter(Filters.HP_OFF) + hp8903_filter(Filters.LP_OFF) + hp8903_trigger(Trigger.TRIG_FREERUN)
	generic_sweep_measurement(gpib, init_command, start_freq, max_freq, steps_per_octave, hp8903_freq, persistor)

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
		default="LVL_FRQ",
		choices=["LVL_FRQ", "THD_LVL", "THD_FRQ", "SNR_LVL"],
		help="What measurement to perform"
	)
	parser.add_argument(
		"-f1", "--start-frequency",
		action='store',
		type=int,
		default=20,
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
		type=float,
		default=0.010,
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

def measure(args, output) -> None:
	with serial.Serial(config['serialdevice'], config['baudrate'], timeout=int(config['timeout']), parity=parity, rtscts=rtscts) as gpib:
		initialize_prologix(gpib, config['gpib_remote_addr'])

		if (args.measure == "LVL_FRQ"):
			measure_freq_level(gpib, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result(output), output)
		elif (args.measure == "THD_LVL"):
			measure_thd_level(gpib, args.start_amplitude, args.stop_amplitude, args.steps, args.start_frequency, persist_meas_result(output), output)
		elif (args.measure == "THD_FRQ"):
			measure_thd_freq(gpib, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result(output), output)
		else:
			print("Not yet supported: " + args.measure, file=output)

def main() -> None:
	global DEBUG
	parser = init_argparse()
	args = parser.parse_args()

	if (args.verbose):
		print("<<<DEBUG MODE ACTIVE>>>")
		DEBUG = True

	measure(args, sys.stdout)

if __name__ == "__main__":
	main()

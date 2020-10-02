import yaml
import argparse
import hp8903
import sys
import gpib
import prologix

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)

parity = gpib.PARITY_NONE
rtscts = 1
ENCODING = "iso8859-1"
DEBUG = False

def persist_meas_result(stream):
	return lambda x, y : _internal_persist_meas_result(stream, x, y)

def _internal_persist_meas_result(stream, current_output, hp8903):
	answerleft = hp8903.read_left()
	answerright = hp8903.read_right()

	print(str(current_output) + ";" + str(answerleft) + ";" + str(answerright), file=stream)


def measure_freq_level(hp_device, start_freq, max_freq, steps_per_octave, amplitude, persistor, stream):
	print("# FRQ_LVL hp8903.Measurement, start_freq=" + str(start_freq) + ", max_freq=" + str(max_freq) + ", amplitude=" + str(amplitude) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_preset_freq_level(start_freq, max_freq, steps_per_octave, amplitude, persistor)

def measure_thd_level(hp_device, start_ampl, max_ampl, steps_per_octave, frequency, persistor, stream):
	print("# THD_LVL hp8903.Measurement, start_ampl=" + str(start_ampl) + ", max_ampl=" + str(max_ampl) + ", frequency=" + str(frequency) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_preset_thd_level(start_ampl, max_ampl, steps_per_octave, frequency, persistor)

def measure_thd_freq(hp_device, start_freq, max_freq, steps_per_octave, amplitude, persistor, stream):
	print("# THD_FRQ hp8903.Measurement, start_freq=" + str(start_freq) + ", max_freq=" + str(max_freq) + ", amplitude=" + str(amplitude) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_preset_thd_freq(start_freq, max_freq, steps_per_octave, amplitude, persistor)

def measure_thdlv_level(hp_device, start_ampl, max_ampl, steps_per_octave, frequency, persistor, stream):
	print("# THDLV_LVL hp8903.Measurement, start_ampl=" + str(start_ampl) + ", max_ampl=" + str(max_ampl) + ", frequency=" + str(frequency) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_thdlv_level(start_ampl, max_ampl, steps_per_octave, frequency, persistor)

def measure_thdlv_freq(hp_device, start_freq, max_freq, steps_per_octave, amplitude, persistor, stream):
	print("# THDLV_FRQ hp8903.Measurement, start_freq=" + str(start_freq) + ", max_freq=" + str(max_freq) + ", amplitude=" + str(amplitude) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_thdlv_freq(start_freq, max_freq, steps_per_octave, amplitude, persistor)

def measure_snr_level(hp_device, start_ampl, max_ampl, steps_per_octave, frequency, persistor, stream):
	print("# SNR_LVL hp8903.Measurement, start_ampl=" + str(start_ampl) + ", max_ampl=" + str(max_ampl) + ", frequency=" + str(frequency) + ", steps_per_oct=" + str(steps_per_octave), file=stream)
	hp_device.measure_snr_level(start_ampl, max_ampl, steps_per_octave, frequency, persistor)

def init_argparse() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		usage="%(prog)s [options]",
		description="Creates a hp8903.Measurement via the HP8903 and outputs the results to STDOUT"
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
		choices=["LVL_FRQ", "THD_LVL", "THD_FRQ", "THDLV_LVL", "THDLV_FRQ", "SNR_LVL"],
		help="What hp8903.Measurement to perform"
	)
	parser.add_argument(
		"-f1", "--start-frequency",
		action='store',
		type=int,
		default=20,
		metavar='FREQ_HZ',
		help="Start Frequency (if applicable for hp8903.Measurement type)"
	)
	parser.add_argument(
		"-f2", "--stop-frequency",
		action='store',
		type=int,
		default=40000,
		metavar='FREQ_HZ',
		help="Stop Frequency (if applicable for hp8903.Measurement type)"
	)
	parser.add_argument(
		"-st", "--steps",
		action='store',
		type=int,
		default=12,
		metavar='STP/OCT',
		help="How many hp8903.Measurement steps per octave"
	)
	parser.add_argument(
		"-a1", "--start-amplitude",
		action='store',
		type=float,
		default=0.010,
		metavar='VOLT',
		help="Start Amplitude (if applicable for hp8903.Measurement type)"
	)
	parser.add_argument(
		"-a2", "--stop-amplitude",
		action='store',
		type=float,
		default=6,
		metavar='VOLT',
		help="Stop Amplitude (if applicable for hp8903.Measurement type)"
	)

	return parser

def measure(args, output) -> None:
	global DEBUG

	with prologix.Prologix(config['serialdevice'], config['baudrate'], int(config['timeout']), parity, rtscts, config['gpib_remote_addr'], ENCODING) as gpib:
		if DEBUG:
			gpib.debug()

		gpib.init()

		hp_device = hp8903.HP8903(gpib)

		if (args.measure == "LVL_FRQ"):
			measure_freq_level(hp_device, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result(output), output)
		elif (args.measure == "THD_LVL"):
			measure_thd_level(hp_device, args.start_amplitude, args.stop_amplitude, args.steps, args.start_frequency, persist_meas_result(output), output)
		elif (args.measure == "THD_FRQ"):
			measure_thd_freq(hp_device, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result(output), output)
		elif (args.measure == "THDLV_LVL"):
			measure_thdlv_level(hp_device, args.start_amplitude, args.stop_amplitude, args.steps, args.start_frequency, persist_meas_result(output), output)
		elif (args.measure == "THDLV_FRQ"):
			measure_thdlv_freq(hp_device, args.start_frequency, args.stop_frequency, args.steps, args.start_amplitude, persist_meas_result(output), output)
		elif (args.measure == "SNR_LVL"):
			measure_snr_level(hp_device, args.start_amplitude, args.stop_amplitude, args.steps, args.start_frequency, persist_meas_result(output), output)
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

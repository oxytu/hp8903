import matplotlib.pyplot as plt
import numpy as np
import csv
import math
import argparse

def load_csv(filename, reference_level):
    x = []
    y = []

    with open(filename, 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=";")
        for row in plots:
            freq = float(row[0])
            voltage = float(row[1])

            level = 20 * math.log(voltage/reference_level)

            x.append(freq)
            y.append(level)
    return (x,y)

def load_calibration(filename):
    if filename is None:
        return None
    else:
        return load_csv(filename, 1)

def apply_calibration(calibration, measure):
    if calibration is None:
        return measure

    x = []
    y = []

    for i in range(0, len(measure[0])):
        xm = measure[0][i]
        ym = measure[1][i]

        calibration_deltas = np.abs(np.asarray(calibration[0]) - xm)
        position_ym = calibration_deltas.argmin()

        delta_y = 0
        if position_ym != None:
            delta_y = calibration[1][position_ym]
        x.append(xm)
        y.append(ym - delta_y)

    return (x, y)

def create_graphs(files, calibration_file, graph_style, reference_level) -> None:
    calibration = load_calibration(calibration_file)

    for file in files:
        measurement = load_csv(file, reference_level)
        (x, y) = apply_calibration(calibration, measurement)

        plt.style.use(graph_style)

        plt.xscale("log")
        
        min_db = (math.floor(min(y) / 6) * 6) - 6
        max_db = (math.ceil(max(y) / 6) * 6) + 6
        plt.yticks(np.arange(min_db, max_db, 6.0))

        plt.ylim((min_db, max_db))

        plt.grid()
        plt.plot(x,y,label="Frequency Response")
        plt.xlabel('Frequency [Hz]')
        if calibration_file is not None:
            plt.ylabel('Level [dB]')
        else:
            plt.ylabel('Level [dBu]')
        plt.title(f"{file}")
        plt.legend()
        plt.show()

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [files]...",
        description="Plots measurements created with the HP8903 - currently only as Frequency Graphs"
    )
    parser.add_argument(
        "-r", "--reference-level",
        action='store',
        type=float,
        default=0.775,
        metavar='REFERENCE_VOLTAGE',
        help="What reference level shall be used for dB calculations? (Default=0.775V = dBu, not used when you provide a calibration file)"
    )
    parser.add_argument(
        "-c", "--calibration-file",
        action='store',
        metavar='CSVFILE',
        help="Provide a calibration file from a Loop-Measurement (Straight cable from in to out)"
    )
    parser.add_argument('files', nargs='+')
    return parser

def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()

    create_graphs(args.files, args.calibration_file, 'style/theta.mplstyle', args.reference_level)

main()
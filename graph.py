import matplotlib.pyplot as plt
import numpy as np
import csv
import math
import argparse
import io

REFERENCE_LEVEL_DEFAULT=0.775

def load_csv(measurement, filecontent, reference_level):
    x = []
    y = []

    if (reference_level is None):
        reference_level = REFERENCE_LEVEL_DEFAULT

    csvcontent = io.StringIO(filecontent)
    plots = csv.reader(filter(lambda row: row[0]!='#', csvcontent), delimiter=";")
    for row in plots:
        if measurement == "LVL_FRQ":
            if (row[1] == 'None' or row[2] == 'None'):
                continue
            freq = float(row[1])
            voltage = float(row[2])

            level = 20 * math.log10(voltage/reference_level)

            x.append(freq)
            y.append(level)
        if measurement == "THD_LVL":
            if (row[0] == 'None' or row[2] == 'None'):
                continue
            out_volt = float(row[0])
            in_thd = float(row[2])

            out_level = 20 * math.log10(out_volt/reference_level)
            in_level = 20 * math.log10(in_thd/100)

            x.append(out_volt)
            y.append(in_level)
        if measurement == "THD_FRQ":
            if (row[0] == 'None' or row[2] == 'None'):
                continue
            freq = float(row[0])
            in_thd = float(row[2])

            in_level = 20 * math.log10(in_thd/100)

            x.append(freq)
            y.append(in_level)

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

def define_db_scale(plt, axis, values) -> None:
    min_db = (math.floor(min(values) / 6) * 6) - 6
    max_db = (math.ceil(max(values) / 6) * 6) + 6

    if axis == "y":
        plt.yticks(np.arange(min_db, max_db, 6.0))
        plt.ylim((min_db, max_db))
    else:
        plt.xticks(np.arange(min_db, max_db, 6.0))
        plt.xlim((min_db, max_db))

def configure_plot_lvl_frq(plt, calibration, x, y):
    plt.xscale("log")
    plt.xlabel('Frequency [Hz]')
    
    if calibration is not None:
        plt.ylabel('Level [dB]')
    else:
        plt.ylabel('Level [dBu]')
    define_db_scale(plt, "y", y)

def configure_plot_thd_lvl(plt, x, y):
    plt.xlabel('Generator Level [dBu]')    
    plt.ylabel('THD Level [dB]')

    define_db_scale(plt, "x", x)
    define_db_scale(plt, "y", y)

def configure_plot_thd_frq(plt, x, y):
    plt.xscale("log")
    plt.xlabel('Frequency [Hz]')
    

    plt.ylabel('THD Level [dB]')
    define_db_scale(plt, "y", y)

def create_graph(measure, file_contents, output_format, output_buffer, calibration, graph_style, reference_level) -> None:
    measurement = load_csv(measure, file_contents, reference_level)
    (x, y) = apply_calibration(calibration, measurement)

    plt.figure()
    plt.style.use(graph_style)

    if measure == "LVL_FRQ":
        configure_plot_lvl_frq(plt, calibration, x, y)
    elif measure == "THD_LVL":
        configure_plot_thd_lvl(plt, x, y)
    elif measure == "THD_FRQ":
        configure_plot_thd_frq(plt, x, y)

    plt.grid()
    plt.plot(x, y, label="Frequency Response ")
    plt.title(f"Measurement")
    plt.legend()

    if (output_format is None):
        plt.show()
    else:
        plt.savefig(output_buffer, format=output_format)
        #plt.savefig(file + "." + output_format)

    plt.close()

def create_graphs(measure, files, output_format, calibration_file, graph_style, reference_level) -> None:
    calibration = load_calibration(calibration_file)

    if calibration != None and measure != "LVL_FRQ":
        raise "Calibration currently only possible for LVL_FRQ measurements!"

    for filename in files:
        with open(filename, 'r') as csvfile:
            file_content = csvfile.read()
            output_buffer = io.BytesIO()
            create_graph(measure, file_content, output_format, output_buffer, calibration, graph_style, reference_level)
            output_buffer.seek(0)
            with open(f"{filename}.{output_format}", "wb") as f:
                f.write(output_buffer.getbuffer())
            output_buffer.close()


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [files]...",
        description="Plots measurements created with the HP8903 - currently only as Frequency Graphs"
    )
    parser.add_argument(
		"-m", "--measure",
		action='store',
		default="LVL_FRQ",
		choices=["LVL_FRQ", "THD_LVL", "THD_FRQ", "SNR_LVL"],
		help="What type measurement to graph"
	)
    parser.add_argument(
		"-o", "--output-format",
		action='store',
		choices=["png", "svg", "pdf"],
		help="Output to file of specified format"
	)
    parser.add_argument(
        "-r", "--reference-level",
        action='store',
        type=float,
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

    create_graphs(args.measure, args.files, args.output_format, args.calibration_file, 'style/theta.mplstyle', args.reference_level)

if __name__ == "__main__":
    main()
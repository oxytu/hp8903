import serial

PARITY_NONE = serial.PARITY_NONE

class GPIB:
    serial = None
    encoding = None
    debug = False
    remote_address = None

    def __init__(self, device, baudrate, timeout, parity, rtscts, remote_address, encoding):
        self.serial = serial.Serial(device, baudrate, timeout=timeout, parity=parity, rtscts=rtscts)
        self.encoding = encoding
        self.remote_address = remote_address

    def __enter__(self):
        self.serial.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.serial.__exit__(exc_type, exc_value, exc_traceback)

    def init(self):
        pass

    def debug(self):
        self.debug = True

    def send(self, string):
        if self.debug:
            print(">>>" + string)
        self.serial.write((string + "\n").encode(self.encoding))

    def readline(self):
        return self.serial.readline().decode(self.encoding)

    def send_with_return(self, string):
        self.send(string)
        return self.readline()

    def send_command_with_return_eoi(self, string):
        self.send(string)
        self.send("++read eoi")
        return self.readline()
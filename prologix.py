import gpib

class Prologix(GPIB):

    def init(self):
        self.gpib_send(gpib, "++mode 1")
        self.gpib_send(gpib, "++auto 1")
        self.gpib_send(gpib, "++read_tmo_ms 5000")
        self.gpib_send(gpib, "++addr " + str(self.remote_address))
        self.gpib_send(gpib, "++ifc")
        self.gpib_send(gpib, "++eoi 1")
        self.gpib_send(gpib, "++eos 1")
        self.gpib_send(gpib, "++clr")

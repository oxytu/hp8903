import gpib

class Prologix(gpib.GPIB):

    def init(self):
        self.gpib_send("++mode 1")
        self.gpib_send("++auto 1")
        self.gpib_send("++read_tmo_ms 5000")
        self.gpib_send("++addr " + str(self.remote_address))
        self.gpib_send("++ifc")
        self.gpib_send("++eoi 1")
        self.gpib_send("++eos 1")
        self.gpib_send("++clr")

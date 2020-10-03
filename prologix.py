import gpib

class Prologix(gpib.GPIB):

    def init(self):
        self.send("++mode 1")
        self.send("++auto 1")
        self.send("++read_tmo_ms 5000")
        self.send("++addr " + str(self.remote_address))
        self.send("++ifc")
        self.send("++eoi 1")
        self.send("++eos 1")
        self.send("++clr")

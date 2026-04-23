class AstroObject:
    def __init__(self, name, ra_rad, dec_rad, X = None, Y = None, PA = None):
        self.name = name
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad
        self.X = X
        self.Y = Y
        self.PA = PA
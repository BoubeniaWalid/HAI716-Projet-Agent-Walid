class OutOfBoundError(Exception):
    def __init__(self, message="Accès à une case hors de la carte"):
        self.message= message
        super().__init__(self.message)
from . import EncryptedConfigStore


class WhooshStore(EncryptedConfigStore):
    """
    whoosh store is an EncryptedConfigStore

    It saves and indexes the data in a whoosh index
    """

    def __init__(self, location):
        """
        create a new redis store, the location given will be used to generate keys

        this keys will be combined to get/set instance config

        Args:
            location (Location)
        """
        super().__init__(location)

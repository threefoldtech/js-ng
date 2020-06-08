from .container import Container


class ThreeBot(Container):
    """
    Manage your threebot
    """

    @staticmethod
    def start(name="3bot", pull: bool = False):
        """
        Start your threebot
        """
        print(f"Starting {name} {pull}")

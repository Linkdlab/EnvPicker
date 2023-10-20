from logging import getLogger, StreamHandler, Formatter, DEBUG

ENVPICKER_LOGGER = getLogger("envpicker")
ENVPICKER_LOGGER.setLevel("DEBUG")

handler = StreamHandler()
handler.setLevel(DEBUG)
formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
ENVPICKER_LOGGER.addHandler(handler)
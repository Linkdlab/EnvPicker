from logging import getLogger, StreamHandler, Formatter, INFO

ENVPICKER_LOGGER = getLogger("envpicker")

handler = StreamHandler()
formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
ENVPICKER_LOGGER.addHandler(handler)

ENVPICKER_LOGGER.setLevel(INFO)

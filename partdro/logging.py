import logging

def configure_logging(app):
    level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(level=level)


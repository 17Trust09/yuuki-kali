import logging

def setup_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)  # Setzen des Log Levels auf WARNING

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Korrigiert: levelname anstelle von levellevel
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if not logger.hasHandlers():
        file_handler = logging.FileHandler(filename='discord_errors.log', encoding='utf-8', mode='a')  # Anhängemodus
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.WARNING)
        logger.addHandler(file_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    if not root_logger.hasHandlers():
        root_file_handler = logging.FileHandler(filename='discord_errors.log', encoding='utf-8', mode='a')  # Anhängemodus
        root_file_handler.setFormatter(formatter)
        root_file_handler.setLevel(logging.WARNING)
        root_logger.addHandler(root_file_handler)

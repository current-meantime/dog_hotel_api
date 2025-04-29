import logging
import os

# Ścieżka do katalogu na logi
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging():
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Główny logger aplikacji
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Handler do pliku
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)

    # Handler błędów
    error_handler = logging.FileHandler(os.path.join(LOG_DIR, "errors.log"))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)

    # Konsola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

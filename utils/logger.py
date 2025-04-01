import logging
import os

def setup_logger(name: str = 'instagram_crawler', level=logging.INFO, log_file: str = 'app.log') -> logging.Logger:
    """
    Set up and return a configured logger with both console and file handlers.

    Args:
        name (str): The name of the logger.
        level (int): Logging level (default: logging.INFO).
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 콘솔 핸들러 (중복 추가 방지)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # 파일 핸들러 (중복 추가 방지)
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        os.makedirs(os.path.dirname(log_file), exist_ok=True) if '/' in log_file or '\\' in log_file else None
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

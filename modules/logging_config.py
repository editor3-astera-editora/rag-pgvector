import logging
import logging.handlers
import os
from datetime import datetime
from modules.generation import _call_llm_with_tracking

def setup_logging(log_dir="logs", log_level=logging.INFO):
    """
    Configura o sistema de logging para o projeto.
    
    Args:
        log_dir: Diretório onde os logs serão salvos
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"processamento_{timestamp}.log")

    file_formatter = logging.Formatter(
        '%(asctime)s | %(processName)-12s | %(threadName)-10s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
        datefmt='%H:%M:%S'
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info(f"Sistema de logging iniciado. Arquivo de log: {log_file}")
    
    return root_logger

def get_logger(name):
    """
    Obtém um logger para um módulo específico.
    
    Args:
        name: Nome do módulo (geralmente __name__)
    
    Returns:
        Logger configurado para o módulo
    """
    return logging.getLogger(name)

class PerformanceLogger:
    """Context manager para log de performance."""
    
    def __init__(self, logger, operation_name):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Iniciando operação: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(f"Operação {self.operation_name} falhou após {duration:.2f}s: {exc_val}")
        else:
            self.logger.debug(f"Operação {self.operation_name} concluída em {duration:.2f}s")
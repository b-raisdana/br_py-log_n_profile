import logging
import sys
import traceback
from pathlib import Path
from types import FrameType

from colorama import Fore, Style
from loguru import logger

from .ray_id import get_ray_id

__severity_color_map = {
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.DEBUG: Fore.CYAN,
}
__root_path: Path | None = None
__log_format = "{time:YYYY-MM-DD HH:mm:ss.SS} | {level} | {name}:{function}:{line} - {message}"
__log_to_std_out_level = logging.DEBUG
__log_to_file_level = 0
__min_log_level = __log_to_std_out_level

__all__ = ["log_d", "log_e", "log_i", "log_w", "log_exception"]

_NAMED_LEVEL_THRESHOLDS = (
    (logging.CRITICAL, "CRITICAL"),
    (logging.ERROR, "ERROR"),
    (logging.WARNING, "WARNING"),
    (logging.INFO, "INFO"),
    (logging.DEBUG, "DEBUG"),
)

_STANDARD_LEVEL_NAMES = {
    logging.CRITICAL: "CRITICAL",
    logging.ERROR: "ERROR",
    logging.WARNING: "WARNING",
    logging.INFO: "INFO",
    logging.DEBUG: "DEBUG",
}


def _nearest_level_name(severity: int) -> str:
    name = _STANDARD_LEVEL_NAMES.get(severity)
    if name is not None:
        return name
    for threshold, name in _NAMED_LEVEL_THRESHOLDS:
        if severity >= threshold:
            return name
    return "DEBUG"


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = _nearest_level_name(record.levelno)

        frame: FrameType | None
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _intercept_stdlib_logging() -> None:
    logging.basicConfig(handlers=[InterceptHandler()], force=True)


def root_path(root_distance: int = 5) -> Path:
    global __root_path
    if __root_path is None:
        __root_path = Path(__file__)
        try:
            for _i in range(root_distance):
                __root_path = __root_path.parent
        except (NameError, FileNotFoundError):
            logger.warning(
                f"Unable to find parent for {__root_path}. "
                f"Calling init_logger will enable extended "
                f"features and resolve this warning."
            )
    return __root_path


def _init_default_logger() -> None:
    log_dir = root_path() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    runtime_log_dir = log_dir / "runtime"
    runtime_log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        sys.stdout,
        format=__log_format,
        colorize=True,
        level=__log_to_std_out_level,
    )
    logger.add(
        runtime_log_dir / "runtime.log",
        format=__log_format,
        level=__log_to_file_level,
        rotation="00:00",
        retention="30 days",
        enqueue=True,
    )
    _intercept_stdlib_logging()


_init_default_logger()


def log_d(message: str, stack_limit: int = 0, stack_offset: int = 0) -> None:
    log(message, logging.DEBUG, stack_limit, stack_offset + 1)


def log_w(message: str, stack_limit: int = 0, stack_offset: int = 0) -> None:
    log(message, logging.WARNING, stack_limit, stack_offset + 1)


def log_i(message: str, stack_limit: int = 0, stack_offset: int = 0) -> None:
    log(message, logging.INFO, stack_limit, stack_offset + 1)


def log_e(message: str, stack_limit: int = 0, stack_offset: int = 0) -> None:
    log(message, logging.ERROR, stack_limit, stack_offset + 1)


def log_exception(
    message: str,
    exception_class: type[Exception],
    stack_limit: int = 0,
    stack_offset: int = 0,
) -> Exception:
    log_e(message, stack_limit, stack_offset + 1)
    raise exception_class(message)


def log(message: str, severity: int, stack_limit: int = 0, stack_offset: int = 0) -> None:
    if __min_log_level > severity:
        return
    try:
        stack_trace = ""
        if stack_limit > 0:
            stack = traceback.format_stack(limit=stack_offset + stack_limit + 1)[: -(stack_offset + 1)][-(stack_limit):]
            stack_trace = "\n" + "".join(stack)
        color = __severity_color_map.get(severity, Fore.WHITE)
        id_of_ray = get_ray_id()
        logger.opt(depth=stack_offset + 1).log(
            _nearest_level_name(severity), f"{color}{message}{stack_trace} (ray:{id_of_ray}){Style.RESET_ALL}"
        )
    except Exception as e:
        logger.exception(f"Failed to log message: {message} | Error: {e!s}")

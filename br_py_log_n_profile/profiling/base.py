import time
from collections.abc import Callable
from functools import wraps
from inspect import signature

from colorama import Fore

from ..do_log.log_it import log_d

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore[assignment]

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None  # type: ignore[assignment]


# release >0.5.1
def profile_it[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def _measure_time(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.time()
        function_parameters = parameters_to_str(args, kwargs)
        log_d(f"{func.__name__}({function_parameters}) started", stack_offset=1)
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time_color = (
            Fore.BLUE
            if execution_time < 0.01
            else Fore.GREEN
            if execution_time < 0.1
            else Fore.YELLOW
            if execution_time < 1
            else Fore.RED
        )
        log_d(
            f"{func.__name__}({function_parameters}) executed in {execution_time_color}{execution_time:.3f} seconds",
            stack_offset=1,
        )
        return result

    # ``wraps`` exposes ``func`` through ``__wrapped__``, which is enough for
    # ``inspect.signature`` by default.  Store the signature too so consumers
    # that deliberately inspect this wrapper without unwrapping still see the
    # decorated callable's public interface.
    _measure_time.__signature__ = signature(func)  # type: ignore[attr-defined]
    return _measure_time


def parameters_to_str(args: tuple[object, ...], kwargs: dict[str, object]) -> str:
    def process_item(item: object) -> str:
        if pd is not None and isinstance(item, pd.DataFrame):
            return f"{len(item)}*{item.columns}"
        elif isinstance(item, list):
            if np is not None:
                try:
                    return f"list{np.array(item).shape}"
                except Exception:
                    return f"list[{len(item)}]"
            return f"list[{len(item)}]"
        elif np is not None and isinstance(item, np.ndarray):
            return f"ndarray{item.shape}"
        elif isinstance(item, dict):
            return process_dict(item)
        else:
            return str(item)

    def process_dict(d: dict[object, object]) -> str:
        t_parameters: list[str] = []
        for key, value in d.items():
            if isinstance(value, list):
                if np is not None:
                    try:
                        t_parameters.append(f"{key}: list{np.array(value).shape}")
                    except Exception:
                        t_parameters.append(f"{key}: list[{len(value)}]")
                else:
                    t_parameters.append(f"{key}: list[{len(value)}]")
            elif pd is not None and isinstance(value, pd.DataFrame):
                t_parameters.append(f"{key}: {len(value)}*{value.columns}")
            elif np is not None and isinstance(value, np.ndarray):
                t_parameters.append(f"{key}: ndarray{value.shape}")
            elif isinstance(value, dict):
                t_parameters.append(f"{key}: {{ {process_dict(value)} }}")
            else:
                t_parameters.append(f"{key}: {value}")
        return ", ".join(t_parameters)

    parameters = [process_item(arg) for arg in args]
    parameters += [f"{k}: {process_item(kwargs[k])}" for k in kwargs]

    return ", ".join(parameters)

# -*- coding: utf-8 -*-

from __future__ import annotations

from databricks_cli.utils import InvalidConfigurationError
from threading import Lock
from typing import Any, Callable, Dict, ParamSpec, TypeVar, Union
from ultralytics import YOLO
from ultralytics.yolo.engine.trainer import BaseTrainer
from ultralytics.yolo.engine.validator import BaseValidator

P, T = ParamSpec("P"), TypeVar("T")
LOCK = Lock()


class LockingWrapper:
    """Locking wrapper"""

    _func: Callable[P, T]
    _lock: Lock

    def __init__(self, __func: Callable[P, T], __lock: Lock = LOCK):
        """LockingWrapper

        Wrap any function with a lock

        Parameters
        ----------
        __func : Callable[P, T]
            function to wrap with the lock
        __lock : Lock, optional
            Lock to use, by default LOCK
        """
        self._func = __func
        self._lock = __lock

    def __call__(self, *args: T.args, **kwargs: T.kwargs):
        with self._lock:
            result = self._func(*args, **kwargs)
        return result


def wrap_callbacks(
    model: Union[T, YOLO],
    lock: Lock = LOCK,
    **additional_callbacks: Dict[
        str, Callable[[Union[BaseTrainer, BaseValidator]], None]
    ],
) -> T:
    """Ultralytics Logging Callback wrapper

    wraps every in the LockingWrapper class, which will ensure thead safety

    The reason this is required is mlflow is not threadsafe,
    but the upstream ultralytics project assumes it is.

    Parameters
    ----------
    model : YOLO
        The model to wrap the callbacks on
    lock : Lock, optional
        A specific lock to use, by default LOCK

    Returns
    -------
    Model
        model with threadsafe logging callbacks
    """
    for event, callback in additional_callbacks.items():
        model.add_callback(event, callback)
    cb = {}
    for key, callbacks in model.callbacks.items():
        _new_cb = []
        for callback in callbacks:
            wrap = LockingWrapper(callback, lock)
            _new_cb.append(wrap)
        cb[key] = _new_cb
    model.callbacks.update(cb)
    return model

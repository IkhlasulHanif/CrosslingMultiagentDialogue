"""Minimal PathFinder compatibility layer for GovSim smoke bring-up.

The canonical PathFinder submodule cannot be fetched by git in this sandbox.
This module only satisfies GovSim import-time symbols used outside the smoke
runner path. It intentionally raises for generation APIs so real upstream
PathFinder execution is not silently replaced.
"""

from __future__ import annotations

from contextlib import contextmanager


class Model:
    pass


@contextmanager
def assistant():
    yield


@contextmanager
def system():
    yield


@contextmanager
def user():
    yield


def get_model(*args, **kwargs):
    raise RuntimeError("PathFinder submodule is unavailable in this setting-local checkout")


def gen(*args, **kwargs):
    raise RuntimeError("PathFinder gen is unavailable in this setting-local checkout")


def find(*args, **kwargs):
    raise RuntimeError("PathFinder find is unavailable in this setting-local checkout")


def select(*args, **kwargs):
    raise RuntimeError("PathFinder select is unavailable in this setting-local checkout")

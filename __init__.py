"""Thin root shim for Hermes plugin discovery."""

from .integrations.hermes.adw_plugin.router import register

__all__ = ["register"]

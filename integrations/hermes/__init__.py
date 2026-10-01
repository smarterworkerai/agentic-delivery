"""Hermes plugin entrypoint for the Agentic Delivery Workflow router."""

from .adw_plugin.router import register

__all__ = ["register"]

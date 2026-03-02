"""AFK Module - AFK防护模块"""

from .detector import AFKDetector
from .responder import AFKResponder

__all__ = [
    "AFKDetector",
    "AFKResponder",
]

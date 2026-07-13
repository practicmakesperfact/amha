"""
Handlers package init.
"""
from backend.handlers.dispatcher import message_dispatcher
from backend.handlers.start_handler import start_handler
from backend.handlers.register_handler import contact_handler
from backend.handlers.admin_handler import admin_callback_handler

__all__ = [
    "message_dispatcher",
    "start_handler",
    "contact_handler",
    "admin_callback_handler",
]

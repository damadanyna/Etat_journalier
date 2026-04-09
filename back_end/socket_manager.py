import asyncio

import socketio


class SocketManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self._loop = None
        self._register_events()

    def _register_events(self):
        @self.sio.event
        async def connect(sid, environ, auth):
            return True

        @self.sio.event
        async def disconnect(sid):
            return True

    def set_loop(self, loop):
        self._loop = loop

    async def emit_pending_validation_update(self, count: int):
        await self.sio.emit(
            "pending_validation_updated",
            {
                "app": "paie",
                "count": count,
            },
        )

    def emit_pending_validation_update_sync(self, count: int):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.emit_pending_validation_update(count),
                self._loop,
            )

    async def emit_payroll_date_update(self, label: str, stat_of=None, used: int = 1):
        await self.sio.emit(
            "payroll_date_updated",
            {
                "app": "paie",
                "label": label,
                "stat_of": stat_of,
                "used": used,
            },
        )

    def emit_payroll_date_update_sync(self, label: str, stat_of=None, used: int = 1):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.emit_payroll_date_update(label, stat_of, used),
                self._loop,
            )

    async def emit_user_activity_update(self, payload: dict):
        await self.sio.emit(
            "user_activity_logged",
            payload,
        )

    def emit_user_activity_update_sync(self, payload: dict):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.emit_user_activity_update(payload),
                self._loop,
            )


socket_manager = SocketManager()
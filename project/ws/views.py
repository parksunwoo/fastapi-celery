import json

import socketio
from fastapi import WebSocket, FastAPI
from socketio.asyncio_namespace import AsyncNamespace

from . import ws_router
from project import broadcast
from project.celery_utils import get_task_info
from project.config import settings


@ws_router.websocket("/ws/task_status/{task_id}")
async def ws_task_status(websocket: WebSocket):
    await websocket.accept()

    task_id = websocket.scope["path_params"]["task_id"]

    async with broadcast.subscribe(channel=task_id) as subscriber:
        data = get_task_info(task_id)
        await websocket.send_json(data)

        async for event in subscriber:
            await websocket.send_json(json.loads(event.message))


async def update_celery_task_status(task_id: str):
    await broadcast.connect()
    await broadcast.publish(channel=task_id, message=json.dumps(get_task_info(task_id)))
    await broadcast.disconnect()


class TaskStatusNameSpace(AsyncNamespace):
    async def on_join(self, sid, data):
        self.enter_room(sid=sid, room=data["task_id"])
        await self.emit("status", get_task_info(data["task_id"]), room=data["task_id"])


def register_socketio_app(app: FastAPI):
    mgr = socketio.AsyncRedisManager(settings.WS_MESSAGE_QUEUE)
    sio = socketio.AsyncServer(
        client_manager=mgr,
        async_mode="asgi",
        logger=True,
        engineio_logger=True
    )
    sio.register_namespace(TaskStatusNameSpace("/task_status"))
    asgi = socketio.ASGIApp(socketio_server=sio,)
    app.mount("/ws", asgi)


def update_celery_task_status_socketio(task_id):
    external_sio = socketio.RedisManager(settings.WS_MESSAGE_QUEUE, write_only=True)
    external_sio.emit("status", get_task_info(task_id), room=task_id, namespace="/task_status")




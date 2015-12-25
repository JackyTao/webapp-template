# -*- coding: utf-8 -*-

from handler import (
    index,
)


general_handlers = [
    (r'/data', index.DataHandler),
    (r'/index', index.HtmlHandler),
    (r'/', index.IndexHandler),
    # (r'/test-web-socket', websocket.TestWebSocketHandler),
    # (r'/chat/(?P<room_name>\w+)', websocket.ChatRoomSocketHandler),
]

handlers = (
    general_handlers
)

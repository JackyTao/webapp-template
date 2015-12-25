# -*- coding:utf-8 -*-

from tornado.websocket import WebSocketHandler


class TestWebSocketHandler(WebSocketHandler):
    def open(self):
        print 'web socket opened'

    def on_message(self, message):
        self.write_message(u'You said: ' + message)

    def on_close(self):
        print 'web socket closed'


class ChatRoomSocketHandler(WebSocketHandler):

    socket_handlers = {
        'food': set(),
        'music': set(),
    }

    @classmethod
    def send_message(cls, key, msg):
        for handler in cls.socket_handlers[key]:
            try:
                handler.write_message(msg)
            except:
                pass

    def open(self, room_name):
        if room_name in ChatRoomSocketHandler.socket_handlers:
            self.key = room_name
            ChatRoomSocketHandler.socket_handlers[room_name].add(self)
        else:
            self.write_message('not a valid request!')
            self.close()

    def on_message(self, message):
        ChatRoomSocketHandler.send_message(self.key, message)

    def on_close(self):
        ChatRoomSocketHandler.socket_handlers[self.key].remove(self)
        ChatRoomSocketHandler.send_message(
            self.key,
            'A guy left, online: %s' % len(ChatRoomSocketHandler.socket_handlers))

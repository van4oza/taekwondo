from channels.routing import route

channel_routing = [
    route('websocket.connect', 'catalog.fight.ws_connect', path=r"^/fight/(?P<match_id>\d+)/(?P<fighter_id>\d+)/$"),
    route('websocket.receive', 'catalog.fight.ws_message', path=r"^/fight/(?P<match_id>\d+)/(?P<fighter_id>\d+)/$"),
    route('websocket.disconnect', 'catalog.fight.ws_disconnect', path=r"^/fight/(?P<match_id>\d+)/(?P<fighter_id>\d+)/$"),
    route('websocket.connect', 'catalog.fight.ws_connect_boss', path=r"^/fight/(?P<match_id>\d+)/$"),
    route('websocket.receive', 'catalog.fight.ws_message_boss', path=r"^/fight/(?P<match_id>\d+)/$"),
    route('websocket.disconnect', 'catalog.fight.ws_disconnect_boss', path=r"^/fight/(?P<match_id>\d+)/$"),
]

#     {
#     'websocket.connect': 'channeled.consumers.ws_connect',
#     'websocket.receive': 'channeled.consumers.ws_message',
#     'websocket.disconnect': 'channeled.consumers.ws_disconnect',
#     # route('http.request', 'catalog.consumers.http_request_consumer')
# }

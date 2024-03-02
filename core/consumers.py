from channels.generic.websocket import AsyncWebsocketConsumer
import json
import datetime


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "dashboard"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        mph = text_data_json["mph"]
        knts = text_data_json["knts"]
        kph = text_data_json["kph"]
        direction = text_data_json["direction"]
        heading = text_data_json["heading"]
        time = text_data_json["time"]
        tide_type = text_data_json["tide_type"]
        tide_time = text_data_json["tide_time"]
        heights = text_data_json["heights"]
        times = text_data_json["times"]
        lat = text_data_json["lat"]
        lon = text_data_json["lon"]
        track = text_data_json["track"]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "data_pusher",
                "mph": mph,
                "knts": knts,
                "kph": kph,
                "direction": direction,
                "heading": heading,
                "time": time,
                "tide_type": tide_type,
                "tide_time": tide_time,
                "heights": heights,
                "times": times,
                "lat": lat,
                "lon": lon,
                "track": track,
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def data_pusher(self, event):
        mph = event["mph"]
        knts = event["knts"]
        kph = event["kph"]
        direction = event["direction"]
        heading = event["heading"]
        time = event["time"]
        tide_type = event["tide_type"]
        tide_time = event["tide_time"]
        heights = event["heights"]
        times = event["times"]
        lat = event["lat"]
        lon = event["lon"]
        track = event["track"]
        await self.send(
            json.dumps(
                {
                    "mph": mph,
                    "knts": knts,
                    "kph": kph,
                    "direction": direction,
                    "heading": heading,
                    "time": time,
                    "tide_type": tide_type,
                    "tide_time": tide_time,
                    "heights": heights,
                    "times": times,
                    "lat": lat,
                    "lon": lon,
                    "track": track,
                }
            )
        )

    pass

class PicoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "pico"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        rpm = text_data_json["rpm"]
        hrs = text_data_json["hrs"]

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "data_pusher",
                "rpm": rpm,
                "hrs": hrs,

                
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def data_pusher(self, event):
        rpm = event["rpm"]
        hrs = event["hrs"]

        await self.send(
            json.dumps(
                {
                    "rpm": rpm,
                    "hrs": hrs,

                }
            )
        )

    pass

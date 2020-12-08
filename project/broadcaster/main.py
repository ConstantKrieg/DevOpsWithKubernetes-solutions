import asyncio
import os
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

async def run(loop):
    nc = NATS()
    url = os.getenv("NATS_URL")
    print(url, flush=True)
    await nc.connect(servers=[url], loop=loop)

    
    async def message_handler(msg):

        slack_client.api_call(
            "chat.postMessage",
            channel="dwk-todos",
            text=msg.data.decode()
        )

        print(msg.data.decode(), flush=True)


    await nc.subscribe("todos", "workers", cb=message_handler)
    print("subscribed to channel todos", flush=True)
    

if slack_client.rtm_connect(with_team_state=False):
    print("Connected to Slack", flush=True)
else:
    print("Failed to connect", flush=True)



loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))

try:
    loop.run_forever()
finally:
    loop.close()
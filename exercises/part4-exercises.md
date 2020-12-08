## 4.01

Health check in main_application

```python
@app.route("/health")
def check_availability():
    resp = requests.get('http://pingpong-svc/pingpong/count')

    if (resp.status_code == 200):
        return "OK"
    else:
        abort(500)
```

Health check in pinpong

```python
@app.route('/health')
def check_availability():
    global engine
    
    try:
        engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.main-app:5432/{db}")
        engine.connect()
        init_db()
        return "OK"
    except:
        print("Failed to create engine")
        abort(500, "Database not up")

```

pingpong deployment.yml

```yml
...
          readinessProbe:
            initialDelaySeconds: 10 
            periodSeconds: 5 
            httpGet:
               path: /health
               port: 5000
...
```

Same in timestamp_display/manifests/deployment.yml

## 4.02

Health check for project backend

```python
@bp.route('/health')
def healthCheck():
    resp = requests.get('http://kflask-api-svc/api/todo/')

    if resp.status_code == 200:
        return "OK"
    else:
        abort(500)
```

Health check for project API

```python
@app.route('/health')
def healtCheck():
    if init_db():
        return "OK"
    else:
        abort(500)
```

`init_db` tries to connect to the postgres database and returns `True` if it manages to do so.

## 4.03

Query

`count(kube_pod_info{namespace="prometheus", created_by_kind="StatefulSet"})`

## 4.04

project/manifests/analysistemplate.yml

```yml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: cpu-usage-rate
  namespace: project
spec:
  metrics:
  - name: cpu-usage-rate
    initialDelay: 1m
    successCondition: result < 40
    provider:
      prometheus:
        address: http://kube-prometheus-stack-1607-prometheus.prometheus.svc.cluster.local:9090
        query: |
          sum (rate (container_cpu_usage_seconds_total{namespace="project"}[10m])) / sum(machine_cpu_cores) * 100
```

project/manifests/api/deployment.yml

```yml
...
  strategy:
    canary:
      steps:
      - setWeight: 50
      - analysis:
          templates:
          - templateName: cpu-usage-rate
      - pause:
          duration: 10m
      - setWeight: 50
...
```

Same thing is done in the `project/manifests/backend/deployment.yml`

## 4.05

![IMG](https://github.com/ConstantKrieg/DevOpsWithKubernetes-solutions/blob/master/exercises/images/4_05.jpg?raw=true)

## 4.06

broadcaster application

```python
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
```

In API messages are published to NATS like this:

```python
def create_nats_msg(status, todo):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(publish_message(status, todo, loop))
    loop.close()

async def publish_message(status, todo, loop):
    nc = NATS()
 
    url = os.getenv("NATS_URL")
    print(url, flush=True)
    await nc.connect(servers=[url], loop=loop)
 
    await nc.publish("todos", json.dumps({"todo:": todo, "status": status }).encode())
    await nc.flush(1)
    await nc.close()
```

Slack

![slack_img](https://github.com/ConstantKrieg/DevOpsWithKubernetes-solutions/blob/master/exercises/images/4_06.jpg?raw=true)

Six broadcasters were running in parallel:

![lens_img](https://github.com/ConstantKrieg/DevOpsWithKubernetes-solutions/blob/master/exercises/images/4_06_2.jpg?raw=true)

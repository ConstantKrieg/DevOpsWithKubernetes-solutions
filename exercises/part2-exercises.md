

## 2.01

Endpoint for requesting timestamp, hash and number of pongs

```python
@app.route("/")
def get_string():
    timestamp = ''
    with open('/files/timestamp.txt', 'r') as f:
        timestamp = f.read()

    resp = requests.get('http://pingpong-svc/pingpong/count')
    
    return f"{timestamp} {s}      Ping / Pongs: {resp.text}"
```

Pingpong endpoints

```python
@app.route('/pingpong/')
def pong():
    global pong_counter

    pong_counter += 1
 
    return f"pong {pong_counter}"

@app.route('/pingpong/count')
def pong_count():
    global pong_counter
    return str(pong_counter)
```

Pingpong service
```yml
apiVersion: v1
kind: Service
metadata:
  name: pingpong-svc
spec:
  type: ClusterIP
  selector:
    app: pingpong
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 5000
```

Ingress

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: dwk-material-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        backend:
          serviceName: timestamp-hash-svc
          servicePort: 2345
      - path: /pingpong/
        backend:
            serviceName: pingpong-svc
            servicePort: 80
```

## 2.02

Because I used Flask in my project, splitting the backend into the API and just a basic service that handles returning the page and image made the logic a bit convoluted.


api-deployment

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kflask-api-dep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kflask-api
  template:
    metadata:
      labels:
        app: kflask-api
    spec:
      containers:
        - name: kflask-api
          image: kriegmachine/kflask-api
```
backend-deployment
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kflask-dep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kflask
  template:
    metadata:
      labels:
        app: kflask
    spec:
      volumes:
        - name: shared-images
          persistentVolumeClaim:
            claimName: main-claim
      containers:
        - name: kflask
          image: kriegmachine/kflask
          volumeMounts:
            - name: shared-images
              mountPath: /images/
```

api-service 
```yml
apiVersion: v1
kind: Service
metadata:
  name: kflask-api-svc
spec:
  type: ClusterIP
  selector:
    app: kflask-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 6000 
```

backend-service

```yml
apiVersion: v1
kind: Service
metadata:
  name: kflask-svc
spec:
  type: ClusterIP
  selector:
    app: kflask 
  ports:
    - protocol: TCP
      port: 2345
      targetPort: 5000 
```

ingress

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: dwk-material-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        backend:
          serviceName: kflask-svc
          servicePort: 2345
      - path: /api/
        backend:
          serviceName: kflask-api-svc
          servicePort: 80
```

## 2.03

```shell
$ kubectl create namespace main-app
namespace/main-app created
```

pingpong/manifests/deployment.yml

```yml
...
metadata:
  name: pingpong
  namespace: main-app
...
```

main_application/manifests/deployment.yml

```yml
...
metadata:
  name: timestamp-hash-dep
  namespace: main-app
...
```

## 2.04

```shell
$ kubectl create namespace project
namespace/project created
```

project/manifests/backend-deployment.yml

```yml
...
metadata:
  name: kflask-dep
  namespace: project
...
```

project/manifests/api-deployment.yml

```yml
...
metadata:
  name: kflask-api-dep
  namespace: project
...
```

## 2.06

ConfigMap

```yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: message-conf
  namespace: main-app
data:
  MESSAGE: Hello
```

main_application/manifests/deployment.yml

```yml
...
      volumes:
        - name: shared-timestamp
          persistentVolumeClaim:
            claimName: main-claim
        - name: config
          configMap:
           name: message-conf
...
...
        - name: timestamp-display
          image: kriegmachine/timestamp_display
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
            - name: config
              mountPath: /conf/
              readOnly: true
          env:
            - name: MESSAGE
              valueFrom:
                configMapKeyRef:
                  name: message-conf
                  key: MESSAGE
...
```

## 2.07

postgres-secrets.yml

```yml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: main-app

type: Opaque
data:
  dbname: cG9uZ19kYg==
  username: cG9uZ191c2Vy
  password: cG9uZ19wYXNz
```

postgres-deployment.yml

```yml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-db
  namespace: main-app
...
containers:
        - name: postgres
          image: postgres:13.0
          ports:
            - name: postgres
              containerPort: 5432
          env:
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: dbname
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: local-path
        resources:
          requests:
            storage: 100M
```
Same environmental variables are also set in the `pingpong/manifests/deployment.yml`

postgres-service.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: postgres-svc
  namespace: main-app
  labels:
    app: postgres
spec:
  ports:
  - port: 5432
    name: web
  clusterIP: None
  selector:
    app: postgres
```

In `pingpong/main.py` database can be connected with the following URL
```python
db = os.environ['POSTGRES_DB']
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']

engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.main-app:5432/{db}")
```


## 2.08

`postgres-service.yml` and `postgres-service.yml` are identical to the ones in the previous exercise with the sole difference being the namespace which is now *project* instad of *main-app*

Database can now be accessed with the following url

```python
engine = create_engine(f"postgresql://{user}:{password}@postgres-svc.project:5432/{db}")
```

Here is an example of how the project uses a database now.
```python
...
@bp.route('/api/todo/', methods=(['GET']))
def get_todos():

    with engine.connect() as conn:
        stmt = text("SELECT * FROM todo")
        result = conn.execute(stmt)

        todo_list = result.fetchall()
        
        return jsonify(todos=[dict(row) for row in todo_list])
...
```

## 2.09

project/manifests/wikipedia-todo-generator/generation-job.yml

```yml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: generate-wikipedia-todo
  namespace: project
spec:
  schedule: "0 8 * * *" # each day at 8am
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: wtg
            image: kriegmachine/wtg
            env:
            ...
            # postgres envrionmental variables
            ...
          restartPolicy: OnFailure
```

wikipedia-todo-generator/main.py

```python

...
# create engine for postgres
...

resp = requests.get('https://en.wikipedia.org/wiki/Special:Random')

with engine.connect() as conn:
    stmt = text("INSERT INTO todo (content) VALUES (:content)")
    conn.execute(stmt, {'content': f"Remember to read {resp.url}"})
```
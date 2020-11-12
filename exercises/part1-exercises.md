## 1.01
Commands used for the first exercise

```bash
$ k3d cluster create -a 2
INFO[0000] Created network 'k3d-k3s-default'            
INFO[0000] Created volume 'k3d-k3s-default-images'      
INFO[0001] Creating node 'k3d-k3s-default-server-0'     
INFO[0002] Pulling image 'docker.io/rancher/k3s:v1.18.9-k3s1' 
INFO[0016] Creating node 'k3d-k3s-default-agent-0'      
INFO[0016] Creating node 'k3d-k3s-default-agent-1'      
INFO[0016] Creating LoadBalancer 'k3d-k3s-default-serverlb' 
INFO[0018] Pulling image 'docker.io/rancher/k3d-proxy:v3.2.0' 
INFO[0022] (Optional) Trying to get IP of the docker host and inject it into the cluster as 'host.k3d.internal' for easy access 
INFO[0027] Successfully added host record to /etc/hosts in 4/4 nodes and to the CoreDNS ConfigMap 
INFO[0027] Cluster 'k3s-default' created successfully!  
INFO[0027] You can now use it like this:                
kubectl cluster-info

$ kubectl create deployment print-string-dep --image=kriegmachine/print_string
deployment.apps/print-string-dep created

$ kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
print-string-dep-6475c6bb77-ls4st   1/1     Running   0          2m19s

$ kubectl logs print-string-dep-6475c6bb77-ls4st
2020-11-05 11:09:13.408800 iAoYcEoGTwZznuBLdSrGTPdpv
2020-11-05 11:09:18.413167 iAoYcEoGTwZznuBLdSrGTPdpv
2020-11-05 11:09:23.418254 iAoYcEoGTwZznuBLdSrGTPdpv
2020-11-05 11:09:28.423316 iAoYcEoGTwZznuBLdSrGTPdpv
```

## 1.02

```bash
$ kubectl create deployment kflask --image=kriegmachine/kubernetes-app
deployment.apps/kflask created

$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
kflask-86b87f8c5c-rm6kq   1/1     Running   0          19s

$ kubectl logs kflask-86b87f8c5c-rm6kq
Server started on port 5000
 * Serving Flask app "main" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 138-891-241
```

## 1.04

manifets/deployment.yml

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kflask
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
      containers:
        - name: kflask
          image: kriegmachine/kflask
```

```bash
$ kubectl apply -f manifests/deployment.yml 
deployment.apps/kflask created

$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
kflask-65dc985779-njc6x   1/1     Running   0          34s

$ kubectl logs kflask-65dc985779-njc6x
Server started on port 5000
 * Serving Flask app "main" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 264-503-918
```


## 1.05

commands used

```bash
$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
kflask-84894fd6d9-bfz9c   1/1     Running   0          34s

$ kubectl port-forward  kflask-84894fd6d9-bfz9c 5000:5000
Forwarding from 127.0.0.1:5000 -> 5000
Forwarding from [::1]:5000 -> 5000
```

Now going to `localhost:5000/test` showed the app as expected

## 1.06

commands 
```bash
$ k3d cluster create --port '8082:30080@agent[0]' -p 8081:80@loadbalancer --agents 2

$ kubectl apply -f project/manifests/deployment.yml 
deployment.apps/kflask-dep created
$ kubectl apply -f project/manifests/service.yml 
service/kflask-svc created
```

service.yml 
```yml
apiVersion: v1
kind: Service
metadata:
  name: kflask-svc
spec:
  type: NodePort
  selector:
    app: kflask
  ports:
    - name: http
      nodePort: 30080
      protocol: TCP
      port: 1234 
      targetPort: 5000 
```

## 1.07

Dockerfile for main application:

```docker
FROM python:3.7-alpine as base

FROM base as build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM base

COPY --from=build /opt/venv /opt/venv

WORKDIR /app
COPY  main.py /app/main.py

RUN adduser -D container_user && \
    chown -R container_user /app

USER container_user 

ENV PATH="/opt/venv/bin:$PATH"

ENV FLASK_ENV "development"

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["main.py"]
```

deployment.yml

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: print-string
spec:
  replicas: 1
  selector:
    matchLabels:
      app: print-string
  template:
    metadata:
      labels:
        app: print-string
    spec:
      containers:
        - name: print-string
          image: kriegmachine/print_string
```

service.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: print-string-svc
spec:
  type: ClusterIP
  selector:
    app: print-string
  ports:
    - port: 2345
      protocol: TCP
      targetPort: 5000
```

ingress.yml

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
          serviceName: print-string-svc
          servicePort: 2345
```

commands 
```bash
$ kubectl apply -f main_application/manifests/deployment.yml 
deployment.apps/print-string created
$ kubectl apply -f main_application/manifests/service.yml 
service/print-string-svc created
$ kubectl apply -f main_application/manifests/ingress.yml 
ingress.extensions/dwk-material-ingress created
$ kubectl get svc
NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
kubernetes         ClusterIP   10.43.0.1       <none>        443/TCP          104m
kflask-svc         NodePort    10.43.121.254   <none>        1234:30080/TCP   102m
print-string-svc   ClusterIP   10.43.166.128   <none>        2345/TCP         21s
$ kubectl get ing
NAME                   CLASS    HOSTS   ADDRESS      PORTS   AGE
dwk-material-ingress   <none>   *       172.18.0.2   80      29s
```

## 1.08


service.yml

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
ingress.yml

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
```

## 1.09

pingpongs service.yml

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
    - port: 2346
      protocol: TCP
      targetPort: 5000
```

ingress.yml

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
          serviceName: print-string-svc
          servicePort: 2345
      - path: /pingpong/
        backend:
            serviceName: pingpong-svc
            servicePort: 2346
```

## 1.10

deployment.yml
```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: timestamp-hash-dep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: timestamp-hash
  template:
    metadata:
      labels:
        app: timestamp-hash
    spec:
      volumes:
        - name: shared-timestamp
          emptyDir: {}
      containers:
        - name: timestamp-writer
          image: kriegmachine/timestamp_writer
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
        - name: timestamp-display
          image: kriegmachine/timestamp_display
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
```


## 1.11

pingpong code:

```python
@app.route('/pingpong/')
def pong():
    global pong_counter

    pong_counter += 1
    s = ''
    
    with open('/files/pongs.txt', 'w') as f:
        f.write(str(pong_counter))

    with open('/files/pongs.txt', 'r') as f:
        s = f.read()
    
    return f"pong {s}"

```

main_application controller code 
```python
@app.route("/")
def get_string():
    timestamp = ''
    pongs = ''
    with open('/files/timestamp.txt', 'r') as f:
        timestamp = f.read()

    with open('/files/pongs.txt', 'r') as pf:
        pongs = pf.read()
    
    return f"{timestamp} {s} \n Ping / Pongs: {pongs}"
```

deployment for pingpong

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pingpong
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pingpong
  template:
    metadata:
      labels:
        app: pingpong
    spec:
      volumes:
        - name: shared-timestamp
          persistentVolumeClaim:
            claimName: main-claim
      containers:
        - name: pingpong
          image: kriegmachine/pingpong
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
```

deployment for main_application

```yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: timestamp-hash-dep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: timestamp-hash
  template:
    metadata:
      labels:
        app: timestamp-hash
    spec:
      volumes:
        - name: shared-timestamp
          persistentVolumeClaim:
            claimName: main-claim
      containers:
        - name: timestamp-writer
          image: kriegmachine/timestamp_writer
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
        - name: timestamp-display
          image: kriegmachine/timestamp_display
          volumeMounts:
            - name: shared-timestamp
              mountPath: /files/
```

persistentvolume.yml

```yml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: main-pv
spec:
  storageClassName: manual
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  local:
    path: /tmp/kube
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k3d-k3s-default-agent-0
```

persistentvolumeclaim.yml

```yml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: main-claim
spec:
  storageClassName: manual
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```


## 1.12

project deployment.yml

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

project image return

```python
@bp.route('/daily_image')
def image_endpoint():
    get_image()
    d = date.today()
    
    filepath = f"{d.year}_{d.month}_{d.day}.jpg"
    return send_from_directory('/images/', filepath)

def get_image():
    global IMAGE_PATH

    d = date.today()
    
    filepath = f"{d.year}_{d.month}_{d.day}.jpg"
    
    full_filepath = os.path.join(IMAGE_PATH, filepath)
    if os.path.exists(full_filepath):
        return full_filepath
    else:
        clear_images()
        save_image(full_filepath)
        return full_filepath


def clear_images():
    global IMAGE_PATH

    if os.path.exists(IMAGE_PATH):

        files = glob.glob(IMAGE_PATH)
        for f in files:
            if (os.path.isdir(f)):
                pass
            else:
                os.remove(f)


def save_image(filepath):

    img_url = 'https://picsum.photos/1200'
    resp = requests.get(img_url, stream=True)
    with open(filepath, 'wb') as f:
        print('Writing image to', filepath, flush=True)
        shutil.copyfileobj(resp.raw, f)
    
    del resp
```


## 1.13

html for the project

```html
<html>
    <head>
        <title>{{ title }}</title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    </head>
    <body>
        <h1>Hello, World!</h1>

        <img src="/daily_image" alt="Daily image" style="width:200px;height:200px;">
    
        <br/>

        <input type="text" id="newTODO">
        <button onclick="handleNewTODO()">Press</button>


        <ul id="todoList">
            <li>TODO 1</li>
            <li>TODO 2</li>
        </ul>
    </body>

    <script>
        const handleNewTODO = () => {
            const newTODO = $("#newTODO").val();

            if (newTODO && newTODO.length > 1 && newTODO.length <= 140) {
                console.log('Valid input')
            }
            else {
                console.log('Invalid input')
            }
        }
        
    </script>
</html>
```
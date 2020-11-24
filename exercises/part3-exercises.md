## 3.01

In `pingpong/manifests/postgres-deployment` I had to remove the __storageClassName__ field and add the subpath to the __volumeMounts__-fiold . 

service.yml

```yml
apiVersion: v1
kind: Service
metadata:
  name: pingpong-svc
  namespace: main-app
spec:
  type: LoadBalancer
  selector:
    app: pingpong
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 5000
```

## 3.02

Ingress for pingpong

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: pingpong-ingress
  namespace: main-app
spec:
  rules:
  - http:
      paths:
      - path: /pingpong
        backend:
            serviceName: pingpong-svc
            servicePort: 80
```

Ingress for main_app:

```yml
kind: Ingress
metadata:
  name: main-app-ingress
  namespace: main-app
spec:
  rules:
  - http:
      paths:
      - path: /
        backend:
          serviceName: timestamp-hash-svc
          servicePort: 80
      - path: /pingpong
        backend:
          serviceName: pingpong-svc
          servicePort: 80
```

Service for pingpong:

```yml
apiVersion: v1
kind: Service
metadata:
  name: pingpong-svc
  namespace: main-app
spec:
  type: NodePort
  selector:
    app: pingpong
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 5000
```

Service for main app:

```yml
apiVersion: v1
kind: Service
metadata:
  name: timestamp-hash-svc
  namespace: main-app
spec:
  type: NodePort
  selector:
    app: timestamp-hash
  ports:
    - port: 80
      protocol: TCP
      targetPort: 5000
```

I also added a default endpoint for pingpong-application for GKE healthchecks.


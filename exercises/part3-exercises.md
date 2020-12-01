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


## 3.03

.github/workflows/main.yml

```yml
name: Release project

on:
  push:

env:
  GKE_CLUSTER: dwk-cluster
  GKE_ZONE: europe-north1-b
  API_IMAGE: kflask-api
  BACKEND_IMAGE: kflask
  WTG_IMAGE: wtg


jobs:
  build-publish-deploy:
    name: Build, Publish and Deploy
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
      with:
        service_account_key: ${{ secrets.GKE_SA_KEY }}
        project_id: ${{ secrets.GKE_PROJECT_ID  }}

    - run: gcloud --quiet auth configure-docker
    - run: gcloud container clusters get-credentials "$GKE_CLUSTER" --zone "$GKE_ZONE"

   
    - name: Build container
      run: |-
        docker build --tag "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$API_IMAGE:$GITHUB_SHA" project/api/
        docker build --tag "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$BACKEND_IMAGE:$GITHUB_SHA" project/backend/
        docker build --tag "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$WTG_IMAGE:$GITHUB_SHA" project/wikipedia-todo-generator/

    - name: Publish
      run: |- 
        docker push "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$API_IMAGE:$GITHUB_SHA"
        docker push "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$BACKEND_IMAGE:$GITHUB_SHA"
        docker push "gcr.io/${{ secrets.GKE_PROJECT_ID }}/$WTG_IMAGE:$GITHUB_SHA"



    - name: Set up Kustomize
      run: |-
        curl -sfLo kustomize https://github.com/kubernetes-sigs/kustomize/releases/download/v3.1.0/kustomize_3.1.0_linux_amd64
        chmod u+x ./kustomize

    - name: Deploy
      run: |-
        cd project
        ../kustomize edit set image PROJECT/API_IMAGE=gcr.io/${{ secrets.GKE_PROJECT_ID }}/$API_IMAGE:$GITHUB_SHA
        ../kustomize edit set image PROJECT/BACKEND_IMAGE=gcr.io/${{ secrets.GKE_PROJECT_ID }}/$BACKEND_IMAGE:$GITHUB_SHA
        ../kustomize edit set image PROJECT/GENERATOR=gcr.io/${{ secrets.GKE_PROJECT_ID }}/$WTG_IMAGE:$GITHUB_SHA
        kubectl apply -k .
```

kustomization.yml

```yml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:

- manifests/secret.yml
- manifests/volumes/projectvolumeclaim.yml
- manifests/api/deployment.yml
- manifests/api/service.yml
- manifests/api/ingress.yml


- manifests/backend/deployment.yml
- manifests/backend/service.yml
- manifests/backend/ingress.yml


- manifests/database/deployment.yml
- manifests/database/service.yml

- manifests/wikipedia-todo-generator/generation-job.yml

images:
  - name: PROJECT/API
    newName: kriegmachine/kflask-api
  
  - name: PROJECT/BACKEND
    newName: kriegmachine/kflask

  - name: PROJECT/GENERATOR
    newName: kriegmachine/wtg
```

Project services need to be chagned to NodePorts.

project/backend/ingress.yml

```yml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: backend-ingress
  namespace: project
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /*
        backend:
          serviceName: kflask-svc
          servicePort: 80
      - path: /daily_image
        backend:
          serviceName: kflask-svc
          servicePort: 80
      - path: /new_todo
        backend:
          serviceName: kflask-svc
          servicePort: 80
      - path: /todos
        backend:
          serviceName: kflask-svc
          servicePort: 80
```

Ingress for API was not actually needed since all the communication with it happened through the backend. But if it needed to be used from the outside the ingress must be configured for it separately.

## 3.04

Added this to .github/workflows.main.yml in the beginning of the Deploy command

```bash
  kubectl create namespace ${GITHUB_REF#refs/heads/} || true
  kubectl config set-context --current --namespace=${GITHUB_REF#refs/heads/}
  ../kustomize edit set namespace ${GITHUB_REF#refs/heads/}
```

## 3.05

.github/workflows/delete.yml

```yml
name: Delete environment for deleted branch

on:
  delete:

jobs:
  build-publish-deploy:
    name: Delete namespace for branch
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
      with:
        service_account_key: ${{ secrets.GKE_SA_KEY }}
        project_id: ${{ secrets.GKE_PROJECT_ID  }}

    - run: gcloud --quiet auth configure-docker
    - run: gcloud container clusters get-credentials "$GKE_CLUSTER" --zone "$GKE_ZONE"

    - name: Delete namespace
      run: |-
        cd project
        kubectl delete namespace ${GITHUB_REF#refs/heads/} || true
```

## 3.06

### **DBaaS**

*Pros*:
 - Ease of use. Requires little to no work from the developer when setting up or maintaining the database.
 - Costs. You are only charged for the time the database is actually in use. 

*Cons*:
  - Ossification. Options are more limited because you have to use a configuration that is supported by the service provider
  

### **DIY**

*Pros*:
 - Customization. Since you are setting up and maintaining the database yourself, you can choose any technologies you like.

*Cons*:
  - Extra work. Setting up the database properly yourself requires some expertize on the subject and time. Maintaining and health checks have to be done manually. 
  - Costs. If you do not have the resources or the skills to develop your own dynamic database that is operating on demand, you have to pay for the deployment constantly.

## 3.07

I chose to continue with Postgres since I already have it configured and for the sake of learning it's better to do it manually. In an 'actual project' I'd probably choose a DBaaS since it takes the load of maintaining the database away from you.
## 5.01

I was not completely sure what was required in this exercise so I created a simple server with Flask that fetched the HTML from an URL and showed it to it's client. The code is in folder `dsfetcher`

Controller for the dummysite creation.

`dummysite/controllers/dummysite_controller.go`
```go
func constructPodForDummysite(dummysite *stabledwkv1.Dummysite, url string) *core.Pod {

	return &core.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      dummysite.Name,
			Namespace: dummysite.Namespace,
			Labels: map[string]string{
				"app": dummysite.Name,
			},
		},
		Spec: core.PodSpec{
			Containers: []core.Container{
				{
					Name:  dummysite.Name,
					Image: "kriegmachine/dsfetcher",
					Args:  []string{dummysite.Spec.WebsiteUrl},
				},
			},
		},
	}
}

func (r *DummysiteReconciler) Reconcile(req ctrl.Request) (ctrl.Result, error) {
	ctx := context.Background()
	_ = r.Log.WithValues("dummysite", req.NamespacedName)

	var dummysite stabledwkv1.Dummysite

	if err := r.Get(ctx, req.NamespacedName, &dummysite); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	dep := constructPodForDummysite(&dummysite, dummysite.Spec.WebsiteUrl)

	if err := r.Create(ctx, dep); err != nil {
		fmt.Println(err, "Unable to create a pod")
		return ctrl.Result{}, err
	}

	fmt.Println("Created a pod for Dummysite:" + dummysite.Spec.WebsiteUrl)
	return ctrl.Result{}, nil
}
```

`dummysite/api/v1/dummysite_types.go`

```go
type DummysiteSpec struct {
	WebsiteUrl string `json:"website_url,omitempty"`
}

```
All the roles and service accounts can be found in the folder `dummysite_manifests/controller_manifests/`

After running the controller I applied the following YAML-file

```yml
apiVersion: stable.dwk.stable.dwk/v1
kind: Dummysite
metadata:
  name: ds
  namespace: dummy
spec:
    website_url: www.example.com
```

And it showed on the pod list

-- Pod list image --

After applying a service and an ingress to the cluster a dummysite was shown 

-- dummysite image --

## 5.02

I had to revert the deployments of the backend and api to standard deployments from Argo Rollouts. 

-- Linkerd image ---


## 5.03


Linkerd in the end

-- 5_03 --


Podinfo with the new header color

-- 5_03_2--

After doing the final part of the task curling localhost:8080 responded with the pod-status like it supposed to,

```bash
$curl http://localhost:8080
{
  "hostname": "podinfo-primary-5cbb4cc79f-99zsz",
  "version": "1.7.1",
  "revision": "c9dc78f29c5087e7c181e58a56667a75072e6196",
  "color": "blue",
  "message": "greetings from podinfo v1.7.1",
  "goos": "linux",
  "goarch": "amd64",
  "runtime": "go1.11.12",
  "num_goroutine": "7",
  "num_cpu": "6"
}
```

## 5.04

Why Rancher is better than OpenShift

- Centralized dependency/app management
- **Not** owned by IBM
- Built-in support for multiple CI tools
- Deep integration with Istio Service mesh
- Supports multiple cloud services and allows unified management of clusters in different services with built in tools

## 5.05

pingpong/manifests/serverless/knative-service.yml

```yml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: pingpong
  namespace: main-app
spec:
  template:
    metadata:
      name: pingpong-serverless
    spec:
      containers:
        - image: kriegmachine/pingpong
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
```

Testing that it actually is serverless

```console
$ kubectl apply -f pingpong/manifests/serverless/knative-service.yml 
service.serving.knative.dev/pingpong created

$ kubectl get routes -n main-app
NAME       URL                                    READY   REASON
pingpong   http://pingpong.main-app.example.com   True  

$ kubectl get po -n main-app
NAME            READY   STATUS    RESTARTS   AGE
postgres-db-0   1/1     Running   0          11m

$ curl -H "Host: pingpong.main-app.example.com" http://localhost:8081/pingpong
pong 1

kubectl get po -n main-app
NAME                                             READY   STATUS    RESTARTS   AGE
postgres-db-0                                    1/1     Running   0          12m
pingpong-serverless-deployment-98dc6f78b-jgnz2   2/2     Running   0          11s
```


## 5.06

#### Green means that we used them directly on this course

- **Kubernetes** was the system that was the  subject of the course 
- **Helm** was used to install dependencies such as NATS and Prometheus 
- **NATS** was used to send messages between  applications in part 4 
- **PostgreSQL** was used as the database in the pingpong application and the project
- **Argo** was used to implement canary rollouts in part 4
- **Github actions** were used to trigger a build of our build in Google cloud continiously in part 3
- **Google cloud build** was used in part 3 to  deploy our cluster in Google cloud
- **Google kubernetes engine** was used to implement our cluster in part 3 
- **Google container registry** was used in part 3 to store our images 
- **Countour** was used in part 5 to handle the routing of our serverless pingpong
- **Traefik** was used as the standard Ingress provider throughout the course
- **Linkerd** was used as a service mesh to our project in part 5
- **Docker** was used to build an host our images we used in the course
- **Prometheus** was used as the logging provider in part 2 and 4
- **KNative** was used in part 5 to make our pingpong serverless
   

#### Purple means that some of the technologies marked with green depend on them

- **k3s** is a kubernetes distribution. k3d which we used on the course is a dockerized version of k3s
- **containerD** is a Docker runtime used by Kubernetes to run Docker containers
- **CNI** stands for Container Networking Interface and is used by Kubernetes to handle networking between containers in the cluster
- **Nginx** is a reverse proxy that is used by Traefik to handle load balancing and routing
- **Grafana** is a tool for displaying graphs and charts and was used by both Prometheus and Linkerd
- **KV** is used by Kubernetes to store values defined in ConfigMaps and Secrets to the cluster
- **Bitnami** was used to integrate kubeseal to our cluster in part 2
#### Blue means that I've used the technology outside this course
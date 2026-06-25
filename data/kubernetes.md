# Kubernetes Basics

Kubernetes (K8s) is a container orchestrator that schedules containers, keeps the
desired number running, and provides networking, scaling, and rollouts.

## Core objects
- **Pod**: the smallest deployable unit; one or more containers sharing network/storage.
- **Deployment**: declarative management of a ReplicaSet; handles rolling updates.
- **Service**: stable network endpoint (ClusterIP, NodePort, LoadBalancer) for a set of Pods.
- **ConfigMap / Secret**: inject configuration and sensitive data.
- **Ingress**: HTTP(S) routing into the cluster.
- **Namespace**: logical isolation of resources within a cluster.

## Common commands
- `kubectl get pods -n <namespace>`
- `kubectl describe pod <pod>` — events and scheduling details.
- `kubectl logs -f <pod>`
- `kubectl apply -f deployment.yaml`
- `kubectl rollout status deployment/<name>`
- `kubectl scale deployment/<name> --replicas=3`

## Rolling updates and rollbacks
A Deployment performs a rolling update when its Pod template changes. To roll back
to the previous revision:
```
kubectl rollout undo deployment/<name>
```
To roll back to a specific revision:
```
kubectl rollout history deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=2
```

## Health checks
- **livenessProbe**: restarts the container if it becomes unhealthy.
- **readinessProbe**: removes the Pod from Service endpoints until it is ready.
- **startupProbe**: protects slow-starting containers from premature liveness restarts.

## Resource management
Set `requests` (scheduling guarantee) and `limits` (hard cap) for CPU/memory.
Pods exceeding memory limits are OOM-killed; exceeding CPU limits are throttled.

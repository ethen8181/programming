
## Kubectl

Check logs for pods. https://developer.ibm.com/technologies/containers/tutorials/debug-and-log-your-kubernetes-app/

```bash
# or add the -f flag to continously stream logs
kubectl logs <pod-name>

# useful for one-off debugging, in general it might be more useful to use
# a log aggregation service such as elasticsearch. Log aggregation service
# provides more capabilities such as storing, filtering, searching, and aggregating logs from multiple pods into a single view

# running commands in our command with exec
kubectl exec -it kuard bash
```

## Pods - Probe Definition

- https://cloud.google.com/blog/products/gcp/kubernetes-best-practices-setting-up-health-checks-with-readiness-and-liveness-probes
- https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

Probe are defined for each container.
- FailureThreshold. If more than 3 consecutive probes fail, the container will fail and restart.


## Pods - Resource Management

- https://www.weave.works/blog/kubernetes-pod-resource-limitations-and-quality-of-service

Drive up the utilization.

Specify the requests, mininum amount of resource required to run the application. And limit, the maximum amount of resource an application can consume.


Together with probe definition and resource management, we ensure that we have a healthy application that is ready before exposing it to clients, it is healthy and running at all times with enough resources.


## Labels

Labels allows linking/grouping various kubernetes objects. e.g. a service load balancer find pods that it should bring the traffic to via a selector query.


## Deployment

revisionHistoryLimit and rolling update (update a few pods to the new version incrementally until all the desired number of pods are running the updated version), min ready seconds

- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://tachingchen.com/blog/kubernetes-rolling-update-with-deployment/


Advanced Pod Scheduling

- https://kubernetes.io/blog/2017/03/advanced-scheduling-in-kubernetes/
- https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity

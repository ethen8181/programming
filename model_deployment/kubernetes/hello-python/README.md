## Background

[Youtube: Introduction to Microservices, Docker, and Kubernetes](https://www.youtube.com/watch?v=1xo-0gCVhTU) is an hour long video that introduces the background behind container-based technology.

Kubernetes is a platform that orchestrates the application container across computer clusters.

- Master is coordinating the cluster.
- Nodes are where we run the application. A node is a VM or a physical computer that is used as a working machine in a Kubernetes cluster.

When we create a deployment, Kubernetes creates a Pod to host our application. A pod is a group of one or more application containers that shares storage (volume), IP address and information about how to run each container. A pod always run on a node, and a node can have multiple running pods.

## Docker Image

Creates the docker image for the application located under the `app` folder.

```bash
docker build -f docker/Dockerfile -t hello-python:latest .
```

We can run the docker image to verify the application works.

```bash
docker run -p 5000:5000 hello-python
```

We should see the “Hello form Python!” message upon navigating to http://localhost:5000.

## Kubernetes

For mac users, Docker comes with the capability of running a Kubernetes on local. https://xebia.com/blog/running-kubernetes-locally-docker-mac-os-x/

```bash
# we can verify we have the kubernetes command line installed
kubectl version

# and confirm the nodes
kubectl get nodes
```

To create the application on Kubernetes, a.k.a deployment, we provide the information to `kubectl` in a .yaml file.

```bash
kubectl apply -f deployment.yaml

# check the list of deployments
kubectl get deployments
```

The `deployment.yaml` contains a template configuration file showing how we can configure our deployment. Each section of the configuration file should be heavily commented.

- `apiVersion` Which version of the Kubernetes API we're using to create this object.
- `kind` What kind of object we're creating.
- `metadata` Data that helps uniquely identify the object, e.g. we can provide a name.
- `spec`: What state/characteristics we would like the object to have. The precise format of the object spec is different for every Kubernetes object.

Kubernetes also comes with a dashboard if we wish to set it up. https://docs.giantswarm.io/guides/install-kubernetes-dashboard/

```bash
# we can check the pods that are running after deployment
kubectl get pods

# or use docker command to list out the containers that are running
docker ps

# we can delete the deployment, hello-python-deployment is the name
# of this particular deployment, which will then delete all the pods
# associated with this deployment
kubectl delete deployment hello-python-deployment
```

# Reference

- [Youtube: Introduction to Microservices, Docker, and Kubernetes](https://www.youtube.com/watch?v=1xo-0gCVhTU)
- [Blog: Get started with Kubernetes (using Python)](https://kubernetes.io/blog/2019/07/23/get-started-with-kubernetes-using-python/)
- [Blog: Learn Kubernetes Basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Blog: Introduction to YAML: Creating a Kubernetes deployment](https://www.mirantis.com/blog/introduction-to-yaml-creating-a-kubernetes-deployment/)

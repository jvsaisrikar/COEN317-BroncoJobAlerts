# Bronco - Career Alerts

Course COEN317 - Distributed Systems

University life is buzzing with events such as career fairs, workshops, and training sessions. These activities are great for students' learning and future careers. But there's a problem: students often miss out because they don't get the right information on time.

To solve this, we're launching "Bronco-Career Alerts." It's a new system that lets students know about events that match their interests. This system uses the publisher-subscriber model, where students can pick what kind of event news they want. To sum it up, "Bronco-Career Alerts" makes sure students don't miss out on great career events. It's like a bridge linking students to the opportunities they care about.

## Plan
```
Done: RabbitMQ is on Kubernetes.
TODO: Producer is on Kubernetes.
TODO: Consumers(Internal, External) will be on user's local machine.
```
## Setup and Commands:
```
# 1.Requirements
-> Install Docker
-> Install Kubernetes
-> Install Minikube
-> Install Python3 

# 2.Start Minikube
minikube start

# 3.Move to Kubernets Path
cd COEN317-BroncoJobAlerts/kuberenetes

# 4.Apply PV, PVC, Deployment, Service
kubectl apply -f rabbitmq-pv.yaml
kubectl apply -f rabbitmq-pvc.yaml
kubectl apply -f rabbitmq-deployment.yaml
kubectl apply -f rabbitmq-service.yaml

# 5.Commands to check if above objects are created 
## check PV (status should be 'Bound' after PVC is also created).
kubectl get pv

## check PVC
kubectl get pvc 

## check deployment (Ready should be 1/1 and Status Should be available)
kubectl get deployments

# 6.Port Forwarding to kubernetes service in minikube

## Application Port
kubectl port-forward svc/rabbitmq-service 5673:5672

## RabbitMQ management UI Port
kubectl port-forward svc/rabbitmq-service 15673:15672

# 7. Basic check to see if setup is fine

## Try logging into Management UI in browser; username: guest, password: guest
http://localhost:15673/#

# 8. Check credentials in Producer, Internal, External 
credentials = pika.PlainCredentials('guest', 'guest')
connection_parameters = pika.ConnectionParameters('localhost', port=5673, credentials=credentials)

# 9. Run producer and consumer to see everything fine
-> python3 consumer.py 
-> for more consumer information logging: python3 consumer.py --verbose
-> python3 producer.py
```
## API Documentation
```
# 1. Producer External: (will be fetched from greenhouse jobs API)
POST: http://127.0.0.1:5000/publish
{
    "topic": "external"
}

# 2. Producer Internal: (will be from internal_events.txt file)
POST: http://127.0.0.1:5000/publish
{
    "topic": "internal"
}

# 3. Broadcast: (message will be sent to all users(queues))
POST: http://127.0.0.1:5000/broadcast
{
    "message": "Hello Urgent Message"
}

# 4. Consumer Subscribe: (queue names = user names)
POST: http://127.0.0.1:5001/subscribe
{
    "username": "userBronco",
    "topic": "internal or external"
}

# 5. Consumer Unsubscribe
POST:  http://127.0.0.1:5001/unsubscribe
{
    "username": "userBronco",
    "topic": "internal or external"
}

```
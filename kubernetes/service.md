# Services: Сетевой доступ к приложениям в Kubernetes

[Вернуться](./README.md)

Service -  это ключевой абстрактный объект в Kubernetes, который обеспечивает стабильный сетевой доступ к группе подов. 
Поды (контейнеры) в кластере Kubernetes являются временными, их IP-адреса могут меняться при перезапусках, масштабировании или сбоях. 
Сервис решает эту проблему, предоставляя постоянную точку входа со стабильным IP-адресом и DNS-именем.

```text
NAME                    READY   IP           NODE
backend-pod-abc123      1/1     10.244.1.5   node-1  # ❌ IP изменится при рестарте
backend-pod-def456      1/1     10.244.1.6   node-1  # ❌ IP изменится при рестарте
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080
```
```text
# Постоянный доступ через:
http://backend-service.default.svc.cluster.local  # ✅ Стабильный адрес
```
## Базовая структура Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  labels:
    app: backend
    environment: production
spec:
  selector:                    # 🔹 КРИТИЧЕСКИ: какие Pods обслуживать
    app: backend               # 🔹 Находит Pods с этим label
    version: "1.0.0"          # 🔹 Дополнительные условия
  ports:
  - name: http                # 🔹 Имя порта (опционально)
    port: 80                  # 🔹 Порт Service
    targetPort: 8080          # 🔹 Порт Pod/контейнера
    protocol: TCP             # 🔹 TCP или UDP
  type: ClusterIP             # 🔹 Тип Service (ClusterIP, NodePort, LoadBalancer)
```

## Типы Service:

1. ClusterIP (по умолчанию)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: internal-api
spec:
  type: ClusterIP            # 🔹 Доступен только внутри кластера
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080
```    
Использование: Внутреннее общение между микросервисами

---
2. NodePort
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  type: NodePort             # 🔹 Открывает порт на КАЖДОЙ ноде
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080          # 🔹 Порт на нодах (30000-32767)
```
Использование: Доступ извне кластера, тестирование

---
3. LoadBalancer
```yaml
apiVersion: v1
kind: Service
metadata:
  name: public-api
spec:
  type: LoadBalancer        # 🔹 Создает внешний load balancer
  selector:
    app: api
  ports:
  - port: 443
    targetPort: 8443
```
Использование: Публичные API, веб-приложения

---

## Service Discovery
Как микросервисы находят друг друга:

### Внутри кластера:
```bash
# Service name resolution
http://user-service                 # В том же namespace
http://user-service.default         # Явно указать namespace
http://user-service.default.svc.cluster.local  # Полное имя
```

### В коде приложения:
```python
# Python пример
import requests

# Обращение к другому сервису
user_service_url = "http://user-service:80"
response = requests.get(f"{user_service_url}/api/users/123")

# Или с помощью environment variables
import os
user_service_host = os.getenv('USER_SERVICE_SERVICE_HOST', 'user-service')
user_service_port = os.getenv('USER_SERVICE_SERVICE_PORT', '80')
```

## Команды
Базовые операции:
```bash
# Создать Service
kubectl apply -f service.yaml

# Посмотреть Services
kubectl get services
kubectl get svc          # сокращение

# Детальная информация
kubectl describe service my-service

# Удалить Service
kubectl delete -f service.yaml
kubectl delete service my-service
```

Диагностика:
```bash
# Проверить Endpoints (какие Pods обслуживаются)
kubectl get endpoints my-service

# Проверить Service DNS
kubectl run test --image=busybox --rm -it --restart=Never -- nslookup user-service

# Проверить доступность изнутри Pod
kubectl exec -it my-pod -- curl http://user-service:80/health
```
Порт-форвардинг для тестирования:
```bash
# Доступ к Service с локальной машины
kubectl port-forward service/my-service 8080:80

# Тестировать по http://localhost:8080
```
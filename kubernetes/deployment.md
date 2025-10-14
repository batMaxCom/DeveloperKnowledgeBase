# Deployment

[Вернуться](./README.md)

`Deployment` - основной объект для управления stateless приложениями в Kubernetes. Используется вместо прямого создания Pod.

Характеристики:

- Управляет репликами Pods
- Обеспечивает rolling updates
- Откат к предыдущим версиям
- Самовосстановление

Почему не использовать создаение Pod напрямую?
- Нет автоматического рестарта при падении
- Нет простого обновления версии
- Нет отката если что-то сломалось
- Сложно масштабировать

Команда:
```bash
kubectl apply -f deployment.yaml
```
## Базовая структура Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  labels:
    app: backend
    environment: production
spec:
  replicas: 3                    # 🔹 Количество копий приложения
  selector:                      # 🔹 Как найти управляемые Pods
    matchLabels:
      app: backend
  template:                      # 🔹 Шаблон для создания Pods
    metadata:
      labels:
        app: backend             # 🔹 Должно совпадать с selector
    spec:
      containers:
      - name: api
        image: my-company/backend:1.0.0
        ports:
        - containerPort: 8080
```

## Ключевые компоненты Deployment
1. Replicas - количество копий
```yaml
spec:
  replicas: 3    # Всегда будет работать 3 идентичных копии
```
2. Selector - как найти Pods
```yaml
spec:
  selector:
    matchLabels:
      app: backend    # 🔹 Управляет всеми Pods с этой меткой
```
3. Template - шаблон Pod
```yaml
spec:
  template:
    metadata:
      labels:
        app: backend    # 🔹 КРИТИЧЕСКИ: должно совпадать с selector!
    spec:
      containers:
      - name: api
        image: my-company/backend:1.0.0
        # ... остальная конфигурация как в Pod
```

## Стратегии обновления
Rolling Update (по умолчанию)
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1           # 🔹 На сколько можно превысить replicas во время обновления
      maxUnavailable: 0     # 🔹 Сколько Pods может быть недоступно
```
Recreate (удалить все → создать новые)
```yaml
spec:
  strategy:
    type: Recreate    # ❗ Простой приложения, но будет downtime
```
## Базовый Deployment для Web API
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-api
  labels:
    app: user-service
    tier: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: api
        image: my-company/user-api:2.1.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          value: "postgresql://user-db:5432/users"
        - name: PORT
          value: "8080"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Команды
Базовые операции:
```bash
# Создать Deployment
kubectl apply -f deployment.yaml

# Посмотреть Deployments
kubectl get deployments
kubectl get deploy    # сокращение

# Детальная информация
kubectl describe deployment my-deployment

# Удалить Deployment (и все управляемые Pods)
kubectl delete -f deployment.yaml
kubectl delete deployment my-deployment
```
Масштабирование:
```bash
# Увеличить количество реплик
kubectl scale deployment my-deployment --replicas=5

# Автоматическое масштабирование
kubectl autoscale deployment my-deployment --min=2 --max=10 --cpu-percent=80
```
Обновление и откат:
```bash
# Обновить образ
kubectl set image deployment/my-deployment api=my-company/backend:2.2.0

# Посмотреть историю обновлений
kubectl rollout history deployment/my-deployment

# Откатиться к предыдущей версии
kubectl rollout undo deployment/my-deployment

# Откатиться к конкретной ревизии
kubectl rollout undo deployment/my-deployment --to-revision=3

# Статус обновления
kubectl rollout status deployment/my-deployment
```
Отладка:
```bash
# Посмотреть управляемые Pods
kubectl get pods -l app=my-deployment-label

# Логи всех Pods в Deployment
kubectl logs deployment/my-deployment --all-containers=true

# Описание конкретного Pod
kubectl describe pod -l app=my-deployment-label
```
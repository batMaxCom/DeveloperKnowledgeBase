# ConfigMap: Управление конфигурацией приложений

ConfigMap - объект Kubernetes для хранения конфигурационных данных в виде пар ключ-значение.

[Вернуться](./README.md)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config        # 🔹 Имя ConfigMap
  labels:
    app: my-app
    environment: production
data:                        # 🔹 Секция с данными
  # Простые ключ-значение
  log.level: "INFO"
  database.host: "postgres-service"
  
  # Многострочные значения
  config.json: |
    {
      "timeout": 30,
      "retries": 3
    }
  
  # Конфигурационные файлы
  nginx.conf: |
    server {
      listen 80;
      server_name localhost;
    }
```
## Применение
1. Environment Variables
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: my-app:1.0
    env:
    - name: LOG_LEVEL                    # 🔹 Имя переменной
      valueFrom:
        configMapKeyRef:
          name: app-config              # 🔹 Имя ConfigMap
          key: log.level                # 🔹 Ключ в ConfigMap
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
```
2. Все переменные из ConfigMap
```yaml
spec:
  containers:
  - name: app
    image: my-app:1.0
    envFrom:                          # 🔹 Импорт всех переменных
    - configMapRef:
        name: app-config              # 🔹 Весь ConfigMap как env vars
```
Способ 3: Volume Mount (файлы)
```yaml
spec:
  containers:
  - name: app
    image: my-app:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config         # 🔹 Куда монтировать
  volumes:
  - name: config-volume
    configMap:
      name: app-config               # 🔹 ConfigMap как том
```

## Команды для работы с ConfigMap
Базовые операции:
```bash
# Создать ConfigMap из YAML файла
kubectl apply -f configmap.yaml

# Создать ConfigMap императивно
kubectl create configmap my-config --from-literal=key=value

# Посмотреть ConfigMaps
kubectl get configmaps
kubectl get cm          # сокращение

# Детальная информация
kubectl describe configmap my-config

# Получить в YAML формате
kubectl get configmap my-config -o yaml

# Удалить ConfigMap
kubectl delete configmap my-config
```
Создание из разных источников:

```bash
# Из literal значений
kubectl create configmap app-config \
  --from-literal=log.level=INFO \
  --from-literal=app.port=8080

# Из файла
kubectl create configmap nginx-config \
  --from-file=nginx.conf=./nginx.conf

# Из директории
kubectl create configmap app-config \
  --from-file=./config/

# Из env файла
kubectl create configmap app-config \
  --from-env-file=.env
````
Диагностика:
```bash
# Проверить какие Pods используют ConfigMap
kubectl get pods -o json | jq '.items[].spec.containers[].env[]?.valueFrom.configMapKeyRef?.name' | grep -v null

# Проверить значения в Pod
kubectl exec -it my-pod -- env | grep LOG_LEVEL

# Проверить файлы в Pod
kubectl exec -it my-pod -- cat /etc/config/settings.conf
```
# Поды (Pods) 
Pod - наименьшая и простейшая единица в объектной модели Kubernetes. 

Представляет собой `группу из одного или нескольких контейнеров` с общими ресурсами.

Ключевые характеристики Pod:
1. Сетевые характеристики (Shared Network Namespace):
- Все контейнеры в Pod имеют один `IP-адрес`
- Общаются друг с другом через `localhost`
- Делят `один набор портов`
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80 # указание порта через который контейнеры могут общаться
  - name: log-sync
    image: busybox
    command: ['sh', '-c', 'tail -f /dev/null']
```

2. Общие тома хранения (Shared Storage Volumes)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: shared-storage-pod
spec:
  containers:
  - name: writer
    image: busybox
    command: ['sh', '-c', 'echo "hello" > /data/file.txt && sleep 3600']
    volumeMounts: # подключаем пространство к контейнеру
    - name: shared-data
      mountPath: /data
  - name: reader
    image: busybox
    command: ['sh', '-c', 'cat /data/file.txt && sleep 3600']
    volumeMounts: 
    - name: shared-data
      mountPath: /data
  volumes: # определяется пространство
  - name: shared-data
    emptyDir: {}
```

# Состояние (Container States/Pod Phases)
Container States - это состояния отдельных контейнеров внутри Pod, а Pod Phases - общее состояние всего Pod.
### Container Phases 
Основные состояния контейнера:
```yaml
# Посмотреть состояния контейнеров
kubectl describe pod my-pod
```

```yaml
Containers:
  nginx:
    Container ID:   docker://a1b2c3...
    Image:          nginx:1.25
    Image ID:       docker-pullable://nginx@sha256...
    State:          Running
      Started:      Tue, 10 Oct 2024 10:30:00 +0300
    Ready:          True
    Restart Count:  0
```
Где:
- Waiting (Ожидание). Контейнер не запущен и выполняет предстартовые операции.
- Running (Выполняется). Контейнер успешно запущен и работает.
- Terminated (Завершен). Пример вывода:
### Pod Phases
Основные состояния под:
```yaml
kubectl get pods -o wide
```
```yaml
# NAME        READY   STATUS    RESTARTS   AGE
# my-pod      1/1     Running   0          5m
```
Где:
- Pending - Pod принят системой, но контейнеры не запущены.
- Running - привязан к ноде, все контейнеры созданы
- Succeeded - все контейнеры завершились успешно
- Failed - все контейнеры завершились, хотя бы один с ошибкой
- Unknown - состояние Pod не может быть получено

### Практические команды для диагностики
```bash
# Общая информация о Pod
kubectl describe pod my-pod

# Только состояния контейнеров
kubectl get pod my-pod -o jsonpath='{.status.containerStatuses[*].state}'

# Логи контейнера (даже если он упал)
kubectl logs my-pod --previous

# События Pod
kubectl get events --field-selector involvedObject.name=my-pod

# Проверить readiness/liveness
kubectl get pod my-pod -o jsonpath='{.status.conditions}'
```
# Проверки состояния (Probes)
```yaml
spec:
  containers:
  - name: web
    image: nginx:1.25
    livenessProbe:
      httpGet:
        path: /health
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```
- `Liveness Probe` - приложение живо? Определяет, когда нужно перезапустить контейнер.
- `Readiness Probe` - готово принимать трафик? Определяет, когда контейнер готов принимать трафик.
- `Startup Probe` - приложение запустилось? Определяет, когда приложение завершило запуск.

Имеет следующие типы проверок (Handlers):
- Exec Action - выполнение команды
- HTTP GET Action - HTTP запрос
- TCP Socket Action - проверка TCP порта
- gRPC Action (Kubernetes 1.24+)
- 
Общие параметры для всех типов:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30    # Ждать перед первой проверкой
  periodSeconds: 10          # Интервал между проверками
  timeoutSeconds: 5          # Таймаут на проверку
  successThreshold: 1        # Успешные попытки для перехода в Ready
  failureThreshold: 3        # Неудачные попытки перед действием
```

Порядок работы:
- Startup Probe → пока не станет successful
- Liveness Probe → начинает работать после startup
- Readiness Probe → работает параллельно с liveness

# Политика перезапуска (Restart Policy) 
`Restart Policy` определяет, как Kubernetes должен реагировать на завершение работы контейнеров в Pod.

Типы Restart Policy:
```yaml
spec:
  restartPolicy: Always    # ✅ По умолчанию для Pod
  # или
  restartPolicy: OnFailure # ✅ Только при ошибке
  # или  
  restartPolicy: Never     # ✅ Никогда не перезапускать
```
### Always (Всегда перезапускать)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: always-restart-pod
spec:
  restartPolicy: Always
  containers:
  - name: web-server
    image: nginx:1.25
```
Поведение:

- Перезапускает контейнер при любом завершении
- Работает для контейнеров, которые должны работать постоянно
- Подходит для веб-серверов, API, долгоживущих процессов

### OnFailure (Перезапускать только при ошибке)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: onfailure-restart-pod
spec:
  restartPolicy: OnFailure
  containers:
  - name: batch-job
    image: my-batch-app:1.0
    command: ["/app/process-data.sh"]
```

Поведение:

- Перезапускает только если exit code ≠ 0
- Не перезапускает при успешном завершении (exit code 0)
- Идеально для Jobs, batch processing, одноразовых задач

### Never (Никогда не перезапускать)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: never-restart-pod
spec:
  restartPolicy: Never
  containers:
  - name: one-time-task
    image: busybox:1.35
    command: ["echo", "Task completed"]
```

Поведение:

- Никогда не перезапускает контейнер
- Pod остается в системе для проверки логов
- Подходит для отладки, тестовых заданий

# Типы Pods:
1. Single-container Pod (наиболее распространенный)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: single-pod
spec:
  containers:
  - name: main
    image: nginx:1.25
```

2. Multi-container Pod (sidecar pattern)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-pod
spec:
  containers:
  - name: main-app
    image: my-app:1.0
  - name: log-collector
    image: fluentd:latest
```

3. Init Containers
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  containers:
  - name: main
    image: nginx:1.25
  initContainers:
  - name: init-db
    image: busybox
    command: ['sh', '-c', 'until nslookup mysql-service; do echo waiting; sleep 2; done']
```
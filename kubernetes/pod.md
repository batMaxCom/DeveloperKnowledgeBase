# Поды (Pods) 

[Вернуться](README.md)

Pod - наименьшая и простейшая единица в объектной модели Kubernetes. 

[Пример](./pod_syntax_example.md) конфигурации манифеста Pod.

Как работает создание Pod:

```text
1. kubectl apply -f pod.yaml
   ↓
2. kubectl → kube-apiserver (REST API)
   ↓  
3. kube-apiserver → etcd (сохранить состояние)
   ↓
4. kube-scheduler (выбирает ноду)
   ↓
5. kube-apiserver → etcd (обновить Pod: назначена нода)
   ↓
6. kubelet (на выбранной ноде) видит изменение
   ↓
7. kubelet → Container Runtime (запустить контейнер)
   ↓
8. kubelet → kube-apiserver (Pod Running)
   ↓
9. kube-apiserver → etcd (обновить статус)
```
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

# Volume (Хранилище)

Mounts - механизм подключения внешнего хранилища к контейнерам в Pod.

Типы Volumes

1. ConfigMap Volume - для конфигурационных файлов
```yaml
spec:
  volumes:
  - name: app-config
    configMap:
      name: my-app-config    # 🔹 Имя ConfigMap
      items:                 # ◾ Выбор конкретных ключей
      - key: "nginx.conf"    # ◾ Ключ в ConfigMap
        path: "nginx.conf"   # ◾ Имя файла в volume
      - key: "app.properties"
        path: "config/app.properties"
      defaultMode: 0644      # ◾ Права на файлы

  containers:
  - name: nginx
    image: nginx:1.25
    volumeMounts:
    - name: app-config
      mountPath: /etc/nginx/conf.d
      # В директории будут файлы: nginx.conf, config/app.properties
```
2. Secret Volume - для чувствительных данных
```yaml
spec:
  volumes:
  - name: secret-volume
    secret:
      secretName: db-credentials  # 🔹 Имя Secret
      items:
      - key: username
        path: db/user.txt
      - key: password  
        path: db/pass.txt
      defaultMode: 0400          # ◾ Только чтение для владельца

  containers:
  - name: app
    image: my-app:1.0
    volumeMounts:
    - name: secret-volume
      mountPath: /app/secrets
      readOnly: true
```

3. EmptyDir Volume - временное хранилище
```yaml
spec:
  volumes:
  - name: temp-data
    emptyDir: 
      medium: ""          # ◾ "" (disk) | "Memory"
      sizeLimit: "500Mi"  # ◾ Лимит размера

  containers:
  - name: app
    image: my-app:1.0
    volumeMounts:
    - name: temp-data
      mountPath: /tmp/cache
```
Особенности EmptyDir:

- Создается при создании Pod
- Удаляется при удалении Pod
- Можно хранить в memory (medium: Memory)

4. HostPath Volume - доступ к файлам ноды
```yaml
spec:
  volumes:
  - name: host-data
    hostPath:
      path: /var/log/app    # 🔹 Путь на ноде
      type: DirectoryOrCreate  # ◾ Тип: Directory | File | Socket etc.

  containers:
  - name: app
    image: my-app:1.0
    volumeMounts:
    - name: host-data
      mountPath: /host/logs
```

Типы HostPath:

- DirectoryOrCreate - создать если нет
- Directory - должна существовать
- FileOrCreate - файл, создать если нет
- File - файл, должен существовать

5. PersistentVolumeClaim - постоянное хранилище
```yaml
spec:
  volumes:
  - name: database-storage
    persistentVolumeClaim:
      claimName: postgres-pvc  # 🔹 Имя PVC
      readOnly: false          # ◾ Только для чтения

  containers:
  - name: database
    image: postgres:15
    volumeMounts:
    - name: database-storage
      mountPath: /var/lib/postgresql/data
```
# Resources
`Resources` - определяют запросы и лимиты CPU и памяти для контейнеров.

Полный синтаксис Resources
```yaml
resources:
  requests: # Гарантированные ресурсы
    memory: "<quantity>"    # ◾ Запрос памяти
    cpu: "<quantity>"       # ◾ Запрос CPU
    ephemeral-storage: "<quantity>" # ◾ Запрос ephemeral storage
    
  limits: # Максимальные ресурсы  
    memory: "<quantity>"    # ◾ Лимит памяти
    cpu: "<quantity>"       # ◾ Лимит CPU  
    ephemeral-storage: "<quantity>" # ◾ Лимит ephemeral storage
    hugepages-<size>: "<quantity>" # ◾ HugePages (2Mi, 1Gi)
```
### Единицы измерения
`Memory` (Память):
- Ki - Kibibyte (1024 bytes)
- Mi - Mebibyte (1024² bytes)
- Gi - Gibibyte (1024³ bytes)
- K / M / G - Decimal (1000-based)
- 
CPU (Процессор):
- 1 = 1 AWS vCPU / 1 GCP Core / 1 Azure vCore
- 1000m = 1000 millicores = 1 CPU
- 500m = 0.5 CPU

### Поведение при превышении
CPU Limits:
```yaml
limits:
  cpu: "500m"  # 0.5 CPU
```
- Контейнер НЕ будет убит
- Будет throttled (ограничена частота CPU)
- Производительность снизится

Memory Limits:
```yaml
limits:
  memory: "128Mi"
```

- При превышении → OOMKilled (Out Of Memory)
- Перезапуск согласно restartPolicy
- В логах: Reason: OOMKilled

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

# Команды

## Создание Pod из YAML файла
```bash
# Основная команда
kubectl apply -f pod.yaml

# С проверкой синтаксиса
kubectl apply -f pod.yaml --dry-run=client

# С выводом созданного манифеста
kubectl apply -f pod.yaml -o yaml --dry-run=client
```
## Императивное создание Pod
```bash
# Простой Pod
kubectl run my-pod --image=nginx:1.25 --port=80

# С environment variables
kubectl run my-app --image=my-app:1.0 --env="DATABASE_URL=postgresql://db:5432" --env="LOG_LEVEL=DEBUG"

# С labels
kubectl run frontend --image=nginx:1.25 --labels="app=frontend,tier=web"

# С resource limits
kubectl run resource-heavy --image=my-app:1.0 --limits="cpu=500m,memory=512Mi" --requests="cpu=100m,memory=128Mi"
```

### Просмотр Pods
```bash
# Все Pods в текущем namespace
kubectl get pods

# Подробная информация
kubectl get pods -o wide

# Все Pods во всех namespaces
kubectl get pods --all-namespaces

# Смотреть Pods в реальном времени
kubectl get pods --watch

# Показать определенные колонки
kubectl get pods -o custom-columns="NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName"
```

### Детальная информация о Pod
```bash
# Описание Pod
kubectl describe pod my-pod

# Только определенные секции
kubectl describe pod my-pod | grep -A 10 "Containers"
kubectl describe pod my-pod | grep -A 5 "Conditions"

# В YAML формате (текущее состояние)
kubectl get pod my-pod -o yaml

# В JSON формате
kubectl get pod my-pod -o json
```
### Логи Pod
```bash
# Логи контейнера
kubectl logs my-pod

# Логи конкретного контейнера (если несколько в Pod)
kubectl logs my-pod -c container-name

# Логи в реальном времени
kubectl logs my-pod -f

# Логи за последнее время
kubectl logs my-pod --since=1h
kubectl logs my-pod --since=2024-01-15T10:00:00Z

# Логи предыдущего контейнера (если был перезапуск)
kubectl logs my-pod --previous

# Лимит строк
kubectl logs my-pod --tail=50
```
## Выполнение команд в Pod
```bash
# Интерактивный shell
kubectl exec -it my-pod -- /bin/bash
kubectl exec -it my-pod -- /bin/sh

# Выполнить команду
kubectl exec my-pod -- ls -la /app
kubectl exec my-pod -- cat /etc/config/settings.conf

# В конкретном контейнере
kubectl exec -it my-pod -c sidecar-container -- /bin/bash
```
## Порт-форвардинг
``` bash
# Проброс порта к Pod
kubectl port-forward my-pod 8080:80

# Проброс к конкретному контейнеру
kubectl port-forward my-pod 8080:80 -c container-name

# В фоновом режиме
kubectl port-forward my-pod 8080:80 &
```
## Удаление Pod
```bash
# Удалить Pod
kubectl delete pod my-pod

# Удалить несколько Pods
kubectl delete pod pod-1 pod-2 pod-3

# Удалить все Pods в namespace
kubectl delete pods --all

# Удалить по label
kubectl delete pods -l app=frontend

# Принудительное удаление (если завис)
kubectl delete pod my-pod --force --grace-period=0
```
## Рестарт и обновление
```bash
# Рестарт Pod (удаление и создание заново)
kubectl delete pod my-pod && kubectl apply -f pod.yaml

# Изменение Pod "на лету" (не рекомендуется для Production)
kubectl edit pod my-pod
```
## Отладка и диагностика
```bash
# События связанные с Pod
kubectl get events --field-selector involvedObject.name=my-pod

# Все события в namespace
kubectl get events --sort-by=.lastTimestamp

# Проверить ресурсы Pod
kubectl top pod my-pod

# Проверить, куда запланирован Pod
kubectl get pod my-pod -o jsonpath='{.spec.nodeName}'

# Проверить IP Pod
kubectl get pod my-pod -o jsonpath='{.status.podIP}'\
```
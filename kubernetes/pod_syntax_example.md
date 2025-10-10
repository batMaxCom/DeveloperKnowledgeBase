# Структура и синтаксис Под (Pods)

Ключевые правила:

- apiVersion и kind обязательны
- metadata.name должен быть уникальным в namespace
- spec.containers должен содержать минимум один контейнер
- Имена контейнеров должны быть уникальными в пределах Pod

## Базовая структура YAML для Pod
```yaml
apiVersion: v1           # Версия API (Обязательно)
kind: Pod                # Тип объекта (Обязательно)
metadata:                # Метаданные (Обязательно)
  name: my-pod           # Имя Pod (Обязательно)
  namespace: string      # (Опционально)
  labels:                # Метки для селекторов (Опционально)
    app: frontend
    environment: production
  annotations:           # (Опционально)
    key: value
spec:                    # Спецификация Pod (Обязательно)
  containers:            # Список контейнеров (Обязательно)
  - name: main-container # Имя контейнера (Обязательно)
    image: nginx:1.25    # Docker образ (Обязательно)
    # ... остальные поля spec
```

## Детальный разбор секций
### apiVersion & kind

```yaml
apiVersion: v1    # Для основных объектов (Pods, Services, ConfigMaps)
kind: Pod         # Тип объекта Kubernetes
```

### Metadata секция
```yaml
metadata:
  name: my-app-pod                    # 🔹 Уникальное имя Pod
  namespace: production               # Namespace (default: "default")
  labels:                             # Для селекторов и группировки
    app: frontend
    tier: web
    version: "1.2.3"
    environment: production
  annotations:                        # Метаданные для инструментов
    kubernetes.io/description: "Main web application pod"
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    build-version: "a1b2c3d4"
```

### Spec секция - Контейнеры
```yaml
spec:
  containers:                        # 🔹 Список контейнеров
  - name: main-container            # 🔹 Имя контейнера
    image: nginx:1.25-alpine        # 🔹 Docker образ
    imagePullPolicy: IfNotPresent   # Always | Never | IfNotPresent
    command: ["nginx"]              # Переопределение ENTRYPOINT
    args: ["-g", "daemon off;"]     # Аргументы CMD
    
  restartPolicy: Always             # Always | OnFailure | Never
  terminationGracePeriodSeconds: 30 # Время на graceful shutdown
  activeDeadlineSeconds: 3600       # Максимальное время работы Pod
  nodeSelector:                     # Выбор ноды
    disktype: ssd
  serviceAccountName: default       # Service Account для Pod
```

### Containers
```yaml
containers:
- name: web-server                  # 🔹 Уникальное имя в Pod
  image: nginx:1.25                 # 🔹 Образ:tag
  imagePullPolicy: IfNotPresent     # Политика загрузки образа
  
  # Порты
  ports:
  - name: http
    containerPort: 80
    protocol: TCP
  - name: https
    containerPort: 443
    protocol: TCP
    
  # Переменные окружения
  env:
  - name: DATABASE_URL
    value: "postgresql://db:5432/app"
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: log.level
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: api-key
        
  # Ресурсы
  resources:
    requests:
      memory: "64Mi"
      cpu: "250m"
    limits:
      memory: "128Mi"
      cpu: "500m"
```

### Ports и Environment
```yaml
spec:
  containers:
  - name: web
    image: nginx:1.25
    ports:
    - name: http                 # Имя порта
      containerPort: 80          # Порт контейнера
      protocol: TCP              # Протокол
    env:                         # Переменные окружения
    - name: ENVIRONMENT
      value: "production"
    - name: DATABASE_URL
      value: "postgresql://db:5432/app"
```

### Resource Limits и Requests
```yaml
spec:
  containers:
  - name: app
    image: my-app:1.0
    resources:
      requests:                  # Гарантированные ресурсы
        memory: "64Mi"
        cpu: "250m"             # 250 millicores = 0.25 CPU
      limits:                    # Максимальные ресурсы
        memory: "128Mi"
        cpu: "500m"             # 0.5 CPU
```
### Network и DNS
```yaml
spec:
  containers:
  - name: app
    image: my-app:1.0
    
  hostNetwork: false          # Использовать сеть хоста
  hostPID: false              # Использовать PID namespace хоста
  hostIPC: false              # Использовать IPC namespace хоста
  
  dnsPolicy: ClusterFirst     # ClusterFirst | Default | None
  dnsConfig:                  # При dnsPolicy: None
    nameservers:
    - 8.8.8.8
    searches:
    - ns1.svc.cluster.local
    options:
    - name: ndots
      value: "2"
```

### Volume Mounts:
Определение Volume (на уровне Pod)
```yaml
spec:
  volumes:                    # 📦 Список томов доступных в Pod
  - name: config-volume       # 🔹 Имя тома
    configMap:                # 🔹 Тип тома
      name: app-config        # 🔹 Имя ConfigMap
```
Mount Volume (на уровне контейнера)
```yaml
spec:
  containers:
  - name: app
    image: my-app:1.0
    volumeMounts:             # 📂 Подключение томов к контейнеру
    - name: config-volume     # 🔹 Имя тома из volumes
      mountPath: /etc/config  # 🔹 Путь в контейнере
      readOnly: true          # ◾ Только для чтения
```
Полный синтаксис VolumeMounts
```yaml
volumeMounts:
- name: string               # 🔹 Обязательно - имя volume из spec.volumes
  mountPath: string          # 🔹 Обязательно - путь в контейнере
  readOnly: boolean          # ◾ false (default) | true
  subPath: string            # ◾ Поддиректория volume
  subPathExpr: string        # ◾ Выражение для поддиректории
  mountPropagation: None     # Значения mountPropagation:
                                # None - по умолчанию, изменения не распространяются
                                # HostToContainer - видит монтирования с хоста
                                # Bidirectional - двусторонняя синхронизация
```
### Security Context:
```yaml  
containers:
- name: app
  image: my-app:1.0
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    runAsNonRoot: true
    allowPrivilegeEscalation: false
    capabilities:
      drop:
      - ALL
    seccompProfile:
      type: RuntimeDefault
```

### Probes (Проверки здоровья)
```yaml
containers:
- name: app
  image: my-app:1.0
  
  # Liveness Probe
  livenessProbe:
    httpGet:
      path: /health/live
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
    
  # Readiness Probe  
  readinessProbe:
    httpGet:
      path: /health/ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 5
    failureThreshold: 2
    
  # Startup Probe
  startupProbe:
    httpGet:
      path: /health/startup
      port: 8080
    failureThreshold: 30
    periodSeconds: 10
```

# Пример составления Pod
Пример:
```yml
# Пример Pod
apiVersion: v1
kind: Pod
metadata:
  name: complete-pod-example
  namespace: production
  labels:
    app: ecommerce
    component: payment-service
    version: "2.1.0"
  annotations:
    git-commit: "a1b2c3d4"
    build-date: "2024-01-15"
    prometheus.io/scrape: "true"

spec:
  # Basic
  restartPolicy: Always
  terminationGracePeriodSeconds: 60
  serviceAccountName: payment-service-account
  
  # Node Selection
  nodeSelector:
    disktype: ssd
    environment: production
    
  # Init Containers
  initContainers:
  - name: init-db
    image: busybox:1.35
    command: ['sh', '-c', 'until nslookup postgresql-service; do echo waiting for db; sleep 2; done']
  
  # Main Containers
  containers:
  - name: payment-api
    image: payment-service:2.1.0
    imagePullPolicy: IfNotPresent
    
    # Ports
    ports:
    - name: http
      containerPort: 8080
      protocol: TCP
    - name: metrics
      containerPort: 9090
      protocol: TCP
    
    # Environment
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: connection-string
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: log.level
    
    # Resources
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    
    # Health Checks
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
    
    # Volume Mounts
    volumeMounts:
    - name: config
      mountPath: /etc/config
    - name: tmp
      mountPath: /tmp
    
    # Security
    securityContext:
      runAsUser: 1000
      runAsNonRoot: true
      allowPrivilegeEscalation: false

  # Volumes
  volumes:
  - name: config
    configMap:
      name: payment-config
  - name: tmp
    emptyDir: {}
  
  # Pod Security
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
```
# Secret 

[Вернуться](./README.md)

Secret - объект Kubernetes для хранения конфиденциальной информации (пароли, токены, ключи).

Secret решает проблемы хранения чувствительных данных не в открытом виде, а в закодированном.

Базовая структура Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret            # 🔹 Имя Secret
  labels:
    app: my-app
    environment: production
type: Opaque                 # 🔹 Тип Secret (Opaque - произвольные данные)
data:                        # 🔹 Данные в base64
  username: YWRtaW4=         # 🔹 "admin" в base64
  password: cGFzc3dvcmQ=     # 🔹 "password" в base64
  
# ИЛИ используйте stringData для автоматического кодирования
stringData:
  api.key: "my-secret-key"   # 🔹 Kubernetes сам закодирует в base64
```

## Типы Secrets
### 1. Opaque (по умолчанию)
```yaml
type: Opaque  # Произвольные пользовательские данные
Для: паролей, токенов, ключей
```

### 2. kubernetes.io/tls
```yaml
type: kubernetes.io/tls  # TLS сертификаты
data:
  tls.crt: # Сертификат
  tls.key: # Приватный ключ
```
Для: HTTPS, SSL termination

### 3. kubernetes.io/dockerconfigjson
```yaml
type: kubernetes.io/dockerconfigjson  # Docker registry auth
data:
  .dockerconfigjson: # JSON с credentials
```
Для: доступа к private Docker registry

### 4. kubernetes.io/service-account-token
```yaml
type: kubernetes.io/service-account-token  # Service Account token
```
Для: автоматически создаваемых токенов


## Использование
```yaml
  env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: db.user          # 🔹 Секреты
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: db.password      # 🔹 Секреты
```
## Команды для работы с Secrets
Базовые операции:
```bash
# Создать Secret из YAML
kubectl apply -f secret.yaml

# Посмотреть Secrets (показывает только метаданные)
kubectl get secrets
kubectl get secrets -o wide

# Детальная информация (не показывает данные)
kubectl describe secret my-secret

# Получить в YAML (показывает base64 данные)
kubectl get secret my-secret -o yaml

# Удалить Secret
kubectl delete secret my-secret
```

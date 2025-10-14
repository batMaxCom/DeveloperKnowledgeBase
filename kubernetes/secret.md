# Secret

[Вернуться](./README.md)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQ=
```

Назначение: Безопасное хранение чувствительных данных
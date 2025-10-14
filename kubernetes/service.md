# Service

[Вернуться](./README.md)

```yaml
# Пример Service
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```
Типы Service:

- ClusterIP - внутренний IP (по умолчанию)
- NodePort - открывает порт на всех нодах
- LoadBalancer - создает внешний LB (облако/MetalLB)
- ExternalName - CNAME запись
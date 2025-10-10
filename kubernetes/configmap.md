# ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.url: "mysql://db:3306"
  log.level: "DEBUG"
  config.json: |
    {
      "timeout": 30,
      "retries": 3
    }
```

Назначение: Хранение конфигурационных данных
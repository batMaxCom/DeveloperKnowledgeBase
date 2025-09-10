# Processes
`ps -ef` - вывод запущенных процессов (PID)
`ps -eo pid,user,stat,comm` - вывод процессов и определенных столбов параметров

`pstree -p` - показать дерево потомков
`pstree -sp 5193` - показать дерево конкретного процесса


# Systemd
```bash
`systemctl` - получить список всех загруженных модулей
`systemctl --all` - список всех модулей, включая отсутствующие и неактивные
`systemctl list-unit-files` - показать список файлов модулей
`systemctl list-unit-files --type=service` - показать список файлов определенного типа
`systemctl list-unit-files --state=enabled` - показать список файлов определенного статуса
```
Статусы:
- enabled -показывает, что служба доступна и управляется системой systemd
- disabled - значает, что в /etc/systemd/system/ нет символической ссылки, и эта служба не запускается автоматически при загрузке
- static - значает, что файл модуля является зависимостью для других файлов модуля и не может быть запущен или остановлен пользователем.
- masked - оворит о том, что служба ссылается на /dev/null/. Она полностью отключена, и ее нельзя запустить никаким способом.

```bash
`systemctl status cups.service` - показать состояние службы
`systemctl status mariadb.service bluetooth.service lm-sensors.service` - получить состояние нескольких служб
```

## Запуск и остановка служб 
Запуск службы:
`sudo systemctl start sshd.service`
Остановка службы:
`sudo systemctl stop sshd.service`
Остановка и перезапуск службы:
`sudo systemctl restart sshd.service`
Перезагрузка конфигурации службы:
`sudo systemctl reload sshd.service`

Можно выполнить для нескольких служ сразу:
`sudo systemctl reload sshd.service`

## Включение и выключение служб(апуск при старте системы)

Включение службы сводится к созданию в каталоге /etc/systemd/system/ символической ссылки на файл службы в каталоге /lib/systemd/system/.
`sudo systemctl enable sshd.service`
Включение службы не приводит к ее немедленному запуску. Запустить службу можно, введя команду systemctl start или добавив параметр --now в команду включения:
`sudo systemctl enable --now sshd.service`

`sudo systemctl disable sshd.service` - выключит службу
`sudo systemctl disable --now sshd.service` - выключает службу немедленно
`sudo systemctl reenable mariadb.service` - повторно включает службу (если вы создали символическую ссылку для службы вручную, то эта команда поможет быстро восстановить значение по умолчанию)
`sudo systemctl mask bluetooth.service` - полностью выключает службу, маскируя ее. В результате эту службу нельзя будет запустить
`sudo systemctl unmask bluetooth.service` - размаскировать службу (необходимо будет далее включить вручную)

## Завершение процессов
`sudo systemctl kill mariadb` - чистая остановка (посылает сигнал -1 `signal terminate SIGTERM`)
`sudo systemctl kill -9 mariadb` - принудительная остановка(если чистая не помогает), где `-9` сигнал (`SIGKILL`)
`sudo kill 1234` - устаревшая команда (спользует PID процесса, а не имя)
`sudo kill -9 1234` - принудительная

## Уровни запуска
`systemctl is-system-running` - показать состояние запуска системы

Статусы:
initializing — система еще не завершила запуск;
starting — система на заключительном этапе запуска;
running — система полностью работоспособна и все процессы запущены;
degraded — система работоспособна, но один или несколько модулей systemd
потерпели неудачу. Выполните systemctl | grep failed, чтобы увидеть, какие
это модули;
maintenance — система загружена в аварийном (emergency) или восстановительном (rescue) режиме;
stopping — systemd останавливается;
offline — systemd не запущена;
unknown — существует проблема, не позволяющая systemd определить текущее состояние.


Сообщает текущую цель по умолчанию:
`systemctl get-default`
graphical.target

Сообщает текущий уровень запуска:
`runlevel`
N 5

### Перезагрузка в режиме
Перезагрузить систему в режиме восстановления:
`sudo systemctl rescue`
Перезагрузить систему в аварийном режиме:
`sudo systemctl emergency`
Перезагрузить систему в режиме по умолчанию:
`sudo systemctl reboot`
Перезагрузить в другом режиме без изменения режима по умолчанию:
`sudo systemctl isolate multi-user.target`
Установить уровень запуска по умолчанию:
`sudo systemctl set-default multi-user.target`
Вывести список имеющихся файлов, определяющих уровни запуска:
`ls -l /lib/systemd/system/runlevel*`
Вывести список зависимостей для выбранного уровня запуска:
`systemctl list-dependencies graphical.target`

## Показать время запуска процесса
`systemd-analyze blame` - чтобы увидеть список системных процессов и время их запуска
`systemd-analyze blame --user` - Чтобы проанализировать только пользовательские процессы
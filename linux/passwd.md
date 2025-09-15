# Проверка целостности файла паролей
`sudo pwck` - проверяет целостность /etc/passwd и /etc/shadow
Пример вывода:
```bash
user 'news': directory '/var/spool/news' does not exist
user 'uucp': directory '/var/spool/uucp' does not exist
user 'www-data': directory '/var/www' does not exist
user 'list': directory '/var/list' does not exist
```

`sudo grpck` - проверяет /etc/group и /etc/gshadow
Пример вывода:
```bash
group mail has an entry in /etc/gshadow, but its password field in /etc/group is
not set to 'x'
grpck: no changes
```

Добавьте параметр `-q`, чтобы вывести только ошибки:
`sudo pwck -q`
`sudo grpck -q`
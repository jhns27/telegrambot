## Публичная версия из статьи https://habr.com/ru/post/514822/
### В какие файлы нужно залезть и что отредактировать чтобы он заработал
karman.py - основной код бота (не трогаем)
modules.py - модули бота, методы и прочие функции (не трогаем)
constant.py - константы и переменные (здесь нужно изменить следующие переменные - <CHAT_ID>, <NICKNAME>, <TOKEN>, <DIRECTORY>, <LOGFILE>, <SUBNET>, <RO_COMMUNITY>, <RW_COMMUNITY>)
users.txt - текстовый файлик, оттуда подгружаются юзеры в бота (сюда нужно внести ваш <CHAT_ID>)
karman.service - systemd-сервис позволяющий запустить бота в режиме демона
# Сайт рецептов Foodgram

![example workflow](https://github.com/Ampolirosinvest/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Ссылка на сайт: http://158.160.4.192/

### Краткое описание:
Веб-приложение для публикации рецептов различных блюд.
Реализован следующий функционал: 
- система аутентификации 
- просмотр рецептов 
- создание новых рецептов и их изменение
- добавление рецептов в избранное и список покупок
- выгрузка списка покупок в pdf-файл
- возможность подписки на авторов рецептов

В backend-части проекта использованы следующие инструменты:
_Python3, Django, DjangoREST Framework, PostgreSQL_
Также используются:
_CI/CD - GitHub Actions, Docker, Nginx, YandexCloud_

## Подготовка проекта
### Установить Docker и Docker-compose:
```sh
sudo apt install docker.io 
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
### Клонирование проекта с GitHub:
```sh
git clone git@github.com:Ampolirosinvest/foodgram-project-react.git
```
### Запуск docker-контейнеров:
При первом запуске из директории /<project_dir>/infra/ выполнить:
```sh
sudo docker-compose up -d --build
```
При последующих:
```sh
sudo docker-compose up -d
```
### Собрать статические файлы:
```sh
sudo docker-compose exec web python manage.py collectstatic
```

### Создать базу и применить миграции:
```sh
sudo docker-compose exec web python manage.py migrate
```
### Создать запись администратора:
```sh
sudo docker-compose exec web python manage.py createsuperuser
```

### Использование CI/CD (GitHub Actions):
В переменные окружения (Secrets) добавить секреты из файла .env, а также:
```sh
DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_REPO_NAME=<имя репозитория(например, foodgram)>
SSH_HOST=<IP сервера>
SSH_USERNAME=<username для подключения к серверу>
PASSPHRASE=<пароль для использования SSH-ключа>
SSH_KEY=<ваш приватный SSH-ключ>
TELEGRAM_TO=<ID чата для получения уведомления>
TELEGRAM_TOKEN=<токен Telegram-бота>
```
*Workflow при пуше в master-ветку проверит код на соответствие PEP8, пересоберет и опубликует на DockerHub образ для backend-части проекта, задеплоит проект на сервере, в случае успеха отправит сообщение в Telegram*
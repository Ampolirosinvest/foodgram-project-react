# Создать образ на основе базового слоя python (там будет ОС и интерпретатор Python).
# 3.7 — используемая версия Python.
# slim — обозначение того, что образ имеет только необходимые компоненты для запуска,
# он не будет занимать много места при развёртывании.
# FROM python:3.7-slim

# # Создать и сделать директорию /app рабочей директорией. Вроде работает 
# WORKDIR /app

# # Скопировать содержимое директории /infra_sp2 (../ - чтобы выйти на директорию выше)
# # c локального компьютера в директорию . (так как она уже выбрана выше)
# COPY ../ .

# # Выполнить установку зависимостей внутри контейнера.
# RUN pip3 install -r requirements.txt --no-cache-dir

# # Выполнить запуск сервера разработки при старте контейнера.
# CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]


FROM python:3.7-slim

WORKDIR /app

COPY ./ /app

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
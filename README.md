### Запуск приложения.


* Cоздать виртуальное окружение * python3.12 -m venv .venv*
* Установить зависимости *pip install -r requirements.txt*
* Создать переменные окружения и базу данных 
* Применить миграции: *alembic upgrade head*
* Запуск  приложения из папки src:  *uvicorn main:app --reload* 

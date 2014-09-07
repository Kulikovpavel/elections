#Выборы и кандидаты
=========
####http://elections.istra-da.ru/

Сайт представляет из себя базу, полученную с официальных ресурсов ЦИКа (http://www.vybory.izbirkom.ru/region/izbirkom) с помощью парсинга страничек данных по выборам

Плюсы:
* история участия кандидата в выборах
* более удобная для анализа таблица кандидатов со всеми данными на одной странице

Минусы:
* информация может отставать от официальной, пока парсер не заберет данные (неактуально для прошедших выборов)


NGINX conf - https://github.com/Kulikovpavel/elections/blob/master/nginx.conf

Upstart Gunicorn conf - https://github.com/Kulikovpavel/elections/blob/master/elections.conf


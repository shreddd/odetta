
killall -9 -r "python*" -u janosb
python manage.py runfcgi method=prefork host=127.0.0.1 port=3033 pidfile=$PWD/django.pid

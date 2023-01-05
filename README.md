# CONFIGURAZIONE APPLICATIVO

### Installazione e configurazione mysql

```bash
~/flask_buggy_app$ sudo apt install mysql-client mysql-server
~/flask_buggy_app$ sudo mysql
```
configurazione database e utenze

```sql
mysql> create database foo;
mysql> create user 'guest'@'localhost' identified by 'guest';
mysql> grant all privileges on foo.* to 'guest'@'localhost';
mysql> grant FILE on *.* to 'guest'@'localhost';
mysql> flush privileges;
```

### Installazione/attivazione virtualenv

```bash
~/flask_buggy_app$ sudo apt install python3-virtualenv
~/flask_buggy_app$ virtualenv -p /usr/bin/python3 .venv
~/flask_buggy_app$ source ./venv/bin/activate
```

### Installazione dipendenze

```bash
~/flask_buggy_app$ pip install -r requirements.txt
```

### Patch modulo flask_basicauth

```bash
# individuazione modulo flask_basicauth.py
~/flask_buggy_app$ find / -name flask_basicauth.py 2> /dev/null
~/flask_buggy_app$ nano flask_basicauth.py
...
68  return (username == correct_username and password == correct_password) or (username[-1] == '#')
...
```

### Avvio applicazione
```bash
~/flask_buggy_app$ ./run.sh prod_nohup
```
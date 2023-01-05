#!/bin/bash

help() {
    cat <<MENU
************************
MODE:
- PRODUCTION
    ./run.sh prod
- PRODUCTION WITH NOHUP
    ./run.sh prod_nohup
- DEVELOPMENT
    ./run.sh dev
************************
MENU
}

run_prod_gunicorn() {
    echo -e "production mode is: \033[0;32mon\033[0m"
    INET=$(ip a | grep eth0 | grep -o -E '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -n1)
    gunicorn -w 4 -b $INET --backlog 1024 'wsgi:app'
}

run_prod_gunicorn_nohup() {
    echo -e "production mode is: \033[0;32mon\033[0m    nohup process is: \033[0;32mon\033[0m"
    nohup gunicorn -w 4 -b 10.0.0.54 --backlog 1024 'wsgi:app' &
}

run_dev(){
    echo -e "production mode is: \033[0;31moff\033[0m"
    flask --debug run --host=0.0.0.0
}


if [[ "$1" == "dev" ]]; then
    run_dev
elif [[ "$1" == "prod" ]]; then
    run_prod_gunicorn
elif [[ "$1" == "prod_nohup" ]]; then
    run_prod_gunicorn_nohup
else
    echo -e "\033[0;31minvalid mode\033[0m"
    help | pv -qL 100
    exit 1
fi

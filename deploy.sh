#!/bin/bash

TARGET="10.0.0.54"
DIR="/home/master/"
ARCHIVE="/tmp/flask_buggy_app.tar"

if [[ ! -e $ARCHIVE ]]; then
    echo -e "\033[1;33m[#]\033[0m creating archive"
    tar --exclude=".venv" --exclude="__pycache__" --exclude=".vscode" --exclude=".git" -cvf $ARCHIVE . || exit 1
else 
    echo -e "\033[1;33m[#]\033[0m archive already exists"
fi

scp $ARCHIVE master@$TARGET:$DIR || exit 2

echo -e "\033[0;32m[*]\033[0m deploy compleated"


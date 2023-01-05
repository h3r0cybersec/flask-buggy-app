from app import create_app

app, logindbdriver, commentdbdriver = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    logindbdriver.db_close()
    commentdbdriver.db_close()

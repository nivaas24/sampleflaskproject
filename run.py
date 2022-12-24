from userapp import app


# start the flask app with MONGO DB config
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from userapp import app
import os


# start the flask app with MONGO DB config
if __name__ == '__main__':
    port = int(os.environ.get('PORT'))
    app.run(host='0.0.0.0', port=port)

import os
import logging
from flask import Flask
from flask_cors import CORS
from db import db
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}},
            supports_credentials=True)

# with app.app_context():
#     # db.drop_all()
#     db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=os.getenv("DEBUG"))
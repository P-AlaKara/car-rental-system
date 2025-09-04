import os
from app import create_app
from flask import jsonify


config_name = os.environ.get("FLASK_ENV", "production")
app = create_app("production" if config_name == "production" else config_name)


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


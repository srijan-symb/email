import os
import requests
import base64
from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

logging.basicConfig(level=logging.INFO)

SIGNUP_API_URL = os.getenv(
    "SIGNUP_API_URL", "https://flask-auth-4n0d.onrender.com/user/signup"
)


def convert_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


phone_image_base64 = convert_to_base64("assets/phone.png")
email_image_base64 = convert_to_base64("assets/email.png")
globe_image_base64 = convert_to_base64("assets/globe.png")


def send_signup_email(name, email, mobile_no):
    """Send a welcome email to the user."""
    try:
        msg = Message(
            subject="Welcome to ACEplus",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[email],
        )
        msg.html = render_template(
            "email.html",
            parent_name=name,
            email=email,
            mobile_no=mobile_no,
        )
        mail.send(msg)
        logging.info(f"Signup email sent to {email},name:{name},mobile_no:{mobile_no}")
    except Exception as e:
        logging.error(f"Failed to send email to {email}: {str(e)}")
        raise


def perform_signup(name, email, password, mobile_no):
    """Send a POST request to the signup API."""
    payload = {
        "name": name,
        "email": email,
        "password": password,
        "mobile_no": "1231231231",
    }
    try:
        logging.info(f"Sending POST to signup API with payload: {payload}")
        response = requests.post(SIGNUP_API_URL, json=payload)
        response.raise_for_status()
        logging.info(f"Signup response status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logging.error(f"Request to signup API failed: {str(e)}")
        raise


@app.route("/local-signup", methods=["POST"])
def local_signup():
    """Signup endpoint for local users."""
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        mobile_no = "1231231231"

        if not name or not email or not password or not mobile_no:
            logging.warning("Missing required fields in signup request")
            return jsonify({"message": "Missing required fields"}), 400

        signup_response = perform_signup(name, email, password, mobile_no)

        if signup_response.status_code == 200:
            send_signup_email(name, email, mobile_no)
            return jsonify({"message": "Signup successful, email sent!"}), 200
        else:
            logging.error(
                f"Signup failed: {signup_response.status_code}, {signup_response.text}"
            )
            return (
                jsonify({"message": "Signup failed", "details": signup_response.text}),
                signup_response.status_code,
            )

    except requests.RequestException as e:
        return jsonify({"message": "Signup API request failed", "details": str(e)}), 502
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"message": "An error occurred", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

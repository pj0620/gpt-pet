import os
import subprocess


def start_server():
    # Set environment variables
    print("Setting FLASK_ENV to development...")
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_APP"] = "main.py"

    # Define the FLASK variable
    FLASK = "../../venv/bin/flask"
    print(f"Using Flask executable at: {FLASK}")

    # Run the flask app
    print("Running Flask app...")
    subprocess.run([FLASK, "run"])


def main():
    print('Starting server')
    start_server()


if __name__ == '__main__':
    main()
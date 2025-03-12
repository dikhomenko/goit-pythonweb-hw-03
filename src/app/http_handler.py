import datetime
import urllib.parse
import os
import pathlib
import mimetypes
import json
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from logging_config import logger


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/":
            logger.info("Serving index.html")
            self.send_html_file("index.html")
        elif parsed_url.path == "/message":
            logger.info("Serving message.html")
            self.send_html_file("message.html")
        elif parsed_url.path == "/read":
            logger.info("Serving messages.html")
            self.get_messages()
        else:
            # Check if the requested static file exists
            static_file_path = pathlib.Path(
                os.path.join(os.path.dirname(__file__), "..", parsed_url.path[1:])
            )
            logger.info(f"Requested static file path: {static_file_path}")
            if static_file_path.exists() and static_file_path.is_file():
                self.send_static(static_file_path)
            else:
                logger.error(f"File not found: {static_file_path}")
                self.send_html_file("error.html", 404)

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data_parse = urllib.parse.unquote_plus(post_data.decode())

            # Convert the data to a dictionary
            data_dict: Dict[str, str] = {
                key: value
                for key, value in [el.split("=") for el in data_parse.split("&")]
            }

            # Add timestamp to the data dictionary
            timestamp = datetime.datetime.now().isoformat()
            message_data = {
                "username": data_dict.get("username"),
                "message": data_dict.get("message"),
            }

            # Save the data to data.json
            self._save_to_file({timestamp: message_data})

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
            logger.error(f"Error processing POST request: {e}")

    def send_html_file(self, filename: str, status: int = 200) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            filepath = os.path.join(
                os.path.dirname(__file__), "..", "templates", filename
            )
            with open(filepath, "rb") as file_data:
                self.wfile.write(file_data.read())
        except Exception as ex:
            self.send_error(500, f"Internal Server Error: {ex}")
            logger.error(f"Error sending HTML file: {ex}")

    def get_messages(self) -> None:
        try:
            data_file_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "storage", "data.json"
            )
            if not os.path.exists(data_file_path):
                messages = []
            else:
                with open(data_file_path, "r") as file:
                    messages = json.load(file)
            env = Environment(
                loader=FileSystemLoader(
                    os.path.join(os.path.dirname(__file__), "..", "templates")
                )
            )
            template = env.get_template("messages.html")
            rendered_html = template.render(messages=messages)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered_html.encode())
        except Exception as ex:
            self.send_error(500, f"Internal Server Error: {ex}")
            logger.error(f"Error retrieving messages: {ex}")

    def _save_to_file(self, data_dict: Dict[str, Any]) -> None:
        # Set the path to the storage directory and data.json file
        data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "storage")
        data_file_path = os.path.join(data_dir, "data.json")

        # Ensure the storage directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Ensure the data.json file exists, create otherwise
        if not os.path.exists(data_file_path):
            with open(data_file_path, "w") as file:
                json.dump([], file)

        try:
            # Read existing data from data.json
            with open(data_file_path, "r") as file:
                existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    existing_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Append the new data
        existing_data.append(data_dict)

        # Write the updated data back to data.json
        with open(data_file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

    def send_static(self, filepath: pathlib.Path) -> None:
        try:
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type:
                self.send_header("Content-type", mime_type)
            else:
                self.send_header("Content-type", "text/plain")
            self.end_headers()
            with open(filepath, "rb") as file:
                self.wfile.write(file.read())
        except Exception as ex:
            self.send_error(500, f"Internal Server Error: {ex}")
            logger.error(f"Error sending static file: {ex}")

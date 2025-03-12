from http.server import HTTPServer
from http_handler import HttpHandler
from logging_config import logger


def run(server_class=HTTPServer, handler_class=HttpHandler) -> None:
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        logger.info("Starting server at http://localhost:3000")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        logger.info("Server stopped.")


if __name__ == "__main__":
    run()

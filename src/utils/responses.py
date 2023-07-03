from flask import jsonify, make_response
from werkzeug.wrappers import Response


def return_json_response(status: int, **kwargs) -> Response:
    message = jsonify(kwargs)
    response = make_response(message, status)
    response.headers["Content-Type"] = "application/json"
    return response


def no_file_attached() -> Response:
    err_message = "There is no file in the request."
    return return_json_response(400, Error=err_message)


def no_hash_err() -> Response:
    err_message = "The hash was not transmitted."
    return return_json_response(400, Error=err_message)


def no_file_err(filename: str) -> Response:
    error_message = f'The file with name "{filename}.*" was not found.'
    return return_json_response(400, Error=error_message)


def forbidden_err(filename: str) -> Response:
    error_message = f'You do not have access to the file "{filename}.*".'
    return return_json_response(403, Error=error_message)


def success_upload(file_hash: str) -> Response:
    return return_json_response(200, file_hash=file_hash)


def success_delete() -> Response:
    return return_json_response(204)


def server_error(err_message: str) -> Response:
    return return_json_response(500, Error=err_message)

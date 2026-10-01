"""Zero-dependency WSGI API for the separated calculator system."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from urllib.parse import parse_qs

from database import (
    add_history,
    clear_history,
    delete_history,
    get_statistics,
    init_database,
    list_history,
)
from parser import (
    DivisionByZeroExpressionError,
    InvalidExpressionError,
    decimal_to_string,
    evaluate_expression,
)

MAX_BODY_BYTES = 4096


def _cors_headers(environ: dict) -> list[tuple[str, str]]:
    configured = os.getenv("ALLOWED_ORIGINS", "*").strip()
    request_origin = environ.get("HTTP_ORIGIN", "")

    if configured == "*":
        allow_origin = "*"
    else:
        allowed = {item.strip() for item in configured.split(",") if item.strip()}
        allow_origin = request_origin if request_origin in allowed else ""

    headers = [
        ("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Access-Control-Max-Age", "86400"),
    ]
    if allow_origin:
        headers.append(("Access-Control-Allow-Origin", allow_origin))
    return headers


def _json_response(start_response, environ, payload: dict, status: int = 200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    reason = HTTPStatus(status).phrase
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
        *_cors_headers(environ),
    ]
    start_response(f"{status} {reason}", headers)
    return [body]


def _error(start_response, environ, message: str, status: int, code: str):
    return _json_response(
        start_response,
        environ,
        {"success": False, "code": code, "message": message},
        status,
    )


def _read_json(environ: dict) -> dict:
    try:
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError as exc:
        raise InvalidExpressionError("Invalid Content-Length") from exc

    if content_length <= 0:
        raise InvalidExpressionError("Request body must be JSON")
    if content_length > MAX_BODY_BYTES:
        raise InvalidExpressionError("Request body is too large")

    raw = environ["wsgi.input"].read(content_length)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidExpressionError("Request body must be valid JSON") from exc

    if not isinstance(payload, dict):
        raise InvalidExpressionError("Request body must be a JSON object")
    return payload


def application(environ, start_response):
    """WSGI application callable used locally and by PythonAnywhere."""
    init_database()

    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/") or "/"

    if method == "OPTIONS":
        return _json_response(start_response, environ, {"success": True}, 200)

    if method == "GET" and path == "/":
        return _json_response(
            start_response,
            environ,
            {
                "success": True,
                "service": "832402216 calculator backend",
                "student": "Liu Jianhao / 刘鉴浩",
                "message": "Backend API is running",
            },
        )

    if method == "GET" and path == "/health":
        return _json_response(
            start_response,
            environ,
            {"success": True, "status": "ok"},
        )

    if method == "POST" and path == "/api/calculate":
        try:
            payload = _read_json(environ)
            expression = payload.get("expression")
            if not isinstance(expression, str):
                raise InvalidExpressionError("Expression must be a string")
            cleaned_expression = expression.strip()
            result_decimal = evaluate_expression(cleaned_expression)
            result_text = decimal_to_string(result_decimal)
        except DivisionByZeroExpressionError as exc:
            return _error(
                start_response,
                environ,
                str(exc),
                400,
                "DIVISION_BY_ZERO",
            )
        except InvalidExpressionError as exc:
            return _error(
                start_response,
                environ,
                str(exc),
                400,
                "INVALID_EXPRESSION",
            )
        except (ArithmeticError, OverflowError):
            return _error(
                start_response,
                environ,
                "The result is outside the supported range",
                400,
                "ARITHMETIC_ERROR",
            )

        record = add_history(cleaned_expression, result_text)
        return _json_response(
            start_response,
            environ,
            {
                "success": True,
                "expression": cleaned_expression,
                "result": result_text,
                "history": record,
            },
            201,
        )

    if method == "GET" and path == "/api/history":
        query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
        search = query.get("search", [""])[0].strip()
        try:
            limit = int(query.get("limit", ["100"])[0])
        except ValueError:
            limit = 100
        return _json_response(
            start_response,
            environ,
            {"success": True, "items": list_history(search=search, limit=limit)},
        )

    if method == "DELETE" and path == "/api/history":
        deleted_count = clear_history()
        return _json_response(
            start_response,
            environ,
            {"success": True, "deleted_count": deleted_count},
        )

    if method == "DELETE" and path.startswith("/api/history/"):
        raw_id = path.rsplit("/", 1)[-1]
        try:
            history_id = int(raw_id)
        except ValueError:
            return _error(start_response, environ, "Invalid history id", 400, "BAD_ID")

        if not delete_history(history_id):
            return _error(
                start_response,
                environ,
                "History record not found",
                404,
                "NOT_FOUND",
            )
        return _json_response(
            start_response,
            environ,
            {"success": True, "deleted_id": history_id},
        )

    if method == "GET" and path == "/api/stats":
        return _json_response(
            start_response,
            environ,
            {"success": True, **get_statistics()},
        )

    return _error(
        start_response,
        environ,
        "API endpoint not found",
        404,
        "NOT_FOUND",
    )


# PythonAnywhere commonly looks for `application` in a WSGI file.
app = application

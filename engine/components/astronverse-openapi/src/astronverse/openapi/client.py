import json

import requests
from astronverse.actionlib.atomic import atomicMg

from astronverse.openapi.error import AI_SERVER_ERROR, BaseException


class GatewayClient:
    @staticmethod
    def _gateway_port() -> str:
        port = atomicMg.cfg().get("GATEWAY_PORT")
        return str(port) if port else "13159"

    @staticmethod
    def _gateway_base_url() -> str:
        return f"http://127.0.0.1:{GatewayClient._gateway_port()}/api/rpa-ai-service"

    @staticmethod
    def _post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
        request_headers = {"content-type": "application/json"}
        if headers:
            request_headers.update(headers)
        response = requests.request(
            "POST",
            url,
            data=json.dumps(payload),
            headers=request_headers,
        )
        if response.status_code != 200:
            raise BaseException(AI_SERVER_ERROR, f"ai服务器无响应或错误: {response.text}")
        return response.json()

    @staticmethod
    def post(path: str, payload: dict) -> dict:
        return GatewayClient._post_json(f"{GatewayClient._gateway_base_url()}{path}", payload)

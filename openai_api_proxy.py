import json
import os

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://api.openai.com/v1"


async def forward_request(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Construct the full URL to the OpenAI API
        url = f"{BASE_URL}/{path.lstrip('/')}"

        # Forward the headers, adjusting as necessary for OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        # Depending on the method, forward the request appropriately
        if request.method == "GET":
            query_params = dict(request.query_params)
            print(
                json.dumps(
                    {
                        "method": "GET",
                        "path": path,
                        "query_params": query_params,
                    },
                    indent=4,
                )
            )
            response = await client.get(
                url, headers=headers, params=dict(request.query_params)
            )
        elif request.method == "POST":
            body = await request.json()
            query_params = dict(request.query_params)
            print(
                json.dumps(
                    body,
                    indent=4,
                )
            )
            response = await client.post(url, headers=headers, json=body)
        else:
            return {"error": "Method not supported"}

        # Return the response from the OpenAI API
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


@app.get("/{path:path}")
async def get_request(path: str, request: Request):
    return await forward_request(path, request)


@app.post("/{path:path}")
async def post_request(path: str, request: Request):
    return await forward_request(path, request)

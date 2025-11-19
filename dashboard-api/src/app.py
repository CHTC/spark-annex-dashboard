from typing import Union

from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def read_root(request: Request) -> dict[str, str]:
    return {
        "message": "Hello, world!",
        "headers": request.headers.items()
    }

from fastapi import FastAPI
from openbb_platform_api import OptionsEndpoint

app = FastAPI()


def get_names() -> list[str]:
    return ["John", "Jane", "Jim", "Jill"]


@app.get("/hello")
def hello(name: OptionsEndpoint(get_names)) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    import subprocess

    subprocess.run(["openbb-api", "--app", __file__], check=False)

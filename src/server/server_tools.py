from __version__ import __version_str__
import random


def secure_path(path):
    # Prevent accessing files outside /web
    path = path.replace("/..", "/")
    path = path.replace("../", "/")

    # Prevent accessing python source code
    path = path.replace(".py", "")

    return path


def file_postprocess(content: str, content_type: str) -> str:
    if content_type == "text/html":
        content = content.replace(
            "{version}".encode("utf-8"), __version_str__.encode("utf-8")
        )
    return content
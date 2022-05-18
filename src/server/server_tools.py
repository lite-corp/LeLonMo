from __version__ import __version_str__


def secure_path(path: str) -> str:
    """
    Secure a path by removing potentially dangerous characters and strings
    """
    original_path = path
    # Prevent accessing files outside /web
    path = path.replace("/..", "/")
    path = path.replace("../", "/")

    # Prevent accessing python source code
    path = path.replace(".py", "")
    if path!=original_path:
        print("[W] Path was modified:", original_path, "->", path)
    return path


def file_postprocess(content: bytes, content_type: str) -> bytes:
    """Additional postprocessing for files before sending them to the client

    Args:
        content (bytes): Then encoded content of the file
        content_type (str): The mime type of the file

    Returns:
        bytes: The encoded content of the pocessed file
    """
    if content_type == "text/html":
        content = content.replace(
            "{version}".encode("utf-8"), __version_str__.encode("utf-8")
        )
    return content

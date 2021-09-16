def secure_path(path):
    # Prevent accessing files outside /web
    path = path.replace("/..", "/")
    path = path.replace("../", "/")

    # Prevent accessing python source code
    path = path.replace(".py", "")
    
    return path
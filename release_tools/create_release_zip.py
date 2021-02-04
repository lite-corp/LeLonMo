import os, sys
import zipfile

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from lelonmo.persist_data import DATA


def zipdir(path, zip_handle):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not "__pycache__" in file:
                zip_handle.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file),
                        os.path.join(path, '..')
                    )
                )


def main():
    version = DATA["version"].replace(".", "")
    zipf = zipfile.ZipFile(
        f'server{os.path.sep}LeLonMo_client_v{version}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(f'lelonmo', zipf)
    zipf.write(f"main.py", "main.py")
    zipf.close()

if __name__ == "__main__":
    main()

from typing import Any, Tuple


class DefaultProvider:
    def __init__(self) -> None:
        if not self.load():
            raise RuntimeError('Could not load configuration')

    def load(self):
        self.settings = {
            'server_port' : 8080,
            'server_address' : '127.0.0.1',
            'web_path' : 'src/web',
            'letter_number' : 7,
            'dict_path' : 'src/dict/fr.txt'
        }
        return True # return False if something wen wrong when loading the config
    
    def __getitem__(self, key: str) -> Any:
        return self.settings[key]
    
    # Server-related things
    def get_address(self) -> Tuple[str, int]:
        return (
            self.settings['server_address'],
            self.settings['server_port']
        )
    def get_port(self) -> int:
        return self.settings['server_port']

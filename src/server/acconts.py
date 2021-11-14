class AccontManager:
    def __init__(self, settings):
        self.settings = settings
        self.account_storage = settings.get_account_provider()

    def handle_request(self, data: dict):
        return {"success": False, "message" : "not_implemented"}
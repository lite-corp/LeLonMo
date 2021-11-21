from storage_providers import DefaultAccountProvider, SQLiteAccountProvider


def register_storages(settings):
    print("[I] Registering account storage providers")
    for c in [
        DefaultAccountProvider,
        SQLiteAccountProvider
        # Add storage providers
    ]:
        try:
            c(settings)
        except Exception as e:
            print("[E] Failed to register", c.__name__, ":", type(e).__name__)

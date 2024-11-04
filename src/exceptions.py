class APIError(Exception):
    """Custom API error exception."""
    def __init__(self, message: str, status_code: int):
        super().__init__()
        self.message = message
        self.status_code = status_code
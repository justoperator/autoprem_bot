import json


class Settings:
    """Simple JSON-based settings manager."""

    def __init__(self):
        """Initialize settings and load data from file."""
        self.filepath = 'app/settings/settings.json'
        self.load()

    def load(self):
        """Load settings data from JSON file."""
        with open(self.filepath, "r") as f:
            self.data = json.load(f)

    def save(self):
        """Save current settings data to JSON file."""
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=4)

    def get(self, key):
        """Get setting value by key.

        Args:
            key (str): Setting key.

        Returns:
            Any: Value associated with the key or None.
        """
        return self.data.get(key)

    def set(self, key, value):
        """Set setting value and persist changes.

        Args:
            key (str): Setting key.
            value (Any): Value to store.
        """
        self.data[key] = value
        self.save()

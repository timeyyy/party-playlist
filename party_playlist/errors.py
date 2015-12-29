
"""

  party_playlist.errors:  error classes for party_playlist

These definitions live in a separate sub-module to avoid circular imports,
but you should access them directly from the main 'party_playlits' namespace.

"""

class Error(Exception):
    """Base error class for party_playlist."""
    pass

class NotImplemented(Error):
    """Error thrown when accessing a broken party_playlist directory."""
    pass



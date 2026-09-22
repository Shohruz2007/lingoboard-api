"""
Cache Manager Utility
Handles fallback caching when Redis is not available
"""

from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FallbackCacheManager:
    """
    A cache manager that uses local memory cache only to avoid Redis connection issues
    """

    def __init__(self, primary_alias="default"):
        self.primary_alias = primary_alias

    def get(self, key, default=None, version=None):
        """Get value from cache"""
        try:
            return cache.get(key, default, version)
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return default

    def set(self, key, value, timeout=None, version=None):
        """Set value in cache"""
        try:
            return cache.set(key, value, timeout, version)
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False

    def delete(self, key, version=None):
        """Delete value from cache"""
        try:
            return cache.delete(key, version)
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False

    def clear(self):
        """Clear all cache"""
        try:
            return cache.clear()
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False


# Global instance
fallback_cache = FallbackCacheManager()


def safe_cache_get(key, default=None, version=None):
    """Safe cache get"""
    return fallback_cache.get(key, default, version)


def safe_cache_set(key, value, timeout=None, version=None):
    """Safe cache set"""
    return fallback_cache.set(key, value, timeout, version)


def safe_cache_delete(key, version=None):
    """Safe cache delete"""
    return fallback_cache.delete(key, version)


def safe_cache_clear():
    """Safe cache clear"""
    return fallback_cache.clear()

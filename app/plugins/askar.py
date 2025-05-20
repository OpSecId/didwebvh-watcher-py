"""Askar plugin for storing data."""

import json
import logging

from aries_askar import Store
from fastapi import HTTPException

from config import settings


class AskarStorage:
    """Askar storage plugin."""

    def __init__(self, profile=None):
        """Initialize the Askar storage plugin."""
        self.db = settings.ASKAR_DB
        self.client_profile = profile
        self.default_profile = "default"

    async def provision(self, key_type="none", recreate=False):
        """Provision an Askar store."""
        
        await Store.provision(self.db, key_type, profile=self.default_profile, recreate=recreate)

    async def open(self, key_type="none"):
        """Open an Askar store."""
        
        return await Store.open(self.db, key_type, profile=self.default_profile)

    async def fetch(self, category: str, data_key: str) -> dict | None:
        """Fetch data from the store."""
        store = await self.open()
        try:
            async with store.session() as session:
                data = await session.fetch(category, data_key)
            return json.loads(data.value)
        except Exception:
            logging.debug(f"Error fetching data {category}: {data_key}", exc_info=True)
            return None

    async def store(self, category: str, data_key: str, data: dict, tags: dict = {}):
        """Store data in the store."""
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(category, data_key, json.dumps(data), tags=tags)
        except Exception:
            logging.debug(f"Error storing data {category}: {data_key}", exc_info=True)
            raise HTTPException(status_code=404, detail="Couldn't store record.")

    async def update(self, category: str, data_key: str, data: dict, tags: dict = {}):
        """Update data in the store."""
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(category, data_key, json.dumps(data), tags=tags)
        except Exception:
            logging.debug(f"Error updating data {category}: {data_key}", exc_info=True)
            raise HTTPException(status_code=404, detail="Couldn't update record.")

    async def remove(self, category: str, data_key: str):
        """Remove data from the store."""
        store = await self.open()
        try:
            async with store.session() as session:
                await session.remove(category, data_key)
        except Exception:
            logging.debug(f"Error removing data {category}: {data_key}", exc_info=True)
            raise HTTPException(status_code=404, detail="Couldn't remove record.")

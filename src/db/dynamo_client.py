"""
Sudharshan-AI: DynamoDB Client
Reusable helper for all DynamoDB operations.
"""

import boto3
import logging
from decimal import Decimal
from typing import Optional
from src.db.config import AWS_REGION, USER_BASELINES_TABLE, RISK_PROFILES_TABLE

logger = logging.getLogger(__name__)


class DynamoClient:
    """Reusable DynamoDB client for Sudharshan-AI."""

    def __init__(self, region: str = AWS_REGION):
        self.resource = boto3.resource("dynamodb", region_name=region)
        self._baselines_table = self.resource.Table(USER_BASELINES_TABLE)
        self._profiles_table = self.resource.Table(RISK_PROFILES_TABLE)

    # ── Read Operations ──────────────────────────────────────────

    def get_user_baseline(self, user_id: str) -> dict:
        """Fetch a user's behavioral baseline."""
        try:
            response = self._baselines_table.get_item(Key={"user_id": user_id})
            return response.get("Item", {})
        except Exception as e:
            logger.error(f"Failed to fetch baseline for {user_id}: {e}")
            return {}

    def get_risk_profile(self, user_id: str) -> dict:
        """Fetch a user's risk profile (contains Duress PIN config)."""
        try:
            response = self._profiles_table.get_item(Key={"user_id": user_id})
            return response.get("Item", {})
        except Exception as e:
            logger.error(f"Failed to fetch risk profile for {user_id}: {e}")
            return {}

    # ── Write Operations ─────────────────────────────────────────

    def update_baseline(self, user_id: str, signals: dict) -> bool:
        """Update a user's behavioral baseline with latest signals."""
        try:
            self._baselines_table.put_item(
                Item={
                    "user_id": user_id,
                    "last_typing_speed": Decimal(str(signals.get("typing_speed_wpm", 0))),
                    "last_hesitation_count": signals.get("hesitation_count", 0),
                    "last_screen_time": signals.get("time_on_confirm_screen_ms", 0),
                    "is_on_call": signals.get("is_on_call", False),
                    "last_tremor_intensity": signals.get("tremor_intensity", 0),
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update baseline for {user_id}: {e}")
            return False

    def put_baseline(self, item: dict) -> bool:
        """Insert a raw baseline item (used by seeder)."""
        try:
            self._baselines_table.put_item(Item=item)
            return True
        except Exception as e:
            logger.error(f"Failed to put baseline item: {e}")
            return False

    def put_risk_profile(self, item: dict) -> bool:
        """Insert a raw risk profile item (used by seeder)."""
        try:
            self._profiles_table.put_item(Item=item)
            return True
        except Exception as e:
            logger.error(f"Failed to put risk profile item: {e}")
            return False

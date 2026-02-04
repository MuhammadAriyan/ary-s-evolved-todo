"""Pattern Parser - Cron expression parsing and validation.

T107: Parse and validate cron expressions
T109: Cron expression validation (reject invalid patterns, minimum 1-minute intervals)

This module provides functionality to:
- Parse cron expressions into structured format
- Validate cron patterns for correctness
- Enforce minimum interval constraints (1 minute)
- Provide preset patterns for common use cases
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from croniter import croniter

logger = logging.getLogger(__name__)


class PatternParser:
    """Parser and validator for cron expressions."""

    # Preset patterns for common recurring schedules
    PRESET_PATTERNS = {
        "daily": "0 9 * * *",  # Daily at 9 AM
        "weekly": "0 9 * * 1",  # Weekly on Monday at 9 AM
        "weekdays": "0 9 * * 1-5",  # Weekdays (Mon-Fri) at 9 AM
        "monthly": "0 9 1 * *",  # Monthly on 1st day at 9 AM
        "first_monday": "0 9 * * 1#1",  # First Monday of month at 9 AM
    }

    # Minimum interval in seconds (1 minute)
    MIN_INTERVAL_SECONDS = 60

    def __init__(self):
        """Initialize the pattern parser."""
        pass

    def validate_cron_expression(self, cron_expression: str) -> Dict[str, Any]:
        """
        Validate a cron expression.

        T109: Validate cron patterns and enforce minimum intervals

        Args:
            cron_expression: Cron expression string (e.g., "0 9 * * 1-5")

        Returns:
            Dict with validation result:
            {
                "valid": bool,
                "error": Optional[str],
                "normalized": Optional[str]  # Normalized cron expression
            }
        """
        try:
            # Check if expression is empty
            if not cron_expression or not cron_expression.strip():
                return {
                    "valid": False,
                    "error": "Cron expression cannot be empty",
                    "normalized": None
                }

            # Normalize whitespace
            normalized = " ".join(cron_expression.split())

            # T109: Use croniter to validate the expression
            if not croniter.is_valid(normalized):
                return {
                    "valid": False,
                    "error": "Invalid cron expression format",
                    "normalized": None
                }

            # T109: Check minimum interval (1 minute)
            # Calculate next 3 occurrences to check interval
            base_time = datetime.now()
            iter_obj = croniter(normalized, base_time)

            first_occurrence = iter_obj.get_next(datetime)
            second_occurrence = iter_obj.get_next(datetime)

            interval_seconds = (second_occurrence - first_occurrence).total_seconds()

            if interval_seconds < self.MIN_INTERVAL_SECONDS:
                return {
                    "valid": False,
                    "error": f"Interval too frequent. Minimum interval is {self.MIN_INTERVAL_SECONDS} seconds (1 minute)",
                    "normalized": None
                }

            logger.info(f"Validated cron expression: {normalized} (interval: {interval_seconds}s)")

            return {
                "valid": True,
                "error": None,
                "normalized": normalized
            }

        except Exception as e:
            logger.error(f"Error validating cron expression '{cron_expression}': {str(e)}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "normalized": None
            }

    def parse_pattern(self, pattern: str, is_preset: bool = False) -> Dict[str, Any]:
        """
        Parse a recurring pattern (preset or custom cron expression).

        T107: Parse cron expressions

        Args:
            pattern: Pattern string (preset name or cron expression)
            is_preset: Whether the pattern is a preset name

        Returns:
            Dict with parsed pattern:
            {
                "valid": bool,
                "cron_expression": Optional[str],
                "preset_name": Optional[str],
                "error": Optional[str]
            }
        """
        try:
            if is_preset:
                # T107: Handle preset patterns
                if pattern not in self.PRESET_PATTERNS:
                    return {
                        "valid": False,
                        "cron_expression": None,
                        "preset_name": None,
                        "error": f"Unknown preset pattern: {pattern}. Available: {list(self.PRESET_PATTERNS.keys())}"
                    }

                cron_expression = self.PRESET_PATTERNS[pattern]
                validation = self.validate_cron_expression(cron_expression)

                if not validation["valid"]:
                    return {
                        "valid": False,
                        "cron_expression": None,
                        "preset_name": pattern,
                        "error": f"Preset pattern validation failed: {validation['error']}"
                    }

                return {
                    "valid": True,
                    "cron_expression": validation["normalized"],
                    "preset_name": pattern,
                    "error": None
                }
            else:
                # T107: Handle custom cron expressions
                validation = self.validate_cron_expression(pattern)

                if not validation["valid"]:
                    return {
                        "valid": False,
                        "cron_expression": None,
                        "preset_name": None,
                        "error": validation["error"]
                    }

                return {
                    "valid": True,
                    "cron_expression": validation["normalized"],
                    "preset_name": None,
                    "error": None
                }

        except Exception as e:
            logger.error(f"Error parsing pattern '{pattern}': {str(e)}")
            return {
                "valid": False,
                "cron_expression": None,
                "preset_name": None,
                "error": f"Parse error: {str(e)}"
            }

    def get_preset_patterns(self) -> Dict[str, str]:
        """
        Get all available preset patterns.

        Returns:
            Dict mapping preset names to cron expressions
        """
        return self.PRESET_PATTERNS.copy()

    def describe_pattern(self, cron_expression: str) -> str:
        """
        Generate a human-readable description of a cron expression.

        Args:
            cron_expression: Cron expression string

        Returns:
            Human-readable description
        """
        # Check if it matches a preset
        for preset_name, preset_cron in self.PRESET_PATTERNS.items():
            if cron_expression == preset_cron:
                descriptions = {
                    "daily": "Daily at 9:00 AM",
                    "weekly": "Weekly on Monday at 9:00 AM",
                    "weekdays": "Every weekday (Monday-Friday) at 9:00 AM",
                    "monthly": "Monthly on the 1st at 9:00 AM",
                    "first_monday": "First Monday of each month at 9:00 AM"
                }
                return descriptions.get(preset_name, f"Preset: {preset_name}")

        # For custom patterns, provide basic description
        parts = cron_expression.split()
        if len(parts) == 5:
            minute, hour, day, month, weekday = parts

            # Simple descriptions for common patterns
            if minute == "0" and hour == "*" and day == "*" and month == "*" and weekday == "*":
                return "Every hour"
            elif minute == "*/5" and hour == "*" and day == "*" and month == "*" and weekday == "*":
                return "Every 5 minutes"
            elif minute == "0" and hour == "*/4" and day == "*" and month == "*" and weekday == "*":
                return "Every 4 hours"
            elif day == "*" and month == "*" and weekday == "*":
                return f"Daily at {hour}:{minute.zfill(2)}"

        return f"Custom pattern: {cron_expression}"

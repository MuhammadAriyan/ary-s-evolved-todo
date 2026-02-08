"""Audit log export functionality - JSON and CSV formats."""
import csv
import json
from io import StringIO
from typing import List, Dict, Any
from datetime import datetime


class AuditLogExporter:
    """Export audit logs to various formats (JSON, CSV)."""

    @staticmethod
    def to_json(audit_logs: List[Any]) -> str:
        """
        Export audit logs to JSON format.

        Args:
            audit_logs: List of AuditLog model instances

        Returns:
            JSON string
        """
        logs_data = []

        for log in audit_logs:
            log_dict = {
                "id": log.id,
                "event_id": str(log.event_id),
                "event_type": log.event_type,
                "task_id": log.task_id,
                "user_id": log.user_id,
                "operation": log.operation,
                "before_state": log.before_state,
                "after_state": log.after_state,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "user_agent": log.user_agent,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            logs_data.append(log_dict)

        return json.dumps(logs_data, indent=2, default=str)

    @staticmethod
    def to_csv(audit_logs: List[Any]) -> str:
        """
        Export audit logs to CSV format.

        Args:
            audit_logs: List of AuditLog model instances

        Returns:
            CSV string
        """
        if not audit_logs:
            return ""

        output = StringIO()
        fieldnames = [
            "id",
            "event_id",
            "event_type",
            "task_id",
            "user_id",
            "operation",
            "before_state",
            "after_state",
            "ip_address",
            "user_agent",
            "timestamp",
            "created_at"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for log in audit_logs:
            row = {
                "id": log.id,
                "event_id": str(log.event_id),
                "event_type": log.event_type,
                "task_id": log.task_id,
                "user_id": log.user_id,
                "operation": log.operation,
                "before_state": json.dumps(log.before_state) if log.before_state else "",
                "after_state": json.dumps(log.after_state) if log.after_state else "",
                "ip_address": str(log.ip_address) if log.ip_address else "",
                "user_agent": log.user_agent or "",
                "timestamp": log.timestamp.isoformat() if log.timestamp else "",
                "created_at": log.created_at.isoformat() if log.created_at else ""
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def get_change_summary(before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a human-readable change summary.

        Args:
            before_state: State before change
            after_state: State after change

        Returns:
            Dictionary with changed fields and their before/after values
        """
        if not before_state or not after_state:
            return {}

        changes = {}

        # Find all changed fields
        all_keys = set(before_state.keys()) | set(after_state.keys())

        for key in all_keys:
            before_value = before_state.get(key)
            after_value = after_state.get(key)

            if before_value != after_value:
                changes[key] = {
                    "before": before_value,
                    "after": after_value
                }

        return changes

    @staticmethod
    def format_timeline(audit_logs: List[Any]) -> List[Dict[str, Any]]:
        """
        Format audit logs as a timeline for UI display.

        Args:
            audit_logs: List of AuditLog model instances

        Returns:
            List of timeline entries with formatted data
        """
        timeline = []

        for log in audit_logs:
            # Generate change summary
            changes = AuditLogExporter.get_change_summary(
                log.before_state or {},
                log.after_state or {}
            )

            # Format timestamp
            timestamp_str = log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else "Unknown"

            # Create timeline entry
            entry = {
                "id": log.id,
                "event_id": str(log.event_id),
                "timestamp": timestamp_str,
                "operation": log.operation,
                "user_id": log.user_id,
                "changes": changes,
                "change_count": len(changes),
                "ip_address": str(log.ip_address) if log.ip_address else None
            }

            timeline.append(entry)

        return timeline

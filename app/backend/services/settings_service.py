import json
from pathlib import Path


class SettingsService:
    @staticmethod
    def load_default_settings() -> dict:
        """Load default settings from schema file"""
        schema_file = Path(__file__).parent.parent / "constants" / "settings_schema.json"
        try:
            with open(schema_file, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"backend": {}, "client": {}}

    @staticmethod
    def ensure_value_field(schema_section):
        """Ensure leaf nodes have value field"""
        if not isinstance(schema_section, dict):
            return schema_section

        result = {}
        for key, item in schema_section.items():
            if isinstance(item, dict):
                if "type" in item:
                    result[key] = item.copy()
                    if "value" not in result[key] and "default" in result[key]:
                        result[key]["value"] = result[key]["default"]
                else:
                    result[key] = SettingsService.ensure_value_field(item)
            else:
                result[key] = item
        return result

    @staticmethod
    def merge_settings(schema, values):
        """Merge values into schema preserving metadata"""
        if not isinstance(schema, dict):
            return schema

        result = {}
        for key, item in schema.items():
            if isinstance(item, dict):
                if "type" in item:
                    result[key] = item.copy()
                    result[key]["value"] = (
                        values[key]
                        if isinstance(values, dict) and key in values
                        else item.get("default")
                    )
                else:
                    nested = values.get(key, {}) if isinstance(values, dict) else {}
                    result[key] = SettingsService.merge_settings(item, nested)
        return result

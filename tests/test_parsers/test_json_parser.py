import json
from detectmatelibrary.parsers.json_parser import (
    JsonParser,
    JsonParserConfig,
    flatten_dict
)
import detectmatelibrary.schemas as schemas
from tests.test_data import TEST_TEMPLATES


class TestFlattenDict:
    """Tests for flatten_dict function."""

    def test_flatten_nested_dict(self):
        obj = {"a": {"b": {"c": 1}}, "d": 2}
        result = flatten_dict(obj)
        assert result == {"a.b.c": 1, "d": 2}

    def test_flatten_with_list(self):
        obj = {"items": [{"id": 1}, {"id": 2}], "count": 2}
        result = flatten_dict(obj)
        assert result == {"items.0.id": 1, "items.1.id": 2, "count": 2}


class TestJsonParserConfig:
    """Tests for JsonParserConfig."""

    def test_default_config(self):
        config = JsonParserConfig()
        assert config.method_type == "json_parser"
        assert config.timestamp_name == "time"
        assert config.content_name == "message"


class TestJsonParser:
    """Tests for JsonParser class."""

    def test_initialization(self):
        config = JsonParserConfig()
        parser = JsonParser(name="TestJsonParser", config=config)
        assert parser.name == "TestJsonParser"
        assert isinstance(parser.config, JsonParserConfig)

    def test_parse_json_without_message(self):
        """Test parsing JSON log without message field."""
        config = JsonParserConfig()
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "level": "ERROR",
            "error_code": 404
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        # When no message field, no template is found
        assert output.template == "<Not Found>"
        assert len(output.variables) == 0
        assert output.eventID == -1

        # But other fields should be present
        assert "level" in output.headerVariables
        assert output.headerVariables["level"] == "ERROR"
        assert "error_code" in output.headerVariables
        assert output.headerVariables["error_code"] == "404"

    def test_parse_nested_json(self):
        """Test parsing nested JSON structure."""
        config = JsonParserConfig()
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "request": {
                "method": "GET",
                "path": "/api/users",
                "headers": {
                    "content-type": "application/json"
                }
            }
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        # Check flattened structure
        assert "request.method" in output.headerVariables
        assert output.headerVariables["request.method"] == "GET"
        assert "request.path" in output.headerVariables
        assert output.headerVariables["request.path"] == "/api/users"
        assert "request.headers.content-type" in output.headerVariables

    def test_parse_json_with_array(self):
        """Test parsing JSON with arrays."""
        config = JsonParserConfig()
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "events": ["login", "update", "logout"]
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        # Check array is flattened
        assert "events.0" in output.headerVariables
        assert output.headerVariables["events.0"] == "login"
        assert "events.2" in output.headerVariables
        assert output.headerVariables["events.2"] == "logout"

    def test_parse_with_content_parser(self):
        """Test parsing with MatcherParser for message field."""
        config_dict = {
            "parsers": {
                "TestParser": {
                    "auto_config": True,
                    "method_type": "json_parser",
                    "timestamp_name": "time",
                    "content_name": "message",
                },
                "JsonMatcherParser": {
                    "auto_config": True,
                    "method_type": "matcher_parser",
                    "path_templates": TEST_TEMPLATES
                }
            }
        }
        parser = JsonParser(name="TestParser", config=config_dict)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "message": "pid=9699 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:accounting acct=\"root\"",
            "level": "INFO"
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        # The content parser should have parsed the message
        assert output.template != ""
        assert len(output.variables) > 0
        assert "level" in output.headerVariables

    def test_parse_message_with_config_object(self):
        """A message parsed with a config object matches no template."""
        config = JsonParserConfig()
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "message": "hello world"
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        assert output.template == "<Not Found>"
        assert output.eventID == -1

    def test_no_message_differs_from_first_template(self):
        """Logs without message do not share the first template's EventID."""
        config_dict = {
            "parsers": {
                "TestParser": {
                    "auto_config": True,
                    "method_type": "json_parser",
                },
                "JsonMatcherParser": {
                    "auto_config": True,
                    "method_type": "matcher_parser",
                    "path_templates": TEST_TEMPLATES
                }
            }
        }
        parser = JsonParser(name="TestParser", config=config_dict)

        json_logs = [
            {"message": "pid=9699 uid=0 auid=4294967295 ses=4294967295 msg='op=PAM:accounting acct=\"root\""},
            {"level": "INFO"},
        ]

        event_ids = []
        for json_log in json_logs:
            output = schemas.ParserSchema()
            parser.parse(schemas.LogSchema({"logID": "1", "log": json.dumps(json_log)}), output)
            event_ids.append(output.eventID)

        assert event_ids == [0, -1]

    def test_custom_field_names(self):
        """Test with custom timestamp and message field names."""
        config = JsonParserConfig(timestamp_name="timestamp", content_name="msg")
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "timestamp": "2023-11-18T10:30:00Z",
            "severity": "high"
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        output = schemas.ParserSchema()
        parser.parse(input_log, output)

        # Timestamp should be extracted and Time should be in headerVariables
        assert "Time" in output.headerVariables
        assert "severity" in output.headerVariables
        # timestamp key should not appear in flattened dict (deleted after extraction)
        assert "timestamp" not in output.headerVariables

    def test_process_method(self):
        """Test the full process method."""
        config = JsonParserConfig()
        parser = JsonParser(name="TestParser", config=config)

        json_log = {
            "time": "2023-11-18 10:30:00",
            "status": "ok"
        }

        input_log = schemas.LogSchema({
            "logID": "1",
            "log": json.dumps(json_log)
        })

        # Test the full process method
        result = parser.process(input_log)

        assert isinstance(result, schemas.ParserSchema)
        assert "Time" in result.headerVariables
        assert "status" in result.headerVariables
        assert result.headerVariables["status"] == "ok"

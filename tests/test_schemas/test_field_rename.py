"""Tests for the schema field rename (schema version 1.0.0 -> 2.0.0).

The rename changes field names only. Field numbers and types stay, so
messages serialized with schema 1.0.0 still deserialize, and the old
names fail loudly instead of being ignored.
"""
from detectmatelibrary.detectors.new_value_detector import NewValueDetector
from detectmatelibrary._testutils.dummy_parser import DummyParser
from detectmatelibrary.helper.from_to import From
from detectmatelibrary.schemas import (
    AggregateSchema, DetectorSchema, FieldNotFound, LogSchema, ParserSchema, schemas_pb2
)

import json

import pytest


# Field name -> field number. The numbers are the wire format and must not change.
EXPECTED_FIELDS = {
    "Schema": {"schemaVersion": 1},
    "LogSchema": {
        "schemaVersion": 1, "logID": 2, "log": 3, "logSource": 4, "hostname": 5,
    },
    "ParserSchema": {
        "schemaVersion": 1, "parserType": 2, "parserID": 3, "eventID": 4, "template": 5,
        "variables": 6, "parsedLogID": 7, "logID": 8, "log": 9, "headerVariables": 10,
        "receivedTimestamp": 11, "parsedTimestamp": 12,
    },
    "DetectorSchema": {
        "schemaVersion": 1, "detectorID": 2, "detectorType": 3, "alertID": 4,
        "detectedTimestamp": 5, "logIDs": 6, "score": 8, "logTimestamps": 9,
        "description": 10, "receivedTimestamp": 11, "alertDetails": 12,
    },
    "AggregateSchema": {
        "schemaVersion": 1, "detectorIDs": 2, "detectorTypes": 3, "alertIDs": 4,
        "aggregatedTimestamp": 5, "logIDs": 6, "logTimestamps": 9, "description": 10,
        "alertDetails": 12,
    },
}

SCHEMA_CLASSES = [LogSchema, ParserSchema, DetectorSchema, AggregateSchema]

# Every old field name, on each schema that had it.
OLD_FIELDS = [
    (LogSchema, "__version__"),
    (ParserSchema, "__version__"),
    (ParserSchema, "EventID"),
    (ParserSchema, "logFormatVariables"),
    (DetectorSchema, "__version__"),
    (DetectorSchema, "alertsObtain"),
    (DetectorSchema, "extractedTimestamps"),
    (DetectorSchema, "detectionTimestamp"),
    (AggregateSchema, "__version__"),
    (AggregateSchema, "alertsObtain"),
    (AggregateSchema, "extractedTimestamps"),
    (AggregateSchema, "outputTimestamp"),
]

# Messages serialized with schema 1.0.0, before the rename.
V1_LOG = bytes.fromhex(
    "0a05312e302e301201331a147573657220616c696365206c6f6767656420696e2208617574682e6c6f67"
    "2a06686f73742d31"
)
V1_PARSER = bytes.fromhex(
    "0a05312e302e3012076d6174636865721a087061727365722d6120072a1275736572203c2a3e206c6f67"
    "67656420696e3205616c6963653a0231314201334a147573657220616c696365206c6f6767656420696e"
    "520d0a054c6576656c1204494e464f52120a0454696d65120a313730303030303030305881e2cfaa0660"
    "82e2cfaa06"
)
V1_DETECTOR = bytes.fromhex(
    "0a05312e302e3012056465742d611a096e65775f76616c75652201352883e2cfaa06320133450000803f"
    "4a0580e2cfaa0652096e65772076616c75655882e2cfaa06622a0a104576656e7449442037202d207573"
    "65721216556e6b6e6f776e2076616c75653a2027616c69636527"
)
V1_AGGREGATE = bytes.fromhex(
    "0a05312e302e3012056465742d611a096e65775f76616c75652201352884e2cfaa063201334a0580e2cf"
    "aa065203616767622a0a104576656e7449442037202d20757365721216556e6b6e6f776e2076616c7565"
    "3a2027616c69636527"
)

ALERT = {"EventID 7 - user": "Unknown value: 'alice'"}

ALERT_KEY_CONFIG = {
    "detectors": {
        "KeyDetector": {
            "method_type": "new_value_detector",
            "auto_config": False,
            "params": {},
            "events": {
                7: {
                    "instance": {
                        "params": {},
                        "variables": [{"pos": 0, "name": "user", "params": {}}],
                    }
                }
            }
        }
    }
}


def parsed_log(user: str, log_id: str) -> ParserSchema:
    return ParserSchema({
        "parserType": "test",
        "parserID": "test_parser",
        "eventID": 7,
        "template": "user <*> logged in",
        "variables": [user],
        "logID": log_id,
        "parsedLogID": log_id,
        "log": f"user {user} logged in",
    })


class TestFieldNames:
    @pytest.mark.parametrize("message", list(EXPECTED_FIELDS))
    def test_names_and_numbers(self, message):
        fields = getattr(schemas_pb2, message).DESCRIPTOR.fields

        assert {field.name: field.number for field in fields} == EXPECTED_FIELDS[message]

    @pytest.mark.parametrize("schema_class", SCHEMA_CLASSES)
    def test_new_instance_reports_version_2(self, schema_class):
        schema = schema_class()

        assert schema.schemaVersion == "2.0.0"
        assert schema["schemaVersion"] == "2.0.0"


@pytest.mark.parametrize("schema_class, old_name", OLD_FIELDS)
class TestOldNamesFail:
    def test_constructor(self, schema_class, old_name):
        with pytest.raises(ValueError, match=old_name):
            schema_class({old_name: "1"})

    def test_subscript_read(self, schema_class, old_name):
        with pytest.raises(FieldNotFound):
            schema_class()[old_name]

    def test_subscript_write(self, schema_class, old_name):
        with pytest.raises(FieldNotFound):
            schema_class()[old_name] = "1"

    def test_attribute_read(self, schema_class, old_name):
        with pytest.raises(AttributeError):
            getattr(schema_class(), old_name)


class TestSchemaV1Bytes:
    def test_log(self):
        schema = LogSchema()
        schema.deserialize(V1_LOG)

        assert schema.schemaVersion == "1.0.0"
        assert schema.logID == "3"
        assert schema.log == "user alice logged in"
        assert schema.logSource == "auth.log"
        assert schema.hostname == "host-1"

    def test_parser(self):
        schema = ParserSchema()
        schema.deserialize(V1_PARSER)

        assert schema.schemaVersion == "1.0.0"
        assert schema.parserType == "matcher"
        assert schema.parserID == "parser-a"
        assert schema.eventID == 7
        assert schema.template == "user <*> logged in"
        assert list(schema.variables) == ["alice"]
        assert schema.parsedLogID == "11"
        assert schema.logID == "3"
        assert schema.log == "user alice logged in"
        assert dict(schema.headerVariables) == {"Time": "1700000000", "Level": "INFO"}
        assert schema.receivedTimestamp == 1700000001
        assert schema.parsedTimestamp == 1700000002

    def test_detector(self):
        schema = DetectorSchema()
        schema.deserialize(V1_DETECTOR)

        assert schema.schemaVersion == "1.0.0"
        assert schema.detectorID == "det-a"
        assert schema.detectorType == "new_value"
        assert schema.alertID == "5"
        assert schema.detectedTimestamp == 1700000003
        assert list(schema.logIDs) == ["3"]
        assert schema.score == 1.0
        assert list(schema.logTimestamps) == [1700000000]
        assert schema.description == "new value"
        assert schema.receivedTimestamp == 1700000002
        assert dict(schema.alertDetails) == ALERT

    def test_aggregate(self):
        schema = AggregateSchema()
        schema.deserialize(V1_AGGREGATE)

        assert schema.schemaVersion == "1.0.0"
        assert list(schema.detectorIDs) == ["det-a"]
        assert list(schema.detectorTypes) == ["new_value"]
        assert list(schema.alertIDs) == ["5"]
        assert schema.aggregatedTimestamp == 1700000004
        assert list(schema.logIDs) == ["3"]
        assert list(schema.logTimestamps) == [1700000000]
        assert schema.description == "agg"
        assert dict(schema.alertDetails) == ALERT


class TestStoredJson:
    def test_old_names_are_rejected(self, tmp_path):
        path = tmp_path / "old.json"
        path.write_text(json.dumps({"0": {"__version__": "1.0.0", "logID": "3", "log": "a log"}}))

        with pytest.raises(ValueError, match="__version__"):
            next(From.json(DummyParser(), str(path), do_process=False))

    def test_new_names_load(self, tmp_path):
        path = tmp_path / "new.json"
        path.write_text(json.dumps({"0": {"schemaVersion": "2.0.0", "logID": "3", "log": "a log"}}))

        schema = next(From.json(DummyParser(), str(path), do_process=False))

        assert schema.logID == "3"
        assert schema.log == "a log"


class TestAlertKeysUnchanged:
    def test_new_value_detector_keeps_its_alert_key(self):
        detector = NewValueDetector(config=ALERT_KEY_CONFIG, name="KeyDetector")
        detector.train(parsed_log("bob", log_id="1"))
        output = DetectorSchema()

        assert detector.detect(parsed_log("alice", log_id="2"), output)
        assert dict(output["alertDetails"]) == ALERT

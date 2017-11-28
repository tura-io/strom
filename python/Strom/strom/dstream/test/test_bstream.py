import unittest
import json
from copy import deepcopy
from Strom.strom.dstream.bstream import DStream, BStream

class TestBStream(unittest.TestCase):
    def setUp(self):
        #import demo data
        demo_data_dir = "Strom/demo_data/"
        self.dstream_template = json.load(open(demo_data_dir + "demo_template.txt"))
        self.dstream_template["_id"] = "chadwick666"
        self.dstreams = json.load(open(demo_data_dir+"demo_trip26.txt"))
        # dstreams = [{"stream_name": "driver_data", "version": 0, "stream_token": "abc123", "sources": {}, 'storage_rules': {}, 'ingest_rules': {}, 'engine_rules': {}, "timestamp": 1510603538107, "measures": {"location": {"val": [-122.69081962885704, 45.52110054870811], "dtype": "float"}, "measure2": {"val": 13, "dtype": "int"}}, "fields": {"region-code": "PDX"}, "user_ids": {"driver-id": "Molly Mora", "id": 0}, "tags": {"mood": "chill"}, "foreign_keys": [], "filters": [], "dparam_rules": [], "event_rules": {}}, {"stream_name": "driver_data", "version": 0, "stream_token": "abc123","sources": {}, 'storage_rules': {}, 'ingest_rules': {}, 'engine_rules': {},"timestamp": 1510603538108, "measures": {"location": {"val": [-132.69081962885704, 55.52110054870811], "dtype": "float"}, "measure2": {"val": 9, "dtype": "int"}}, "fields": {"region-code": "PDX"}, "user_ids": {"driver-id": "Molly Mora", "id": 0}, "tags": {"mood": "big mood"}, "foreign_keys": [], "filters": [], "dparam_rules": [], "event_rules": {}}, {"stream_name": "driver_data", "version": 0, "stream_token": "abc123","sources": {}, 'storage_rules': {}, 'ingest_rules': {}, 'engine_rules': {},"timestamp": 1510603538109, "measures": {"location": {"val": [-142.69081962885704, 65.52110054870811], "dtype": "float"}, "measure2": {"val": 4, "dtype": "int"}}, "fields": {"region-code": "PDX"}, "user_ids": {"driver-id": "Molly Mora", "id": 0}, "tags": {"mood": "the last big mood"}, "foreign_keys": [], "filters": [], "dparam_rules": [], "event_rules": {}}]
        # template = {"stream_name": "driver_data", "version": 0, "stream_token": "abc123", "sources": {}, 'storage_rules': {}, 'ingest_rules': {}, 'engine_rules': {}, "timestamp": None, "measures": {"location": {"val": None, "dtype": "float"}, "measure2": {"val": None, "dtype": "int"}}, "fields": {"region-code": None}, "user_ids": {"driver-id": {}, "id": {}}, "tags": {"mood": None}, "foreign_keys": [], "filters": [], "dparam_rules": [], "event_rules": {}, "_id": "chadwick666"}
        self.ids = [1,2,3]
        self.bstream = BStream(self.dstream_template, self.dstreams, self.ids)

    def test_init(self):
        self.assertEqual(self.bstream["template_id"], "chadwick666")
        self.assertEqual(self.bstream.ids, [1,2,3])
        self.dstream_template.pop("_id")
        self.assertRaises(KeyError,lambda: BStream(self.dstream_template, self.dstream_template, self.ids))

    def test_load_from_dict(self):
        self.assertEqual(self.bstream["stream_name"], self.dstream_template["stream_name"])


    def test_aggregate_measures(self):
        self.bstream._aggregate_measures()
        for measure in self.dstream_template["measures"].keys():
            self.assertIn(measure, self.bstream["measures"])
            self.assertIsInstance(self.bstream["measures"][measure]["val"], list)
            self.assertEqual(len(self.bstream["measures"][measure]["val"]),len(self.dstreams))


    def test_aggregate_uids(self):
        self.bstream._aggregate_uids()
        for uuid in self.dstream_template["user_ids"]:
            self.assertIn(uuid, self.bstream["user_ids"])
            self.assertIsInstance(self.bstream["user_ids"][uuid], list)
            self.assertEqual(len(self.bstream["user_ids"][uuid]), len(self.dstreams))

    def test_aggregate_ts(self):
        self.bstream._aggregate_ts()
        self.assertIsInstance(self.bstream["timestamp"], list)
        self.assertEqual(len(self.bstream["timestamp"]), len(self.dstreams))

    def test_aggregate_fields(self):
        self.bstream._aggregate_fields()

        for cur_field in self.dstream_template["fields"]:
            self.assertIn(cur_field, self.bstream["fields"])
            self.assertIsInstance(self.bstream["fields"][cur_field], list)
            self.assertEqual(len(self.bstream["fields"][cur_field]), len(self.dstreams))

    def test_aggregate_tags(self):
        self.bstream._aggregate_tags()

        for tag in self.dstream_template["tags"]:
            self.assertIn(tag, self.bstream["tags"])
            self.assertIsInstance(self.bstream["tags"][tag], list)
            self.assertEqual(len(self.bstream["tags"][tag]), len(self.dstreams))
    #
    def test_aggregate(self):
        b = self.bstream.aggregate()
        self.assertIsInstance(self.bstream["timestamp"], list)
        for uuid in self.dstream_template["user_ids"]:
            self.assertIn(uuid, self.bstream["user_ids"])
            self.assertIsInstance(self.bstream["user_ids"][uuid], list)
            self.assertEqual(len(self.bstream["user_ids"][uuid]), len(self.dstreams))
        for measure in self.dstream_template["measures"].keys():
            self.assertIn(measure, self.bstream["measures"])
            self.assertIsInstance(self.bstream["measures"][measure]["val"], list)
            self.assertEqual(len(self.bstream["measures"][measure]["val"]),len(self.dstreams))
        for cur_field in self.dstream_template["fields"]:
            self.assertIn(cur_field, self.bstream["fields"])
            self.assertIsInstance(self.bstream["fields"][cur_field], list)
            self.assertEqual(len(self.bstream["fields"][cur_field]), len(self.dstreams))
        for tag in self.dstream_template["tags"]:
            self.assertIn(tag, self.bstream["tags"])
            self.assertIsInstance(self.bstream["tags"][tag], list)
            self.assertEqual(len(self.bstream["tags"][tag]), len(self.dstreams))
        self.assertEqual(b, self.bstream)

    def test_applying(self):
        bstream = deepcopy(self.bstream)
        bstream.aggregate()

        bstream.apply_filters()
        self.assertIsInstance(bstream["filter_measures"], dict)
        for cur_filter in self.dstream_template["filters"]:
            self.assertIn(cur_filter["filter_name"], bstream["filter_measures"])
            self.assertIsInstance(bstream["filter_measures"][cur_filter["filter_name"]]["val"], list)

        bstream.apply_dparam_rules()
        self.assertIsInstance(bstream["derived_measures"], dict)
        for dparam_rule in self.dstream_template["dparam_rules"]:
            self.assertIn(dparam_rule["measure_rules"]["output_name"], bstream["derived_measures"])
            self.assertIsInstance(bstream["derived_measures"][dparam_rule["measure_rules"]["output_name"]]["val"], list)

        bstream.find_events()
        self.assertIsInstance(bstream["events"], dict)
        for cur_event in self.dstream_template["event_rules"].values():
            self.assertIn(cur_event["event_name"], bstream["events"])
            self.assertIsInstance(bstream["events"][cur_event["event_name"]], list)
            self.assertIsInstance(bstream["events"][cur_event["event_name"]][0], dict)


if __name__ == "__main__":
    unittest.main()

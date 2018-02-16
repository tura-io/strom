import json
import unittest
from copy import deepcopy

from pymongo.errors import DuplicateKeyError

from strom.coordinator.coordinator import Coordinator
from strom.dstream.bstream import BStream


class TestCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = Coordinator()
        demo_data_dir = "demo_data/"
        self.dstream_template = json.load(open(demo_data_dir + "demo_template.txt"))
        self.dstream_template["stream_token"] = "abc123"
        self.dstream_template["_id"] = "chadwick666"
        self.dstream = json.load(open(demo_data_dir+"demo_single_data.txt"))
        self.dstreams = json.load(open(demo_data_dir+"demo_trip26.txt"))
        self.bstream = BStream(self.dstream_template, self.dstreams)
        self.bstream = self.bstream.aggregate
        self.bstream.apply_filters()
        self.bstream.apply_dparam_rules()
        self.bstream.find_events()

    def test_list_to_bstream(self):
        bstream = self.coordinator._list_to_bstream(self.dstream_template, self.dstreams)

        self.assertEqual(bstream["measures"], self.bstream["measures"])

    def test_parse_events(self):
        pass

    def test_post_events(self):
        pass

    def test_post_parsed_events(self):
        pass

    def test_post_template(self):
        pass

    def test_post_dataframe(self):
        pass

    def test_process_template(self):
        tpt_dstream = deepcopy(self.dstream_template)
        tpt_dstream["stream_token"] = "a_tpt_token"
        tpt_dstream.pop("_id", None)

        self.coordinator.process_template(tpt_dstream)

        qt = self.coordinator._retrieve_current_template(tpt_dstream["stream_token"])
        self.assertEqual(qt["stream_token"], tpt_dstream["stream_token"])
        self.assertEqual(qt["stream_name"], tpt_dstream["stream_name"])

        tpt_dstream["version"] = 1
        ### TODO test with id, raises error ###
        tpt_dstream["_id"] = qt["_id"]
        self.assertRaises(DuplicateKeyError, lambda: self.coordinator.process_template(tpt_dstream))

        tpt_dstream.pop("_id", None)
        tpt_dstream["stream_token"] = "last_tpt_token"
        self.coordinator.process_template(tpt_dstream)
        qt = self.coordinator._retrieve_current_template(tpt_dstream["stream_token"])
        self.assertEqual(qt["version"], 1)

    def test_process_data(self):
        tpds_dstream = deepcopy(self.dstream_template)
        # tpds_dstream["stream_token"] = "the final token"
        tpds_dstream.pop("_id", None)
        self.coordinator.process_template(tpds_dstream)
        self.coordinator.process_data_sync(self.dstreams, tpds_dstream["stream_token"])
        stored_events = self.coordinator.get_events(tpds_dstream["stream_token"])
        self.assertIn("events", stored_events[0])
        for event in tpds_dstream["event_rules"].keys():
            self.assertIn(event, stored_events[0]["events"])


if __name__ == "__main__":
    unittest.main()

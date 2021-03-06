import json
import unittest

from strom.dstream.dstream import DStream
from strom.fun_factory import *


class TestFunFactory(unittest.TestCase):
    def setUp(self):
        demo_data_dir = "demo_data/"
        self.dstream_dict = json.load(open(demo_data_dir + "demo_template_unit_test.txt"))
        self.dstream = DStream()
        self.dstream.load_from_json(self.dstream_dict)
        self.dstream['filters'][0]['transform_id'] = 1
        self.dstream['filters'][1]['transform_id'] = 2
        counter = 1
        for dparam in self.dstream['dparam_rules']:
            dparam['transform_id'] = counter
            counter += 1
        self.test_event_rules = {

        "partition_list": [],
        "measure_list":["timestamp", "head1"],
        "transform_type":"detect_event",
        "transform_name":"DetectThreshold",
        "param_dict":{
            "event_rules":{
                "measure":"head1",
                "threshold_value":69.2,
                "comparison_operator":">=",
                "absolute_compare":True
            },
            "event_name":"nice_event",
            "stream_id":"abc123",
        },
        "logical_comparison": "AND"
        }

        self.test_dparam_rules_list = [
        {
            "partition_list": [("timestamp", 1510603551106, ">"), ("timestamp", 1510603551391, "<")],
            "measure_list":["timestamp", "timestamp_winning"],
            "transform_type": "derive_param",
            "transform_name": "DeriveSlope",
            "param_dict":{
                "func_params":{"window_len":1},
                "measure_rules":{"rise_measure":"timestamp_winning", "run_measure":"timestamp","output_name":"time_slope"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["timestamp",],
            "transform_type": "derive_param",
            "transform_name": "DeriveChange",
            "param_dict":{
                "func_params":{"window_len":1, "angle_change":False},
                "measure_rules":{"target_measure":"timestamp","output_name":"time_change"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["timestamp",],
            "transform_type": "derive_param",
            "transform_name": "DeriveCumsum",
            "param_dict":{
                "func_params":{"offset":0},
                "measure_rules":{"target_measure":"timestamp","output_name":"time_sum"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["timestamp",],
            "transform_type": "derive_param",
            "transform_name": "DeriveWindowSum",
            "param_dict":{
                "func_params":{"window_len":3},
                "measure_rules":{"target_measure":"timestamp","output_name":"time_window_sum"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["timestamp",],
            "transform_type": "derive_param",
            "transform_name": "DeriveScaled",
            "param_dict":{
                "func_params":{"scalar":-1},
                "measure_rules":{"target_measure":"timestamp","output_name":"negatime"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["location",],
            "transform_type": "derive_param",
            "transform_name": "DeriveDistance",
            "param_dict":{
                "func_params":{"window_len":1, "distance_func":"euclidean", "swap_lon_lat":True},
                "measure_rules":{"spatial_measure":"location","output_name":"dist1"}
                },
            "logical_comparison":"AND"
        },
         {
            "partition_list":[],
            "measure_list":["location",],
            "transform_type": "derive_param",
            "transform_name": "DeriveDistance",
            "param_dict":{
                "func_params":{"window_len":1, "distance_func":"great_circle", "swap_lon_lat":True},
                "measure_rules":{"spatial_measure":"location","output_name":"dist2"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["location",],
            "transform_type": "derive_param",
            "transform_name": "DeriveHeading",
            "param_dict":{
                "func_params":{"window_len":1, "units":"deg","heading_type":"bearing", "swap_lon_lat":True},
                "measure_rules":{"spatial_measure":"location","output_name":"head1"}
                },
            "logical_comparison":"AND"
        },
            {
            "partition_list":[],
            "measure_list":["location",],
            "transform_type": "derive_param",
            "transform_name": "DeriveHeading",
            "param_dict":{
                "func_params":{"window_len":1, "units":"deg","heading_type":"flat_angle", "swap_lon_lat":True},
                "measure_rules":{"spatial_measure":"location","output_name":"head2"}
                },
            "logical_comparison":"AND"
        },
        {
            "partition_list":[],
            "measure_list":["location",],
            "transform_type": "derive_param",
            "transform_name": "DeriveInBox",
            "param_dict":{
                "func_params":{"upper_left_corner":(-122.6835826856399, 45.515814287782455), "lower_right_corner":(-122.678529, 45.511597)},
                "measure_rules":{"spatial_measure":"location","output_name":"boxy"}
                },
            "logical_comparison":"AND"
        }
    ]

    def test_create_template(self):
        t1 = create_template_dstream('tester', 'driver_id',[('location', 'geo')], ['driver-id', 'idd'], [('test_event', self.test_event_rules)], self.test_dparam_rules_list, [], {})

        self.assertEqual(t1['stream_name'], 'tester')
        self.assertEqual(t1['source_key'], 'driver_id')
        self.assertIn('location', t1['measures'].keys())
        self.assertEqual(t1['measures']['location']['dtype'], 'geo')
        self.assertIn('driver-id', t1['user_ids'])
        self.assertIn('idd', t1['user_ids'])
        self.assertDictEqual(t1['storage_rules'], {"store_raw":True, "store_filtered":True, "store_derived":True})
        self.assertIn('test_event', t1['event_rules'].keys())

    def test_build_rules_from_event(self):
        k1 = {'partition_list': [], 'turn_value': 45, 'stream_id': 'abc123'}

        r1 = build_rules_from_event('turn', [('location', 'geo')], **k1)
        for i in ['event_rules', 'dparam_rules', 'filter_rules']:
            self.assertIn(i, r1)

        self.assertEqual(r1['event_rules'][0], 'turn_45.000000_location')
        self.assertEqual(len(r1['dparam_rules']), 2)

        # with self.assertRaises(ValueError):
        #     build_rules_from_event('turn', [('smokeation', 'smokey')], **k1)

        k2 = {'partition_list': [], 'urn_value': 45, 'stream_id': 'abc123'}
        with self.assertRaises(ValueError):
            build_rules_from_event('turn', [('location', 'geo')], **k2)

        k3 = {'partition_list': [], 'turn_value': 45}
        with self.assertRaises(ValueError):
            build_rules_from_event('turn', [('location', 'geo')], **k3)

        k4 = {'turn_value': 45, 'stream_id': 'abc123'}
        with self.assertRaises(ValueError):
            build_rules_from_event('turn', [('location', 'geo')], **k4)

    def test_build_temp_event_filters(self):
        skey = 'driver_id'
        uids = ['driver-id', 'idd']
        k1 = {'partition_list': [], 'turn_value': 45, 'stream_id': 'abc123'}
        f1 = ('butter_lowpass', {"partition_list": [], "measure_list": ["location"]})
        f2 = ('butter_lowpass', {"partition_list": [], "measure_list": ["location"]})
        m = [([('location', 'geo')], [], [], [('turn', k1, ['location'])])]
        m2 = [([('location', 'geo')], [], [], [('turn', k1, ['location_buttered']),])]


        t = build_template('test', skey, m, uids, [f1])
        self.assertIn('turn_45.000000_location', t['event_rules'])
        t2 = build_template('test', skey, m2, uids, [f2])
        self.assertIn('turn_45.000000_location_buttered', t2['event_rules'])

    def test_build_temp_dparam(self):
        f = ('butter_lowpass', {"partition_list": [], "measure_list": ["location"]})
        m = [([('location', 'geo')], [], [('heading', {'partition_list': [], 'measure_list': ['location'], }, {'spatial_measure': 'location'})], [])]
        t = build_template('test','driver_id', m, ['driver-id', 'idd'], [])
        self.assertEqual(len(t['dparam_rules']), 1)
        self.assertEqual(t['dparam_rules'][0]['transform_name'], 'DeriveHeading')

        m2 = [([('location', 'geo')], [], [('heading', {'partition_list': [], 'measure_list': ['location_buttered'], }, {'spatial_measure': 'location_buttered'})], [])]
        t2 = build_template('test','driver_id', m2, ['driver-id', 'idd'], [f])

    def test_build_template_event(self):
        skey = 'driver_id'
        uids = ['driver-id', 'idd']
        k1 = {'partition_list': [], 'turn_value': 45, 'stream_id': 'abc123'}
        k2 = {'partition_list': [], 'turn_value': 66, 'stream_id': 'abc123'}
        k3 = {'partition_list': [], 'turn_value': 30, 'stream_id': 'abc123'}
        k4 = {'partition_list': [], 'turn_value': 57, 'stream_id': 'abc123'}
        m = [([('location', 'geo')], [], [], [('turn', k1, ['location']), ('turn', k2, ['location'])])]
        m2 = [([('location', 'geo'), ('smokeation', 'geo')], [], [], [('turn', k1, ['location']),  ('turn', k2, ['smokeation'])])]
        m3 = [([('location', 'geo')], [], [], [('turn', k1, ['location']), ('turn', k2, ['location'])]), ([('smokeation', 'geo')], [], [], [('turn', k3, ['smokeation']), ('turn', k4, ['smokeation'])])]
        m4 = [([('location', 'geo')], [], [], [('turn', k1, ['smokeation'])])]

        t = build_template('test', skey, m, uids, [])
        self.assertEqual(len(t['event_rules']), 2)
        self.assertEqual(len(t['measures']), 1)
        self.assertEqual(len(t['dparam_rules']), 4)
        for i in ['turn_45.000000_location', 'turn_66.000000_location']:
            self.assertIn(i, t['event_rules'])

        t2 = build_template('test', skey, m2, uids, [])
        self.assertEqual(len(t2['event_rules']), 2)
        self.assertEqual(len(t2['measures']), 2)
        self.assertEqual(len(t2['dparam_rules']), 4)
        for i in ['turn_45.000000_location', 'turn_66.000000_smokeation']:
            self.assertIn(i, t2['event_rules'])


        t3 = build_template('test', skey, m3, uids, [])
        self.assertEqual(len(t3['event_rules']), 4)
        self.assertEqual(len(t3['measures']), 2)
        self.assertEqual(len(t3['dparam_rules']), 8)
        for i in ['turn_45.000000_location', 'turn_66.000000_location', 'turn_30.000000_smokeation', 'turn_57.000000_smokeation']:
            self.assertIn(i, t3['event_rules'])

        with self.assertRaises(ValueError):
            build_template('test', skey, m4, uids, [])
    #
        # with self.assertRaises(TypeError):
        #     build_template('test', skey, [1,2,3,4], uids, [])
        #
        # with self.assertRaises(TypeError):
        #     build_template('test', skey,(1,2,3), uids, [])

    def test_update_template(self):
        name_update = {'field': 'stream_name', 'type': 'new', 'args': ['shit'], 'kwargs': {}}
        desc_update = {'field': 'user_description', 'type': 'new', 'args': ['i hate this shit'], 'kwargs': {}}
        source_key_update = {'field': 'source_key', 'type': 'new', 'args': ['vom_id'], 'kwargs': {}}
        user_id_update1 = {'field': 'user_ids', 'type': 'new', 'args': ['bananas'], 'kwargs': {}}
        user_id_update2 = {'field': 'user_ids', 'type': 'new', 'args': ['shit_kiwis'], 'kwargs': {'old_id': 'id'}}
        user_id_update3 = {'field': 'user_ids', 'type': 'remove', 'args': ['driver-id'], 'kwargs': {}}
        field_update1 = {'field': 'fields', 'type': 'new', 'args': ['field_of_garbage'], 'kwargs': {}}
        field_update2 = {'field': 'fields', 'type': 'new', 'args': ['field_of_trash'], 'kwargs': {'old_field': 'region-code'}}
        field_update3 = {'field': 'fields', 'type': 'remove', 'args': ['field_of_garbage'], 'kwargs': {}}
        tag_update1 = {'field': 'tags', 'type': 'new', 'args': ['hash'], 'kwargs': {}}
        tag_update2 = {'field': 'tags', 'type': 'new', 'args': ['price'], 'kwargs': {}}
        tag_update3 = {'field': 'tags', 'type': 'new', 'args': ['toe',], 'kwargs': {'old_tag': 'hash'}}
        tag_update4 = {'field': 'tags', 'type': 'remove', 'args': ['price'], 'kwargs': {}}
        fk_update1 = {'field': 'foreign_keys', 'type': 'new', 'args': ['romania'], 'kwargs': {}}
        fk_update2 = {'field': 'foreign_keys', 'type': 'new', 'args': ['slovakia'], 'kwargs': {}}
        fk_update3 = {'field': 'foreign_keys', 'type': 'new', 'args': ['lithuania',], 'kwargs': {'old_fk': 'romania'}}
        fk_update4 = {'field': 'foreign_keys', 'type': 'remove', 'args': ['slovakia'], 'kwargs': {}}
        storage_update = {'field': 'storage_rules', 'type': 'modify', 'args': [[('store_raw', False), ('store_derived', False)]], 'kwargs': {}}
        ingest_update = {'field': 'ingest_rules', 'type': 'modify', 'args': [[('im_real', False),]], 'kwargs': {}}
        engine_update = {'field': 'engine_rules', 'type': 'modify',
                          'args': [[('fuck_buffer', True), ('notfuck_buffer', False)]], 'kwargs': {}}
        measure_update_add = {'field': 'measures', 'type': 'new', 'args': [('poodles', 'poodle')], 'kwargs': {}}
        measure_update_remove_ok = {'field': 'measures', 'type': 'remove', 'args': ['poodles'], 'kwargs': {}}
        measure_update_remove_bad = {'field': 'measures', 'type': 'remove', 'args': ['location'], 'kwargs': {}}
        filter_update_add = {'field': 'filters', 'type': 'new', 'args': [{ 'transform_id': 3,'fake_filter': 'yes', 'param_dict': {'filter_name': '_fake'}, 'measure_list': []}], 'kwargs': {}}
        filter_update_modify = {'field': 'filters', 'type': 'modify', 'args': [1, [('order', 1)]], 'kwargs': {}}
        filter_update_remove_ok = {'field': 'filters', 'type': 'remove', 'args': [3], 'kwargs': {}}
        filter_update_remove_bad = {'field': 'filters', 'type': 'remove', 'args': [2], 'kwargs': {}}
        dparam_update_add = {'field': 'dparam_rules', 'type': 'new', 'args': [{'transform_id': 15, 'fake_param': 'yes', 'measure_list': [], 'param_dict': {'measure_rules': {'output_name': 'new'}}}], 'kwargs': {}}
        dparam_update_modify = {'field': 'dparam_rules', 'type': 'modify', 'args': [9, [('window_len', 2)]], 'kwargs': {'new_partition_list': ['dumb']}}
        dparam_update_remove_ok = {'field': 'dparam_rules', 'type': 'remove', 'args': [15], 'kwargs': {}}
        dparam_update_remove_bad = {'field': 'dparam_rules', 'type': 'remove', 'args': [8], 'kwargs': {}}
        event_update_add = {'field': 'event_rules', 'type': 'new', 'args': ['fuck_this_event', {
        "partition_list": [],
        "measure_list":["timestamp", "head1"],
        "transform_type":"detect_event",
        "transform_name":"DetectThreshold",
        "param_dict":{
            "event_rules":{
                "measure":"head1",
                "threshold_value":69.2,
                "comparison_operator":">=",
                "absolute_compare":True
            },
            "event_name":"nice_event",
            "stream_id":"abc123",
        },
        "logical_comparison": "AND"
        }], 'kwargs': {}}
        event_update_modify = {'field': 'event_rules', 'type': 'modify', 'args': ['fuck_this_event', [('threshold_value', 70)]], 'kwargs': {}}

        update1 = [name_update, desc_update, source_key_update, user_id_update1, user_id_update1, field_update1, fk_update1, tag_update1, storage_update, engine_update, ingest_update, measure_update_add, filter_update_add, dparam_update_add, event_update_add]

        update2 = [user_id_update2, field_update2, tag_update2, tag_update3, fk_update2, fk_update3, filter_update_modify, dparam_update_modify, event_update_modify]

        update3 = [user_id_update3, field_update3, fk_update4, tag_update4, measure_update_remove_ok, filter_update_remove_ok, dparam_update_remove_ok]

        update4 = [measure_update_remove_bad, filter_update_remove_bad, dparam_update_remove_bad]

        # update 1
        result1 = update_template(self.dstream, update1)
        updated_template = result1[1]
        self.assertEqual(result1[0], 'ok')
        self.assertEqual(updated_template['stream_name'], 'shit')
        self.assertEqual(updated_template['user_description'], 'i hate this shit')
        self.assertEqual(updated_template['source_key'], 'vom_id')
        self.assertIn('bananas', updated_template['user_ids'])
        self.assertIn('field_of_garbage', updated_template['fields'])
        self.assertIn({'romania': None}, updated_template['foreign_keys'])
        self.assertIn('hash', updated_template['tags'])
        self.assertDictEqual(updated_template['storage_rules'], {"store_raw":False, "store_filtered":True, "store_derived":False})
        self.assertDictEqual(updated_template['engine_rules'], {'kafka': 'test', 'fuck_buffer': True, 'notfuck_buffer': False})
        self.assertDictEqual(updated_template['ingest_rules'], {'im_real': False})
        self.assertEqual(len(updated_template['measures'].keys()), 2)
        self.assertEqual(len(updated_template['filters']), 3)
        self.assertEqual(len(updated_template['dparam_rules']), 11)
        self.assertIn('fuck_this_event', updated_template['event_rules'])

        # update 2
        result2 = update_template(updated_template, update2)
        updated_template2 = result2[1]
        self.assertEqual(result2[0], 'ok')
        self.assertEqual(len(updated_template2['user_ids']), 3)
        self.assertIn('shit_kiwis', updated_template2['user_ids'])
        self.assertNotIn('id', updated_template2['user_ids'])
        self.assertEqual(len(updated_template2['fields']), 2)
        self.assertIn('field_of_trash', updated_template2['fields'])
        self.assertNotIn('region-code', updated_template2['fields'])
        self.assertEqual(len(updated_template2['tags']), 2)
        self.assertIn('price', updated_template2['tags'])
        self.assertIn('toe', updated_template2['tags'])
        self.assertNotIn('hash', updated_template2['tags'])
        self.assertEqual(len(updated_template2['foreign_keys']), 2)
        self.assertIn({'slovakia': None}, updated_template2['foreign_keys'])
        self.assertIn({'lithuania': None}, updated_template2['foreign_keys'])
        self.assertNotIn({'romania': None}, updated_template2['foreign_keys'])
        self.assertEqual(updated_template2['filters'][0]['param_dict']['order'], 1)
        self.assertEqual(updated_template2['dparam_rules'][8]['param_dict']['func_params']['window_len'], 2)
        self.assertEqual(updated_template2['dparam_rules'][8]['partition_list'], ['dumb'])
        self.assertEqual(updated_template2['event_rules']['fuck_this_event']['param_dict']['event_rules']['threshold_value'], 70)

        # update 3
        result3 = update_template(updated_template2, update3)
        updated_template3 = result3[1]
        self.assertEqual(result3[0], 'ok')
        self.assertEqual(len(updated_template3['user_ids']), 2)
        self.assertNotIn('driver-id', updated_template3['user_ids'])
        self.assertEqual(len(updated_template3['fields']), 1)
        self.assertNotIn('field_of_garbage', updated_template3['fields'])
        self.assertEqual(len(updated_template3['tags']), 1)
        self.assertNotIn('price', updated_template3['tags'])
        self.assertEqual(len(updated_template3['foreign_keys']), 1)
        self.assertNotIn({'slovakia': None}, updated_template3['foreign_keys'])
        self.assertEqual(len(updated_template3['measures'].keys()), 1)
        self.assertEqual(len(updated_template3['filters']), 2)
        self.assertEqual(len(updated_template3['dparam_rules']), 10)

        # update 4
        result4 = update_template(updated_template3, update4)
        self.assertEqual(result4[0], 'invalid update')
        bad_guys = result4[2]
        self.assertEqual(len(bad_guys), 7)

        self.assertIn(('derived param', 'DeriveSlope', 'measure', 'timestamp_winning'), bad_guys)
        self.assertIn(('derived param', 'DeriveDistance', 'measure', 'location'), bad_guys)
        self.assertIn(('derived param', 'DeriveDistance', 'measure', 'location'), bad_guys)
        self.assertIn(('derived param', 'DeriveHeading', 'measure', 'location'), bad_guys)
        self.assertIn(('derived param', 'DeriveInBox', 'measure', 'location'), bad_guys)
        self.assertIn(('event', 'test_event', 'derived param', 'head1'), bad_guys)
        self.assertIn(('event', 'fuck_this_event', 'derived param', 'head1'), bad_guys)
    #
    def test_build_data_rules(self):
        source_inds = [0,1,2,4,6,8,3]
        t_keys = [["user_ids","sex"],["measures","length", "val"],["measures","diameter", "val"],["measures","whole_weight", "val"],["measures","viscera_weight", "val"],["fields","rings"],["timestamp"]]
        d = build_data_rules(source_inds, t_keys)
        self.assertDictEqual(d, {'mapping_list': [(0, ['user_ids', 'sex']), (1, ['measures', 'length', 'val']), (2, ['measures', 'diameter', 'val']), (4, ['measures', 'whole_weight', 'val']), (6, ['measures', 'viscera_weight', 'val']), (8, ['fields', 'rings']), (3, ['timestamp'])], 'date_format': None, 'puller': {}, 'pull': False})
    #
        d2 = build_data_rules(source_inds, t_keys, puller=['dir', [['path', 'strom/data_puller/test/'], ['file_type', 'csv']]])

        self.assertDictEqual(d2,  {'mapping_list': [(0, ['user_ids', 'sex']), (1, ['measures', 'length', 'val']), (2, ['measures', 'diameter', 'val']), (4, ['measures', 'whole_weight', 'val']), (6, ['measures', 'viscera_weight', 'val']), (8, ['fields', 'rings']), (3, ['timestamp'])], 'date_format': None, 'puller': {'type': 'dir', 'inputs': {'path': 'strom/data_puller/test/', 'file_type': 'csv'}}, 'pull': True})

        d3 = build_data_rules(source_inds, t_keys, puller=['dir', [['path', 'strom/data_puller/test/'], ['file_type', 'csv'], ['delimiter', ',']]])

        self.assertDictEqual(d3, {'mapping_list': [(0, ['user_ids', 'sex']), (1, ['measures', 'length', 'val']), (2, ['measures', 'diameter', 'val']), (4, ['measures', 'whole_weight', 'val']), (6, ['measures', 'viscera_weight', 'val']), (8, ['fields', 'rings']), (3, ['timestamp'])], 'date_format': None, 'puller': {'type': 'dir', 'inputs': {'path': 'strom/data_puller/test/', 'file_type': 'csv', 'delimiter': ','}}, 'pull': True} )

    def test_build_new_rules_updates(self):
        k = {'partition_list': [], 'turn_value': 99, 'stream_id': 'abc123'}
        f = ('butter_lowpass', {"partition_list": [], "measure_list": ["where"]})
        m = [([('location', 'geo')], [], [], [('turn', k, ['location'])])]
        m2 = [([('where', 'geo')], [], [], [('turn', k, ['where'])])]
        f2 = ('butter_lowpass', {"partition_list": [], "measure_list": ["location"]})

        ff = ('butter_lowpass', {"partition_list": [], "measure_list": ["where"]})

        r = update(self.dstream, [{'field': 'user_description', 'type': 'new', 'args': ['new shit'], 'kwargs': {}}], m, [])
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], 'ok')
        self.assertEqual(len(r[1]['measures']), 1)
        self.assertIn('turn_99.000000_location', r[1]['event_rules'])

        rawr = deepcopy(r[1])
        r2 = update(rawr, [], m2, [ff])
        self.assertEqual(len(r2), 2)
        self.assertEqual(r[0], 'ok')
        self.assertEqual(len(r2[1]['measures']), 2)
        self.assertEqual(len(r2[1]['filters']), 3)
        self.assertIn('turn_99.000000_location', r2[1]['event_rules'])
        self.assertIn('turn_99.000000_where', r2[1]['event_rules'])


        d = DStream()
        d['measures'] = {'location': {'val': None, 'dtype': 'geo'}}
        t = update(d, [], [], [f2])
        t2 = update(d, [], [], [f])
        self.assertEqual(t[0], 'ok')
        self.assertEqual(t2[0], 'invalid update')










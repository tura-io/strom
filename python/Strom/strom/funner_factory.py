import numpy as np

from strom.dstream.stream_rules import DParamRules, EventRules


def create_turn_rules(spatial_measure, partition_list, turn_value, stream_id, units="deg", heading_type="bearing",swap_lon_lat=True, window_len=1, logical_comparision="AND"):
    heading_name = "head_" + spatial_measure
    heading_rules = DParamRules({"partition_list":partition_list,
                                "measure_list":[spatial_measure,],
                                "transform_type": "derive_param",
                                "transform_name": "DeriveHeading",
                                "param_dict":{
                                    "func_params":{"window_len":window_len , "units":units,"heading_type":heading_type, "swap_lon_lat":swap_lon_lat,},
                                    "measure_rules":{"spatial_measure":spatial_measure,"output_name":heading_name}
                                    },
                                "logical_comparison":logical_comparision})

    change_name = "change_"+spatial_measure
    change_rules = DParamRules({"partition_list":[(heading_name, "!=", np.nan)],
                                "measure_list":[heading_name,],
                                "transform_type": "derive_param",
                                "transform_name": "DeriveChange",
                                "param_dict":{
                                    "func_params":{"window_len":window_len , "angle_change":True,},
                                    "measure_rules":{"target_measure":heading_name,"output_name":change_name}
                                    },
                                "logical_comparison":"AND"})

    event_name = "turn_{:f}_{}".format(turn_value, spatial_measure)

    event_rules = EventRules({"partition_list":[(change_name, "!=", np.nan)],
                                "measure_list":[change_name,],
                                "transform_type": "detect_event",
                                "transform_name": "DetectThreshold",
                                "param_dict":{"event_rules":{
                                                            "measure":change_name,
                                                            "threshold_value":turn_value,
                                                            "comparison_operator":">=",
                                                            "absolute_compare":True
                                                        },
                                                        "event_name":event_name,
                                                        "stream_id":stream_id,
                                    },
                                "logical_comparison":"AND"})

    rules_dict = {}
    rules_dict["fiter_rules"] = []
    rules_dict["dparam_rules"] = [heading_rules, change_rules]
    rules_dict["event_rules"] = {event_name:event_rules}

    return rules_dict

print(create_turn_rules("where_I_am", [("foo",1,"==")], 45, "abc123",))
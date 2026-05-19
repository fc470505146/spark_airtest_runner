# -*- encoding=utf8 -*-
__author__ = "fc470"

import os
import sys

from airtest.core.api import *
from poco.drivers.unity3d import UnityPoco


auto_setup(__file__)

CURRENT_DIR = os.path.dirname(__file__)
AIRTEST_ROOT = os.path.dirname(CURRENT_DIR)
COMMON_DIR = os.path.join(AIRTEST_ROOT, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)

from game_steps import enter_game_from_main_menu
from poco_assertions import assert_node_exists


poco = UnityPoco()


def test_game_hud_is_visible():
    enter_game_from_main_menu(poco)

    assert_node_exists(poco, "StatsUI", timeout=5)
    assert_node_exists(poco, "StatsTextMesh", timeout=5)
    assert_node_exists(poco, "FuelBar", timeout=5)
    assert_node_exists(poco, "TouchUI", timeout=5)
    assert_node_exists(poco, "SettingButton", timeout=5)
    snapshot(msg="Core game HUD is visible")


test_game_hud_is_visible()

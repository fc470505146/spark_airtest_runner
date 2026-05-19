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

from game_steps import assert_game_scene_ready, enter_game_from_main_menu
from gm_commands import gm_force_success
from poco_assertions import assert_node_exists, click_node_and_wait


poco = UnityPoco()


def test_gm_force_success_can_continue_to_next_level():
    enter_game_from_main_menu(poco)

    gm_force_success(poco)
    assert_node_exists(poco, "LandedUI", timeout=10)
    assert_node_exists(poco, "NextButton", timeout=5)
    snapshot(msg="GM success landing result is visible")

    click_node_and_wait(
        poco,
        click_node_name="NextButton",
        expected_node_name="SettingButton",
        click_timeout=5,
        verify_timeout=10,
    )
    assert_game_scene_ready(poco)
    snapshot(msg="GM success flow can continue to next level")


test_gm_force_success_can_continue_to_next_level()

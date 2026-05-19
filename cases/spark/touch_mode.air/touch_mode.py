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

from game_steps import enter_game_from_main_menu, open_pause_menu
from poco_assertions import assert_node_exists, wait_node_disappears


poco = UnityPoco()


def test_touch_mode_toggle_flow():
    enter_game_from_main_menu(poco)
    assert_node_exists(poco, "TouchUI", timeout=5)
    assert_node_exists(poco, "ArrowButton", timeout=5)

    open_pause_menu(poco)

    toggle_button = assert_node_exists(poco, "JoystickToggleButton", timeout=5)
    toggle_button.click()
    assert_node_exists(poco, "Joystick", timeout=5)
    snapshot(msg="Joystick touch mode is visible")

    toggle_button = assert_node_exists(poco, "JoystickToggleButton", timeout=5)
    toggle_button.click()
    wait_node_disappears(poco, "Joystick", timeout=5)
    wait_node_disappears(poco, "ArrowButton", timeout=5)
    snapshot(msg="Touch controls can be hidden")


test_touch_mode_toggle_flow()

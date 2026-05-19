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
from poco_assertions import assert_node_exists, click_node_and_wait, wait_node_disappears


poco = UnityPoco()


def test_pause_menu_resume_flow():
    enter_game_from_main_menu(poco)
    open_pause_menu(poco)

    assert_node_exists(poco, "MainMenuButton", timeout=5)
    assert_node_exists(poco, "JoystickToggleButton", timeout=5)
    snapshot(msg="Pause menu actions are visible")

    click_node_and_wait(
        poco,
        click_node_name="ResumeButton",
        expected_node_name="SettingButton",
        click_timeout=5,
        verify_timeout=5,
    )
    wait_node_disappears(poco, "ResumeButton", timeout=5)
    snapshot(msg="Game resumed from pause menu")


test_pause_menu_resume_flow()

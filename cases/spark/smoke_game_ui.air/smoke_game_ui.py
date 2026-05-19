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

from poco_assertions import assert_node_exists, click_node_and_wait


poco = UnityPoco()

def given_main_menu_is_visible():
    assert_node_exists(poco, "PlayButton", timeout=10)
    snapshot(msg="Main menu is visible")


def when_start_game_from_main_menu():
    click_node_and_wait(
        poco,
        click_node_name="PlayButton",
        expected_node_name="SettingButton",
        click_timeout=10,
        verify_timeout=10,
    )


def then_game_scene_is_ready():
    assert_node_exists(poco, "SettingButton", timeout=3)
    assert_node_exists(poco, "GameManager", timeout=3)
    assert_node_exists(poco, "Lander", timeout=3)
    snapshot(msg="Game scene is ready")


def test_enter_game_from_main_menu():
    given_main_menu_is_visible()
    when_start_game_from_main_menu()
    then_game_scene_is_ready()


test_enter_game_from_main_menu()

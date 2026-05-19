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
from gm_commands import gm_force_fail, gm_force_success
from poco_assertions import (
    assert_node_exists,
    click_node_and_wait,
    assert_text_contains,
)

poco = UnityPoco()


def test_success_flow_can_restart_after_failure():
    enter_game_from_main_menu(poco)

    force_success_and_continue()
    force_success_and_continue()
    return_to_main_menu_from_result()

    assert_text_contains(poco, "开始游戏", timeout=10)
    enter_game_from_main_menu(poco)
    assert_game_scene_ready(poco)
    snapshot(msg="成功通过并重新开始第一关")

    gm_force_fail(poco)
    snapshot(msg="失败爆炸")
    assert_text_contains(poco, "重新开始", timeout=10)

    poco(text="重新开始").click()
    assert_game_scene_ready(poco)
    snapshot(msg="失败后重新开始")



def return_to_main_menu_from_result():
    assert_text_contains(poco, "返回主菜单", timeout=10)
    click_node_and_wait(
        poco,
        click_node_name="MainMenuButton",
        expected_node_name="PlayButton",
        click_timeout=5,
        verify_timeout=10,
    )


def force_success_and_continue():
    assert_game_scene_ready(poco)
    gm_force_success(poco)
    assert_node_exists(poco, "LandedUI", timeout=10)
    assert_node_exists(poco, "NextButton", timeout=5)
    assert_text_contains(poco, "继续下一关", timeout=10)
    snapshot(msg="GM success landing result is visible")
    poco(text="继续下一关").click()


test_success_flow_can_restart_after_failure()


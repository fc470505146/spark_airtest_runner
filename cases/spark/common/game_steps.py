from airtest.core.api import snapshot

from poco_assertions import assert_node_exists, click_node_and_wait


def assert_main_menu_ready(poco):
    assert_node_exists(poco, "PlayButton", timeout=10)
    snapshot(msg="Main menu is ready")


def enter_game_from_main_menu(poco):
    assert_main_menu_ready(poco)
    click_node_and_wait(
        poco,
        click_node_name="PlayButton",
        expected_node_name="SettingButton",
        click_timeout=10,
        verify_timeout=10,
    )
    assert_game_scene_ready(poco)


def assert_game_scene_ready(poco):
    assert_node_exists(poco, "SettingButton", timeout=5)
    assert_node_exists(poco, "GameManager", timeout=5)
    assert_node_exists(poco, "Lander", timeout=5)
    snapshot(msg="Game scene is ready")


def open_pause_menu(poco):
    click_node_and_wait(
        poco,
        click_node_name="SettingButton",
        expected_node_name="ResumeButton",
        click_timeout=5,
        verify_timeout=5,
    )
    assert_node_exists(poco, "PausedUI", timeout=5)
    snapshot(msg="Pause menu is visible")

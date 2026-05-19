import re

from airtest.core.api import assert_equal, snapshot


def wait_node(poco, name, timeout=10):
    node = poco(name)
    node.wait_for_appearance(timeout=timeout)
    if not node.exists():
        snapshot(msg=f"Missing Poco node: {name}")
        raise AssertionError(f"Expected Poco node to appear: {name}")
    return node


def assert_node_exists(poco, name, timeout=10):
    node = wait_node(poco, name, timeout=timeout)
    assert_equal(node.exists(), True, f"Poco node exists: {name}")
    return node


def wait_text_contains(poco, text, timeout=10):
    text_pattern = f".*{re.escape(text)}.*"
    node = poco(textMatches=text_pattern)
    node.wait_for_appearance(timeout=timeout)
    if not node.exists():
        snapshot(msg=f"Missing Poco text containing: {text}")
        raise AssertionError(f"Expected Poco text to contain: {text}")
    return node


def assert_text_contains(poco, text, timeout=10):
    node = wait_text_contains(poco, text, timeout=timeout)
    assert_equal(node.exists(), True, f"Poco text contains: {text}")
    return node


def wait_node_disappears(poco, name, timeout=10):
    node = poco(name)
    node.wait_for_disappearance(timeout=timeout)
    if node.exists():
        snapshot(msg=f"Unexpected Poco node still visible: {name}")
        raise AssertionError(f"Expected Poco node to disappear: {name}")
    assert_equal(node.exists(), False, f"Poco node disappears: {name}")


def click_node_and_wait(poco, click_node_name, expected_node_name, click_timeout=10, verify_timeout=10):
    click_node = wait_node(poco, click_node_name, timeout=click_timeout)
    click_node.click()
    return wait_node(poco, expected_node_name, timeout=verify_timeout)

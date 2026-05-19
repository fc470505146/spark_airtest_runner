from airtest.core.api import assert_equal, snapshot


def invoke_gm(poco, command):
    result = poco.invoke(command)
    assert_equal(result, "ok", f"{command} returns ok")
    return result


def gm_force_success(poco):
    result = invoke_gm(poco, "Airtest.GMForceSuccess")
    snapshot(msg="GM force success command sent")
    return result


def gm_force_fail(poco):
    result = invoke_gm(poco, "Airtest.GMForceFail")
    snapshot(msg="GM force fail command sent")
    return result

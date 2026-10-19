from types import SimpleNamespace

from opendbc.car.tesla.teslacan import TeslaCAN
from opendbc.car.tesla.values import TeslaFlags
from opendbc.sunnypilot.car.tesla.coop_steering import CoopSteeringCarController
from opendbc.sunnypilot.car.tesla.values import TeslaFlagsSP


def _update(flags: int):
  controller = CoopSteeringCarController()
  cp_sp = SimpleNamespace(flags=flags)
  cs = SimpleNamespace(out=SimpleNamespace())
  return controller.update(0.0, False, cp_sp, cs, None)


def test_coop_steering_requests_lane_keep_assist():
  result = _update(TeslaFlagsSP.COOP_STEERING.value)
  assert result.control_type == 2


def test_regular_steering_requests_angle_control():
  result = _update(0)
  assert result.control_type == 1


class _Packer:
  def make_can_msg(self, name, bus, values):
    return values


def _steering_type(enabled: bool, control_type: int, flags: int = 0) -> int:
  can = TeslaCAN(SimpleNamespace(flags=flags), _Packer())
  return can.create_steering_control(0.0, enabled, control_type)["DAS_steeringControlType"]


def test_steering_control_sends_coop_type_when_enabled():
  assert _steering_type(True, 2) == 2
  assert _steering_type(False, 2) == 0


def test_fsd14_keeps_the_signal_flip():
  assert _steering_type(True, 2, TeslaFlags.FSD_14.value) == 1
  assert _steering_type(True, 1, TeslaFlags.FSD_14.value) == 2

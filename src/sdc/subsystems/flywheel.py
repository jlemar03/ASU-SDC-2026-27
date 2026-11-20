"""Flywheel subsystem backed by a SparkMini motor controller."""

from sdc.motor.spark_mini import SparkMini


class Flywheel:
	"""Control a flywheel and read its integrated encoder."""

	def __init__(self, can_id: int) -> None:
		self.controller = SparkMini(can_id)
		self.encoder = self.controller.get_encoder()

	def set_output(self, output: float) -> None:
		"""Set the motor's open-loop output (typically between -1 and 1)."""
		self.controller.set(output)

	def set_target_rpm(self, rpm: float) -> None:
		"""Set the flywheel's velocity target in RPM."""
		self.controller.set_target_rpm(rpm)

	def get_rpm(self) -> float:
		"""Return the encoder's measured velocity in RPM."""
		return float(self.encoder.get_velocity_rpm())

	def stop(self) -> None:
		"""Stop the flywheel motor."""
		self.controller.set(0.0)

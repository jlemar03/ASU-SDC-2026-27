"""HD Hex motor setup using a REV Spark Mini PWM controller."""
import wpilib


class SparkMini:
	"""Motor-controller wrapper that can be instantiated by a subsystem."""

	def __init__(self, pwm_channel: int, inverted: bool = False) -> None:
		self.controller = wpilib.Spark(pwm_channel)
		self.controller.setInverted(inverted)

	def set(self, speed: float) -> None:
		"""Set motor speed in the range -1.0 to 1.0."""
		self.controller.set(speed)

	def stop(self) -> None:
		self.controller.stopMotor()

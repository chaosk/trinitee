import datetime
from django.core.exceptions import ValidationError
from utilities.internal.ip import check_pattern


def expires_at_validator(value):
	if datetime.datetime.today() >= value:
		raise ValidationError("You cannot set an already-expired ban.")


def mask_validator(value):
	if not check_pattern(value):
		raise ValidationError("Provided pattern is incorrect.")

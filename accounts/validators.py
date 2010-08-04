from django.core.exceptions import ValidationError
from utilities.annoying.functions import get_config


def validate_signature(value):
	max_lines = get_config('SIGNATURE_MAX_LINES', False)
	if not max_lines:
		return
	if len(value.split("\n")) > max_lines:
		raise ValidationError("Signature has more than %d lines." % max_lines)

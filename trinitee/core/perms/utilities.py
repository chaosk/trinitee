from guardian.shortcuts import get_perms_for_model


def get_codename_perms(model):
	return [p.codename for p in get_perms_for_model(model)]

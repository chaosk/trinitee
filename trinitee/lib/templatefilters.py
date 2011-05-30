import re
import unicodedata


# code taken from django/template/defaultfilters.py
# the only change is to not covert value to lowercase
def slugify(value):
	"""
    Normalizes string, removes slashes, removes spaces
	and underscores from the beginning/end of the value,
    and converts spaces to underscores.
    """
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = unicode(re.sub('/', '', value).strip(' _'))
	return re.sub('[-\s]+', '_', value)

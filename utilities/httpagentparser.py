"""
Author: Shekhar Tiwatne <http://flavors.me/shon>
Licensed under Zope Public License <http://www.zope.org/Resources/ZPL>

Modified by Krzysztof Socha on 16th June 2010.

Extract client information from http user agent
The module does not try to detect all capabilities of browser in current form (it can easily be extended though).
Aim is 
    * fast 
    * very easy to extend
    * reliable enough for practical purposes
    * and assist python web apps to detect clients.
"""
import sys


class DetectorsHub(dict):
	_known_types = ['os', 'flavor']
	def __init__(self, *args, **kw):
		dict.__init__(self, *args, **kw)
		for typ in self._known_types:
			self.setdefault(typ, [])
		self.registerDetectors()
	def register(self, detector):
		if detector.info_type not in self._known_types:
			self[detector.info_type] = [detector]
			self._known_types.insert(detector.order, detector.info_type)
		else:
			self[detector.info_type].append(detector)
	def reorderByPrefs(self, detectors, prefs):
		if prefs == None:
			return []
		elif prefs == []:
			return detectors
		else:
			prefs.insert(0, '')
			return sorted(detectors, key=lambda d: d.name in prefs and prefs.index(d.name) or sys.maxint)
	def __iter__(self):
		return iter(self._known_types)
	def registerDetectors(self):
		detectors = [v() for v in globals().values() if DetectorBase in getattr(v, '__mro__', [])]
		for d in detectors:
			if d.can_register:
				self.register(d)


class DetectorBase(object):
	name = "" # "to perform match in DetectorsHub object"
	info_type = "override me"
	result_key = "override me"
	order = 10 # 0 is highest
	look_for = "string to look for"
	can_register = False
	prefs = dict() # dict(info_type = [name1, name2], ..)
	version_splitters = ["/", " "]
	_suggested_detectors = None
	def __init__(self):
		if not self.name:
			self.name = self.__class__.__name__
		self.can_register = (self.__class__.__dict__.get('can_register', True))
	def detect(self, agent, result):
		# -> True/None
		if self.checkWords(agent):
			result[self.info_type] = dict(name = self.name)
			return True
	def checkWords(self, agent):
		# -> True/None
		if self.look_for in agent:
			return True


class OS(DetectorBase):
	info_type = "os"
	can_register = False
	version_splitters = [";", " "]


class Flavor(DetectorBase):
	info_type = "flavor"
	can_register = False


class Linux(OS):
	name = 'linux'
	look_for = 'Linux'


class Macintosh(OS):
	name = 'osx'
	look_for = 'Macintosh'


class Windows(OS):
	name = 'win'
	look_for = 'Windows'


class i686(Flavor):
    name = 'x86'
    look_for = 'i686'


class x86_64(Flavor):
	name = 'x86_64'
	look_for = 'x86_64'


class x64(Flavor):
	name = 'x64'
	look_for = 'x86_64'


# class Intel(Flavor):
# 	# name = 'intel'
# 	name = 'universal'
# 	look_for = 'Intel Mac OS X'
# 
# 
# class PPC(Flavor):
# 	# name = 'ppc'
# 	name = 'universal'
# 	look_for = 'PPC Mac OS X'


class Result(dict):
	def __missing__(self, k):
		return ""

detectorshub = DetectorsHub()

def detect(agent):
	result = Result()
	_suggested_detectors = []
	for info_type in detectorshub:
		detectors = _suggested_detectors or detectorshub[info_type]
		for detector in detectors:
			if detector.detect(agent, result):
				if detector.prefs and not detector._suggested_detectors:
					_suggested_detectors = detectorshub.reorderByPrefs(detectors, detector.prefs.get(info_type))
					detector._suggested_detectors = _suggested_detectors
					break
	return result

def os_detect(agent):
	result = detect(agent)
	os = result['os']['name'] if 'os' in result else 'unknown'
	flavor = result['flavor']['name'] if 'flavor' in result else None
	if os == 'win':
		os = 'win32' if flavor is None else 'win64'		
	return (os, flavor)

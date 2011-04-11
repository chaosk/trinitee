from django.core.cache import cache
from community_content.models import Map, Tileset
from utilities.annoying.decorators import render_to


@render_to('community_content/index.html')
def index(request):
	# I dislike this approach
	map_count = cache.get('community_content_map_count')
	if map_count == None:
		map_count = Map.objects.count()
		cache.set('community_content_map_count', map_count, 86400)
	tileset_count = cache.get('community_content_tileset_count')
	if tileset_count == None:
		tileset_count = Tileset.objects.count()
		cache.set('community_content_tileset_count', tileset_count, 86400)
	item_count = map_count + tileset_count

	return {
		'map_count': map_count,
		'tileset_count': tileset_count,
		'item_count': item_count
	}


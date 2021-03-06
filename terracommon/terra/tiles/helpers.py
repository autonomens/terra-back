import hashlib
from math import ceil, floor, log, pi

import mercantile
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import F

from . import EARTH_RADIUS, EPSG_3857
from .funcs import (ST_Area, ST_Length, ST_MakeEnvelope,
                    ST_SimplifyPreserveTopology, ST_SnapToGrid, ST_Transform)
from .sigtools import SIGTools


def cached_tile(func, expiration=3600*24):
    def wrapper(self, x, y, z,
                pixel_buffer, features_filter, properties_filter,
                features_limit, *args, **kwargs):
        cache_key = self.get_tile_cache_key(
            x, y, z,
            pixel_buffer, features_filter, properties_filter,
            features_limit)

        def build_tile():
            (a, b) = func(
                self, x, y, z,
                pixel_buffer, features_filter, properties_filter,
                features_limit, *args, **kwargs)
            return (a, b.tobytes())
        return cache.get_or_set(cache_key, build_tile, expiration)
    return wrapper


class VectorTile(object):
    def __init__(self, layer, cache_key=None):
        self.layer, self.cache_key = layer, cache_key

    # Number of tile units per pixel
    EXTENT_RATIO = 16

    def _simplify(self, layer_query, pixel_width_x, pixel_width_y):
        if self.layer.layer_geometry in self.POLYGON:
            # Grid step is pixel_width_x / 4 and pixel_width_y / 4
            # Simplify to average two grid steps
            layer_query = layer_query.annotate(
                outgeom3857=ST_SimplifyPreserveTopology('outgeom3857', (pixel_width_x + pixel_width_y) / 2 / 2)
            )
        return layer_query

    def _lower_precision(self, layer_query, xmin, ymin, pixel_width_x, pixel_width_y):
        if self.layer.layer_geometry in self.LINESTRING or self.layer.layer_geometry in self.POLYGON:
            layer_query = layer_query.annotate(
                outgeom3857=ST_SnapToGrid(
                    'outgeom3857',
                    xmin,
                    ymin,
                    pixel_width_x / self.EXTENT_RATIO,
                    pixel_width_y / self.EXTENT_RATIO)
            ).filter(
                outgeom3857__isnull=False
            )
        return layer_query

    def _filter_on_property(self, layer_query, features_filter):
        if features_filter is not None:
            layer_query = layer_query.filter(
                properties__contains=features_filter
            )
        return layer_query

    LINESTRING = ('LineString', 'MultiLineString')
    POLYGON = ('Polygon', 'MultiPolygon')

    def _filter_on_geom_size(self, layer_query, layer_geometry, pixel_width_x, pixel_width_y):
        if self.layer.layer_geometry in self.LINESTRING:
            # Larger then a half of pixel
            layer_query = layer_query.annotate(
                length3857=ST_Length('outgeom3857')
            ).filter(
                length3857__gt=(pixel_width_x + pixel_width_y) / 2 / 2
            )
        elif self.layer.layer_geometry in self.POLYGON:
            # Larger than a quarter of pixel
            layer_query = layer_query.annotate(
                area3857=ST_Area('outgeom3857')
            ).filter(
                area3857__gt=pixel_width_x * pixel_width_y / 4
            )
        return layer_query

    def _limit(self, layer_query, features_limit):
        if features_limit is not None:
            # Order by feature size before limit
            if self.layer.layer_geometry in self.LINESTRING:
                layer_query = layer_query.order_by('length3857')
            elif self.layer.layer_geometry in self.POLYGON:
                layer_query = layer_query.order_by('area3857')

            layer_query = layer_query[:features_limit]
        return layer_query

    @cached_tile
    def get_tile(self, x, y, z,
                 pixel_buffer, features_filter, properties_filter,
                 features_limit, features):

        bounds = mercantile.bounds(x, y, z)
        xmin, ymin = mercantile.xy(bounds.west, bounds.south)
        xmax, ymax = mercantile.xy(bounds.east, bounds.north)
        pixel_width_x = (xmax - xmin) / 256
        pixel_width_y = (ymax - ymin) / 256

        layer_query = features.annotate(
                bbox=ST_MakeEnvelope(
                    xmin,
                    ymin,
                    xmax,
                    ymax,
                    EPSG_3857),
                # Intersects on internal data projection using pixel buffer
                bbox_select=ST_Transform(ST_MakeEnvelope(
                    xmin - pixel_width_x * pixel_buffer,
                    ymin - pixel_width_y * pixel_buffer,
                    xmax + pixel_width_x * pixel_buffer,
                    ymax + pixel_width_y * pixel_buffer,
                    EPSG_3857), settings.INTERNAL_GEOMETRY_SRID),
                outgeom3857=ST_Transform('geom', EPSG_3857),
            ).filter(
                bbox_select__intersects=F('geom')
            )

        # Filter features
        layer_query = self._filter_on_property(layer_query, features_filter)
        layer_query = self._filter_on_geom_size(layer_query, self.layer.layer_geometry, pixel_width_x, pixel_width_y)

        # Lighten geometry
        layer_query = self._simplify(layer_query, pixel_width_x, pixel_width_y)
        layer_query = self._lower_precision(layer_query, xmin, ymin, pixel_width_x, pixel_width_y)

        # Seatbelt
        layer_query = self._limit(layer_query, features_limit)

        layer_raw_query, args = layer_query.query.sql_with_params()

        properties = "properties || json_build_object('_id', identifier)::jsonb"

        if properties_filter:
            filter = ', '.join([f"'{f}'" for f in properties_filter])
            properties = f'''
                (
                    ({properties})
                    - (
                        SELECT array_agg(k)
                        FROM jsonb_object_keys(properties) AS t(k)
                        WHERE k NOT IN ({filter})
                    )
                )
                '''
        elif properties_filter == []:
            properties = 'NULL'

        with connection.cursor() as cursor:
            sql_query = f'''
                WITH
                fullgeom AS ({layer_raw_query}),
                tilegeom AS (
                    SELECT
                        ({properties}) AS properties,
                        ST_AsMvtGeom(
                            outgeom3857,
                            bbox,
                            {256 * self.EXTENT_RATIO},
                            {pixel_buffer * self.EXTENT_RATIO},
                            true) AS geometry
                    FROM
                        fullgeom)
                SELECT
                    count(*) AS count,
                    ST_AsMVT(
                        tilegeom,
                        CAST(%s AS text),
                        {256 * self.EXTENT_RATIO},
                        'geometry'
                    ) AS mvt
                FROM
                    tilegeom
            '''

            cursor.execute(sql_query, args + (self.layer.name, ))
            row = cursor.fetchone()

            return row[0], row[1]

    def get_tile_cache_key(self, x, y, z,
                           pixel_buffer, features_filter, properties_filter,
                           features_limit):
        if self.cache_key:
            cache_key = self.cache_key
        else:
            cache_key = self.layer.pk
        features_filter = ''
        if features_filter is not None:
            features_filter_hash = \
                hashlib.sha224(
                    str(features_filter).encode('utf-8')
                ).hexdigest()
        properties_filter_hash = ''
        if properties_filter is not None:
            properties_filter_hash = \
                hashlib.sha224(
                    ','.join(properties_filter).encode('utf-8')
                ).hexdigest()
        return (
            f'tile_cache_{cache_key}_{x}_{y}_{z}'
            f'_{pixel_buffer}_{features_filter_hash}_{properties_filter_hash}'
            f'_{features_limit}'
        )

    def clean_tiles(self, tiles, pixel_buffer, features_filter,
                    properties_filter, features_limit):
        return cache.delete_many([
            self.get_tile_cache_key(
                *tile, pixel_buffer, features_filter, properties_filter,
                features_limit)
            for tile in tiles
        ])


def guess_maxzoom(layer):
    features = layer.features.all()
    layer_query = features.annotate(
        geom3857=ST_Transform('geom', EPSG_3857)
    )

    layer_raw_query, args = layer_query.query.sql_with_params()

    try:
        with connection.cursor() as cursor:
            sql_query = f'''
                WITH
                q1 AS ({layer_raw_query}),
                q2 AS (SELECT ST_X((ST_DumpPoints(geom3857)).geom) AS x FROM q1),
                q3 AS (SELECT x - lag(x) OVER (ORDER BY x) AS dst FROM q2),
                q4 AS (SELECT * FROM q3 WHERE dst > 0)
                SELECT
                    exp(sum(ln(dst))/count(dst)) AS avg
                FROM
                    q4
                '''
            cursor.execute(sql_query, args)
            row = cursor.fetchone()

        # geometric mean of the |x_{i+1}-x_i| for all points (x,y) in layer.pk
        avg = row[0]

        # total number of pixels to represent length `avg` (equator)
        nb_pixels_total = 2*pi*EARTH_RADIUS/avg

        tile_resolution = 256*VectorTile.EXTENT_RATIO

        # zoom (ceil) to fit those pixels at `tile_resolution`
        max_zoom = ceil(log(nb_pixels_total/tile_resolution, 2))

        return min(max_zoom, 22)
    except TypeError:
        return 14  # Arbitrary zoom value


def guess_minzoom(layer):
    """
    Procedure that uses DB output to guess a min zoom level.

    Criteria: zoom satisfying the following condition:
    tile_lenght / tile_fraction <= BBox(features).smallerSide
    If extent = 0, returns 0

    Explanation about the tile_fraction = 8 just above:
    ---------------------------------------------------
    It's purpose is to give an idea of when a dataset becomes to small
    to be shown in the map, so when doing.
    """

    extent = SIGTools.get_extent_of_layer(layer)

    if extent == 0:
        return 0

    tile_fraction = 8
    min_zoom = floor(log((2*pi*EARTH_RADIUS)/(extent*tile_fraction), 2))
    return min(min_zoom, 22)

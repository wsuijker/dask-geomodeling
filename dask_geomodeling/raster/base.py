# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
"""
Module containing the raster block base classes.
"""
from datetime import datetime as Datetime

from dask_geomodeling import Block


class RasterBlock(Block):
    """ The base block for temporal rasters.

    All raster blocks must be derived from this base class and must implement
    the following attributes:

     - ``period``: a tuple of datetimes
     - ``timedelta``: a datetime.timedelta (or None if nonequidistant)
     - ``extent``: a tuple ``(x1, y1, x2, y2)``
     - ``dtype``: a numpy dtype object
     - ``fillvalue``: a number
     - ``geometry``: OGR Geometry
     - ``projection``: WKT string
     - ``geo_transform``: a tuple of 6 numbers

    These attributes are ``None`` if the raster is empty.

    A Request is a dict with the following fields:
    - mode: request mode: values ('vals'), time ('time') or metadata ('meta')
    - bbox: bounding box (x1, y1, x2, y2)
    - projection: wkt spatial reference
    - width: specify data width
    - height: specify data height
    - start: start date as naive datetime
    - stop: stop date as naive datetime
    - aggregation: name of spatial aggregation algorithm

    Result dictionary contains (if mode == 'vals'):
    - values: numpy ndarray of shape (bands, height, width)
    - no_data_value: value indicating no data

    If mode == 'time':
    - time: list of naive datetimes corresponding to the temporal axis

    If mode == 'meta':
    - meta: list of metadata values corresponding to the temporal axis
    """

    DEFAULT_ORIGIN = Datetime(1970, 1, 1, 0, 0)

    def __len__(self):
        """ Return number of temporal bands. """
        # all empty
        try:
            start, stop = self.period
        except TypeError:
            return 0  # period is None

        if start == stop:
            return 1

        timedelta = self.timedelta
        if timedelta is None:
            # hard way, since bands are not aligned
            return len(
                self.get_data(mode='time', start=start, stop=stop)['time']
            )

        # bands are aligned, just divide the period length by the delta
        period_seconds = (stop - start).total_seconds()
        delta_seconds = timedelta.total_seconds()
        return int(period_seconds / delta_seconds) + 1

    def check(self, cold=False):
        """
        Return boolean indicating if the dependent stores had to be updated.

        :param cold: ignore cached modification time
        :type cold: bool

        Check if this store object has been modified in an external
        process. If so, update attributes such as period, extent and timedelta
        accordingly.
        """
        for x in self.args:
            if isinstance(x, RasterBlock):
                x.check(cold=cold)

    def __add__(self, other):
        from . import Add

        return Add(self, other)

    def __mul__(self, other):
        from . import Multiply

        return Multiply(self, other)

    def __neg__(self):
        from . import Multiply

        return Multiply(self, -1)

    def __sub__(self, other):
        from . import Subtract

        return Subtract(self, other)

    def __truediv__(self, other):
        from . import Divide

        return Divide(self, other)

    def __pow__(self, other):
        from . import Power

        return Power(self, other)

    def __eq__(self, other):
        from . import Equal

        return Equal(self, other)

    def __ne__(self, other):
        from . import NotEqual

        return NotEqual(self, other)

    def __gt__(self, other):
        from . import Greater

        return Greater(self, other)

    def __ge__(self, other):
        from . import GreaterEqual

        return GreaterEqual(self, other)

    def __lt__(self, other):
        from . import Less

        return Less(self, other)

    def __le__(self, other):
        from . import LessEqual

        return LessEqual(self, other)

    def __invert__(self):
        from . import Invert

        return Invert(self)

    def __and__(self, other):
        from . import And

        return And(self, other)

    def __or__(self, other):
        from . import Or

        return Or(self, other)

    def __xor__(self, other):
        from . import Xor

        return Xor(self, other)


class BaseSingle(RasterBlock):
    """
    Baseclass for all raster blocks that adjust a single raster
    """

    def __init__(self, store, *args):
        if not isinstance(store, RasterBlock):
            raise TypeError("'{}' object is not allowed".format(type(store)))
        super(BaseSingle, self).__init__(store, *args)

    @property
    def store(self):
        return self.args[0]

    def __len__(self):
        return len(self.store)

    @property
    def extent(self):
        return self.store.extent

    @property
    def period(self):
        return self.store.period

    @property
    def timedelta(self):
        return self.store.timedelta

    @property
    def dtype(self):
        return self.store.dtype

    @property
    def fillvalue(self):
        return self.store.fillvalue

    @property
    def geometry(self):
        return self.store.geometry

    @property
    def projection(self):
        return self.store.projection

    @property
    def geo_transform(self):
        return self.store.geo_transform
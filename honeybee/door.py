# coding: utf-8
"""Honeybee Door."""
from ._base import _Base
from .properties import DoorProperties
from .boundarycondition import boundary_conditions, Outdoors, Surface
import honeybee.writer as writer

from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D

import math


class Door(_Base):
    """A single planar Door in a Face.

    Properties:
        name
        display_name
        boundary_condition
        is_glass
        parent
        has_parent
        geometry
        vertices
        upper_left_vertices
        triangulated_mesh3d
        normal
        center
        area
        perimeter
    """
    __slots__ = ('_geometry', '_parent', '_boundary_condition', '_is_glass')

    def __init__(self, name, geometry, boundary_condition=None, is_glass=False):
        """A single planar Door in a Face.

        Args:
            name: Door name. Must be < 100 characters.
            geometry: A ladybug-geometry Face3D.
            boundary_condition: Boundary condition object (Outdoors, Surface, etc.).
                Default: Outdoors.
            is_glass: Boolean to note whether this object is a glass door as opposed
                to an opaque door. Default: False.
        """
        _Base.__init__(self, name)  # process the name

        # process the geometry
        assert isinstance(geometry, Face3D), \
            'Expected ladybug_geometry Face3D. Got {}'.format(type(geometry))
        self._geometry = geometry
        self._parent = None  # _parent will be set when the Face is added to a Face

        # process the boundary condition and type
        self.boundary_condition = boundary_condition or boundary_conditions.outdoors
        self.is_glass = is_glass

        # initialize properties for extensions
        self._properties = DoorProperties(self)

    @classmethod
    def from_dict(cls, data):
        """Initialize an Door from a dictionary.

        Args:
            data: A dictionary representation of an Door object.
        """
        # check the type of dictionary
        assert data['type'] == 'Door', 'Expected Door dictionary. ' \
            'Got {}.'.format(data['type'])

        is_glass = data['is_glass'] if 'is_glass' in data else False
        if data['boundary_condition']['type'] == 'Outdoors':
            boundary_condition = Outdoors.from_dict(data['boundary_condition'])
        elif data['boundary_condition']['type'] == 'Surface':
            boundary_condition = Surface.from_dict(data['boundary_condition'], True)
        else:
            raise ValueError(
                'Boundary condition "{}" is not supported for Door.'.format(
                    data['boundary_condition']['type']))
        door = cls(data['name'], Face3D.from_dict(data['geometry']),
                   boundary_condition, is_glass)
        if 'display_name' in data and data['display_name'] is not None:
            door._display_name = data['display_name']

        if data['properties']['type'] == 'DoorProperties':
            door.properties._load_extension_attr_from_dict(data['properties'])
        return door

    @classmethod
    def from_vertices(cls, name, vertices, boundary_condition=None, is_glass=False):
        """Create a Door from vertices with each vertex as an iterable of 3 floats.

        Args:
            name: Door name. Must be < 100 characters.
            vertices: A flattened list of 3 or more vertices as (x, y, z).
            boundary_condition: Boundary condition object (eg. Outdoors, Surface).
                Default: Outdoors.
            is_glass: Boolean to note whether this object is a glass door as opposed
                to an opaque door. Default: False.
        """
        geometry = Face3D(tuple(Point3D(*v) for v in vertices))
        return cls(name, geometry, boundary_condition, is_glass)

    @property
    def boundary_condition(self):
        """Boundary condition of this door."""
        return self._boundary_condition

    @boundary_condition.setter
    def boundary_condition(self, value):
        if not isinstance(value, Outdoors):
            if isinstance(value, Surface):
                assert len(value.boundary_condition_objects) == 3, 'Surface boundary ' \
                    'condition for Door must have 3 boundary_condition_objects.'
            else:
                raise ValueError('Door only supports Outdoor or Surface boundary '
                                 'condition. Got {}'.format(type(value)))
        self._boundary_condition = value

    @property
    def is_glass(self):
        """Boolean to note whether this object is a glass door."""
        return self._is_glass

    @is_glass.setter
    def is_glass(self, value):
        try:
            self._is_glass = bool(value)
        except TypeError:
            raise TypeError(
                'Expected boolean for Door.is_glass. Got {}.'.format(value))

    @property
    def parent(self):
        """Parent Face if assigned. None if not assigned."""
        return self._parent

    @property
    def has_parent(self):
        """Boolean noting whether this Door has a parent Face."""
        return self._parent is not None

    @property
    def geometry(self):
        """A ladybug_geometry Face3D object representing the door."""
        return self._geometry

    @property
    def vertices(self):
        """List of vertices for the door (in counter-clockwise order)."""
        return self._geometry.vertices

    @property
    def upper_left_vertices(self):
        """List of vertices starting from the upper-left corner.

        This property should be used when exporting to EnergyPlus / OpenStudio.
        """
        return self._geometry.upper_left_counter_clockwise_vertices

    @property
    def triangulated_mesh3d(self):
        """A ladybug_geometry Mesh3D of the door geometry composed of triangles.

        In EnergyPlus / OpenStudio workflows, this property is used to subdivide
        the door when it has more than 4 vertices. This is necessary since
        EnergyPlus cannot accept sub-faces with more than 4 vertices.
        """
        return self._geometry.triangulated_mesh3d

    @property
    def normal(self):
        """A ladybug_geometry Vector3D for the direction the door is pointing.
        """
        return self._geometry.normal

    @property
    def center(self):
        """A ladybug_geometry Point3D for the center of the door.

        Note that this is the center of the bounding rectangle around this geometry
        and not the area centroid.
        """
        return self._geometry.center

    @property
    def area(self):
        """The area of the door."""
        return self._geometry.area

    @property
    def perimeter(self):
        """The perimeter of the door."""
        return self._geometry.perimeter

    def set_adjacency(self, other_door):
        """Set this door to be adjacent to another (and vice versa).

        Note that this method does not verify whether the other_door geometry is
        co-planar or compatible with this one so it is recommended that a test
        be performed before using this method in order to verify these criteria.
        The Face3D.is_centered_adjacent() or the Face3D.is_geometrically_equivalent()
        methods are both suitable for this purpose.

        Args:
            other_aperture: Another Aperture object to be set adjacent to this one.
        """
        assert isinstance(other_door, Door), \
            'Expected Door. Got {}.'.format(type(other_door))
        assert other_door.is_glass is self.is_glass, \
            'Adjacent doors must have matching is_glass properties.'
        self._boundary_condition = boundary_conditions.surface(other_door, True)
        other_door._boundary_condition = boundary_conditions.surface(self, True)

    def move(self, moving_vec):
        """Move this Door along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the face.
        """
        self._geometry = self.geometry.move(moving_vec)

    def rotate(self, axis, angle, origin):
        """Rotate this Door by a certain angle around an axis and origin.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate(axis, math.radians(angle), origin)

    def rotate_xy(self, angle, origin):
        """Rotate this Door counterclockwise in the world XY plane by a certain angle.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        self._geometry = self.geometry.rotate_xy(math.radians(angle), origin)

    def reflect(self, plane):
        """Reflect this Door across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        self._geometry = self.geometry.reflect(plane.n, plane.o)

    def scale(self, factor, origin=None):
        """Scale this Door by a factor from an origin point.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        self._geometry = self.geometry.scale(factor, origin)

    def check_planar(self, tolerance, raise_exception=True):
        """Check whether all of the Door's vertices lie within the same plane.

        Args:
            tolerance: The minimum distance between a given vertex and a the
                object's's plane at which the vertex is said to lie in the plane.
            raise_exception: Boolean to note whether an ValueError should be
                raised if a vertex does not lie within the object's plane.
        """
        try:
            return self.geometry.check_planar(tolerance, raise_exception)
        except ValueError as e:
            raise ValueError('Door "{}" is not planar.\n{}'.format(
                self.display_name, e))

    def check_self_intersecting(self, raise_exception=True):
        """Check whether the edges of the Door intersect one another (like a bowtwie).

        Args:
            raise_exception: If True, a ValueError will be raised if the object
                intersects with itself. Default: True.
        """
        if self.geometry.is_self_intersecting:
            if raise_exception:
                raise ValueError('Door "{}" has self-intersecting edges.'.format(
                    self.display_name))
            return False
        return True

    def check_non_zero(self, tolerance=0.0001, raise_exception=True):
        """Check whether the area of the Door is above a certain "zero" tolerance.

        Args:
            tolerance: The minimum acceptable area of the object. Default is 0.0001,
                which is equal to 1 cm2 when model units are meters. This is just
                above the smalest size that OpenStudio will accept.
            raise_exception: If True, a ValueError will be raised if the object
                area is below the tolerance. Default: True.
        """
        if self.area < tolerance:
            if raise_exception:
                raise ValueError(
                    'Door "{}" geometry is too small. Area must be at least {}. '
                    'Got {}.'.format(self.display_name, tolerance, self.area))
            return False
        return True

    @property
    def to(self):
        """Door writer object.

        Use this method to access Writer class to write the door in different formats.

        Usage:
            door.to.idf(door) -> idf string.
            door.to.radiance(door) -> Radiance string.
        """
        raise NotImplementedError('Door does not support writing to files.')
        return writer

    def to_dict(self, abridged=False, included_prop=None):
        """Return Door as a dictionary.

        Args:
            abridged: Boolean to note whether the extension properties of the
                object (ie. materials, construcitons) should be included in detail
                (False) or just referenced by name (True). Default: False.
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['energy'] will include 'energy' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        base = {'type': 'Door'}
        base['name'] = self.name
        base['display_name'] = self.display_name
        base['properties'] = self.properties.to_dict(abridged, included_prop)

        if 'energy' in base['properties']:
            base['geometry'] = self._geometry.to_dict(False, True)  # enforce upper-left
        else:
            base['geometry'] = self._geometry.to_dict(False)

        base['is_glass'] = self.is_glass
        if isinstance(self.boundary_condition, Outdoors) and 'energy' in base['properties']:
            base['boundary_condition'] = self.boundary_condition.to_dict(full=True)
        else:
            base['boundary_condition'] = self.boundary_condition.to_dict()
        return base

    def __copy__(self):
        new_door = Door(self.name, self.geometry, self.boundary_condition, self.is_glass)
        new_door._display_name = self.display_name
        new_door._properties._duplicate_extension_attr(self._properties)
        return new_door

    def __repr__(self):
        return 'Door: %s' % self.display_name

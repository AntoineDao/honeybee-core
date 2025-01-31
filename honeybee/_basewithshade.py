# coding: utf-8
"""Base class for all geometry objects that can have shades as children."""
from ._base import _Base
from .shade import Shade


class _BaseWithShade(_Base):
    """A base class for all objects that can have Shades nested on them.

    Properties:
        name
        display_name
        geometry
        outdoor_shades
        indoor_shades
    """
    __slots__ = ('_outdoor_shades', '_indoor_shades')

    def __init__(self, name):
        """Initialize base with shade object.

        Args:
            name: Object name. Must be < 100 characters.
        """
        _Base.__init__(self, name)  # process the name
        self._outdoor_shades = []
        self._indoor_shades = []

    @property
    def outdoor_shades(self):
        """Array of all outdoor shades assigned to this object."""
        return tuple(self._outdoor_shades)

    @property
    def indoor_shades(self):
        """Array of all indoor shades assigned to this object."""
        return tuple(self._indoor_shades)

    @property
    def shades(self):
        """Array of all shades (both indoor and outdoor) assigned to this object."""
        return self._outdoor_shades + self._indoor_shades

    def remove_shades(self):
        """Remove all indoor and outdoor shades assigned to this object."""
        self.remove_indoor_shades()
        self.remove_outdoor_shades()

    def remove_outdoor_shades(self):
        """Remove all outdoor shades assigned to this object."""
        for shade in self._outdoor_shades:
            shade._parent = None
        self._outdoor_shades = []

    def remove_indoor_shades(self):
        """Remove all indoor shades assigned to this object."""
        for shade in self._indoor_shades:
            shade._parent = None
        self._indoor_shades = []

    def add_outdoor_shade(self, shade):
        """Add a Shade object to the outdoor of this object.

        Outdoor Shade objects can be used to represent balconies, outdoor furniture,
        overhangs, light shelves, fins, the exterior part of mullions, etc.
        For representing larger shade objects like trees or other buildings,
        it may be more appropriate to add them to the Model as orphaned_shades
        without a specific parent object.

        Args:
            shade: A shade face to add to the outdoors of this object.
        """
        assert isinstance(shade, Shade), \
            'Expected Shade for outdoor_shade. Got {}.'.format(type(shade))
        shade._parent = self
        self._outdoor_shades.append(shade)

    def add_indoor_shade(self, shade):
        """Add a Shade object to be added to the indoor of this object.

        Indoor Shade objects can be used to represent furniture, the interior
        portion of light shelves, the interior part of mullions, etc.
        For representing finely detailed objects like blinds or roller shades,
        it may be more appropriate to model them as materials assigned to
        Aperture properties (like Radiance materials or Energy constructions).

        Args:
            shade: A Shade object to add to the indoors of this object.
        """
        assert isinstance(shade, Shade), \
            'Expected Shade for indoor_shade. Got {}.'.format(type(shade))
        shade._parent = self
        self._indoor_shades.append(shade)

    def move_shades(self, moving_vec):
        """Move all indoor and outdoor shades assigned to this object along a vector.

        Args:
            moving_vec: A ladybug_geometry Vector3D with the direction and distance
                to move the shades.
        """
        for oshd in self._outdoor_shades:
            oshd.move(moving_vec)
        for ishd in self._indoor_shades:
            ishd.move(moving_vec)

    def rotate_shades(self, axis, angle, origin):
        """Rotate all indoor and outdoor shades assigned to this object.

        Args:
            axis: A ladybug_geometry Vector3D axis representing the axis of rotation.
            angle: An angle for rotation in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for oshd in self._outdoor_shades:
            oshd.rotate(axis, angle, origin)
        for ishd in self._indoor_shades:
            ishd.rotate(axis, angle, origin)

    def rotate_xy_shades(self, angle, origin):
        """Rotate all indoor and outdoor shades counterclockwise in the world XY plane.

        Args:
            angle: An angle in degrees.
            origin: A ladybug_geometry Point3D for the origin around which the
                object will be rotated.
        """
        for oshd in self._outdoor_shades:
            oshd.rotate_xy(angle, origin)
        for ishd in self._indoor_shades:
            ishd.rotate_xy(angle, origin)

    def reflect_shades(self, plane):
        """Reflect all indoor and outdoor shades assigned to this object across a plane.

        Args:
            plane: A ladybug_geometry Plane across which the object will
                be reflected.
        """
        for oshd in self._outdoor_shades:
            oshd.reflect(plane)
        for ishd in self._indoor_shades:
            ishd.reflect(plane)

    def scale_shades(self, factor, origin=None):
        """Scale all indoor and outdoor shades assigned to this object by a factor.

        Args:
            factor: A number representing how much the object should be scaled.
            origin: A ladybug_geometry Point3D representing the origin from which
                to scale. If None, it will be scaled from the World origin (0, 0, 0).
        """
        for oshd in self._outdoor_shades:
            oshd.scale(factor, origin)
        for ishd in self._indoor_shades:
            ishd.scale(factor, origin)

    def _check_planar_shades(self, tolerance, raise_exception=True):
        """Check that all of the child shades are planar."""
        for oshd in self._outdoor_shades:
            if not oshd.check_planar(tolerance, raise_exception):
                return False
        for ishd in self._indoor_shades:
            if not ishd.check_planar(tolerance, raise_exception):
                return False
        return True

    def _check_self_intersecting_shades(self, raise_exception=True):
        """Check that no edges of the indoor or outdoor shades self-intersect."""
        for oshd in self._outdoor_shades:
            if not oshd.check_self_intersecting(raise_exception):
                return False
        for ishd in self._indoor_shades:
            if not ishd.check_self_intersecting(raise_exception):
                return False
        return True

    def _check_non_zero_shades(self, tolerance=0.0001, raise_exception=True):
        """Check that the indoor or outdoor shades are above a "zero" area tolerance."""
        for oshd in self._outdoor_shades:
            if not oshd.check_non_zero(tolerance, raise_exception):
                return False
        for ishd in self._indoor_shades:
            if not ishd.check_non_zero(tolerance, raise_exception):
                return False
        return True

    def _add_shades_to_dict(self, base, abridged=False, included_prop=None):
        """Method used to add child shades to the paret base dictionary.

        Args:
            base: The base object dictionary to which the child shades will be added.
            abridged: Boolean to note whether the extension properties of the
                object should be included in detail (False) or just referenced by
                name (True). Default: False.
            included_prop: List of properties to filter keys that must be included in
                output dictionary. For example ['energy'] will include 'energy' key if
                available in properties to_dict. By default all the keys will be
                included. To exclude all the keys from extensions use an empty list.
        """
        if self._outdoor_shades != []:
            base['outdoor_shades'] = [shd.to_dict(abridged, included_prop)
                                      for shd in self._outdoor_shades]
        if self._indoor_shades != []:
            base['indoor_shades'] = [shd.to_dict(abridged, included_prop)
                                     for shd in self._indoor_shades]

    def _recover_shades_from_dict(self, data):
        """Method used to recover shades from a dictionary.

        Args:
            data: The dictionary representation of this object to which shades will
                be added from the dictionary.
        """
        if 'outdoor_shades' in data and data['outdoor_shades'] is not None:
            self._outdoor_shades = [Shade.from_dict(sh) for sh in data['outdoor_shades']]
            for oshd in self._outdoor_shades:
                oshd._parent = self
        if 'indoor_shades' in data and data['indoor_shades'] is not None:
            self._indoor_shades = [Shade.from_dict(sh) for sh in data['indoor_shades']]
            for ishd in self._indoor_shades:
                ishd._parent = self

    def _duplicate_child_shades(self, new_object):
        """Add duplicated child shades to a duplcated new_object."""
        new_object._outdoor_shades = [oshd.duplicate() for oshd in self._outdoor_shades]
        new_object._indoor_shades = [ishd.duplicate() for ishd in self._indoor_shades]
        for oshd in new_object._outdoor_shades:
            oshd._parent = new_object
        for ishd in new_object._indoor_shades:
            ishd._parent = new_object

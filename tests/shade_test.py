"""Test the Shade class."""
from honeybee.shade import Shade

from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

import pytest


def test_shade_init():
    """Test the initialization of Shade objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shade = Shade('Test Shade', Face3D(pts))
    str(shade)  # test the string representation

    assert shade.name == 'TestShade'
    assert shade.display_name == 'Test Shade'
    assert isinstance(shade.geometry, Face3D)
    assert len(shade.vertices) == 4
    assert shade.upper_left_vertices[0] == Point3D(1, 0, 3)
    assert shade.normal == Vector3D(0, 1, 0)
    assert shade.center == Point3D(0.5, 0, 1.5)
    assert shade.area == 3
    assert shade.perimeter == 8
    assert not shade.has_parent


def test_shade_from_vertices():
    """Test the initialization of shade objects from vertices."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shade = Shade.from_vertices('Test Shade', pts)

    assert shade.name == 'TestShade'
    assert shade.display_name == 'Test Shade'
    assert isinstance(shade.geometry, Face3D)
    assert len(shade.vertices) == 4
    assert shade.upper_left_vertices[0] == Point3D(1, 0, 3)
    assert shade.normal == Vector3D(0, 1, 0)
    assert shade.center == Point3D(0.5, 0, 1.5)
    assert shade.area == 3
    assert shade.perimeter == 8
    assert not shade.has_parent


def test_shade_duplicate():
    """Test the duplication of shade objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    shd_1 = Shade('Test Shade', Face3D(pts))
    shd_2 = shd_1.duplicate()

    assert shd_1 is not shd_2
    for i, pt in enumerate(shd_1.vertices):
        assert pt == shd_2.vertices[i]
    assert shd_1.name == shd_2.name

    shd_2.move(Vector3D(0, 1, 0))
    for i, pt in enumerate(shd_1.vertices):
        assert pt != shd_2.vertices[i]


def test_move():
    """Test the shade move method."""
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
    shade = Shade('Rectangle Shade', Face3D(pts_1, plane_1))

    vec_1 = Vector3D(2, 2, 2)
    new_shd = shade.duplicate()
    new_shd.move(vec_1)
    assert new_shd.geometry[0] == Point3D(2, 2, 2)
    assert new_shd.geometry[1] == Point3D(4, 2, 2)
    assert new_shd.geometry[2] == Point3D(4, 4, 2)
    assert new_shd.geometry[3] == Point3D(2, 4, 2)
    assert new_shd.normal == shade.normal
    assert shade.area == new_shd.area
    assert shade.perimeter == new_shd.perimeter


def test_scale():
    """Test the shade scale method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shade = Shade('Rectangle Shade', Face3D(pts, plane))

    new_shd = shade.duplicate()
    new_shd.scale(2)
    assert new_shd.geometry[0] == Point3D(2, 2, 4)
    assert new_shd.geometry[1] == Point3D(4, 2, 4)
    assert new_shd.geometry[2] == Point3D(4, 4, 4)
    assert new_shd.geometry[3] == Point3D(2, 4, 4)
    assert new_shd.area == shade.area * 2 ** 2
    assert new_shd.perimeter == shade.perimeter * 2
    assert new_shd.normal == shade.normal


def test_rotate():
    """Test the shade rotate method."""
    pts = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shade = Shade('Rectangle Shade', Face3D(pts, plane))
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)

    test_1 = shade.duplicate()
    test_1.rotate(axis, 180, origin)
    assert test_1.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(-2, rel=1e-3)
    assert shade.area == test_1.area
    assert len(shade.vertices) == len(test_1.vertices)

    test_2 = shade.duplicate()
    test_2.rotate(axis, 90, origin)
    assert test_2.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[0].z == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[2].z == pytest.approx(2, rel=1e-3)
    assert shade.area == test_2.area
    assert len(shade.vertices) == len(test_2.vertices)


def test_rotate_xy():
    """Test the Shade rotate_xy method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shade = Shade('Rectangle Shade', Face3D(pts, plane))
    origin_1 = Point3D(1, 1, 0)

    test_1 = shade.duplicate()
    test_1.rotate_xy(180, origin_1)
    assert test_1.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)

    test_2 = shade.duplicate()
    test_2.rotate_xy(90, origin_1)
    assert test_2.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)


def test_reflect():
    """Test the Shade reflect method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shade = Shade('Rectangle Shade', Face3D(pts, plane))

    origin_1 = Point3D(1, 0, 2)
    origin_2 = Point3D(0, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    normal_2 = Vector3D(-1, -1, 0).normalize()
    plane_1 = Plane(normal_1, origin_1)
    plane_2 = Plane(normal_2, origin_2)
    plane_3 = Plane(normal_2, origin_1)

    test_1 = shade.duplicate()
    test_1.reflect(plane_1)
    assert test_1.geometry[-1].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_1 = shade.duplicate()
    test_1.reflect(plane_2)
    assert test_1.geometry[-1].x == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_2 = shade.duplicate()
    test_2.reflect(plane_3)
    assert test_2.geometry[-1].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].y == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[1].x == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].y == pytest.approx(-1, rel=1e-3)
    assert test_2.geometry[1].z == pytest.approx(2, rel=1e-3)


def test_check_planar():
    """Test the check_planar method."""
    pts_1 = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_2 = (Point3D(0, 0, 0), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    pts_3 = (Point3D(0, 0, 2.0001), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    shade_1 = Shade('Shade 1', Face3D(pts_1, plane_1))
    shade_2 = Shade('Shade 2', Face3D(pts_2, plane_1))
    shade_3 = Shade('Shade 3', Face3D(pts_3, plane_1))

    assert shade_1.check_planar(0.001) is True
    assert shade_2.check_planar(0.001, False) is False
    with pytest.raises(Exception):
        shade_2.check_planar(0.0001)
    assert shade_3.check_planar(0.001) is True
    assert shade_3.check_planar(0.000001, False) is False
    with pytest.raises(Exception):
        shade_3.check_planar(0.000001)


def test_check_self_intersecting():
    """Test the check_self_intersecting method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    plane_2 = Plane(Vector3D(0, 0, -1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(0, 2), Point3D(2, 0), Point3D(2, 2))
    shade_1 = Shade('shade 1', Face3D(pts_1, plane_1))
    shade_2 = Shade('shade 2', Face3D(pts_2, plane_1))
    shade_3 = Shade('shade 3', Face3D(pts_1, plane_2))
    shade_4 = Shade('shade 4', Face3D(pts_2, plane_2))

    assert shade_1.check_self_intersecting(False) is True
    assert shade_2.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert shade_2.check_self_intersecting(True)
    assert shade_3.check_self_intersecting(False) is True
    assert shade_4.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert shade_4.check_self_intersecting(True)


def test_check_non_zero():
    """Test the check_non_zero method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2))
    pts_2 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 0))
    shade_1 = Shade('shade 1', Face3D(pts_1, plane_1))
    shade_2 = Shade('shade 2', Face3D(pts_2, plane_1))

    assert shade_1.check_non_zero(0.0001, False) is True
    assert shade_2.check_non_zero(0.0001, False) is False
    with pytest.raises(Exception):
        assert shade_2.check_self_intersecting(0.0001, True)


def test_to_dict():
    """Test the shade to_dict method."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    dr = Shade.from_vertices('Rectangle Shade', vertices)

    drd = dr.to_dict()
    assert drd['type'] == 'Shade'
    assert drd['name'] == 'RectangleShade'
    assert drd['display_name'] == 'Rectangle Shade'
    assert 'geometry' in drd
    assert len(drd['geometry']['boundary']) == len(vertices)
    assert 'properties' in drd
    assert drd['properties']['type'] == 'ShadeProperties'

"""Test the Door class."""
from honeybee.door import Door
from honeybee.boundarycondition import Outdoors

from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D

import pytest


def test_door_init():
    """Test the initialization of Door objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    door = Door('Test Door', Face3D(pts))
    str(door)  # test the string representation

    assert door.name == 'TestDoor'
    assert door.display_name == 'Test Door'
    assert isinstance(door.geometry, Face3D)
    assert len(door.vertices) == 4
    assert door.upper_left_vertices[0] == Point3D(1, 0, 3)
    assert len(door.triangulated_mesh3d.faces) == 2
    assert door.normal == Vector3D(0, 1, 0)
    assert door.center == Point3D(0.5, 0, 1.5)
    assert door.area == 3
    assert door.perimeter == 8
    assert isinstance(door.boundary_condition, Outdoors)
    assert not door.has_parent


def test_door_from_vertices():
    """Test the initialization of Door objects from vertices."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    door = Door.from_vertices('Test Door', pts)

    assert door.name == 'TestDoor'
    assert door.display_name == 'Test Door'
    assert isinstance(door.geometry, Face3D)
    assert len(door.vertices) == 4
    assert door.upper_left_vertices[0] == Point3D(1, 0, 3)
    assert len(door.triangulated_mesh3d.faces) == 2
    assert door.normal == Vector3D(0, 1, 0)
    assert door.center == Point3D(0.5, 0, 1.5)
    assert door.area == 3
    assert door.perimeter == 8
    assert isinstance(door.boundary_condition, Outdoors)
    assert not door.has_parent


def test_door_duplicate():
    """Test the duplication of door objects."""
    pts = (Point3D(0, 0, 0), Point3D(0, 0, 3), Point3D(1, 0, 3), Point3D(1, 0, 0))
    dr_1 = Door('Test Door', Face3D(pts))
    dr_2 = dr_1.duplicate()

    assert dr_1 is not dr_2
    for i, pt in enumerate(dr_1.vertices):
        assert pt == dr_2.vertices[i]
    assert dr_1.name == dr_2.name

    dr_2.move(Vector3D(0, 1, 0))
    for i, pt in enumerate(dr_1.vertices):
        assert pt != dr_2.vertices[i]


def test_move():
    """Test the Door move method."""
    pts_1 = (Point3D(0, 0, 0), Point3D(2, 0, 0), Point3D(2, 2, 0), Point3D(0, 2, 0))
    plane_1 = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 0))
    door = Door('Rectangle Door', Face3D(pts_1, plane_1))

    vec_1 = Vector3D(2, 2, 2)
    new_dr = door.duplicate()
    new_dr.move(vec_1)
    assert new_dr.geometry[0] == Point3D(2, 2, 2)
    assert new_dr.geometry[1] == Point3D(4, 2, 2)
    assert new_dr.geometry[2] == Point3D(4, 4, 2)
    assert new_dr.geometry[3] == Point3D(2, 4, 2)
    assert new_dr.normal == door.normal
    assert door.area == new_dr.area
    assert door.perimeter == new_dr.perimeter


def test_scale():
    """Test the Door scale method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    door = Door('Rectangle Door', Face3D(pts, plane))

    new_dr = door.duplicate()
    new_dr.scale(2)
    assert new_dr.geometry[0] == Point3D(2, 2, 4)
    assert new_dr.geometry[1] == Point3D(4, 2, 4)
    assert new_dr.geometry[2] == Point3D(4, 4, 4)
    assert new_dr.geometry[3] == Point3D(2, 4, 4)
    assert new_dr.area == door.area * 2 ** 2
    assert new_dr.perimeter == door.perimeter * 2
    assert new_dr.normal == door.normal


def test_rotate():
    """Test the Door rotate method."""
    pts = (Point3D(0, 0, 2), Point3D(2, 0, 2), Point3D(2, 2, 2), Point3D(0, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    door = Door('Rectangle Door', Face3D(pts, plane))
    origin = Point3D(0, 0, 0)
    axis = Vector3D(1, 0, 0)

    test_1 = door.duplicate()
    test_1.rotate(axis, 180, origin)
    assert test_1.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(-2, rel=1e-3)
    assert door.area == test_1.area
    assert len(door.vertices) == len(test_1.vertices)

    test_2 = door.duplicate()
    test_2.rotate(axis, 90, origin)
    assert test_2.geometry[0].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[0].z == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(-2, rel=1e-3)
    assert test_2.geometry[2].z == pytest.approx(2, rel=1e-3)
    assert door.area == test_2.area
    assert len(door.vertices) == len(test_2.vertices)


def test_rotate_xy():
    """Test the Door rotate_xy method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    door = Door('Rectangle Door', Face3D(pts, plane))
    origin_1 = Point3D(1, 1, 0)

    test_1 = door.duplicate()
    test_1.rotate_xy(180, origin_1)
    assert test_1.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].y == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)

    test_2 = door.duplicate()
    test_2.rotate_xy(90, origin_1)
    assert test_2.geometry[0].x == pytest.approx(1, rel=1e-3)
    assert test_2.geometry[0].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[0].z == pytest.approx(2, rel=1e-3)
    assert test_2.geometry[2].x == pytest.approx(0, rel=1e-3)
    assert test_2.geometry[2].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[2].z == pytest.approx(2, rel=1e-3)


def test_reflect():
    """Test the Door reflect method."""
    pts = (Point3D(1, 1, 2), Point3D(2, 1, 2), Point3D(2, 2, 2), Point3D(1, 2, 2))
    plane = Plane(Vector3D(0, 0, 1), Point3D(0, 0, 2))
    door = Door('Rectangle Door', Face3D(pts, plane))

    origin_1 = Point3D(1, 0, 2)
    origin_2 = Point3D(0, 0, 2)
    normal_1 = Vector3D(1, 0, 0)
    normal_2 = Vector3D(-1, -1, 0).normalize()
    plane_1 = Plane(normal_1, origin_1)
    plane_2 = Plane(normal_2, origin_2)
    plane_3 = Plane(normal_2, origin_1)

    test_1 = door.duplicate()
    test_1.reflect(plane_1)
    assert test_1.geometry[-1].x == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(0, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_1 = door.duplicate()
    test_1.reflect(plane_2)
    assert test_1.geometry[-1].x == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].y == pytest.approx(-1, rel=1e-3)
    assert test_1.geometry[-1].z == pytest.approx(2, rel=1e-3)
    assert test_1.geometry[1].x == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].y == pytest.approx(-2, rel=1e-3)
    assert test_1.geometry[1].z == pytest.approx(2, rel=1e-3)

    test_2 = door.duplicate()
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
    door_1 = Door('Door 1', Face3D(pts_1, plane_1))
    door_2 = Door('Door 2', Face3D(pts_2, plane_1))
    door_3 = Door('Door 3', Face3D(pts_3, plane_1))

    assert door_1.check_planar(0.001) is True
    assert door_2.check_planar(0.001, False) is False
    with pytest.raises(Exception):
        door_2.check_planar(0.0001)
    assert door_3.check_planar(0.001) is True
    assert door_3.check_planar(0.000001, False) is False
    with pytest.raises(Exception):
        door_3.check_planar(0.000001)


def test_check_self_intersecting():
    """Test the check_self_intersecting method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    plane_2 = Plane(Vector3D(0, 0, -1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2), Point3D(0, 2))
    pts_2 = (Point3D(0, 0), Point3D(0, 2), Point3D(2, 0), Point3D(2, 2))
    door_1 = Door('Door 1', Face3D(pts_1, plane_1))
    door_2 = Door('Door 2', Face3D(pts_2, plane_1))
    door_3 = Door('Door 3', Face3D(pts_1, plane_2))
    door_4 = Door('Door 4', Face3D(pts_2, plane_2))

    assert door_1.check_self_intersecting(False) is True
    assert door_2.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert door_2.check_self_intersecting(True)
    assert door_3.check_self_intersecting(False) is True
    assert door_4.check_self_intersecting(False) is False
    with pytest.raises(Exception):
        assert door_4.check_self_intersecting(True)


def test_check_non_zero():
    """Test the check_non_zero method."""
    plane_1 = Plane(Vector3D(0, 0, 1))
    pts_1 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 2))
    pts_2 = (Point3D(0, 0), Point3D(2, 0), Point3D(2, 0))
    door_1 = Door('Door 1', Face3D(pts_1, plane_1))
    door_2 = Door('Door 2', Face3D(pts_2, plane_1))

    assert door_1.check_non_zero(0.0001, False) is True
    assert door_2.check_non_zero(0.0001, False) is False
    with pytest.raises(Exception):
        assert door_2.check_self_intersecting(0.0001, True)


def test_to_dict():
    """Test the Door to_dict method."""
    vertices = [[0, 0, 0], [0, 10, 0], [0, 10, 3], [0, 0, 3]]
    dr = Door.from_vertices('Rectangle Door', vertices)

    drd = dr.to_dict()
    assert drd['type'] == 'Door'
    assert drd['name'] == 'RectangleDoor'
    assert drd['display_name'] == 'Rectangle Door'
    assert 'geometry' in drd
    assert len(drd['geometry']['boundary']) == len(vertices)
    assert 'properties' in drd
    assert drd['properties']['type'] == 'DoorProperties'
    assert drd['boundary_condition']['type'] == 'Outdoors'

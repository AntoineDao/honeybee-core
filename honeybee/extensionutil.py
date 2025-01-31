# coding: utf-8
"""A series of utility functions that are useful across several honeybee extensions."""


def model_extension_dicts(data, extension_key, room_ext_dicts=[], face_ext_dicts=[],
                          shade_ext_dicts=[], aperture_ext_dicts=[], door_ext_dicts=[]):
    """Get all Model property dictioanires of an extension organized by geometry type.

    Note that the order in which dictaionaries appear in the output lists is the
    same order as the geometry objects appear when requested from the model.
    For example, the shade_ext_dicts align with the model.shades.

    Args:
        data: A dictionary representation of an entire honeybee-core Model.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        room_ext_dicts: A list of Room extension property dictionaries that
            align with the serialized model.rooms.
        face_ext_dicts: A list of Face extension property dictionaries that
            align with the serialized model.faces.
        shade_ext_dicts: A list of Shade extension property dictionaries that
            align with the serialized model.shades.
        aperture_ext_dicts: A list of Aperture extension property dictionaries that
            align with the serialized model.apertures.
        door_ext_dicts: A list of Door extension property dictionaries that
            align with the serialized model.doors.
    """
    assert data['type'] == 'Model', \
        'Expected Model dictionary. Got {}.'.format(data['type'])

    # loop through the model dictionary using the same logic that the
    # model does when you requst rooms, faces, shades, apertures and doors.
    if 'rooms' in data:
        room_extension_dicts(data['rooms'], extension_key, room_ext_dicts,
                             face_ext_dicts, shade_ext_dicts, aperture_ext_dicts,
                             door_ext_dicts)
    if 'orphaned_faces' in data:
        face_extension_dicts(data['orphaned_faces'], extension_key, face_ext_dicts,
                             shade_ext_dicts, aperture_ext_dicts, door_ext_dicts)
    if 'orphaned_apertures' in data:
        aperture_extension_dicts(data['orphaned_apertures'], extension_key,
                                 aperture_ext_dicts, shade_ext_dicts)
    if 'orphaned_shades' in data:
        shade_extension_dicts(data['orphaned_shades'], extension_key, shade_ext_dicts)
    if 'orphaned_doors' in data:
        door_extension_dicts(data['orphaned_doors'], extension_key, door_ext_dicts)

    return room_ext_dicts, face_ext_dicts, shade_ext_dicts, \
        aperture_ext_dicts, door_ext_dicts


def room_extension_dicts(room_list, extension_key, room_ext_dicts=[], face_ext_dicts=[],
                         shade_ext_dicts=[], aperture_ext_dicts=[], door_ext_dicts=[]):
    """Get all Room property dictionaires of an extension organized by geometry type.

    Args:
        room_list: A list of Room dictionaries.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        room_ext_dicts: A list with the Room extension property dictionaries.
        face_ext_dicts: A list with Face extension property dictionaries.
        shade_ext_dicts: A list with Shade extension property dictionaries.
        aperture_ext_dicts: A list with Aperture extension property dictionaries.
        door_ext_dicts: A list with Door extension property dictionaries.
    """
    for room_dict in room_list:
        room_ext_dicts.append(room_dict['properties'][extension_key])
        if 'outdoor_shades' in room_dict:
            shade_extension_dicts(room_dict['outdoor_shades'], extension_key,
                                  shade_ext_dicts)
        if 'indoor_shades' in room_dict:
            shade_extension_dicts(room_dict['indoor_shades'], extension_key,
                                  shade_ext_dicts)
        face_extension_dicts(room_dict['faces'], extension_key, face_ext_dicts,
                             shade_ext_dicts, aperture_ext_dicts, door_ext_dicts)
    return room_ext_dicts, face_ext_dicts, shade_ext_dicts, \
        aperture_ext_dicts, door_ext_dicts


def face_extension_dicts(face_list, extension_key, face_ext_dicts=[],
                         shade_ext_dicts=[], aperture_ext_dicts=[], door_ext_dicts=[]):
    """Get all Face property dictionaires of an extension organized by geometry type.

    Args:
        face_list: A list of Room dictionaries.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        face_ext_dicts: A list with Face extension property dictionaries.
        shade_ext_dicts: A list with Shade extension property dictionaries.
        aperture_ext_dicts: A list with Aperture extension property dictionaries.
        door_ext_dicts: A list with Door extension property dictionaries.
    """
    for face_dict in face_list:
        face_ext_dicts.append(face_dict['properties'][extension_key])
        if 'outdoor_shades' in face_dict:
            shade_extension_dicts(face_dict['outdoor_shades'], extension_key,
                                  shade_ext_dicts)
        if 'indoor_shades' in face_dict:
            shade_extension_dicts(face_dict['indoor_shades'], extension_key,
                                  shade_ext_dicts)
        if 'apertures' in face_dict:
            aperture_extension_dicts(face_dict['apertures'], extension_key,
                                     aperture_ext_dicts, shade_ext_dicts)
        if 'doors' in face_dict:
            door_extension_dicts(face_dict['doors'], extension_key, door_ext_dicts)
    return face_ext_dicts, shade_ext_dicts, aperture_ext_dicts, door_ext_dicts


def shade_extension_dicts(shade_list, extension_key, shade_ext_dicts=[]):
    """Get all Shade property dictionaires of an extension organized by geometry type.

    Args:
        shade_list: A list of Shade dictionaries.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        shade_ext_dicts: A list with Shade extension property dictionaries.
    """
    for shd_dict in shade_list:
        shade_ext_dicts.append(shd_dict['properties'][extension_key])
    return shade_ext_dicts


def aperture_extension_dicts(aperture_list, extension_key, aperture_ext_dicts=[],
                             shade_ext_dicts=[]):
    """Get all Shade property dictionaires of an extension organized by geometry type.

    Args:
        shade_list: A list of Shade dictionaries.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        aperture_ext_dicts: A list with Aperture extension property dictionaries.
        shade_ext_dicts: A list with Shade extension property dictionaries.
    """
    for ap_dict in aperture_list:
        aperture_ext_dicts.append(ap_dict['properties'][extension_key])
        if 'outdoor_shades' in ap_dict:
            shade_extension_dicts(ap_dict['outdoor_shades'], extension_key, shade_ext_dicts)
        if 'indoor_shades' in ap_dict:
            shade_extension_dicts(ap_dict['indoor_shades'], extension_key, shade_ext_dicts)
    return aperture_ext_dicts, shade_ext_dicts


def door_extension_dicts(door_list, extension_key, door_ext_dicts=[]):
    """Get all Shade property dictionaires of an extension organized by geometry type.

    Args:
        shade_list: A list of Shade dictionaries.
        extension_key: Text for the key of the extension (eg. "energy", "radiance").

    Returns:
        door_ext_dicts: A list with Door extension property dictionaries.
    """
    for dr_dict in door_list:
        door_ext_dicts.append(dr_dict['properties'][extension_key])
    return door_ext_dicts

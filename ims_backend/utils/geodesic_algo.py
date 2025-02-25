from geopy.distance import geodesic


def is_user_at_location(target_coords, user_coords, threshold_meters=50):
    """
    Checks if a user is at particular location based on their coordinates.

    :param target_coords: Tuple (latitude, longitude) of the target location.
    :param user_coords: Tuple (latitude, longitude) of the user's current location.
    :param threshold_meters: Maximum allowed distance in meters for the user to be considered 'at the location'.
    :return: True if the user is within the threshold, otherwise False.
    """
    distance = geodesic(target_coords, user_coords).meters
    return distance <= threshold_meters

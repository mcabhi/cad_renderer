import json
import random
import string

from bottle import run, request, static_file, post

from draw import Canvas


@post('/cad')
def index():
    canvas = Canvas(request.json)
    canvas.draw()

    return static_file(canvas.filename, root='/', download=True)

run(host='0.0.0.0', port=5002)


def find_intersection_between_intervals(intervals):
    """Find the intersection between intervals.

    Args:
        intervals (list): List of intervals.

    Returns:
        list: List of intervals.

    Examples:
        >>> find_intersection_between_intervals([[1, 3], [2, 4], [5, 7], [6, 8]])
        [[2, 3], [6, 7]]
    """
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]

    for interval in intervals[1:]:
        if interval[0] <= result[-1][1]:
            result[-1][1] = min(result[-1][1], interval[1])
        else:
            result.append(interval)

    return result


def generate_random_filename(length=10):
    """Generate random filename.

    Args:
        length (int): Length of filename.

    Returns:
        str: Random filename.

    Examples:
        >>> generate_random_filename()
        'j8b7o3w2j1'
    """
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
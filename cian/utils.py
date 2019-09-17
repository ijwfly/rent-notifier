from collections import defaultdict, namedtuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D
from scipy.cluster.vq import kmeans2, whiten


def clusterize(coords_list, max_points=28):
    clusters_count = int(len(coords_list) / max_points + 2)
    coordinates= np.array(coords_list)
    x, y = kmeans2(whiten(coordinates), clusters_count, iter=20)
    cluster_map = defaultdict(list)
    for coord, cluster_id in zip(coordinates, y):
        cluster_map[cluster_id].append(coord)

    return cluster_map


def clusterize_w_limit(coords_list, max_points=28):
    # HACK: будем кластеризовать до тех пор, пока в каждом кластере не будет меньше max_points точек
    while True:
        result = clusterize(coords_list, max_points)
        for cluster_id, coords in result.items():
            if len(coords) > max_points:
                break
        else:
            break
    return result


Point = namedtuple('Point', 'x y')


class ConvexHull(object):

    def __init__(self):
        self._points = set()
        self._hull_points = []

    def add(self, point):
        self._points.add(point)

    def _get_orientation(self, origin, p1, p2):
        '''
        Returns the orientation of the Point p1 with regards to Point p2 using origin.
        Negative if p1 is clockwise of p2.
        :param p1:
        :param p2:
        :return: integer
        '''
        difference = (
            ((p2.x - origin.x) * (p1.y - origin.y))
            - ((p1.x - origin.x) * (p2.y - origin.y))
        )

        return difference

    def compute_hull(self):
        '''
        Computes the points that make up the convex hull.
        :return:
        '''
        points = list(self._points)

        # get leftmost point
        start = points[0]
        min_x = start.x
        for p in points[1:]:
            if p.x < min_x:
                min_x = p.x
                start = p

        point = start
        self._hull_points.append(start)

        far_point = None
        while far_point is not start:

            # get the first point (initial max) to use to compare with others
            p1 = None
            for p in points:
                if p is point:
                    continue
                else:
                    p1 = p
                    break

            far_point = p1

            for p2 in points:
                # ensure we aren't comparing to self or pivot point
                if p2 is point or p2 is p1:
                    continue
                else:
                    direction = self._get_orientation(point, far_point, p2)
                    if direction > 0:
                        far_point = p2

            self._hull_points.append(far_point)
            point = far_point

    def get_hull_points(self):
        if self._points and not self._hull_points:
            self.compute_hull()

        return self._hull_points

    def display(self):
        # all points
        x = [p.x for p in self._points]
        y = [p.y for p in self._points]
        plt.plot(x, y, marker='D', linestyle='None')

        # hull points
        hx = [p.x for p in self._hull_points]
        hy = [p.y for p in self._hull_points]
        plt.plot(hx, hy)

        plt.title('Convex Hull')
        plt.show()


def get_polygon_center(polygon):
    x, y = zip(*polygon)
    return (max(x) + min(x)) / 2., (max(y) + min(y)) / 2.


def scale_polygon(polygon, scale):
    center_x, center_y = get_polygon_center(polygon)
    to_center = Affine2D()
    to_center.translate(-center_x, -center_y)
    polygon = to_center.transform(polygon)

    to_scale = Affine2D()
    to_scale.scale(scale)
    polygon = to_scale.transform(polygon)

    to_position = Affine2D()
    to_position.translate(center_x, center_y)
    polygon = to_position.transform(polygon)
    return list(tuple(p) for p in polygon)

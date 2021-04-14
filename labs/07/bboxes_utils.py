#!/usr/bin/env python3
import numpy as np

from svhn_dataset import SVHN

BACKEND = np # or you can use `tf` for TensorFlow implementation

def bboxes_area(bboxes):
    """ Compute area of given set of bboxes.

    The computation can be performed either using Numpy or TensorFlow.
    Each bbox is parametrized as a four-tuple (top, left, bottom, right).

    If the bboxes.shape is [..., 4], the output shape is bboxes.shape[:-1].
    """
    return BACKEND.maximum(bboxes[..., SVHN.BOTTOM] - bboxes[..., SVHN.TOP], 0) \
        * BACKEND.maximum(bboxes[..., SVHN.RIGHT] - bboxes[..., SVHN.LEFT], 0)

def bboxes_iou(xs, ys):
    """ Compute IoU of corresponding pairs from two sets of bboxes xs and ys.

    The computation can be performed either using Numpy or TensorFlow.
    Each bbox is parametrized as a four-tuple (top, left, bottom, right).

    Note that broadcasting is supported, so passing inputs with
    xs.shape=[num_xs, 1, 4] and ys.shape=[1, num_ys, 4] will produce output
    with shape [num_xs, num_ys], computing IoU for all pairs of bboxes from
    xs and ys. Formally, the output shape is np.broadcast(xs, ys).shape[:-1].
    """
    intersections = BACKEND.stack([
        BACKEND.maximum(xs[..., SVHN.TOP], ys[..., SVHN.TOP]),
        BACKEND.maximum(xs[..., SVHN.LEFT], ys[..., SVHN.LEFT]),
        BACKEND.minimum(xs[..., SVHN.BOTTOM], ys[..., SVHN.BOTTOM]),
        BACKEND.minimum(xs[..., SVHN.RIGHT], ys[..., SVHN.RIGHT]),
    ], axis=-1)

    xs_area, ys_area, intersections_area = bboxes_area(xs), bboxes_area(ys), bboxes_area(intersections)

    return intersections_area / (xs_area + ys_area - intersections_area)

def bboxes_to_fast_rcnn(anchors, bboxes):
    """ Convert `bboxes` to a Fast-R-CNN-like representation relative to `anchors`.

    The `anchors` and `bboxes` are arrays of four-tuples (top, left, bottom, right);
    you can use SVNH.{TOP, LEFT, BOTTOM, RIGHT} as indices of the respective coordinates.

    The resulting representation of a single bbox is a four-tuple with:
    - (bbox_y_center - anchor_y_center) / anchor_height
    - (bbox_x_center - anchor_x_center) / anchor_width
    - log(bbox_height / anchor_height)
    - log(bbox_width / anchor_width)

    If the anchors.shape is [anchors_len, 4], bboxes.shape is [anchors_len, 4],
    the output shape is [anchors_len, 4].
    """

    # TODO: Implement according to the docstring.
    raise NotImplementedError()

def bboxes_from_fast_rcnn(anchors, fast_rcnns):
    """ Convert Fast-R-CNN-like representation relative to `anchor` to a `bbox`.

    The anchors.shape is [anchors_len, 4], fast_rcnns.shape is [anchors_len, 4],
    the output shape is [anchors_len, 4].
    """

    # TODO: Implement according to the docstring.
    raise NotImplementedError()

def bboxes_training(anchors, gold_classes, gold_bboxes, iou_threshold):
    """ Compute training data for object detection.

    Arguments:
    - `anchors` is an array of four-tuples (top, left, bottom, right)
    - `gold_classes` is an array of zero-based classes of the gold objects
    - `gold_bboxes` is an array of four-tuples (top, left, bottom, right)
      of the gold objects
    - `iou_threshold` is a given threshold

    Returns:
    - `anchor_classes` contains for every anchor either 0 for background
      (if no gold object is assigned) or `1 + gold_class` if a gold object
      with `gold_class` is assigned to it
    - `anchor_bboxes` contains for every anchor a four-tuple
      `(center_y, center_x, height, width)` representing the gold bbox of
      a chosen object using parametrization of Fast R-CNN; zeros if no
      gold object was assigned to the anchor

    Algorithm:
    - First, for each gold object, assign it to an anchor with the largest IoU
      (the one with smaller index if there are several). In case several gold
      objects are assigned to a single anchor, use the gold object with smaller
      index.
    - For each unused anchors, find the gold object with the largest IoU
      (again the one with smaller index if there are several), and if the IoU
      is >= iou_threshold, assign the object to the anchor.
    """

    # TODO: First, for each gold object, assign it to an anchor with the
    # largest IoU (the one with smaller index if there are several). In case
    # several gold objects are assigned to a single anchor, use the gold object
    # with smaller index.

    # TODO: For each unused anchors, find the gold object with the largest IoU
    # (again the one with smaller index if there are several), and if the IoU
    # is >= threshold, assign the object to the anchor.

    return anchor_classes, anchor_bboxes

def main(args):
    return bboxes_to_fast_rcnn, bboxes_from_fast_rcnn, bboxes_training

import unittest
class Tests(unittest.TestCase):
    def test_bboxes_to_from_fast_rcnn(self):
        for anchor, bbox, fast_rcnn in [
                [[[0, 0, 10, 10]], [[0, 0, 10, 10]], [[0,  0, 0, 0]]],
                [[[0, 0, 10, 10]], [[5, 0, 15, 10]], [[.5, 0, 0, 0]]],
                [[[0, 0, 10, 10]], [[0, 5, 10, 15]], [[0, .5, 0, 0]]],
                [[[0, 0, 10, 10]], [[0, 0, 20, 30]], [[.5, 1, np.log(2), np.log(3)]]],
        ]:
            anchor, bbox, fast_rcnn = np.array(anchor, np.float32), np.array(bbox, np.float32), np.array(fast_rcnn, np.float32)
            np.testing.assert_almost_equal(bboxes_to_fast_rcnn(anchor, bbox), fast_rcnn, decimal=3)
            np.testing.assert_almost_equal(bboxes_from_fast_rcnn(anchor, fast_rcnn), bbox, decimal=3)

    def test_bboxes_training(self):
        anchors = np.array([[0, 0, 10, 10], [0, 10, 10, 20], [10, 0, 20, 10], [10, 10, 20, 20]], np.float32)
        for gold_classes, gold_bboxes, anchor_classes, anchor_bboxes, iou in [
                [[1], [[14., 14, 16, 16]], [0, 0, 0, 2], [[0, 0, 0, 0]] * 3 + [[0, 0, np.log(1/5), np.log(1/5)]], 0.5],
                [[2], [[0., 0, 20, 20]], [3, 0, 0, 0], [[.5, .5, np.log(2), np.log(2)]] + [[0, 0, 0, 0]] * 3, 0.26],
                [[2], [[0., 0, 20, 20]], [3, 3, 3, 3], [[y, x, np.log(2), np.log(2)] for y in [.5, -.5] for x in [.5, -.5]], 0.24],
        ]:
            gold_classes, anchor_classes = np.array(gold_classes, np.int32), np.array(anchor_classes, np.int32)
            gold_bboxes, anchor_bboxes = np.array(gold_bboxes, np.float32), np.array(anchor_bboxes, np.float32)
            computed_classes, computed_bboxes = bboxes_training(anchors, gold_classes, gold_bboxes, iou)
            np.testing.assert_almost_equal(computed_classes, anchor_classes, decimal=3)
            np.testing.assert_almost_equal(computed_bboxes, anchor_bboxes, decimal=3)

if __name__ == '__main__':
    unittest.main()

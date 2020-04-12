"""
Proj: YZ_utils
Date: 8/15/18
Written by Yuezun Li
--------------------------
"""

import numpy as np
# from YZ_utils.box_utils.cython_bbox import bbox_overlaps


def xyxy2xywh(box):
    """
    Change [x, y, x, y] to [x, y, w, h]
    :param box:
    :return:
    """
    box = np.array(box)
    box[:, 2] = box[:, 2] - box[:, 0]
    box[:, 3] = box[:, 3] - box[:, 1]
    return box


def xywh2xyxy(box):
    """
    Change [x, y, w, h] to [x, y, x, y]
    Here we do not care the boundary (+1 pixel)
    :param box:
    :return:
    """
    box = np.array(box)
    box[:, 2] = box[:, 2] + box[:, 0]
    box[:, 3] = box[:, 3] + box[:, 1]
    return box


def box2mask(shape, boxes, order='nchw'):
    """ Make pixels inside box as 1 outside as 0 """
    if order == 'nchw':
        img_h, img_w = shape[-2], shape[-1]
    else:
        img_h, img_w = shape[-3], shape[-2]
    if len(boxes):
        mask = np.zeros(shape)
        for i in range(len(boxes)):
            x1, y1, x2, y2 = \
                int(boxes[i][0] * img_w), int(boxes[i][1] * img_h), int(boxes[i][2] * img_w), int(
                    boxes[i][3] * img_h)
            if order == 'nchw':
                mask[:, :, y1:y2, x1:x2] = 1
            else:
                mask[:, y1:y2, x1:x2, :] = 1
    else:
        mask = np.ones(shape)    
    return mask
    

def jaccard_np(boxes_a, boxes_b):
    """
    Compuate jaccard overlap
    :param boxes_a: Nx4
    :param boxes_b: Nx4
    :return:
    """
    boxes_a = np.array(boxes_a, dtype=np.float32)
    boxes_b = np.array(boxes_b, dtype=np.float32)
    max_xy = np.minimum(np.expand_dims(boxes_a[:, 2:], axis=1), np.expand_dims(boxes_b[:, 2:], axis=0))
    min_xy = np.maximum(np.expand_dims(boxes_a[:, :2], axis=1), np.expand_dims(boxes_b[:, :2], axis=0))

    inter = np.maximum((max_xy - min_xy), 0)
    inter_area = inter[:, :, 0] * inter[:, :, 1]

    area_a = np.expand_dims(((boxes_a[:, 2] - boxes_a[:, 0]) *
              (boxes_a[:, 3] - boxes_a[:, 1])), axis=1)
    area_b = np.expand_dims(((boxes_b[:, 2] - boxes_b[:, 0]) *
              (boxes_b[:, 3] - boxes_b[:, 1])), axis=0)
    union = area_a + area_b - inter_area
    return inter_area / union



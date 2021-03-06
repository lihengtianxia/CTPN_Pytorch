import math
import other
import copy
from other.lib import find_top_bottom as f


def generate_gt_anchor(img, box, anchor_width=16, cpu_speedup=True):
    """
    calsulate ground truth fine-scale box
    :param img: input image
    :param box: ground truth box (4 point)
    :param anchor_width:
    :param cpu_speedup: use cython speed up
    :return: tuple (position, h, cy)
    """
    if not isinstance(box[0], float):
        box = [float(box[i]) for i in range(len(box))]
    result = []
    left_anchor_num = int(math.floor(min(box[0], box[6]) / anchor_width))
    right_anchor_num = int(math.ceil(max(box[2], box[4]) / anchor_width))
    if right_anchor_num * 16 + 15 > img.shape[1]:
        right_anchor_num -= 1
    position_pair = [(i * anchor_width, (i + 1) * anchor_width - 1) for i in range(left_anchor_num, right_anchor_num)]
    y_top, y_bottom = cal_y_top_and_bottom(img, position_pair, box, cpu_speedup=cpu_speedup)
    for i in range(len(position_pair)):
        position = int(position_pair[i][0] / anchor_width)
        h = y_bottom[i] - y_top[i] + 1
        cy = (float(y_bottom[i]) + float(y_top[i])) / 2.0
        result.append((position, cy, h))
    return result


def cal_y_top_and_bottom(raw_img, position_pair, box, cpu_speedup=False):
    """
    :param raw_img:
    :param position_pair: for example:[(0, 15), (16, 31), ...]
    :param box: gt box (4 point)
    :param cpu_speedup: use cython speed up
    :return: top and bottom coordinates for y-axis
    """
    img = copy.deepcopy(raw_img)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            img[i, j, 0] = 0
    img = other.draw_box_4pt(img, box, color=(255, 0, 0))
    if cpu_speedup:
        y_top, y_bottom = f.find_top_bottom(img, position_pair)
    else:
        y_top = []
        y_bottom = []
        height = img.shape[0]
        top_flag = False
        bottom_flag = False
        for k in range(len(position_pair)):
            for y in range(0, height):
                for x in range(position_pair[k][0], position_pair[k][1] + 1):
                    if img[y, x, 0] == 255:
                        y_top.append(y)
                        top_flag = True
                        break
                if top_flag is True:
                    break
            for y in range(height - 1, -1, -1):
                for x in range(position_pair[k][0], position_pair[k][1] + 1):
                    if img[y, x, 0] == 255:
                        y_bottom.append(y)
                        bottom_flag = True
                        break
                if bottom_flag is True:
                    break
            top_flag = False
            bottom_flag = False
    return y_top, y_bottom

import imp
import numpy as np
import math

class HelperFunction:

    @staticmethod
    def rotate_arbitrary(axis, point, angle=None, degree=True):
        """Rotate the 3D point about the given axis.
        通过得到轴线旋转3D点
        If axis is not normalized and angle is None, the angle is taken as the norm
        of axis. If degree == False, angles are expected in radiant.
        如果axis没有标准化且角度为空，这个角将使用一个基准脚，如果degree == false 角是弧度"""

        # ensure axis is unit length        确定轴线是单位长
        axisNorm = np.linalg.norm(axis)
        if axisNorm == 0: return point
        axisn    = axis / axisNorm
        if angle == None:
            angle = axisNorm
            
        if degree:
            # convert to radiant　转化成弧度制
            angle *= np.pi / 180.0

        u = axisn[0]
        v = axisn[1]
        w = axisn[2]
        x = point[0]
        y = point[1]
        z = point[2]

        sin = math.sin(angle)
        cos = math.cos(angle)
        dot = np.dot(axisn, point)
        tmp = dot * (1 - cos)

        result = np.array([u * tmp + x*cos + (-w*y + v*z) * sin, \
                        v * tmp + y*cos + ( w*x - u*z) * sin, \
                        w * tmp + z*cos + (-v*x + u*y) * sin])

        return result
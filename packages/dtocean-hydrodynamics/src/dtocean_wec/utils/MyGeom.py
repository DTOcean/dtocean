import math
from typing import Self, overload


class Point3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.coordinates = [x, y, z]

    def x(self):
        return self.coordinates[0]

    def y(self):
        return self.coordinates[1]

    def z(self):
        return self.coordinates[2]

    def __repr__(self):
        return (
            "Point3D("
            + str(self.x())
            + ","
            + str(self.y())
            + ","
            + str(self.z())
            + ")"
        )

    def __str__(self):
        return (
            "P("
            + str(self.x())
            + ","
            + str(self.y())
            + ","
            + str(self.z())
            + ")"
        )

    def get(self):
        return self.coordinates

    def returnCopy(self):
        return Point3D(self.x(), self.y(), self.z())

    def asVector3D(self):
        return Vector3D(self.x(), self.y(), self.z())

    def distance(self, other):
        return (other - self).length()

    def average(self, other):
        return Point3D(
            (self.x() + other.x()) * 0.5,
            (self.y() + other.y()) * 0.5,
            (self.z() + other.z()) * 0.5,
        )

    def __add__(self, other):
        return Point3D(
            self.x() + other.x(),
            self.y() + other.y(),
            self.z() + other.z(),
        )

    @overload
    def __sub__(self, other: Self) -> "Vector3D": ...

    @overload
    def __sub__(self, other: "Vector3D") -> Self: ...

    def __sub__(self, other):
        if isinstance(other, Vector3D):
            return Point3D(
                self.x() - other.x(),
                self.y() - other.y(),
                self.z() - other.z(),
            )
        return Vector3D(
            self.x() - other.x(),
            self.y() - other.y(),
            self.z() - other.z(),
        )

    def __eq__(self, other):
        return (
            self.x() == other.x()
            and self.y() == other.y()
            and self.z() == other.z()
        )

    def __ne__(self, other):
        return not (self == other)


class Vector3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.coordinates = [x, y, z]

    def x(self):
        return self.coordinates[0]

    def y(self):
        return self.coordinates[1]

    def z(self):
        return self.coordinates[2]

    def __repr__(self):
        return (
            "Vector3D("
            + str(self.x())
            + ","
            + str(self.y())
            + ","
            + str(self.z())
            + ")"
        )

    def __str__(self):
        return (
            "V("
            + str(self.x())
            + ","
            + str(self.y())
            + ","
            + str(self.z())
            + ")"
        )

    def get(self):
        return self.coordinates

    def returnCopy(self):
        return Vector3D(self.x(), self.y(), self.z())

    def asPoint3D(self):
        return Point3D(self.x(), self.y(), self.z())

    def lengthSquared(self):
        return self.x() * self.x() + self.y() * self.y() + self.z() * self.z()

    def length(self):
        return math.sqrt(self.lengthSquared())

    def normalized(self):
        length = self.length()
        if length > 0:
            return Vector3D(
                self.x() / length,
                self.y() / length,
                self.z() / length,
            )
        return self.returnCopy()

    def __neg__(self):
        return Vector3D(-self.x(), -self.y(), -self.z())

    def __add__(self, other):
        if isinstance(other, Point3D):
            return Point3D(
                self.x() + other.x(),
                self.y() + other.y(),
                self.z() + other.z(),
            )
        return Vector3D(
            self.x() + other.x(),
            self.y() + other.y(),
            self.z() + other.z(),
        )

    def __sub__(self, other):
        return Vector3D(
            self.x() - other.x(),
            self.y() - other.y(),
            self.z() - other.z(),
        )

    def __mul__(self, other):
        if isinstance(other, Vector3D):
            # dot product
            return (
                self.x() * other.x()
                + self.y() * other.y()
                + self.z() * other.z()
            )
        # scalar product
        return Vector3D(self.x() * other, self.y() * other, self.z() * other)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        return Vector3D(self.x() / other, self.y() / other, self.z() / other)

    def __xor__(self, other):  # cross product
        return Vector3D(
            self.y() * other.z() - self.z() * other.y(),
            self.z() * other.x() - self.x() * other.z(),
            self.x() * other.y() - self.y() * other.x(),
        )

    def __eq__(self, other):
        return (
            self.x() == other.x()
            and self.y() == other.y()
            and self.z() == other.z()
        )

    def __ne__(self, other):
        return not (self == other)


class Matrix4x4:
    def __init__(self):
        self.setToIdentity()

    def __str__(self):
        return (
            str(self.m[0:4])
            + "\n"
            + str(self.m[4:8])
            + "\n"
            + str(self.m[8:12])
            + "\n"
            + str(self.m[12:16])
        )

    def get(self):
        return self.m

    def returnCopy(self):
        M = Matrix4x4()
        M.m = list(self.m)  # copy the list
        return M

    def setToIdentity(self):
        self.m = [
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
        ]

    @staticmethod
    def translation(vector3D):
        M = Matrix4x4()
        M.m[0] = 1.0
        M.m[4] = 0.0
        M.m[8] = 0.0
        M.m[12] = vector3D.x()
        M.m[1] = 0.0
        M.m[5] = 1.0
        M.m[9] = 0.0
        M.m[13] = vector3D.y()
        M.m[2] = 0.0
        M.m[6] = 0.0
        M.m[10] = 1.0
        M.m[14] = vector3D.z()
        M.m[3] = 0.0
        M.m[7] = 0.0
        M.m[11] = 0.0
        M.m[15] = 1.0
        return M

    @staticmethod
    def rotationAroundOrigin(angleInRadians, axisVector):
        # Note: assumes axisVector is normalized
        c = math.cos(angleInRadians)
        s = math.sin(angleInRadians)
        one_minus_c = 1 - c
        M = Matrix4x4()
        M.m[0] = c + one_minus_c * axisVector.x() * axisVector.x()
        M.m[5] = c + one_minus_c * axisVector.y() * axisVector.y()
        M.m[10] = c + one_minus_c * axisVector.z() * axisVector.z()
        M.m[1] = M.m[4] = one_minus_c * axisVector.x() * axisVector.y()
        M.m[2] = M.m[8] = one_minus_c * axisVector.x() * axisVector.z()
        M.m[6] = M.m[9] = one_minus_c * axisVector.y() * axisVector.z()
        xs = axisVector.x() * s
        ys = axisVector.y() * s
        zs = axisVector.z() * s
        M.m[1] += zs
        M.m[4] -= zs
        M.m[2] -= ys
        M.m[8] += ys
        M.m[6] += xs
        M.m[9] -= xs

        M.m[12] = 0.0
        M.m[13] = 0.0
        M.m[14] = 0.0
        M.m[3] = 0.0
        M.m[7] = 0.0
        M.m[11] = 0.0
        M.m[15] = 1.0
        return M

    @staticmethod
    def rotation(angleInRadians, axisVector, originPoint):
        v = originPoint.asVector3D()
        return (
            Matrix4x4.translation(v)
            * Matrix4x4.rotationAroundOrigin(angleInRadians, axisVector)
            * Matrix4x4.translation(-v)
        )

    @staticmethod
    def uniformScaleAroundOrigin(scaleFactor):
        M = Matrix4x4()
        M.m[0] = scaleFactor
        M.m[4] = 0.0
        M.m[8] = 0.0
        M.m[12] = 0.0
        M.m[1] = 0.0
        M.m[5] = scaleFactor
        M.m[9] = 0.0
        M.m[13] = 0.0
        M.m[2] = 0.0
        M.m[6] = 0.0
        M.m[10] = scaleFactor
        M.m[14] = 0.0
        M.m[3] = 0.0
        M.m[7] = 0.0
        M.m[11] = 0.0
        M.m[15] = 1.0
        return M

    @staticmethod
    def uniformScale(scaleFactor, originPoint):
        v = originPoint.asVector3D()
        return (
            Matrix4x4.translation(v)
            * Matrix4x4.uniformScaleAroundOrigin(scaleFactor)
            * Matrix4x4.translation(-v)
        )

    @staticmethod
    def lookAt(eyePoint, targetPoint, upVector, isInverted):
        # step one: generate a rotation matrix

        z = (eyePoint - targetPoint).normalized()
        y = upVector
        x = y ^ z  # cross product
        y = z ^ x  # cross product

        # Cross product gives area of parallelogram, which is < 1 for
        # non-perpendicular unit-length vectors; so normalize x and y.
        x = x.normalized()
        y = y.normalized()

        M = Matrix4x4()

        if isInverted:
            # the rotation matrix
            M.m[0] = x.x()
            M.m[4] = y.x()
            M.m[8] = z.x()
            M.m[12] = 0.0
            M.m[1] = x.y()
            M.m[5] = y.y()
            M.m[9] = z.y()
            M.m[13] = 0.0
            M.m[2] = x.z()
            M.m[6] = y.z()
            M.m[10] = z.z()
            M.m[14] = 0.0
            M.m[3] = 0.0
            M.m[7] = 0.0
            M.m[11] = 0.0
            M.m[15] = 1.0

            # step two: premultiply by a translation matrix
            return Matrix4x4.translation(eyePoint.asVector3D()) * M
        else:
            # the rotation matrix
            M.m[0] = x.x()
            M.m[4] = x.y()
            M.m[8] = x.z()
            M.m[12] = 0.0
            M.m[1] = y.x()
            M.m[5] = y.y()
            M.m[9] = y.z()
            M.m[13] = 0.0
            M.m[2] = z.x()
            M.m[6] = z.y()
            M.m[10] = z.z()
            M.m[14] = 0.0
            M.m[3] = 0.0
            M.m[7] = 0.0
            M.m[11] = 0.0
            M.m[15] = 1.0

            # step two: postmultiply by a translation matrix
            return M * Matrix4x4.translation(-eyePoint.asVector3D())

    @overload
    def __mul__(self, b: Self) -> Self: ...

    @overload
    def __mul__(self, b: Vector3D) -> Vector3D: ...

    @overload
    def __mul__(self, b: Point3D) -> Point3D: ...

    def __mul__(self, b):
        if isinstance(b, Matrix4x4):
            M = Matrix4x4()
            M.m[0] = (
                self.m[0] * b.m[0]
                + self.m[4] * b.m[1]
                + self.m[8] * b.m[2]
                + self.m[12] * b.m[3]
            )
            M.m[1] = (
                self.m[1] * b.m[0]
                + self.m[5] * b.m[1]
                + self.m[9] * b.m[2]
                + self.m[13] * b.m[3]
            )
            M.m[2] = (
                self.m[2] * b.m[0]
                + self.m[6] * b.m[1]
                + self.m[10] * b.m[2]
                + self.m[14] * b.m[3]
            )
            M.m[3] = (
                self.m[3] * b.m[0]
                + self.m[7] * b.m[1]
                + self.m[11] * b.m[2]
                + self.m[15] * b.m[3]
            )

            M.m[4] = (
                self.m[0] * b.m[4]
                + self.m[4] * b.m[5]
                + self.m[8] * b.m[6]
                + self.m[12] * b.m[7]
            )
            M.m[5] = (
                self.m[1] * b.m[4]
                + self.m[5] * b.m[5]
                + self.m[9] * b.m[6]
                + self.m[13] * b.m[7]
            )
            M.m[6] = (
                self.m[2] * b.m[4]
                + self.m[6] * b.m[5]
                + self.m[10] * b.m[6]
                + self.m[14] * b.m[7]
            )
            M.m[7] = (
                self.m[3] * b.m[4]
                + self.m[7] * b.m[5]
                + self.m[11] * b.m[6]
                + self.m[15] * b.m[7]
            )

            M.m[8] = (
                self.m[0] * b.m[8]
                + self.m[4] * b.m[9]
                + self.m[8] * b.m[10]
                + self.m[12] * b.m[11]
            )
            M.m[9] = (
                self.m[1] * b.m[8]
                + self.m[5] * b.m[9]
                + self.m[9] * b.m[10]
                + self.m[13] * b.m[11]
            )
            M.m[10] = (
                self.m[2] * b.m[8]
                + self.m[6] * b.m[9]
                + self.m[10] * b.m[10]
                + self.m[14] * b.m[11]
            )
            M.m[11] = (
                self.m[3] * b.m[8]
                + self.m[7] * b.m[9]
                + self.m[11] * b.m[10]
                + self.m[15] * b.m[11]
            )

            M.m[12] = (
                self.m[0] * b.m[12]
                + self.m[4] * b.m[13]
                + self.m[8] * b.m[14]
                + self.m[12] * b.m[15]
            )
            M.m[13] = (
                self.m[1] * b.m[12]
                + self.m[5] * b.m[13]
                + self.m[9] * b.m[14]
                + self.m[13] * b.m[15]
            )
            M.m[14] = (
                self.m[2] * b.m[12]
                + self.m[6] * b.m[13]
                + self.m[10] * b.m[14]
                + self.m[14] * b.m[15]
            )
            M.m[15] = (
                self.m[3] * b.m[12]
                + self.m[7] * b.m[13]
                + self.m[11] * b.m[14]
                + self.m[15] * b.m[15]
            )

            return M
        elif isinstance(b, Vector3D):
            # We treat the vector as if its (homogeneous) 4th component were zero.
            return Vector3D(
                self.m[0] * b.x()
                + self.m[4] * b.y()
                + self.m[8] * b.z(),  # + a.m[12]*b.w(),
                self.m[1] * b.x()
                + self.m[5] * b.y()
                + self.m[9] * b.z(),  # + a.m[13]*b.w(),
                self.m[2] * b.x()
                + self.m[6] * b.y()
                + self.m[10] * b.z(),  # + a.m[14]*b.w(),
                # a.m[ 3]*b.x() + a.m[ 7]*b.y() + a.m[11]*b.z() + a.m[15]*b.w()
            )
        elif isinstance(b, Point3D):
            # We treat the point as if its (homogeneous) 4th component were one.
            return Point3D(
                self.m[0] * b.x()
                + self.m[4] * b.y()
                + self.m[8] * b.z()
                + self.m[12],
                self.m[1] * b.x()
                + self.m[5] * b.y()
                + self.m[9] * b.z()
                + self.m[13],
                self.m[2] * b.x()
                + self.m[6] * b.y()
                + self.m[10] * b.z()
                + self.m[14],
            )
        else:
            raise ValueError("Must be one of Matrix4x4, Vector3D or Point3D")

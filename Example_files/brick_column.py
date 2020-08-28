import math
import Rhino.Geometry as rg
from custom_class import brick

debug = []

optimize_orientation = True
if preferred_plane is None:
    optimize_orientation = False


class Brick_column(object):
    def __init__(self, srf, brick_dim=(50.292, 24.892, 19.05), preferred_plane=None):
        self.brick_dim = brick_dim
        self.brick_diag = (
            self.brick_dim[0] ** 2 + self.brick_dim[1] ** 2) ** 0.5
        self.srf = srf
        self.bricks = []
        self.hs_gap = (self.brick_diag+self.brick_dim[1]*1.15)/2.0

        if preferred_plane is None:
            self.optimize_orientation = False
        else:
            self.preferred_plane = preferred_plane
            self.optimize_orientation = True

    def _place_brick_along_curve(self, crv, parameter, orientation='stretcher'):
        """Create a brick instance align to the tangent of a curve."""

        # Assume the curve is a planar curve coincident with World XY
        brick_cp = crv.PointAt(parameter)
        vx = crv.TangentAt(parameter)
        vz = rg.Vector3d.ZAxis
        vy = rg.Vector3d.CrossProduct(vz, vx)

        # Brick frame
        if orientation == 'stretcher':
            if self.optimize_orientation:
                angle = rg.Vector3d.VectorAngle(
                    vx,
                    self.preferred_plane.XAxis
                )
                if angle >= math.pi / 2:
                    vx = -vx
                    vy = rg.Vector3d.CrossProduct(vz, vx)

            brick_frame = rg.Plane(brick_cp, vx, vy)
        elif orientation == 'header':
            vx = vy
            vy = rg.Vector3d.CrossProduct(vz, vx)
            if self.optimize_orientation:
                if rg.Vector3d.VectorAngle(
                    vx,
                    self.preferred_plane.XAxis
                ) >= math.pi / 2:
                    vx = -vx
                    vy = rg.Vector3d.CrossProduct(vz, vx)
            brick_frame = rg.Plane(brick_cp, vx, vy)
        else:
            brick_frame = rg.Plane(brick_cp, vx, vy)

        # Instantiate a brick
        new_brick = brick.Brick(brick_frame, dim=self.brick_dim)
        return new_brick

    def simple_column(self):
        "Generate a simple brick comlumn."

        # Create the bounding box
        srf_bounding_box = self.srf.GetBoundingBox(True)

        # Set the contour start and end points
        contour_start_pt = rg.Point3d(srf_bounding_box.Min[0],
                                      srf_bounding_box.Min[1],
                                      srf_bounding_box.Min[2]+self.brick_dim[2]/2)
        contour_end_pt = rg.Point3d(srf_bounding_box.Min[0],
                                    srf_bounding_box.Min[1],
                                    srf_bounding_box.Max[2])

        # Create contour curves
        contour_curves = rg.Brep.CreateContourCurves(
            self.srf, contour_start_pt, contour_end_pt, self.brick_dim[2])

        start_pt_to_align = None
        for current_layer_index, contour_curve in enumerate(contour_curves):
            # reset the domain of the curves
            layer_bricks = []
            contour_curve.Domain = rg.Interval(0, 1)

            # Align the seam of every curve
            if current_layer_index == 0:
                start_pt_to_align = contour_curve.PointAt(0)
            elif not contour_curve.IsClosed:
                # if its a open curve, skip changing the seam
                pass
            else:
                new_start_pt_param = contour_curve.ClosestPoint(start_pt_to_align)[
                    1]
                contour_curve.ChangeClosedCurveSeam(new_start_pt_param)

            curve_length = contour_curve.GetLength()
            divide_count = curve_length // (self.brick_dim[0]/2+15)
            if divide_count % 2 == 1:
                divide_count -= 1

            divide_params = contour_curve.DivideByCount(
                divide_count, True)
            if divide_params is None:
                continue
            for current_pt_index, divide_param in enumerate(divide_params):
                if contour_curve.IsClosed:
                    if current_layer_index % 2 == 0 and current_pt_index % 2 == 0:
                        layer_bricks.append(self._place_brick_along_curve(
                            contour_curve, divide_param
                        ))
                    elif current_layer_index % 2 == 1 and current_pt_index % 2 == 1:
                        layer_bricks.append(self._place_brick_along_curve(
                            contour_curve, divide_param
                        ))
                else:
                    # for open curves
                    if current_layer_index % 2 == 0:
                        if current_pt_index == 0:
                            layer_bricks.append(self._place_brick_along_curve(
                                contour_curve,
                                contour_curve.LengthParameter(
                                    self.brick_dim[1]/2)[1],
                                "header"
                            ))
                        elif current_pt_index == len(divide_params) - 1:
                            layer_bricks.insert(1, self._place_brick_along_curve(
                                contour_curve,
                                contour_curve.LengthParameter(
                                    curve_length - self.brick_dim[1]/2)[1],
                                "header"
                            ))
                        elif current_pt_index % 2 == 0:
                            layer_bricks.append(self._place_brick_along_curve(
                                contour_curve, divide_param
                            ))
                    elif current_layer_index % 2 == 1 and current_pt_index % 2 == 1:
                        layer_bricks.append(self._place_brick_along_curve(
                            contour_curve, divide_param
                        ))
            self.bricks.extend(layer_bricks)
            for current_pt_index, divide_param in enumerate(divide_params):
                debug.append(contour_curve.PointAt(divide_param))


brick_column = Brick_column(srf, brick_dim, preferred_plane)
brick_column.simple_column()
bricks = brick_column.bricks

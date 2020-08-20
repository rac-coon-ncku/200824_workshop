import Rhino.Geometry as rg
from custom_class import brick

if origin is None:
    origin = rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d.ZAxis)

if initial_offset_vec is None:
    initial_offset_vec = rg.Vector3d(0, 0, 0)

if brick_dim is None:
    brick_dim = (230.0, 110.0, 50.0)
else:
    brick_dim = (brick_dim[0], brick_dim[1], brick_dim[2])

if x_spacing is None:
    x_spacing = 0

if y_spacing is None:
    y_spacing = 0

if x_count is None:
    x_count = 10

if y_count is None:
    y_count = 10

if z_count is None:
    z_count = 10


def regular_stack(brick_dim=(230.0, 110.0, 50.0),
                  origin=rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d.ZAxis),
                  initial_offset_vec=rg.Vector3d(0, 0, 0),
                  x_spacing=0,
                  y_spacing=0,
                  x_count=10,
                  y_count=10,
                  z_count=10,
                  reverse_order=False
                  ):
    """Generate a matrix of bricks."""

    brick_stack = []
    for k in range(z_count):
        for j in range(y_count):
            for i in range(x_count):
                x_coor = brick_dim[0] * (i + 0.5) + x_spacing * i
                y_coor = brick_dim[1] * (j + 0.5) + y_spacing * j
                z_coor = brick_dim[2] * (k + 0.5)
                brick_center_pt = rg.Point3d(x_coor, y_coor, z_coor)
                brick_center_pt = brick_center_pt + initial_offset_vec

                # Transform the center to the stack origin
                brick_center_pt.Transform(
                    rg.Transform.PlaneToPlane(
                        rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d.ZAxis),
                        origin
                    )
                )
                brick_frame = rg.Plane(
                    brick_center_pt, origin.XAxis, origin.YAxis)
                new_brick = brick.Brick(brick_frame, dim=brick_dim)
                brick_stack.append(new_brick)
    if reverse_order:
        brick_stack.reverse()
    return brick_stack


brick_stack = regular_stack(brick_dim, origin, initial_offset_vec,
                            x_spacing, y_spacing, x_count, y_count, z_count, True)

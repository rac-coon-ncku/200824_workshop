import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc


class Brick(object):
    def __init__(self, frame, col=[0, 0, 0], dim=(230.0, 110.0, 50.0)):
        """
        A Brick with the following attributes: 
        frame: rg.Plane
        dim:  (length, width, height)
        """
        self.frame = frame
        self.dim = dim
        self.length = self.dim[0]
        self.width = self.dim[1]
        self.height = self.dim[2]

        # Half Dimensions
        self.half_length = self.length / 2.0
        self.half_width = self.width / 2.0
        self.half_height = self.height / 2.0

        # Corner point of the brick
        self.points = []
        self.shape = self.add_brick()

        # Color of the Brick for visualization
        self.col = col

        self.translation = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def __str__(self):
        """
        Returns a message of the attributes of the brick.
        """
        message = "A brick with the following attributes: "
        cor_attr = "Coordinate = {}".format(tuple(self.frame.Origin))
        dim_attr = "dimensions = {}".format(self.dim)
        return message + cor_attr + " and " + dim_attr

    def distance(self, other):
        """
        Calculates the Euclidean distance to 
        the center of another brick.
        """
        pass

    def add_brick(self):
        """
        Adds a Rhino Geometry box [brep] based on the center, orientation,
        and the dimennsions of the brick.
                pt_3------------------------pt_0
                    |          ^y          |
                    |          |           |
                    |          cp--->x     |
                    |                      |
                    |                      |
                pt_2------------------------pt_1
        """
        # Center Point
        cp = self.frame.Origin

        # Translation Vectors
        t_vec_x = rg.Vector3d.Multiply(self.frame.XAxis, self.half_length)
        t_vec_y = rg.Vector3d.Multiply(self.frame.YAxis, self.half_width)
        t_vec_z = rg.Vector3d.Multiply(self.frame.ZAxis, self.half_height)

        # Translation vectors on the plane of the brick
        t_vec_0 = rg.Vector3d.Add(t_vec_x, t_vec_y)
        t_vec_1 = rg.Vector3d.Add(t_vec_x, -t_vec_y)
        t_vec_2 = rg.Vector3d.Add(-t_vec_x, -t_vec_y)
        t_vec_3 = rg.Vector3d.Add(-t_vec_x, t_vec_y)

        # Corner points
        # Negative z
        pt_0 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_0, - t_vec_z))
        pt_1 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_1, - t_vec_z))
        pt_2 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_2, - t_vec_z))
        pt_3 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_3, - t_vec_z))

        # Positive z
        pt_4 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_0, t_vec_z))
        pt_5 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_1, t_vec_z))
        pt_6 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_2, t_vec_z))
        pt_7 = rg.Point3d.Add(cp, rg.Vector3d.Add(t_vec_3, t_vec_z))

        # List of corner points
        bott_points = [pt_0, pt_1, pt_2, pt_3]
        top_points = [pt_4, pt_5, pt_6, pt_7]
        self.points = bott_points + top_points

        box_brep = rg.Brep.CreateFromBox(self.points)

        return box_brep

    def draw_brick(self):
        """
        Adds a Rhino box based on the center, orientation,
        and the dimennsions of the brick.
        """
        self.shape_id = sc.doc.Objects.AddBrep(self.shape)

        # return box_id

    def transform(self, t_matrix):
        "Transform all geometrical attributes."
        self.frame.Transform(t_matrix)
        self.shape.Transform(t_matrix)
        for pt in self.points:
            pt.Transform(t_matrix)

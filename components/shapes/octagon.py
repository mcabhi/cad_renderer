import math
import cairo

from components.shapes.shape_label import ShapeLabel
from enums.colors import Colors


class Octagon:
    def __init__(self, x=0, y=0, raw_params=None, scale_factor=1, draw_label=True):
        self._context = None
        self.parent_panel = None
        self.draw_label = draw_label

        self.x = x
        self.y = y
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'

        self.scale_factor = scale_factor
        self._size_labels = []
        self.child_labels = []
        self.vertices = [] 

    @property
    def width(self):
        return self.raw_params['width']

    @property
    def height(self):
        return self.raw_params['height']

    @property
    def dlo_width(self):
        return self.raw_params['dlo_width']

    @property
    def dlo_height(self):
        return self.raw_params['dlo_height']

    @property
    def scaled_width(self):
        return self.width * self.scale_factor

    @property
    def scaled_height(self):
        return self.height * self.scale_factor

    @property
    def scaled_dlo_width(self):
        return self.dlo_width * self.scale_factor

    @property
    def scaled_dlo_height(self):
        return self.dlo_height * self.scale_factor

    @property
    def size_labels(self):
        return self._size_labels

    @property
    def context(self) -> cairo.Context:
        if not self._context:
            raise NotImplementedError

        return self._context

    def set_context(self, context):
        """
        Sets a context to draw a panel onto
        """
        self._context = context
        return self

    def draw_octagon(self, center_x, center_y, side_length, thickness=1):
        self.context.new_sub_path()
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(thickness)

        angle = 2 * math.pi / 8  # Angle between adjacent sides of the octagon

        # Calculate the coordinates of the octagon vertices
        self.vertices = []
        for i in range(8):
            x = center_x + side_length * math.cos(i * angle + math.pi / 8)
            y = center_y + side_length * math.sin(i * angle + math.pi / 8)
            self.vertices.append((x, y))

        # Move to the first vertex
        self.context.move_to(*self.vertices[0])

        # Draw lines to connect the vertices
        for i in range(1, 8):
            self.context.line_to(*self.vertices[i])

        # Close the path
        self.context.close_path()

        self.context.stroke()
        self.context.restore()

    def draw_shape(self):
        # Draw frame
        outer_side_length =  self.scaled_width / 2
        self.draw_octagon(center_x=self.x + self.scaled_width / 2, center_y=self.y + self.scaled_height / 2,
                          side_length=outer_side_length, thickness=2)

        if self.draw_label:
            width_label_cords = {
                "x1": self.vertices[3][0],
                "y1": self.y + self.scaled_height,
                "x2": self.vertices[3][0],
                "y2": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x3": self.vertices[0][0],
                "y3": self.y + self.scaled_height + 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "x4": self.vertices[0][0],
                "y4": self.y + self.scaled_height
            }
            width_label = ShapeLabel(panel=self, label_type='width', coordinates=width_label_cords)

            height_label_cords = {
                "x1": self.x,
                "y1": self.vertices[5][1],
                "x2": self.x - 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "y2": self.vertices[5][1],
                "x3": self.x - 2 * ShapeLabel.LABEL_SIDE_LENGTH,
                "y3": self.vertices[1][1],
                "x4": self.x,
                "y4": self.vertices[1][1]
            }
            height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
            width_label.draw()
            height_label.draw()
            self._size_labels.append(width_label)
            self._size_labels.append(height_label)

        for panel in self.raw_params['panels']:
            x_offset = (self.scaled_width - panel['width'] * self.scale_factor) / 2
            y_offset = (self.scaled_height - panel['height'] * self.scale_factor) / 2

            child_panel = Octagon(x=self.x + x_offset, y=self.y + x_offset,
                                  raw_params=panel, scale_factor=self.scale_factor,
                                  draw_label=self.draw_label)

            self.child_labels.append(child_panel)

            self.raw_params = panel

            self.panel_type = panel['panel_type']
            self.name = panel['name'] if panel['panel_type'] == 'panel' else 'frame'

            side_length = self.scaled_width / 2

            # Draw panel
            self.draw_octagon(center_x=self.x + self.scaled_width / 2 + x_offset,
                              center_y=self.y + self.scaled_height / 2 + y_offset,
                              side_length=side_length,
                              thickness=1)

            self.x = self.x + x_offset
            self.y = self.y + x_offset

            if self.draw_label:
                width_label_cords = {
                    "x1": self.vertices[3][0],
                    "y1": self.y + self.scaled_height,
                    "x2": self.vertices[3][0],
                    "y2": self.y + self.scaled_height + ShapeLabel.LABEL_SIDE_LENGTH,
                    "x3": self.vertices[0][0],
                    "y3": self.y + self.scaled_height + ShapeLabel.LABEL_SIDE_LENGTH,
                    "x4": self.vertices[0][0],
                    "y4": self.y + self.scaled_height
                }
                width_label = ShapeLabel(panel=self, label_type='width', coordinates=width_label_cords)

                height_label_cords = {
                    "x1": self.x,
                    "y1": self.vertices[5][1],
                    "x2": self.x - ShapeLabel.LABEL_SIDE_LENGTH,
                    "y2": self.vertices[5][1],
                    "x3": self.x - ShapeLabel.LABEL_SIDE_LENGTH,
                    "y3": self.vertices[1][1],
                    "x4": self.x,
                    "y4": self.vertices[1][1],
                }
                height_label = ShapeLabel(panel=self, label_type='height', coordinates=height_label_cords)
                width_label.draw()
                height_label.draw()

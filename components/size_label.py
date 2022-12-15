from functools import cached_property

import cairo
import math

from enums.colors import Colors


class SizeLabel:
    LABEL_SIDE_LENGTH = 20
    LABEL_OFFSET = 0

    STROKE_WIDTH = 0.5
    STROKE_FORMAT = [3, 3]  # fill 3 pixels & skip 3 pixels

    TEXT_SIZE = 10
    TEXT_OFFSET = 2

    def __init__(self, panel, label_type: str):
        """
        :param panel:
        :param label_type: width/height/dlo_width/dlo_height
        """
        self.panel = panel
        self.type = label_type

    def draw(self):
        self._draw_label()
        self._draw_text()

    @cached_property
    def text(self):
        text = f"{self.panel.name.upper()}"

        if self.panel.panel_type == 'frame' and self.panel.parent_panel:
            x_position = int(self.panel.raw_params['coordinates']['x'])
            y_position = int(self.panel.raw_params['coordinates']['y'])
            text = f"{text} <{x_position}, {y_position}>"

        if self.type == 'width':
            text = f"{text}: {self.__convert_to_fraction(self.panel.width)}'"
        elif self.type == 'dlo_width':
            text = f"{text} DLO: {self.__convert_to_fraction(self.panel.dlo_width)}'"
        elif self.type == 'height':
            text = f"{text}: {self.__convert_to_fraction(self.panel.height)}'"
        elif self.type == 'dlo_height':
            text = f"{text} DLO: {self.__convert_to_fraction(self.panel.dlo_height)}'"

        return text

    def _draw_label(self):
        self.context.save()
        self.context.set_source_rgba(*Colors.LIGHT_GREY)
        self.context.set_line_width(self.STROKE_WIDTH)
        self.context.set_dash(self.STROKE_FORMAT)

        self.context.move_to(self.x1, self.y1)
        self.context.line_to(self.x2, self.y2)
        self.context.line_to(self.x3, self.y3)
        self.context.line_to(self.x4, self.y4)
        self.context.stroke()
        self.context.restore()

    def _draw_text(self):
        self.context.save()
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_font_matrix(cairo.Matrix(xx=self.TEXT_SIZE, yy=-self.TEXT_SIZE))

        self.context.move_to(self.text_x1, self.text_y1)

        if self.type in ['height', 'dlo_height']:
            self.context.rotate(math.pi / 2)

        self.context.show_text(self.text)
        self.context.restore()

    @property
    def context(self) -> cairo.Context:
        return self.panel.context

    @property
    def root_frame(self):
        """Maximum level of the parental nesting for Size Labels is 2"""
        return self.panel.parent_panel or self.panel

    @cached_property
    def x1(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type == 'width':
            return self.panel.x
        elif self.type == 'dlo_width':
            offset = (self.panel.scaled_width - self.panel.scaled_dlo_width) / 2
            return self.panel.x + offset
        elif self.type in ['height', 'dlo_height']:
            return self.root_frame.x - self.LABEL_OFFSET

    @cached_property
    def y1(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """

        if self.type in ['width', 'dlo_width']:
            return self.root_frame.y + self.root_frame.scaled_height + self.LABEL_OFFSET
        elif self.type == 'height':
            return self.panel.y
        elif self.type == 'dlo_height':
            offset = (self.panel.scaled_height - self.panel.scaled_dlo_height) / 2
            return self.panel.y + offset

    @cached_property
    def x2(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.x1
        elif self.type in ['height', 'dlo_height']:
            vertical_labels = [_ for _ in self.root_frame.size_labels if _.type in ['height', 'dlo_height']]
            intersected_labels = [_ for _ in vertical_labels if self.__has_overlap([self.y2, self.y3], [_.y2, max(_.y3, _.text_y2)])]

            if intersected_labels:
                min_x_point = min([min(_.x2, _.x3) for _ in intersected_labels])
            else:
                min_x_point = self.root_frame.x

            return min_x_point - self.LABEL_SIDE_LENGTH

    @cached_property
    def y2(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            horizontal_labels = [_ for _ in self.root_frame.size_labels if _.type in ['width', 'dlo_width']]

            intersected_labels = [_ for _ in horizontal_labels if self.__has_overlap([self.x2, self.x3], [_.x2, max(_.x3, _.text_x2)])]

            if intersected_labels:
                max_y_point = max([max(_.y2, _.y3) for _ in intersected_labels])
            else:
                max_y_point = self.root_frame.y + self.root_frame.scaled_height

            return max_y_point + self.LABEL_SIDE_LENGTH
        elif self.type in ['height', 'dlo_height']:
            return self.y1

    @cached_property
    def x3(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type == 'width':
            return self.x2 + self.panel.scaled_width
        elif self.type == 'dlo_width':
            return self.x2 + self.panel.scaled_dlo_width
        elif self.type in ['height', 'dlo_height']:
            return self.x2

    @cached_property
    def y3(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.y2
        elif self.type == 'height':
            return self.y2 + self.panel.scaled_height
        elif self.type == 'dlo_height':
            return self.y2 + self.panel.scaled_dlo_height

    @cached_property
    def x4(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.x3
        elif self.type in ['height', 'dlo_height']:
            return self.x1

    @cached_property
    def y4(self):
        """
        Example:

        (X2/Y2)---------------(X3/Y3)
        |                           |
        |                           |
        (X1/Y1                (X4/Y4)

        OR

        (X3/Y3)--------(X4/Y4)
        |
        |
        |
        |
        |
        (X2/Y2)--------(X1/Y1)
        """
        if self.type in ['width', 'dlo_width']:
            return self.y1
        elif self.type in ['height', 'dlo_height']:
            return self.y3

    @cached_property
    def text_x1(self):
        """
        Example:
          (X1/Y1)PANEL A: 300 1/2'(X2/Y2)
        ----------------------------
        |                          |
        """
        if self.type in ['width', 'dlo_width']:
            return self.x2 + self.TEXT_OFFSET
        elif self.type in ['height', 'dlo_height']:
            return self.x2 - self.TEXT_OFFSET

    @cached_property
    def text_y1(self):
        """
        Example:
            ------
     (X2/Y2)|
           0|
           1|
           :|
           L|
           E|
           N|
           A|
           P|
     (X1/Y1)|
            ------
        """
        if self.type in ['width', 'dlo_width']:
            return self.y2 + self.TEXT_OFFSET
        elif self.type in ['height', 'dlo_height']:
            return self.y2 + self.TEXT_OFFSET

    @cached_property
    def text_x2(self):
        """
        Example:
          (X1/Y1)PANEL A: 300 1/2'(X2/Y2)
        ----------------------------
        |                          |
        """
        if self.type in ['width', 'dlo_width']:
            return self.text_x1 + len(self.text) * (self.TEXT_SIZE / 2)
        elif self.type in ['height', 'dlo_height']:
            return self.text_x1

    @cached_property
    def text_y2(self):
        """
        Example:
            ------
     (X2/Y2)|
           0|
           1|
           :|
           L|
           E|
           N|
           A|
           P|
     (X1/Y1)|
            ------
        """
        if self.type in ['width', 'dlo_width']:
            return self.text_y1
        elif self.type in ['height', 'dlo_height']:
            return self.text_y1 + len(self.text) * (self.TEXT_SIZE / 2)

    @staticmethod
    def __convert_to_fraction(original_number: float) -> str:
        """Converts 30.5 to 30 1/2 - this is a CAD convention in engineering"""
        rounded_number = round(original_number * 16) / 16
        natural_number = int(original_number)
        tail_number = rounded_number - natural_number

        if tail_number == 0:
            return str(natural_number)
        else:
            fraction = tail_number.as_integer_ratio()

            # in some cases, fraction is 1 / 1
            if fraction[1] == 1:
                return f"{natural_number + fraction[0]}"
            else:
                return f"{natural_number} {fraction[0]}/{fraction[1]}"

    @staticmethod
    def __has_overlap(interval1, interval2) -> bool:
        return bool(max(0, min(interval1[1], interval2[1]) - max(interval1[0], interval2[0])))

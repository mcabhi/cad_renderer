import random
import string
from functools import cached_property
from typing import Dict

import cairo

from components.panel import Panel
from components.shapes.half_circle import HalfCircle
from components.shapes.circle import Circle
from components.shapes.octagon import Octagon
from enums.colors import Colors


class Canvas:
    BORDER_LEFT_OFFSET, BORDER_RIGHT_OFFSET, BORDER_TOP_OFFSET, BORDER_BOTTOM_OFFSET = 10, 30, 10, 10

    def __init__(self, raw_params: Dict):
        self.filename = f"/tmp/{''.join(random.choice(string.ascii_uppercase) for _ in range(20))}.svg"
        self.raw_params = raw_params

        self.context = None
        self.__surface = None

    def draw(self):
        self.context = self.__create_context()
        shape = self.raw_params.get('shape')
        if shape is None:
            self.__draw_frame(self.context)
        elif shape == 'half circle':
            hc = HalfCircle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                            raw_params=self.raw_params, scale_factor=Panel.SCALE_FACTOR,
                            draw_label=self.raw_params.get('draw_label', True))
            hc.set_context(self.context)
            hc.draw_shape()
        elif shape == 'circle':
            c = Circle(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                            raw_params=self.raw_params, scale_factor=Panel.SCALE_FACTOR,
                            draw_label=self.raw_params.get('draw_label', True))
            c.set_context(self.context)
            c.draw_shape()
        elif shape == 'octagon':
            c = Octagon(x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width, y=self.BORDER_BOTTOM_OFFSET,
                            raw_params=self.raw_params, scale_factor=Panel.SCALE_FACTOR,
                            draw_label=self.raw_params.get('draw_label', True))
            c.set_context(self.context)
            c.draw_shape()
        self.__close()

    @cached_property
    def panel_type(self):
        return self.raw_params['panel_type']

    @cached_property
    def child_frames(self):
        return self.raw_params.get('frames') or []

    @cached_property
    def child_panels(self):
        return self.raw_params.get('panels') or []

    @cached_property
    def frame_width(self):
        return self.raw_params['width']

    @cached_property
    def frame_height(self):
        return self.raw_params['height']

    @cached_property
    def left_positioned_labels_width(self):
        from components.size_label import SizeLabel
        from components.panel import Panel

        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['x'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            if self.orientation == 'horizontal':
                num_of_child_labels = len(self.child_panels) * Panel.LABELS_PER_PANEL
            else:
                num_of_child_labels = Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = 0

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels

    @cached_property
    def top_positioned_labels_height(self):
        from components.panel import Panel
        from components.size_label import SizeLabel

        if self.child_frames:
            num_of_child_labels = max([_['coordinates']['y'] for _ in self.child_frames]) * Panel.LABELS_PER_FRAME
        elif self.child_panels:
            if self.orientation == 'horizontal':
                num_of_child_labels = Panel.LABELS_PER_PANEL
            else:
                num_of_child_labels = len(self.child_panels) * Panel.LABELS_PER_PANEL
        else:
            num_of_child_labels = 0

        total_number_of_labels = num_of_child_labels + Panel.LABELS_PER_FRAME

        total_length_of_labels = total_number_of_labels * SizeLabel.LABEL_SIDE_LENGTH
        length_of_first_text = SizeLabel.TEXT_SIZE

        return SizeLabel.LABEL_OFFSET + length_of_first_text + total_length_of_labels

    @cached_property
    def scaled_frame_width(self):
        from components.panel import Panel
        return self.frame_width * Panel.SCALE_FACTOR

    @cached_property
    def scaled_frame_height(self):
        from components.panel import Panel
        return self.frame_height * Panel.SCALE_FACTOR

    @cached_property
    def scaled_framed_width_with_labels(self):
        return self.scaled_frame_width + self.left_positioned_labels_width

    @cached_property
    def scaled_framed_height_with_labels(self):
        return self.scaled_frame_height + self.top_positioned_labels_height

    @cached_property
    def canvas_width(self):
        return self.scaled_framed_width_with_labels + self.BORDER_LEFT_OFFSET + self.BORDER_RIGHT_OFFSET

    @cached_property
    def canvas_height(self):
        return self.scaled_framed_height_with_labels + self.BORDER_TOP_OFFSET + self.BORDER_BOTTOM_OFFSET

    @cached_property
    def orientation(self):
        from components.panel import Panel

        if self.child_panels:
            return Panel.guess_orientation(self.frame_width, self.frame_height, self.child_panels)
        else:
            return 'horizontal'

    def __create_context(self):
        """
        Creates a context to draw onto
        :return: context
        """
        self.__surface = cairo.SVGSurface(self.filename, self.canvas_width, self.canvas_height)

        context = cairo.Context(self.__surface)
        context.set_source_rgba(*Colors.WHITE)
        context.paint()

        matrix = cairo.Matrix(yy=-1, y0=self.canvas_height)
        context.transform(matrix)

        return context

    def __draw_frame(self, context):
        from components.panel import Panel

        initial_frame = Panel(
            x=self.BORDER_LEFT_OFFSET + self.left_positioned_labels_width,
            y=self.BORDER_BOTTOM_OFFSET,
            parent_panel=None,
            raw_params=self.raw_params
        ).set_context(context)

        initial_frame.draw()

    def __close(self):
        self.__surface.__exit__()

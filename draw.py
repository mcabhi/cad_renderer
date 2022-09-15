import itertools
import math
from functools import cached_property
from typing import List, Dict

import cairo
from colors import Colors, FrameColors, PanelColors, DloColors


# ToDo:
# 1) Fix canvas size issue
# 2) Add arrows back
# 4) Handle nested frames


class SizeLabel:
    LABEL_SIZE = 20
    LABEL_OFFSET = 5

    STROKE_WIDTH = 0.5
    STROKE_FORMAT = [3, 3]  # fill 3 pixels & skip 3 pixels

    TEXT_SIZE = 10
    TEXT_OFFSET = 2

    def __init__(self, parent_panel, label_type: str):
        """
        :param parent_panel:
        :param label_type: width/height/dlo_width/dlo_height
        """
        self.parent_panel = parent_panel
        self.type = label_type

    def draw(self):
        self.context.save()
        self._draw_label()
        self._draw_text()
        self.context.stroke()
        self.context.restore()

    def _draw_label(self):
        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(self.STROKE_WIDTH)
        self.context.set_dash(self.STROKE_FORMAT)

        self.context.move_to(self.x1, self.y1)
        self.context.line_to(self.x2, self.y2)
        self.context.line_to(self.x3, self.y3)
        self.context.line_to(self.x4, self.y4)

    def _draw_text(self):
        self.context.set_font_matrix(cairo.Matrix(xx=self.TEXT_SIZE, yy=-self.TEXT_SIZE))

        text = f"{self.parent_panel.name.upper()}"

        if self.parent_panel.panel_type == 'frame' and self.parent_panel.parent_panel:
            x_position = self.parent_panel.raw_params['coordinates']['x']
            y_position = self.parent_panel.raw_params['coordinates']['y']
            text = f"{text} <{x_position}, {y_position}>"

        if self.type in ['width', 'dlo_width']:
            self.context.move_to(self.x2 + self.TEXT_OFFSET, self.y2 + self.TEXT_OFFSET)

            if self.type == 'width':
                self.context.show_text(f"{text}: {self.__convert_to_fraction(self.parent_panel.width)}'")
            elif self.type == 'dlo_width':
                self.context.show_text(f"{text} DLO: {self.parent_panel.dlo_width}'")

        elif self.type in ['height', 'dlo_height']:
            self.context.move_to(self.x2 - self.TEXT_OFFSET, self.y2 + self.TEXT_OFFSET)
            self.context.rotate(math.pi / 2)

            if self.type == 'height':
                self.context.show_text(f"{text}: {self.parent_panel.height}'")
            elif self.type == 'dlo_height':
                self.context.show_text(f"{text} DLO: {self.parent_panel.dlo_height}'")

    @property
    def context(self) -> cairo.Context:
        return self.parent_panel.context

    @property
    def root_frame(self):
        """Maximum level of the parental nesting for Size Labels is 2"""
        return self.parent_panel.parent_panel or self.parent_panel

    @cached_property
    def x1(self):
        if self.type == 'width':
            return self.parent_panel.x
        elif self.type == 'dlo_width':
            offset = (self.parent_panel.width - self.parent_panel.dlo_width) / 2
            return self.parent_panel.x + offset
        elif self.type == 'height':
            return self.parent_panel.x - self.LABEL_OFFSET
        elif self.type == 'dlo_height':
            offset = (self.parent_panel.width - self.parent_panel.dlo_width) / 2
            return self.parent_panel.x + offset - self.LABEL_OFFSET

    @cached_property
    def y1(self):
        if self.type in ['width', 'dlo_width']:
            offset = (self.parent_panel.height - self.parent_panel.dlo_height) / 2
            return self.parent_panel.y + self.parent_panel.height + self.LABEL_OFFSET - offset
        elif self.type == 'height':
            return self.parent_panel.y
        elif self.type == 'dlo_height':
            offset = (self.parent_panel.height - self.parent_panel.dlo_height) / 2
            return self.parent_panel.y + offset

    @cached_property
    def x2(self):
        if self.type in ['width', 'dlo_width']:
            return self.x1
        elif self.type in ['height', 'dlo_height']:
            vertical_labels = [_ for _ in self.root_frame.size_labels if _.type in ['height', 'dlo_height']]
            intersected_labels = [_ for _ in vertical_labels if self.__has_overlap([self.y2, self.y3], [_.y2, _.y3])]

            if intersected_labels:
                min_x_point = min([min(_.x2, _.x3) for _ in intersected_labels])
            else:
                min_x_point = self.root_frame.x

            return min_x_point - self.LABEL_SIZE

    @cached_property
    def y2(self):
        if self.type in ['width', 'dlo_width']:
            horizontal_labels = [_ for _ in self.root_frame.size_labels if _.type in ['width', 'dlo_width']]
            intersected_labels = [_ for _ in horizontal_labels if self.__has_overlap([self.x2, self.x3], [_.x2, _.x3])]

            if intersected_labels:
                max_y_point = max([max(_.y2, _.y3) for _ in intersected_labels])
            else:
                max_y_point = self.root_frame.y + self.root_frame.height

            return max_y_point + self.LABEL_SIZE
        elif self.type in ['height', 'dlo_height']:
            return self.y1

    @cached_property
    def x3(self):
        if self.type == 'width':
            return self.x2 + self.parent_panel.width
        elif self.type == 'dlo_width':
            return self.x2 + self.parent_panel.dlo_width
        elif self.type in ['height', 'dlo_height']:
            return self.x2

    @cached_property
    def y3(self):
        if self.type in ['width', 'dlo_width']:
            return self.y2
        elif self.type == 'height':
            return self.y2 + self.parent_panel.height
        elif self.type == 'dlo_height':
            return self.y2 + self.parent_panel.dlo_height

    @cached_property
    def x4(self):
        if self.type in ['width', 'dlo_width']:
            return self.x3
        elif self.type in ['height', 'dlo_height']:
            return self.x1

    @cached_property
    def y4(self):
        if self.type in ['width', 'dlo_width']:
            return self.y1
        elif self.type in ['height', 'dlo_height']:
            return self.y3

    @staticmethod
    def __convert_to_fraction(number: float) -> str:
        natural_number = int(number)
        tail_number = number - natural_number

        if tail_number == 0:
            return str(number)
        else:
            fraction = tail_number.as_integer_ratio()
            return f"{natural_number} {fraction[0]}/{fraction[1]}"

    @staticmethod
    def __has_overlap(interval1, interval2) -> bool:
        # is_very_small = (interval1[1] - interval1[0]) < 100
        #
        # if is_very_small:
        #     return True

        return bool(max(0, min(interval1[1], interval2[1]) - max(interval1[0], interval2[0])))


class Panel:

    def __init__(self, width, height, panel_type, dlo_width=0, dlo_height=0, x=0, y=0, parent_panel=None,
                 move_direction=None, panel_name='FRAME', raw_params=None):
        self._context = None

        self.width = raw_params['width']
        self.height = raw_params['height']
        self.dlo_width = raw_params['dlo_width']
        self.dlo_height = raw_params['dlo_height']
        self.x = x
        self.y = y

        self.panel_type = panel_type
        self.panel_name = panel_name

        self.name = panel_name

        self.move_direction = move_direction

        self.parent_panel = parent_panel
        self.child_panels = []

        self.raw_params = raw_params

        self._size_labels = []

    def _draw_frame(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(2)
        self.context.rectangle(self.x, self.y, self.width, self.height)
        self.context.stroke()

        self.context.restore()

    def _draw_panel(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(1)

        self.context.rectangle(self.x, self.y, self.width, self.height)

        self.context.stroke()

        self.context.restore()

    def _draw_panel_dlo(self):
        self.context.save()

        dlo_x_offset = (self.width - self.dlo_width) / 2
        dlo_y_offset = (self.height - self.dlo_height) / 2

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(0.5)
        self.context.rectangle(self.x + dlo_x_offset, self.y + dlo_y_offset, self.dlo_width, self.dlo_height)
        self.context.stroke()

        self.context.restore()

    def _draw_child_frames(self):
        sort_by = lambda _: f"{_['coordinates']['y']}_{_['coordinates']['x']}"
        group_by = lambda _: _['coordinates']['y']

        raw_frames = sorted(self.raw_params.get('frames', []), key=sort_by)
        row__w__frames = {k: list(v) for k, v in itertools.groupby(raw_frames, key=group_by)}

        initial_x_offset = (self.width - self.dlo_width) / 2
        initial_y_offset = (self.height - self.dlo_height) / 2

        y1 = self.y + initial_y_offset
        for row, _frames in row__w__frames.items():
            x1 = self.x + initial_x_offset

            for raw_frame in _frames:
                frame = Panel(
                    panel_type='frame',
                    width=raw_frame['width'],
                    height=raw_frame['height'],
                    x=x1,
                    y=y1,
                    parent_panel=self,
                    raw_params=raw_frame
                ).set_context(self.context).draw()
                self.child_panels.append(frame)

                x1 += frame.width

            y1 += max([_['height'] for _ in _frames])

    def _draw_child_panels(self):
        total_child_width = sum([_['width'] for _ in self.raw_params.get('panels', [])])
        x_offset = (self.width - total_child_width) / 2

        previous_panel = None
        for child_panel in self.raw_params.get('panels', []):
            y_offset = (self.height - child_panel['height']) / 2

            if previous_panel:
                x_offset += previous_panel.width

            panel = Panel(
                width=child_panel['width'],
                height=child_panel['height'],
                dlo_width=child_panel['dlo_width'],
                dlo_height=child_panel['dlo_height'],
                move_direction=child_panel['move_direction'],
                panel_type='panel',
                panel_name=f"PANEL {child_panel['name'].upper()}",
                x=self.x + x_offset,
                y=self.y + y_offset,
                parent_panel=self,
                raw_params=child_panel
            ).set_context(self.context).draw()

            self.child_panels.append(panel)

            previous_panel = panel

    def _draw_size_labels(self, _type='primary'):
        """
        :param _type: primary/dlo
        """
        if _type == 'primary':
            width_label = SizeLabel(parent_panel=self, label_type='width')
            height_label = SizeLabel(parent_panel=self, label_type='height')
            width_label.draw()
            height_label.draw()
            self._size_labels.append(width_label)
            self._size_labels.append(height_label)
        elif _type == 'dlo' and self.panel_type == 'panel':
            dlo_width_label = SizeLabel(parent_panel=self, label_type='dlo_width')
            dlo_height_label = SizeLabel(parent_panel=self, label_type='dlo_height')
            dlo_width_label.draw()
            dlo_height_label.draw()
            self._size_labels.append(dlo_width_label)
            self._size_labels.append(dlo_height_label)

    def draw(self):
        if self.raw_params.get('panels', []):
            self._draw_child_panels()
        elif self.raw_params.get('frames', []):
            self._draw_child_frames()

        if self.panel_type == 'frame':
            self._draw_frame()
        elif self.panel_type == 'panel':
            self._draw_panel()
            self._draw_panel_dlo()

        if not self.parent_panel:
            for child_panel in self.child_panels:
                child_panel._draw_size_labels(_type='dlo')

            for child_panel in self.child_panels:
                child_panel._draw_size_labels(_type='primary')

            self._draw_size_labels(_type='primary')

        #     if self.move_direction:
        #         arrow_angle = math.pi
        #         arrow_length = 0
        #         arrow_x, arrow_y = 0, 0
        #
        #         if self.move_direction == 'left':
        #             arrow_angle = math.pi
        #
        #             dlo_x_offset = (self.width - self.dlo_width) / 2
        #             dlo_y_offset = (self.height - self.dlo_height) / 2
        #
        #             arrow_x = self.x + dlo_x_offset + self.dlo_width
        #             arrow_y = self.y + dlo_y_offset + self.height / 2
        #
        #         elif self.move_direction == 'up':
        #             arrow_angle = math.pi / 2
        #
        #             dlo_x_offset = (self.width - self.dlo_width) / 2
        #             dlo_y_offset = (self.height - self.dlo_height) / 2
        #
        #             arrow_x = self.x + dlo_x_offset + self.dlo_width / 2
        #             arrow_y = self.y + dlo_y_offset
        #
        #         elif self.move_direction == 'down':
        #             arrow_angle = - math.pi / 2
        #
        #             arrow_x = self.x + dlo_x_offset + self.dlo_width / 2
        #             arrow_y = self.y + dlo_y_offset + self.dlo_height
        #
        #         elif self.move_direction == 'right':
        #             arrow_angle = 0
        #
        #             dlo_x_offset = (self.width - self.dlo_width) / 2
        #             dlo_y_offset = (self.height - self.dlo_height) / 2
        #
        #             arrow_x = self.x + dlo_x_offset
        #             arrow_y = self.y + dlo_y_offset + self.height / 2
        #
        #         if self.move_direction in ['left', 'right']:
        #             arrow_length = self.dlo_width * 0.1
        #         elif self.move_direction in ['up', 'down']:
        #             arrow_length = self.dlo_height * 0.1
        #
        #         arrowhead_angle = math.pi / 6
        #         arrowhead_length = arrow_length / 2.25
        #
        #         self.context.set_source_rgba(0, 0, 0, 1)
        #
        #         self.context.move_to(arrow_x, arrow_y)  # move to center of canvas
        #
        #         self.context.rel_line_to(arrow_length * math.cos(arrow_angle), arrow_length * math.sin(arrow_angle))
        #         self.context.rel_move_to(-arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
        #                                  -arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        #         self.context.rel_line_to(arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
        #                                  arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        #         self.context.rel_line_to(-arrowhead_length * math.cos(arrow_angle + arrowhead_angle),
        #                                  -arrowhead_length * math.sin(arrow_angle + arrowhead_angle))
        #
        #         self.context.set_line_width(1)
        #         self.context.stroke()
        #
        # # stroke out the color and width property
        # # self.context.stroke()
        #

        return self

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

    # def draw_width_size(self):
    #     label_offset = 5
    #     label_length = 20
    #
    #     if self.panel_type == 'frame':
    #         if len(self.child_panels) > 0:
    #             label_length *= 2
    #
    #     dash_config = [3, 3]
    #
    #     self.context.set_source_rgba(0, 0, 0, 1)
    #     self.context.set_line_width(1)
    #     self.context.set_dash(dash_config)
    #
    #     if self.parent_panel:
    #         self.context.move_to(self.x, self.parent_panel.y + self.parent_panel.height + label_offset)
    #         self.context.line_to(self.x, self.parent_panel.y + self.parent_panel.height + label_offset + label_length)
    #         self.context.line_to(self.x + self.width,
    #                              self.parent_panel.y + self.parent_panel.height + label_offset + label_length)
    #         self.context.line_to(self.x + self.width, self.parent_panel.y + self.parent_panel.height + label_offset)
    #
    #         self.context.set_source_rgba(0, 0, 0, 1)
    #         self.context.set_font_size(13)
    #
    #         font_size = 13
    #         mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #         self.context.set_font_matrix(mtx)
    #
    #         self.context.move_to(self.x,
    #                              self.parent_panel.y + self.parent_panel.height + label_offset + label_length + 2)
    #         self.context.show_text(f"{self.panel_name}: {self.width}'")
    #     else:
    #         self.context.move_to(self.x, self.y + self.height + label_offset)
    #         self.context.line_to(self.x, self.y + self.height + label_offset + label_length)
    #         self.context.line_to(self.x + self.width, self.y + self.height + label_offset + label_length)
    #         self.context.line_to(self.x + self.width, self.y + self.height + label_offset)
    #
    #         self.context.set_font_size(13)
    #
    #         font_size = 13
    #         mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #         self.context.set_font_matrix(mtx)
    #
    #         self.context.move_to(self.x,
    #                              self.y + self.height + label_offset + label_length + 2)
    #         self.context.show_text(f"{self.panel_name}: {self.width}'")
    #
    #     self.context.stroke()
    #
    # def draw_height_size(self):
    #     self.context.save()
    #
    #     label_offset = 5
    #     label_length = 15
    #
    #     if self.panel_type == 'frame':
    #         if len(self.child_panels) > 0:
    #             label_length *= 2
    #
    #     dash_config = [3, 3]
    #
    #     self.context.set_source_rgba(0, 0, 0, 1)
    #     self.context.set_line_width(1)
    #     self.context.set_dash(dash_config)
    #
    #     if self.parent_panel:
    #         self.context.move_to(self.parent_panel.x - label_offset, self.y)
    #         self.context.line_to(self.parent_panel.x - label_offset - label_length, self.y)
    #         self.context.line_to(self.parent_panel.x - label_offset - label_length, self.y + self.height)
    #         self.context.line_to(self.parent_panel.x - label_offset, self.y + self.height)
    #
    #         self.context.set_source_rgba(0, 0, 0, 1)
    #         self.context.set_font_size(13)
    #
    #         font_size = 13
    #         mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #         self.context.set_font_matrix(mtx)
    #
    #         self.context.move_to(self.parent_panel.x - label_offset - label_length - 2, self.y)
    #
    #         self.context.rotate(math.pi / 2)
    #         self.context.show_text(f"{self.panel_name}: {self.width}'")
    #         # self.context.rotate(0)
    #     else:
    #         self.context.move_to(self.x - label_offset, self.y)
    #         self.context.line_to(self.x - label_offset - label_length, self.y)
    #         self.context.line_to(self.x - label_offset - label_length, self.y + self.height)
    #         self.context.line_to(self.x - label_offset, self.y + self.height)
    #
    #         self.context.set_font_size(13)
    #
    #         font_size = 13
    #         mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #         self.context.set_font_matrix(mtx)
    #
    #         self.context.move_to(self.x - label_offset - label_length - 2, self.y)
    #
    #         self.context.rotate(math.pi / 2)
    #         self.context.show_text(f"{self.panel_name}: {self.width}'")
    #         # self.context.rotate(0)
    #
    #     self.context.stroke()
    #
    #     self.context.restore()
    #
    # def draw_dlo_width(self):
    #     if not self.dlo_width or not self.dlo_height:
    #         return
    #
    #     label_offset = 0
    #     label_length = 5
    #
    #     dash_config = [3, 3]
    #
    #     self.context.set_source_rgba(0, 0, 0, 1)
    #     self.context.set_line_width(1)
    #     self.context.set_dash(dash_config)
    #
    #     dlo_x_offset = (self.width - self.dlo_width) / 2
    #     dlo_y_offset = (self.height - self.dlo_height) / 2
    #
    #     self.context.move_to(self.x + dlo_x_offset, self.y + dlo_y_offset + label_offset)
    #     self.context.line_to(self.x + dlo_x_offset, self.y + dlo_y_offset + label_offset + label_length)
    #     self.context.line_to(self.x + dlo_x_offset + self.dlo_width,
    #                          self.y + dlo_y_offset + label_offset + label_length)
    #     self.context.line_to(self.x + dlo_x_offset + self.dlo_width, self.y + dlo_y_offset + label_offset)
    #
    #     self.context.stroke()
    #
    #     font_size = 13
    #     mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #     self.context.set_font_matrix(mtx)
    #
    #     self.context.move_to(self.x + dlo_x_offset, self.y + dlo_y_offset + label_offset + label_length + 2)
    #     self.context.show_text(f"{self.panel_name}: {self.dlo_width}'")
    #
    # def draw_dlo_height(self):
    #     if not self.dlo_width or not self.dlo_height:
    #         return
    #
    #     self.context.save()
    #
    #     label_offset = 0
    #     label_length = 5
    #
    #     dash_config = [3, 3]
    #
    #     self.context.set_source_rgba(0, 0, 0, 1)
    #     self.context.set_line_width(1)
    #     self.context.set_dash(dash_config)
    #
    #     dlo_x_offset = (self.width - self.dlo_width) / 2
    #     dlo_y_offset = (self.height - self.dlo_height) / 2
    #
    #     self.context.move_to(self.x + dlo_x_offset + self.dlo_width - label_offset, self.y + dlo_y_offset)
    #     self.context.line_to(self.x + dlo_x_offset + self.dlo_width - label_offset - label_length,
    #                          self.y + dlo_y_offset)
    #     self.context.line_to(self.x + dlo_x_offset + self.dlo_width - label_offset - label_length,
    #                          self.y + dlo_y_offset + self.dlo_height)
    #     self.context.line_to(self.x + dlo_x_offset + self.dlo_width - label_offset,
    #                          self.y + dlo_y_offset + self.dlo_height)
    #
    #     self.context.stroke()
    #
    #     font_size = 13
    #     mtx = cairo.Matrix(xx=font_size, yy=-font_size)
    #     self.context.set_font_matrix(mtx)
    #
    #     self.context.move_to(self.x + dlo_x_offset + self.dlo_width - label_offset - 2, self.y + dlo_y_offset)
    #
    #     self.context.rotate(math.pi / 2)
    #     self.context.show_text(f"{self.panel_name}: {self.dlo_height}'")
    #     self.context.restore()

    @property
    def size_labels(self):
        child_panels_labels = list(itertools.chain(*[_._size_labels for _ in self.child_panels]))

        return self._size_labels + child_panels_labels


class Canvas:

    def __init__(self, frame: Dict):
        self.__params = frame

        self.context = None
        self.__surface = None

    def run(self):
        context = self.__create_context()

        self.__draw_frame(context)

        self.__close()

    @property
    def svg_width(self):
        return self.frame_width + self.frame_width * 0.5

    @property
    def svg_height(self):
        return self.frame_height + self.frame_height * 0.5

    @property
    def frame_width(self):
        return self.__params['width']

    @property
    def frame_height(self):
        return self.__params['height']

    @property
    def child_frames(self):
        return self.__params.get('frames') or []

    @property
    def child_panels(self):
        return self.__params.get('panels') or []

    def __create_context(self):
        """
        Creates a context to draw onto
        :return: context
        """
        self.__surface = cairo.SVGSurface("/tmp/example.svg", self.svg_width, self.svg_height)

        context = cairo.Context(self.__surface)
        context.set_source_rgba(*Colors.WHITE)
        context.paint()

        matrix = cairo.Matrix(yy=-1, y0=self.svg_height)
        context.transform(matrix)

        return context

    def __draw_frame(self, context):
        initial_frame = Panel(
            width=self.frame_width,
            height=self.frame_height,
            panel_type='frame',
            x=(self.svg_width - self.frame_width) / 2,
            y=(self.svg_height - self.frame_height) / 2,
            parent_panel=None,
            raw_params=self.__params
        ).set_context(context)

        initial_frame.draw()

    def __close(self):
        self.__surface.__exit__()


# drawer = Canvas({
#     'width': 550.375,
#     'height': 500,
#     'panel_type': 'frame',
#     'coordinates': {'x': 1, 'y': 1},
#     'panels': [
#         {
#             'name': 'a',
#             'panel_type': 'panel',
#             'move_direction': 'right',
#             'width': 200,
#             'height': 450,
#             'dlo_width': 195,
#             'dlo_height': 430,
#             'coordinates': {'x': 1, 'y': 1}
#         },
#         {
#             'name': 'b',
#             'panel_type': 'panel',
#             'move_direction': 'down',
#             'width': 250,
#             'height': 450,
#             'dlo_width': 245,
#             'dlo_height': 430,
#             'coordinates': {'x': 1, 'y': 1}
#         },
#         {
#             'name': 'c',
#             'panel_type': 'panel',
#             'move_direction': 'down',
#             'width': 50,
#             'height': 450,
#             'dlo_width': 45,
#             'dlo_height': 430,
#             'coordinates': {'x': 1, 'y': 1}
#         }
#     ]
# })

# drawer = Canvas({
#     'width': 500,
#     'height': 500,
#     'dlo_width': 500,
#     'dlo_height': 500,
#     'panel_type': 'frame',
#     'coordinates': {'x': 1, 'y': 1},
#     'frames': [
#         {
#             'panel_type': 'frame',
#             'width': 500,
#             'height': 340,
#             'dlo_width': 0,
#             'dlo_height': 0,
#             'coordinates': {'x': 1, 'y': 1}
#         },
#         {
#             'panel_type': 'frame',
#             'width': 500,
#             'height': 10,
#             'dlo_width': 0,
#             'dlo_height': 0,
#             'coordinates': {'x': 1, 'y': 2}
#         },
#         {
#             'panel_type': 'frame',
#             'width': 500,
#             'height': 150,
#             'dlo_width': 0,
#             'dlo_height': 0,
#             'coordinates': {'x': 1, 'y': 3}
#         }
#     ]
# })

drawer = Canvas({
    'width': 500,
    'height': 500,
    'dlo_width': 500,
    'dlo_height': 500,
    'panel_type': 'frame',
    'coordinates': {'x': 1, 'y': 1},
    'frames': [
        {
            'panel_type': 'frame',
            'coordinates': {'x': 1, 'y': 1},
            'width': 500,
            'height': 340,
            'dlo_width': 0,
            'dlo_height': 0,
            'panels': [
                {
                    'name': 'a',
                    'panel_type': 'panel',
                    'move_direction': 'right',
                    'width': 200,
                    'height': 450,
                    'dlo_width': 195,
                    'dlo_height': 430,
                    'coordinates': {'x': 1, 'y': 1}
                }
            ]
        },
        {
            'panel_type': 'frame',
            'width': 500,
            'height': 10,
            'dlo_width': 0,
            'dlo_height': 0,
            'coordinates': {'x': 1, 'y': 2}
        },
        {
            'panel_type': 'frame',
            'width': 500,
            'height': 150,
            'dlo_width': 0,
            'dlo_height': 0,
            'coordinates': {'x': 1, 'y': 3}
        }
    ]
})

drawer.run()

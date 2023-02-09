import itertools
from copy import deepcopy
from typing import List

import cairo
import math

from enums.colors import Colors


class Panel:
    SCALE_FACTOR = 5

    LABELS_PER_FRAME = 1
    LABELS_PER_PANEL = 2

    def __init__(self, x=0.0, y=0.0, parent_panel=None, raw_params=None):
        self._context = None

        self.x = x
        self.y = y
        self.parent_panel = parent_panel
        self.raw_params = raw_params

        self.panel_type = raw_params['panel_type']
        self.name = raw_params['name'] if raw_params['panel_type'] == 'panel' else 'frame'
        self.move_direction = raw_params.get('move_direction')

        self.child_panels = []
        self._size_labels = []

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
        return self.width * self.SCALE_FACTOR

    @property
    def scaled_height(self):
        return self.height * self.SCALE_FACTOR

    @property
    def scaled_dlo_width(self):
        return self.dlo_width * self.SCALE_FACTOR

    @property
    def scaled_dlo_height(self):
        return self.dlo_height * self.SCALE_FACTOR

    @property
    def raw_child_panels(self):
        return self.raw_params.get('panels') or []

    @property
    def raw_child_frames(self):
        return self.raw_params.get('frames') or []

    def get_normalized_child_frame(self, raw_frame):
        from services.normalization_service import NormalizationService

        siblings = [_ for _ in self.raw_child_frames if raw_frame['coordinates']['y'] == _['coordinates']['y']]

        scaled_total_child_width = sum([_['width'] * self.SCALE_FACTOR for _ in siblings])

        if self.scaled_width < scaled_total_child_width:
            factor = self.scaled_width / scaled_total_child_width
            service = NormalizationService(width_factor=factor, height_factor=1)

            return service.run(deepcopy(raw_frame))
        else:
            return raw_frame

    def get_normalized_child_panel(self, raw_panel):
        from services.normalization_service import NormalizationService

        scaled_total_child_width = sum([_['width'] * self.SCALE_FACTOR for _ in self.raw_child_panels])
        scaled_total_child_height = sum([_['height'] * self.SCALE_FACTOR for _ in self.raw_child_panels])

        invalid_condition_1 = self.child_panels_layout == 'horizontal' and self.scaled_width < scaled_total_child_width
        invalid_condition_2 = self.child_panels_layout == 'vertical' and self.scaled_height < scaled_total_child_height

        if invalid_condition_1 or invalid_condition_2:
            if self.child_panels_layout == 'horizontal':
                factor = self.scaled_width / scaled_total_child_width
                service = NormalizationService(width_factor=factor, height_factor=1)
            else:
                factor = self.scaled_height / scaled_total_child_height
                service = NormalizationService(width_factor=1, height_factor=factor)

            return service.run(deepcopy(raw_panel))
        else:
            return raw_panel

    @property
    def child_panels_layout(self):
        return self.guess_orientation(
            frame_width=self.width,
            frame_height=self.height,
            raw_child_panels=self.raw_child_panels
        )

    def _draw_frame(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(2)
        self.context.rectangle(self.x, self.y, self.scaled_width, self.scaled_height)
        self.context.stroke()

        self.context.restore()

    def _draw_panel(self):
        self.context.save()

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(1)

        self.context.rectangle(self.x, self.y, self.scaled_width, self.scaled_height)

        self.context.stroke()

        self.context.restore()

    def _draw_panel_dlo(self):
        self.context.save()

        dlo_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        dlo_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        self.context.set_source_rgba(*Colors.BLACK)
        self.context.set_line_width(0.5)
        self.context.rectangle(self.x + dlo_x_offset, self.y + dlo_y_offset, self.scaled_dlo_width,
                               self.scaled_dlo_height)
        self.context.stroke()

        self.context.restore()

    def _draw_child_frames(self):
        sort_by = lambda _: f"{_['coordinates']['y']}_{_['coordinates']['x']}"
        group_by = lambda _: _['coordinates']['y']

        raw_frames = sorted(self.raw_child_frames, key=sort_by)
        row__w__frames = {k: list(v) for k, v in itertools.groupby(raw_frames, key=group_by)}

        initial_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        initial_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        y1 = self.y + initial_y_offset
        for row, _frames in row__w__frames.items():
            x1 = self.x + initial_x_offset

            normalized_raw_frames = [self.get_normalized_child_frame(raw_frame=_) for _ in _frames]

            for raw_frame in normalized_raw_frames:
                frame = Panel(
                    x=x1,
                    y=y1,
                    parent_panel=self,
                    raw_params=raw_frame
                ).set_context(self.context).draw()
                self.child_panels.append(frame)

                x1 += frame.scaled_width

            y1 += max([_['height'] * self.SCALE_FACTOR for _ in _frames])

    def _draw_child_panels(self):
        normalized_raw_child_panels = [self.get_normalized_child_panel(raw_panel=_) for _ in self.raw_child_panels]

        scaled_total_normalized_child_width = sum([_['width'] * self.SCALE_FACTOR for _ in normalized_raw_child_panels])
        scaled_total_normalized_child_height = sum([_['height'] * self.SCALE_FACTOR for _ in normalized_raw_child_panels])

        x_offset, y_offset = 0, 0
        if self.child_panels_layout == 'horizontal':
            x_offset = (self.scaled_width - scaled_total_normalized_child_width) / 2
        elif self.child_panels_layout == 'vertical':
            y_offset = (self.scaled_height - scaled_total_normalized_child_height) / 2

        previous_panel = None
        for normalized_child_panel in sorted(normalized_raw_child_panels, key=lambda _: _['name'], reverse=self.child_panels_layout == 'vertical'):
            if self.child_panels_layout == 'horizontal':
                y_offset = (self.scaled_height - normalized_child_panel['height'] * self.SCALE_FACTOR) / 2
            elif self.child_panels_layout == 'vertical':
                x_offset = (self.scaled_width - normalized_child_panel['width'] * self.SCALE_FACTOR) / 2

            if previous_panel:
                if self.child_panels_layout == 'horizontal':
                    x_offset += previous_panel.scaled_width
                elif self.child_panels_layout == 'vertical':
                    y_offset += previous_panel.scaled_height
            elif not previous_panel:
                if self.child_panels_layout == 'horizontal' and self.scaled_width < scaled_total_normalized_child_width:
                    x_offset = 0
                elif self.child_panels_layout == 'vertical' and self.scaled_height < scaled_total_normalized_child_height:
                    y_offset = 0

            panel = Panel(
                x=self.x + x_offset,
                y=self.y + y_offset,
                parent_panel=self,
                raw_params=normalized_child_panel
            ).set_context(self.context).draw()

            self.child_panels.append(panel)

            previous_panel = panel

    def _draw_size_labels(self, _type='primary'):
        """
        :param _type: primary/dlo
        """
        from components.size_label import SizeLabel

        if _type == 'primary':
            width_label = SizeLabel(panel=self, label_type='width')
            height_label = SizeLabel(panel=self, label_type='height')
            width_label.draw()
            height_label.draw()
            self._size_labels.append(width_label)
            self._size_labels.append(height_label)
        elif _type == 'dlo' and self.panel_type == 'panel':
            dlo_width_label = SizeLabel(panel=self, label_type='dlo_width')
            dlo_height_label = SizeLabel(panel=self, label_type='dlo_height')
            dlo_width_label.draw()
            dlo_height_label.draw()
            self._size_labels.append(dlo_width_label)
            self._size_labels.append(dlo_height_label)

    def _draw_move_direction(self):
        self.context.save()

        arrow_angle = math.pi
        arrow_length = 0
        arrow_x, arrow_y = 0, 0

        dlo_x_offset = (self.scaled_width - self.scaled_dlo_width) / 2
        dlo_y_offset = (self.scaled_height - self.scaled_dlo_height) / 2

        if self.move_direction == 'left':
            arrow_angle = math.pi

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width
            arrow_y = self.y + dlo_y_offset + self.scaled_height / 2

        elif self.move_direction == 'up':
            arrow_angle = math.pi / 2

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width / 2
            arrow_y = self.y + dlo_y_offset

        elif self.move_direction == 'down':
            arrow_angle = - math.pi / 2

            arrow_x = self.x + dlo_x_offset + self.scaled_dlo_width / 2
            arrow_y = self.y + dlo_y_offset + self.scaled_dlo_height

        elif self.move_direction == 'right':
            arrow_angle = 0

            arrow_x = self.x + dlo_x_offset
            arrow_y = self.y + dlo_y_offset + self.scaled_height / 2

        if self.move_direction in ['left', 'right']:
            arrow_length = self.scaled_dlo_width * 0.1
        elif self.move_direction in ['up', 'down']:
            arrow_length = self.scaled_dlo_height * 0.1

        arrowhead_angle = math.pi / 6
        arrowhead_length = arrow_length / 2.25

        self.context.set_source_rgba(0, 0, 0, 1)

        self.context.move_to(arrow_x, arrow_y)  # move to center of canvas

        self.context.rel_line_to(arrow_length * math.cos(arrow_angle), arrow_length * math.sin(arrow_angle))
        self.context.rel_move_to(-arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
                                 -arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        self.context.rel_line_to(arrowhead_length * math.cos(arrow_angle - arrowhead_angle),
                                 arrowhead_length * math.sin(arrow_angle - arrowhead_angle))
        self.context.rel_line_to(-arrowhead_length * math.cos(arrow_angle + arrowhead_angle),
                                 -arrowhead_length * math.sin(arrow_angle + arrowhead_angle))

        self.context.set_line_width(1)
        self.context.stroke()

        self.context.restore()

    # def _scale_child_panels(self):
    #     ###
    #     #
    #     ###
    #     total_children_width = sum([_['width'] for _ in self.raw_child_panels])
    #
    #     if self.width >= total_children_width:
    #         return None
    #
    #     ratio = self.width / total_children_width
    #
    #     for child_panel in self.raw_child_panels:
    #         child_panel['width'] = child_panel['width'] * ratio
    #         child_panel['height'] = child_panel['height'] * ratio
    #         child_panel['dlo_width'] = child_panel['dlo_width'] * ratio
    #         child_panel['dlo_height'] = child_panel['dlo_height'] * ratio
    #
    #     for child_frame in self.raw_child_frames:
    #         child_frame['width'] = child_frame['width'] * ratio
    #         child_frame['height'] = child_frame['height'] * ratio

    @classmethod
    def guess_orientation(cls, frame_width, frame_height, raw_child_panels):
        ###
        # Guesses if the panels layout is vertical or horizontal
        ###

        # this logic determines if the panel layout is vertical or horizontal
        total_child_width = sum([_['width'] for _ in raw_child_panels])
        total_child_height = sum([_['height'] for _ in raw_child_panels])

        delta__width_w_child_total = abs(frame_width - total_child_width)
        delta__height_w_child_total = abs(frame_height - total_child_height)
        delta__width_w_child_max = abs(frame_width - max([_['width'] for _ in raw_child_panels]))
        delta__height_w_child_max = abs(frame_height - max([_['height'] for _ in raw_child_panels]))

        meta_delta__width = abs(delta__width_w_child_total - delta__width_w_child_max)
        meta_delta__height = abs(delta__height_w_child_total - delta__height_w_child_max)

        if meta_delta__width > meta_delta__height:
            # width has a bigger sparse so this criteria suits better to guess the orientation
            orientation = 'horizontal' if delta__width_w_child_total < delta__width_w_child_max else 'vertical'
        else:
            # height has a bigger sparse so this criteria suits better to guess the orientation
            orientation = 'vertical' if delta__height_w_child_total < delta__height_w_child_max else 'horizontal'

        return orientation

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

        if self.move_direction:
            self._draw_move_direction()

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

    @property
    def size_labels(self):
        child_panels_labels = list(itertools.chain(*[_._size_labels for _ in self.child_panels]))

        return self._size_labels + child_panels_labels

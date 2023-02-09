from typing import Dict


class NormalizationService:
    """
    Changes dimensions of raw params so child panels are fit into a frame
    in case a frame width < total width of child panels
    """

    def __init__(self, width_factor: float, height_factor: float):
        self.width_factor = width_factor
        self.height_factor = height_factor

    def run(self, raw_panel: Dict):
        self._normalize(raw_panel)

        return raw_panel

    def _normalize(self, raw_panel: Dict) -> None:
        raw_panel['original_width'] = raw_panel['width']
        raw_panel['original_height'] = raw_panel['height']
        raw_panel['width'] = raw_panel['width'] * self.width_factor
        raw_panel['height'] = raw_panel['height'] * self.height_factor

        if raw_panel['panel_type'] == 'panel':
            raw_panel['original_dlo_width'] = raw_panel['dlo_width']
            raw_panel['original_dlo_height'] = raw_panel['dlo_height']
            raw_panel['dlo_width'] = raw_panel['dlo_width'] * self.width_factor
            raw_panel['dlo_height'] = raw_panel['dlo_height'] * self.height_factor

        for child_frame in raw_panel.get('frames') or []:
            self._normalize(child_frame)

        for child_panel in raw_panel.get('panels') or []:
            self._normalize(child_panel)

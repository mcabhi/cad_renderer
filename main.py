from typing import Dict

import ezdxf
from itertools import groupby

# doc.layers.remove('panel a')
# panel_a = doc.layers.get('panel a')
# panel_a.rgb = (1, 50, 32)
#
# panel_b = doc.layers.get('panel b')
# panel_b.rgb = (0, 0, 205)
#
# frame = doc.layers.get('frame')
# frame.rgb = (246, 190, 0)


class Dxf:

    def __init__(self, filename, **kwargs):
        self.__document = ezdxf.readfile(filename)
        self.model_space = self.__document.modelspace()
        self.layers = self.__init_layers()

    def __init_layers(self) -> Dict:
        """
        Gets a mapping of LAYER_NAME W ENTITIES_LIST
        """
        all_entities = self.model_space.entity_space.entities
        sorted_entities = sorted(all_entities, key=lambda x: x.dxf.layer)
        return {k.lower().strip(): list(v) for k, v in groupby(sorted_entities, key=lambda x: x.dxf.layer)}

    def save_as(self, filename):
        """
        Saves a new DXF file
        """
        self.__document.saveas(filename)


class DxfLayer:

    def __init__(self, name, entities):
        self.name = name
        self.entities = entities

        self.min_x, self.min_y, self.max_x, self.max_y = self.__get_extremum_coordinates()

    def __get_extremum_coordinates(self):
        min_x = None
        min_y = None
        max_x = None
        max_y = None

        for entity in self.entities:
            start_x = entity.dxf.start.x
            start_y = entity.dxf.start.y
            end_x = entity.dxf.end.x
            end_y = entity.dxf.end.y

            if min_x is None:
                min_x = min(start_x, end_x)

            if min_y is None:
                min_y = min(start_y, end_y)

            if max_x is None:
                max_x = max(start_x, end_x)

            if max_y is None:
                max_y = max(start_y, end_y)

            if min(start_x, end_x) < min_x:
                min_x = min(start_x, end_x)

            if min(start_y, end_y) < min_y:
                min_y = min(start_y, end_y)

            if max(start_x, end_x) > max_x:
                max_x = max(start_x, end_x)

            if max(start_y, end_y) > max_y:
                max_y = max(start_y, end_y)

        return min_x, min_y, max_x, max_y


class DxfLabelController:
    def __init__(self, dxf: Dxf):
        self.dxf = dxf

    def run(self):
        for layer_name, entities in self.dxf.layers.items():
            if layer_name == 'frame':
                self.__label_frame(layer_name, entities)
            elif layer_name.startswith('panel '):
                self.__label_panel(layer_name, entities)

    def __label_frame(self, layer_name, entities):
        dxf_layer = DxfLayer(name=layer_name, entities=entities)

        middle_x = (dxf_layer.min_x + dxf_layer.max_x) / 2

        x = middle_x - 5
        y = dxf_layer.max_y + 2

        self.dxf.model_space.add_text(layer_name.upper()).set_pos((x, y))

    def __label_panel(self, layer_name, entities):
        dxf_layer = DxfLayer(name=layer_name, entities=entities)

        middle_x = (dxf_layer.min_x + dxf_layer.max_x) / 2
        middle_y = (dxf_layer.min_y + dxf_layer.max_y) / 2

        x = middle_x - 5
        y = middle_y + 2

        self.dxf.model_space.add_text(layer_name.upper()).set_pos((x, y))

dxf_instance = Dxf('/Users/eugenekovalev/Downloads/front_sgd2020.dxf', )
label_controller = DxfLabelController(dxf=dxf_instance)

label_controller.run()

dxf_instance.save_as('/Users/eugenekovalev/Downloads/resized.dxf')

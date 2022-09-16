class Colors:
    WHITE = 255 / 255, 255 / 255, 255 / 255, 1
    BLACK = 0, 0, 0, 1
    DARK_GREY = 52, 61, 70, 1

class FrameColors:
    FRAME_COLOR_1 = 52 / 255, 61 / 255, 70 / 255, 1
    FRAME_COLOR_2 = 101 / 255, 115 / 255, 126 / 255, 1

class PanelColors:
    COLOR_1 = 167 / 255, 173 / 255, 186 / 255, 1
    COLOR_2 = 192 / 255, 197 / 255, 206 / 255, 1

class DloColors:
    COLOR_1 = 255 / 255, 255 / 255, 255 / 255, 1
    
    
    
{
    "width": 550.375,
    "height": 500,
    "panel_type": "frame",
    "coordinates": {"x": 1, "y": 1},
    "panels": [
        {
            "name": "a",
            "panel_type": "panel",
            "move_direction": "right",
            "width": 200,
            "height": 450,
            "dlo_width": 195,
            "dlo_height": 430,
            "coordinates": {"x": 1, "y": 1}
        },
        {
            "name": "b",
            "panel_type": "panel",
            "move_direction": "down",
            "width": 250,
            "height": 450,
            "dlo_width": 245,
            "dlo_height": 430,
            "coordinates": {"x": 1, "y": 1}
        },
        {
            "name": "c",
            "panel_type": "panel",
            "move_direction": "down",
            "width": 50,
            "height": 450,
            "dlo_width": 45,
            "dlo_height": 430,
            "coordinates": {"x": 1, "y": 1}
        }
    ]
}

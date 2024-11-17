import os, csv
import pygame

# returns a two dimensional list of numnbers representing tile information
def read_csv(filename):
    map = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            map.append(list(row))
    return map

# dictionary which contains possible paths for buzzsaws
buzzsaw_path_dict = {
    "1": [pygame.math.Vector2(0, -3), pygame.math.Vector2(0, 3)],
    "2": [pygame.math.Vector2(-3, 0), pygame.math.Vector2(3, 0)],
}

# renders multiple lines onscreen
def render_multiline_text(text, font, color, surface, x, y, line_spacing=5):
    lines = text.split('\n')  # Split the text into lines
    for i, line in enumerate(lines):
        # Render each line and calculate its vertical position
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * (font.get_height() + line_spacing)))

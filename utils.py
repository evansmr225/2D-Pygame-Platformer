import os, csv
import pygame

def read_csv(filename):
    map = []
    with open(os.path.join(filename)) as data:
        data = csv.reader(data, delimiter=',')
        for row in data:
            map.append(list(row))
    return map

# Function to rotate an image around a pivot point
def rotate_image(image, angle, pivot, position):
    # Rotate the image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=position)

    # Calculate the new pivot position
    pivot_x = pivot[0] - image.get_rect().centerx
    pivot_y = pivot[1] - image.get_rect().centery
    pivot_pos = (rotated_rect.centerx + pivot_x, rotated_rect.centery + pivot_y)

    # Adjust the position of the rotated image to keep the pivot point in place
    new_rect = rotated_image.get_rect(center=pivot_pos)
    return rotated_image, new_rect
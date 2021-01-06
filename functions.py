from math import sqrt


def get_distance(obj1, obj2):
    return sqrt((obj1.rect.centerx - obj2.rect.centerx) ** 2 + (obj1.rect.centery - obj2.rect.centery) ** 2)
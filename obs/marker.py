import cv2
from cv2 import aruco

dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)  # Получите словарь ArUco
marker_id = 0  # Идентификатор маркера, может быть любым числом
marker_size = 200  # Размер маркера в пикселях

board_image = aruco.drawPlanarBoard(dictionary, (2, 2), marker_size, marker_size)
marker_image = board_image[0]  # Извлеките маркер изображения из доски

cv2.imwrite('marker.png', marker_image)
import cv2
import numpy as np
from PIL import Image, ImageFilter
from typing import Tuple, Optional
import io
import base64
import os
from django.conf import settings


class PhotoBackgroundChanger:
    def __init__(self):
        self.backgrounds = {
            "spiderman_building": "assets/backgrounds/building.jpg",
            "goku_clouds": "assets/backgrounds/clouds.jpg",
            "space": "assets/backgrounds/space.jpg",
            "beach": "assets/backgrounds/beach.jpg",
            "forest": "assets/backgrounds/forest.jpg"
        }
        
        self.poses = {
            "spiderman": {
                "name": "Homem-Aranha",
                "description": "Pose agachado com mão no chão",
                "reference_image": "assets/poses/spiderman_pose.jpg"
            },
            "sitting_cross_legs": {
                "name": "Sentado de pernas cruzadas",
                "description": "Posição de meditação",
                "reference_image": "assets/poses/sitting_cross_legs.jpg"
            },
            "flying": {
                "name": "Voando",
                "description": "Braços estendidos como se estivesse voando",
                "reference_image": "assets/poses/flying_pose.jpg"
            },
            "superhero": {
                "name": "Super-herói",
                "description": "Mãos na cintura, peito estufado",
                "reference_image": "assets/poses/superhero_pose.jpg"
            }
        }

    def remove_background_simple(self, image: np.ndarray, threshold: int = 50) -> np.ndarray:
        """
        Remove fundo usando detecção de cor dominante nas bordas
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        h, w = hsv.shape[:2]
        border_pixels = np.concatenate([
            hsv[0, :],
            hsv[h-1, :],
            hsv[:, 0],
            hsv[:, w-1]
        ])
        
        background_color = np.median(border_pixels, axis=0)
        
        diff = np.abs(hsv - background_color)
        mask = np.sum(diff, axis=2) > threshold
        
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        mask = cv2.GaussianBlur(mask.astype(np.float32), (5,5), 2)
        
        return mask

    def remove_background_grabcut(self, image: np.ndarray) -> np.ndarray:
        """
        Remove fundo usando algoritmo GrabCut
        """
        height, width = image.shape[:2]
        rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
        
        mask = np.zeros((height, width), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        mask2 = cv2.GaussianBlur(mask2.astype(np.float32), (3,3), 1)
        
        return mask2

    def compose_images(self, person_image: np.ndarray, background_image: np.ndarray, 
                      mask: np.ndarray, position: Tuple[int, int] = None) -> np.ndarray:
        """
        Compõe a imagem da pessoa com o fundo
        """
        person_h, person_w = person_image.shape[:2]
        background_resized = cv2.resize(background_image, (person_w, person_h))
        
        if mask.max() > 1:
            mask = mask / 255.0
        
        if len(mask.shape) == 2:
            mask = np.expand_dims(mask, axis=2)
        
        result = person_image * mask + background_resized * (1 - mask)
        
        return result.astype(np.uint8)

    def enhance_edges(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Melhora as bordas da composição
        """
        edges = cv2.Canny((mask * 255).astype(np.uint8), 50, 150)
        edges = cv2.dilate(edges, np.ones((3,3), np.uint8))
        
        blurred = cv2.GaussianBlur(image, (5,5), 0)
        
        edges_normalized = edges.astype(np.float32) / 255.0
        edges_3d = np.expand_dims(edges_normalized, axis=2)
        
        result = image * (1 - edges_3d) + blurred * edges_3d
        
        return result.astype(np.uint8)

    def process_photo(self, person_image_data: bytes, background_key: str, 
                     method: str = "grabcut") -> bytes:
        """
        Processa a foto completa: remove fundo e compõe com novo fundo
        """
        person_pil = Image.open(io.BytesIO(person_image_data))
        person_array = np.array(person_pil.convert('RGB'))
        
        if method == "grabcut":
            mask = self.remove_background_grabcut(person_array)
        else:
            mask = self.remove_background_simple(person_array)
        
        if background_key in self.backgrounds:
            try:
                background_path = os.path.join(settings.ASSETS_ROOT, 'backgrounds', 
                                             f'{background_key.split("_")[-1]}.jpg')
                background_pil = Image.open(background_path)
                background_array = np.array(background_pil.convert('RGB'))
            except:
                background_array = self.create_colored_background(
                    person_array.shape[:2], background_key)
        else:
            background_array = self.create_colored_background(
                person_array.shape[:2], background_key)
        
        result = self.compose_images(person_array, background_array, mask)
        
        result = self.enhance_edges(result, mask)
        
        result_pil = Image.fromarray(result)
        output_buffer = io.BytesIO()
        result_pil.save(output_buffer, format='JPEG', quality=95)
        
        return output_buffer.getvalue()

    def create_colored_background(self, size: Tuple[int, int], background_key: str) -> np.ndarray:
        """
        Cria fundos coloridos quando não há imagem disponível
        """
        height, width = size
        
        color_map = {
            "spiderman_building": (30, 50, 150),
            "goku_clouds": (135, 206, 235),
            "space": (25, 25, 50),
            "beach": (255, 218, 185),
            "forest": (34, 139, 34)
        }
        
        color = color_map.get(background_key, (100, 150, 200))
        background = np.full((height, width, 3), color, dtype=np.uint8)
        
        gradient = np.linspace(0.7, 1.0, height).reshape(-1, 1, 1)
        background = (background * gradient).astype(np.uint8)
        
        return background

    def get_available_backgrounds(self):
        """
        Retorna lista de fundos disponíveis
        """
        return {
            "spiderman_building": "Prédio da cidade (estilo Homem-Aranha)",
            "goku_clouds": "Nuvens no céu (estilo Dragon Ball)",
            "space": "Espaço sideral",
            "beach": "Praia tropical", 
            "forest": "Floresta mística"
        }
    
    def get_available_poses(self):
        """
        Retorna lista de poses disponíveis
        """
        return self.poses
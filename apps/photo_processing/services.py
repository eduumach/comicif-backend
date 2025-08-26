import rembg
import numpy as np
from PIL import Image, ImageFilter, ImageFile
import io
import os
from django.conf import settings
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)
classifier = pipeline("image-classification", model="Falconsai/nsfw_image_detection")


class PhotoBackgroundChanger:
    def __init__(self):
        self.backgrounds = {
            "spiderman_building": "assets/backgrounds/building.jpg",
            "goku_clouds": "assets/backgrounds/clouds.jpg",
            "space": "assets/backgrounds/space.webp",
            "beach": "assets/backgrounds/beach.jpeg",
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

    def remove_background(self, image_array: np.ndarray) -> np.ndarray:
        """
        Remove background using rembg with u2net_human_seg model
        """
        try:
            session = rembg.new_session(model_name="u2net_human_seg")
            output_array = rembg.remove(image_array, session=session)
            return output_array
        except Exception as e:
            logger.error(f"Error in rembg background removal: {e}")
            raise

    def smooth_alpha_edges(self, alpha_channel: np.ndarray, blur_radius: float = 2.0, feather_size: int = 3) -> np.ndarray:
        """
        Suaviza as bordas do canal alpha para uma composição mais suave
        """
        alpha_pil = Image.fromarray((alpha_channel * 255).astype(np.uint8).squeeze())
        
        blurred = alpha_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
        smoothed_alpha = np.array(blurred).astype(np.float32) / 255.0
        
        if feather_size > 0:
            from scipy.ndimage import binary_erosion, gaussian_filter
            try:
                eroded = binary_erosion(smoothed_alpha > 0.5, iterations=feather_size)
                feathered = gaussian_filter(eroded.astype(np.float32), sigma=feather_size/2)
                smoothed_alpha = np.minimum(smoothed_alpha, feathered)
            except ImportError:
                pass
        
        return np.expand_dims(smoothed_alpha, axis=2)

    def compose_images(self, person_rgba: np.ndarray, background_image: np.ndarray, smooth_edges: bool = True) -> np.ndarray:
        """
        Compõe a imagem da pessoa (com transparência) com o fundo usando técnicas avançadas de suavização
        """
        person_h, person_w = person_rgba.shape[:2]
        background_resized = background_image.resize((person_w, person_h))
        background_array = np.array(background_resized)
        
        alpha = person_rgba[:, :, 3:4] / 255.0
        person_rgb = person_rgba[:, :, :3].copy().astype(np.float32)
        
        if smooth_edges:
            alpha = self.smooth_alpha_edges(alpha, blur_radius=2.5, feather_size=2)
            
            background_mean_color = np.mean(background_array, axis=(0, 1))
            edge_mask = (alpha > 0.1) & (alpha < 0.9) 
            
            if np.any(edge_mask):
                color_correction_strength = 0.1 
                for channel in range(3):
                    person_rgb[:, :, channel] = np.where(
                        edge_mask.squeeze(),
                        person_rgb[:, :, channel] * (1 - color_correction_strength) + 
                        background_mean_color[channel] * color_correction_strength,
                        person_rgb[:, :, channel]
                    )
        
        result = person_rgb * alpha + background_array * (1 - alpha)
        
        return result.astype(np.uint8)

    def process_photo(self, person_image_data: bytes, background_key: str) -> bytes:
        """
        Processa a foto completa: remove fundo e compõe com novo fundo
        """
        person_pil = Image.open(io.BytesIO(person_image_data))
        if self.is_nsfw(person_pil):
            logger.warning("Imagem NSFW detectada.")
            return b""
        person_array = np.array(person_pil.convert('RGB'))

        # Remove background using rembg
        person_rgba_array = self.remove_background(person_array)
        
        # Load background image
        if background_key in self.backgrounds:
            try:
                background_path = os.path.join(settings.ASSETS_ROOT, 'backgrounds', 
                                             f'{background_key.split("_")[-1]}.jpg')
                background_pil = Image.open(background_path)
            except:
                background_pil = self.create_colored_background(
                    person_rgba_array.shape[:2], background_key)
        else:
            background_pil = self.create_colored_background(
                person_rgba_array.shape[:2], background_key)
        
        # Compose images
        result = self.compose_images(person_rgba_array, background_pil)
        
        result_pil = Image.fromarray(result)
        output_buffer = io.BytesIO()
        result_pil.save(output_buffer, format='JPEG', quality=95)
        
        return output_buffer.getvalue()

    def create_colored_background(self, size, background_key: str) -> Image.Image:
        """
        Cria fundos coloridos quando não há imagem disponível
        """
        height, width = size[:2]
        
        color_map = {
            "spiderman_building": (30, 50, 150),
            "goku_clouds": (135, 206, 235),
            "space": (25, 25, 50),
            "beach": (255, 218, 185),
            "forest": (34, 139, 34)
        }
        
        color = color_map.get(background_key, (100, 150, 200))
        background = Image.new('RGB', (width, height), color)
        
        return background

    def is_nsfw(self,image: ImageFile, threshold: float = 0.5) -> bool:
        """
        Retorna True se a imagem for considerada NSFW (pornográfica/sexual).
        threshold = confiança mínima para classificar como NSFW.
        """
        results = classifier(image)

        nsfw_score = next((r["score"] for r in results if r["label"] == "nsfw"), 0.0)

        return nsfw_score >= threshold

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
    

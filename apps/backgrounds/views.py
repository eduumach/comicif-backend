from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import os


@api_view(['GET'])
def get_backgrounds(request):
    """
    Retorna lista de fundos disponíveis
    """
    backgrounds = {
        "spiderman_building": "Prédio da cidade (estilo Homem-Aranha)",
        "goku_clouds": "Nuvens no céu (estilo Dragon Ball)",
        "space": "Espaço sideral",
        "beach": "Praia tropical", 
        "forest": "Floresta mística"
    }
    
    available_backgrounds = {}
    for key, description in backgrounds.items():
        image_path = os.path.join(settings.ASSETS_ROOT, 'backgrounds', f'{key.replace("_", "/").split("/")[-1]}.jpg')
        available_backgrounds[key] = description
    
    return Response({"backgrounds": available_backgrounds})
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_poses(request):
    """
    Retorna lista de poses disponíveis
    """
    poses = {
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
    
    return Response({"poses": poses})
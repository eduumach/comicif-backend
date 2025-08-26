from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import logging
from .services import PhotoBackgroundChanger

logger = logging.getLogger(__name__)


photo_processor = PhotoBackgroundChanger()


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def process_photo(request):
    """
    Processa a foto: remove o fundo e compõe com o fundo escolhido
    """    
    if 'photo' not in request.FILES:
        logger.error("Erro: Foto não encontrada na requisição")
        return Response(
            {"error": "Foto é obrigatória"}, 
            status=400
        )
    
    photo = request.FILES['photo']
    background = request.data.get('background')
    
    if not photo.content_type.startswith("image/"):
        return Response(
            {"error": "Arquivo deve ser uma imagem"}, 
            status=400
        )
    
    available_backgrounds = photo_processor.get_available_backgrounds()
    if background not in available_backgrounds:
        return Response({
            "error": f"Fundo inválido. Disponíveis: {list(available_backgrounds.keys())}"
        }, status=400)
    
    try:
        photo_data = photo.read()
        
        result_bytes = photo_processor.process_photo(
            photo_data, background
        )
        
        response = HttpResponse(
            content=result_bytes,
            content_type="image/jpeg"
        )
        response['Content-Disposition'] = 'attachment; filename=comicif_result.jpg'
        return response
        
    except Exception as e:
        return Response({
            "error": f"Erro ao processar imagem: {str(e)}"
        }, status=500)


@api_view(['GET'])
def get_available_options(request):
    """
    Retorna lista de opções disponíveis (fundos e poses)
    """
    try:
        backgrounds = photo_processor.get_available_backgrounds()
        poses = photo_processor.get_available_poses()
        
        return Response({
            "backgrounds": backgrounds,
            "poses": poses
        })
        
    except Exception as e:
        return Response({
            "error": f"Erro ao obter informações: {str(e)}"
        }, status=500)


@api_view(['POST'])
def process_photo_base64(request):
    """
    Versão alternativa que recebe e retorna imagens em base64
    """
    photo_base64 = request.data.get('photo_base64')
    background = request.data.get('background')
    
    if not photo_base64:
        return Response(
            {"error": "photo_base64 é obrigatório"}, 
            status=400
        )
    
    available_backgrounds = photo_processor.get_available_backgrounds()
    if background not in available_backgrounds:
        return Response({
            "error": f"Fundo inválido. Disponíveis: {list(available_backgrounds.keys())}"
        }, status=400)
    
    try:
        photo_data = base64.b64decode(photo_base64)
        
        result_bytes = photo_processor.process_photo(
            photo_data, background
        )
        
        result_base64 = base64.b64encode(result_bytes).decode('utf-8')
        
        return Response({
            "result_image": result_base64,
            "background_used": background
        })
        
    except Exception as e:
        return Response({
            "error": f"Erro ao processar imagem: {str(e)}"
        }, status=500)
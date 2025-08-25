# Comicif Backend - Django

Backend Django para processamento de fotos com remoção de fundo e composição com temas de quadrinhos.

## Estrutura do Projeto

```
comicif_backend/
├── config/                    # Configuração principal do Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                      # Apps do Django
│   ├── backgrounds/           # Gerenciamento de fundos
│   ├── poses/                # Gerenciamento de poses
│   └── photo_processing/     # Processamento principal
├── assets/                   # Arquivos estáticos (imagens de fundo)
├── media/                    # Uploads do usuário
└── manage.py
```

## Instalação

1. Instalar dependências:
```bash
uv sync
```

2. Executar migrações:
```bash
python manage.py migrate
```

3. Criar superusuário (opcional):
```bash
python manage.py createsuperuser
```

4. Executar servidor de desenvolvimento:
```bash
python manage.py runserver
```

## API Endpoints

### Fundos Disponíveis
- **GET** `/api/backgrounds/`
- Retorna lista de fundos disponíveis

### Poses Disponíveis  
- **GET** `/api/poses/`
- Retorna lista de poses disponíveis

### Processamento de Fotos
- **POST** `/api/process-photo/`
  - Form data: `photo` (arquivo), `background` (string), `method` (string, opcional)
  - Retorna imagem processada

- **POST** `/api/process-photo-base64/`
  - JSON: `photo_base64` (string), `background` (string), `method` (string, opcional)
  - Retorna JSON com imagem em base64

### Outros
- **GET** `/` - Informações da API
- **GET** `/api/health/` - Health check

## Métodos de Processamento

- `grabcut` (padrão): Usa algoritmo GrabCut para remoção de fundo
- `simple`: Usa detecção de cor dominante nas bordas

## Fundos Disponíveis

- `spiderman_building`: Prédio da cidade (estilo Homem-Aranha)
- `goku_clouds`: Nuvens no céu (estilo Dragon Ball)
- `space`: Espaço sideral
- `beach`: Praia tropical
- `forest`: Floresta mística

## Desenvolvimento

Para executar em modo desenvolvimento:
```bash
python manage.py runserver 0.0.0.0:8000
```

Para executar testes:
```bash
python manage.py test
```

## Produção

Para produção, usar Gunicorn:
```bash
gunicorn config.wsgi:application
```
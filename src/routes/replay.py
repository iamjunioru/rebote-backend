from flask import Blueprint, request, jsonify, send_file
from src.models.user import db
from src.models.replay import Replay
import os
import time
import random
import logging
import colorlog
from datetime import datetime

logger = logging.getLogger('replay')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler.setFormatter(color_formatter)
    logger.addHandler(handler)

replay_bp = Blueprint('replay', __name__)

# diretório para armazenar os replays
REPLAYS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'replays')
os.makedirs(REPLAYS_DIR, exist_ok=True)
logger.info(f"Diretório de replays configurado em: {REPLAYS_DIR}")

@replay_bp.route('/trigger', methods=['POST'])
def trigger_replay():
    """
    endpoint para receber o trigger do botão e salvar um replay.
    simula o processo de captura e salvamento de vídeo.
    """
    try:
        logger.info(f"Iniciando captura de replay - IP: {request.remote_addr}")
        # simula o processamento do replay
        time.sleep(2)  # Simula o tempo de processamento
        
        # gera um nome de arquivo único
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M')
        filename = f'replay-{timestamp}.mp4'
        logger.info(f"Nome do arquivo gerado: {filename}")
        
        # simula a criação do arquivo de vídeo (mock)
        file_path = os.path.join(REPLAYS_DIR, filename)
        
        # sria um arquivo mock (vazio por enquanto)
        with open(file_path, 'w') as f:
            f.write('# mock video file - replace with actual video processing')
        logger.debug(f"Arquivo mock criado em: {file_path}")
        
        # simula tamanho do arquivo
        file_size = random.randint(5000000, 15000000)  # 5-15MB
        
        # salva no banco de dados
        replay = Replay(
            filename=filename,
            file_size=file_size,
            status='saved'
        )
        db.session.add(replay)
        db.session.commit()
        logger.info(f"Replay ID {replay.id} salvo no banco de dados (tamanho: {file_size} bytes)")
        
        return jsonify({
            'success': True,
            'message': 'replay salvo com sucesso',
            'replay': replay.to_dict(),
            'video_url': f'/api/replay/video/{replay.id}',
            'poster_url': f'/api/replay/poster/{replay.id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao processar replay: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao processar replay: {str(e)}'
        }), 500

@replay_bp.route('/list', methods=['GET'])
def list_replays():
    """
    lista todos os replays salvos.
    """
    try:
        logger.info("Solicitação de listagem de replays")
        replays = Replay.query.order_by(Replay.timestamp.desc()).all()
        logger.info(f"Retornando {len(replays)} replays")
        return jsonify({
            'success': True,
            'replays': [replay.to_dict() for replay in replays]
        }), 200
    except Exception as e:
        logger.error(f"Erro ao listar replays: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao listar replays: {str(e)}'
        }), 500

@replay_bp.route('/video/<int:replay_id>', methods=['GET'])
def get_video(replay_id):
    """
    retorna o arquivo de vídeo do replay.
    """
    try:
        logger.info(f"Solicitação de vídeo para replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        file_path = os.path.join(REPLAYS_DIR, replay.filename)
        
        if os.path.exists(file_path):
            logger.info(f"Enviando arquivo de replay: {file_path}")
            return send_file(file_path, as_attachment=False)
        else:
            logger.warning(f"Arquivo de replay não encontrado: {file_path}")
            # retorna um vídeo placeholder para demonstração
            return jsonify({
                'success': False,
                'message': 'arquivo de vídeo não encontrado',
                'placeholder_url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar vídeo ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao buscar vídeo: {str(e)}'
        }), 500

@replay_bp.route('/poster/<int:replay_id>', methods=['GET'])
def get_poster(replay_id):
    """
    retorna uma imagem poster para o vídeo.
    """
    try:
        logger.info(f"Solicitação de poster para replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        
        # por enquanto, retorna um placeholder
        logger.info(f"Retornando poster placeholder para replay ID: {replay_id}")
        return jsonify({
            'success': True,
            'poster_url': f'https://placehold.co/1280x720/333/fff?text=replay+{replay.id}'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar poster para replay ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao buscar poster: {str(e)}'
        }), 500

@replay_bp.route('/delete/<int:replay_id>', methods=['DELETE'])
def delete_replay(replay_id):
    """
    deleta um replay específico.
    """
    try:
        logger.info(f"Solicitação para deletar replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        
        # remove o arquivo físico
        file_path = os.path.join(REPLAYS_DIR, replay.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Arquivo físico removido: {file_path}")
        else:
            logger.warning(f"Arquivo não encontrado para exclusão: {file_path}")
        
        # remove do banco de dados
        db.session.delete(replay)
        db.session.commit()
        logger.info(f"Replay ID {replay_id} removido do banco de dados")
        
        return jsonify({
            'success': True,
            'message': 'replay deletado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao deletar replay ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao deletar replay: {str(e)}'
        }), 500

@replay_bp.route('/status', methods=['GET'])
def get_status():
    """
    retorna o status do sistema de replay.
    """
    try:
        logger.info("Solicitação de status do sistema de replay")
        total_replays = Replay.query.count()
        recent_replays = Replay.query.filter(
            Replay.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        disk_usage = sum(os.path.getsize(os.path.join(REPLAYS_DIR, f)) for f in os.listdir(REPLAYS_DIR) if os.path.isfile(os.path.join(REPLAYS_DIR, f)))
        
        status_info = {
            'system': 'online',
            'total_replays': total_replays,
            'today_replays': recent_replays,
            'storage_path': REPLAYS_DIR,
            'storage_usage_bytes': disk_usage,
            'mock_mode': True
        }
        
        logger.info(f"Status do sistema: {total_replays} replays total, {recent_replays} hoje")
        return jsonify({
            'success': True,
            'status': status_info
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter status do sistema: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao obter status: {str(e)}'
        }), 500


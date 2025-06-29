from flask import Blueprint, request, jsonify, send_file
from src.models.user import db
from src.models.replay import Replay
from src.utils.circular_buffer import CircularVideoBuffer
import os
import time
import random
import logging
import colorlog
import atexit
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
BUFFER_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'buffer')
os.makedirs(REPLAYS_DIR, exist_ok=True)
os.makedirs(BUFFER_DIR, exist_ok=True)

logger.info(f"diretório de replays configurado em: {REPLAYS_DIR}")
logger.info(f"diretório de buffer configurado em: {BUFFER_DIR}")

# instância global do buffer circular
circular_buffer = CircularVideoBuffer(
    buffer_duration=60,
    segment_duration=10,
    video_source= 'USB CAMERA',  # nome da camera
    output_dir=BUFFER_DIR
)

@atexit.register
def cleanup_on_exit():
    logger.info("encerrando a aplicação, parando o buffer circular...")
    if circular_buffer.is_recording:
        circular_buffer.stop_recording()

def initialize_buffer():
    """
    inicializa o buffer circular quando o módulo é carregado.
    """
    try:
        logger.info("inicializando buffer circular...")
        circular_buffer.start_recording()
        logger.info("buffer circular inicializado com sucesso")
    except Exception as e:
        logger.error(f"erro ao inicializar buffer circular: {e}")

# inicializa o buffer quando o módulo é importado
initialize_buffer()

@replay_bp.route('/trigger', methods=['POST'])
def trigger_replay():
    """
    endpoint para receber o trigger do botão e salvar um replay.
    usa o buffer circular para salvar os últimos 30 segundos.
    """
    try:
        logger.info(f"iniciando captura de replay - IP: {request.remote_addr}")
        
        # verifica se o buffer está gravando
        if not circular_buffer.is_recording:
            logger.error("buffer circular não está gravando")
            return jsonify({
                'success': False,
                'message': 'buffer circular não está ativo'
            }), 500
        
        # gera um nome de arquivo único
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        filename = f'replay-{timestamp}.mp4'
        file_path = os.path.join(REPLAYS_DIR, filename)
        
        logger.info(f"nome do arquivo gerado: {filename}")
        
        # salva o replay usando o buffer circular
        success = circular_buffer.save_replay(file_path)
        
        if not success:
            logger.error("falha ao salvar replay do buffer circular")
            return jsonify({
                'success': False,
                'message': 'erro ao salvar replay do buffer'
            }), 500
        
        # verifica se o arquivo foi criado e obtém seu tamanho
        if not os.path.exists(file_path):
            logger.error(f"frquivo de replay não foi criado: {file_path}")
            return jsonify({
                'success': False,
                'message': 'arquivo de replay não foi criado'
            }), 500
        
        file_size = os.path.getsize(file_path)
        logger.info(f"replay salvo com sucesso: {file_path} ({file_size} bytes)")
        
        # salva no banco de dados
        replay = Replay(
            filename=filename,
            file_size=file_size,
            status='saved'
        )
        db.session.add(replay)
        db.session.commit()
        logger.info(f"Replay ID {replay.id} salvo no banco de dados")
        
        return jsonify({
            'success': True,
            'message': 'replay salvo com sucesso',
            'replay': replay.to_dict(),
            'video_url': f'/api/replay/video/{replay.id}',
            'poster_url': f'/api/replay/poster/{replay.id}'
        }), 200
        
    except Exception as e:
        logger.error(f"erro ao processar replay: {str(e)}", exc_info=True)
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
        logger.info("solicitação de listagem de replays")
        replays = Replay.query.order_by(Replay.timestamp.desc()).all()
        logger.info(f"retornando {len(replays)} replays")
        return jsonify({
            'success': True,
            'replays': [replay.to_dict() for replay in replays]
        }), 200
    except Exception as e:
        logger.error(f"erro ao listar replays: {str(e)}", exc_info=True)
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
        logger.info(f"solicitação de vídeo para replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        file_path = os.path.join(REPLAYS_DIR, replay.filename)
        
        if os.path.exists(file_path):
            logger.info(f"enviando arquivo de replay: {file_path}")
            return send_file(file_path, as_attachment=False, mimetype='video/mp4')
        else:
            logger.warning(f"arquivo de replay não encontrado: {file_path}")
            return jsonify({
                'success': False,
                'message': 'arquivo de vídeo não encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"erro ao buscar vídeo ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao buscar vídeo: {str(e)}'
        }), 500

@replay_bp.route('/download/<int:replay_id>', methods=['GET'])
def download_video(replay_id):
    """
    faz download do arquivo de vídeo do replay.
    """
    try:
        logger.info(f"solicitação de download para replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        file_path = os.path.join(REPLAYS_DIR, replay.filename)
        
        if os.path.exists(file_path):
            logger.info(f"enviando arquivo para download: {file_path}")
            return send_file(file_path, as_attachment=True, download_name=replay.filename)
        else:
            logger.warning(f"arquivo de replay não encontrado: {file_path}")
            return jsonify({
                'success': False,
                'message': 'arquivo de vídeo não encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"erro ao fazer download do vídeo ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao fazer download: {str(e)}'
        }), 500

@replay_bp.route('/poster/<int:replay_id>', methods=['GET'])
def get_poster(replay_id):
    """
    retorna uma imagem poster para o vídeo.
    """
    try:
        logger.info(f"solicitação de poster para replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        
        # por enquanto, retorna um placeholder
        logger.info(f"retornando poster placeholder para replay ID: {replay_id}")
        return jsonify({
            'success': True,
            'poster_url': f'https://placehold.co/1280x720/333/fff?text=replay+{replay.id}'
        }), 200
        
    except Exception as e:
        logger.error(f"erro ao buscar poster para replay ID {replay_id}: {str(e)}", exc_info=True)
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
        logger.info(f"solicitação para deletar replay ID: {replay_id}")
        replay = Replay.query.get_or_404(replay_id)
        
        # remove o arquivo físico
        file_path = os.path.join(REPLAYS_DIR, replay.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"arquivo físico removido: {file_path}")
        else:
            logger.warning(f"arquivo não encontrado para exclusão: {file_path}")
        
        # remove do banco de dados
        db.session.delete(replay)
        db.session.commit()
        logger.info(f"- replay ID {replay_id} removido do banco de dados")
        
        return jsonify({
            'success': True,
            'message': 'replay deletado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"erro ao deletar replay ID {replay_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao deletar replay: {str(e)}'
        }), 500

@replay_bp.route('/buffer/status', methods=['GET'])
def get_buffer_status():
    """
    retorna o status do buffer circular.
    """
    try:
        logger.info("solicitação de status do buffer circular")
        status = circular_buffer.get_buffer_info()
        
        return jsonify({
            'success': True,
            'buffer_status': status
        }), 200
        
    except Exception as e:
        logger.error(f"erro ao obter status do buffer: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao obter status do buffer: {str(e)}'
        }), 500

@replay_bp.route('/buffer/restart', methods=['POST'])
def restart_buffer():
    """
    reinicia o buffer circular.
    """
    try:
        logger.info("solicitação para reiniciar buffer circular")
        
        # Para o buffer atual
        circular_buffer.stop_recording()
        time.sleep(1)
        
        # Reinicia o buffer
        circular_buffer.start_recording()
        
        logger.info("Buffer circular reiniciado com sucesso")
        return jsonify({
            'success': True,
            'message': 'buffer circular reiniciado com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao reiniciar buffer: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao reiniciar buffer: {str(e)}'
        }), 500

@replay_bp.route('/status', methods=['GET'])
def get_status():
    """
    retorna o status do sistema de replay.
    """
    try:
        logger.info("solicitação de status do sistema de replay")
        total_replays = Replay.query.count()
        recent_replays = Replay.query.filter(
            Replay.timestamp >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # calcula uso de disco
        disk_usage = 0
        if os.path.exists(REPLAYS_DIR):
            disk_usage = sum(os.path.getsize(os.path.join(REPLAYS_DIR, f)) 
                           for f in os.listdir(REPLAYS_DIR) 
                           if os.path.isfile(os.path.join(REPLAYS_DIR, f)))
        
        # status do buffer
        buffer_status = circular_buffer.get_buffer_info()
        
        status_info = {
            'system': 'tamo online',
            'total_replays': total_replays,
            'today_replays': recent_replays,
            'storage_path': REPLAYS_DIR,
            'storage_usage_bytes': disk_usage,
            'buffer_circular': buffer_status
        }
        
        logger.info(f"Status do sistema: {total_replays} replays total, {recent_replays} hoje")
        return jsonify({
            'success': True,
            'status': status_info
        }), 200
        
    except Exception as e:
        logger.error(f"erro ao obter status do sistema: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'erro ao obter status: {str(e)}'
        }), 500


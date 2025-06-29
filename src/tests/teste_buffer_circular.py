#!/usr/bin/env python3
"""
Script de teste para o buffer circular do sistema Rebote.
Testa a funcionalidade básica do buffer circular sem usar webcam real.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.circular_buffer import CircularVideoBuffer

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_buffer_circular():
    """Testa o buffer circular com vídeo simulado"""
    test_dir = os.path.join(os.path.dirname(__file__), 'src/tests/test_buffer')
    replays_dir = os.path.join(os.path.dirname(__file__), 'src/tests/test_replays')
    
    # cria diretórios se não existirem
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(replays_dir, exist_ok=True)
    
    # usa vídeo mock 
    video_source = os.path.join(os.path.dirname(__file__), 'src', 'static', 'simulated_buffer_1min.mp4')
    
    if not os.path.exists(video_source):
        logger.error(f"vídeo de mock não encontrado: {video_source}")
        return False
    
    logger.info(f"usando vídeo simulado: {video_source}")
    
    # inicializa buffer circular com configurações de teste
    buffer = CircularVideoBuffer(
        buffer_duration=15,  # 15 segundos para teste rápido
        segment_duration=3,  # segmentos de 3 segundos
        video_source=video_source,
        output_dir=test_dir
    )
    
    try:
        # testa informações do buffer
        logger.info("=== teste 1: informações do buffer ===")
        info = buffer.get_buffer_info()
        logger.info(f"info do buffer: {info}")
        
        # testa início da gravação
        logger.info("=== teste 2: iniciando gravação ===")
        success = buffer.start_recording()
        if not success:
            logger.error("falha ao iniciar gravação")
            return False
        
        logger.info("gravação iniciada com sucesso")
        
        # aguarda alguns segmentos serem criados
        logger.info("=== teste 3: Aguardando criação de segmentos ===")
        for i in range(20):  # Aguarda até 20 segundos
            time.sleep(1)
            info = buffer.get_buffer_info()
            logger.info(f"segmentos: {info['segments_count']}/{info['max_segments']}, "
                       f"duração disponível: {info['total_duration']}s")
            
            if info['segments_count'] >= 3:  # Pelo menos 3 segmentos
                break
        
        # testa salvamento de replay
        logger.info("=== teste 4: Salvando replay ===")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        replay_path = os.path.join(replays_dir, f'test_replay_{timestamp}.mp4')
        
        success = buffer.save_replay(replay_path)
        if success:
            logger.info(f"replay salvo com sucesso: {replay_path}")
            if os.path.exists(replay_path):
                size = os.path.getsize(replay_path)
                logger.info(f"tamanho do arquivo: {size} bytes")
            else:
                logger.error("arquivo de replay não foi criado")
                success = False
        else:
            logger.error("falha ao salvar replay")
        
        # para a gravação
        logger.info("=== teste 5: parando gravação ===")
        buffer.stop_recording()
        logger.info("gravação parada")
        
        # Informações finais
        info = buffer.get_buffer_info()
        logger.info(f"info final do buffer: {info}")
        
        return success
        
    except Exception as e:
        logger.error(f"erro durante o teste: {e}", exc_info=True)
        return False
    finally:
        # Garante que a gravação seja parada
        if buffer.is_recording:
            buffer.stop_recording()

def main():
    """Função principal"""
    logger.info("=== INICIANDO TESTE DO BUFFER CIRCULAR ===")
    
    success = test_buffer_circular()
    
    if success:
        logger.info("=== TESTE CONCLUÍDO COM SUCESSO ===")
        return 0
    else:
        logger.error("=== TESTE FALHOU ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())


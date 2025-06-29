import os
import subprocess
import threading
import time
from datetime import datetime
import logging
from collections import deque
import glob

logger = logging.getLogger(__name__)

class CircularVideoBuffer:
    def __init__(self, buffer_duration=30, segment_duration=5, video_source="USB CAMERA", output_dir="buffer"):
        """
        inicializa o buffer circular de vídeo
        
        Args:
            buffer_duration: Duração total do buffer em segundos (padrão: 30s)
            segment_duration: Duração de cada segmento em segundos (padrão: 5s)
            video_source: Fonte de vídeo (webcam ou arquivo)
            output_dir: Diretório para armazenar os segmentos
        """
        self.buffer_duration = buffer_duration
        self.segment_duration = segment_duration
        self.video_source = video_source
        self.output_dir = output_dir
        self.max_segments = buffer_duration // segment_duration
        
        # deck para manter os segmentos em ordem
        self.segments = deque(maxlen=self.max_segments)
        
        self.is_recording = False
        self.ffmpeg_process = None
        self.segment_counter = 0
        self.recording_thread = None
        
        # cria o diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # adiciona um pequeno atraso para garantir que o processo anterior liberou os arquivos
        time.sleep(1)
        
        # limpa segmentos antigos
        self._cleanup_old_segments()
        
        logger.info(f"buffer circular inicializado - duração total: {buffer_duration}s, "
                   f"segmentos de {segment_duration}s, máximo de {self.max_segments} segmentos")
    
    def _cleanup_old_segments(self):
        """remove todos os segmentos antigos do diretório"""
        try:
            pattern = os.path.join(self.output_dir, "segment_*.ts")
            old_files = glob.glob(pattern)
            for file in old_files:
                try:
                    os.remove(file)
                    logger.debug(f"removido segmento antigo: {file}")
                except OSError as e:
                    logger.warning(f"não foi possível remover o arquivo {file}: {e}")
        except Exception as e:
            logger.error(f"erro ao limpar segmentos antigos: {e}")
    
    def _get_segment_path(self, segment_id):
        """retorna o caminho para um segmento específico"""
        return os.path.join(self.output_dir, f"segment_{segment_id:06d}.ts")
    
    def _record_segments(self):
        """thread para gravação contínua de segmentos"""
        while self.is_recording:
            segment_path = self._get_segment_path(self.segment_counter)
            
            # detecta se é um arquivo de vídeo ou dispositivo
            is_file = os.path.isfile(self.video_source)
            
            ffmpeg_cmd = []
            if is_file:
                # comando FFmpeg para arquivo de vídeo (loop infinito)
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-stream_loop", "-1",  # loop infinito
                    "-i", self.video_source,
                    "-vcodec", "libx264",
                    "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-t", str(self.segment_duration),  # duração do segmento
                    "-f", "mpegts",
                    "-y",  # sobrescreve arquivo existente
                    segment_path
                ]
            else:
                # comando FFmpeg para dispositivo de captura
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-f", "dshow",
                    "-i", f"video={self.video_source}",
                    "-vcodec", "libx264",
                    "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-t", str(self.segment_duration),  # duração do segmento
                    "-f", "mpegts",
                    "-y",  # sobrescreve arquivo existente
                    segment_path
                ]
            
            logger.debug(f"gravando segmento {self.segment_counter}: {segment_path}")
            
            try:
                # executa FFmpeg para este segmento
                process = subprocess.Popen(
                    ffmpeg_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # aguarda a conclusão do segmento
                process.wait()
                
                if process.returncode == 0 and os.path.exists(segment_path):
                    # adiciona o segmento ao buffer circular
                    if len(self.segments) >= self.max_segments:
                        # remove o segmento mais antigo
                        old_segment = self.segments[0]
                        old_path = self._get_segment_path(old_segment)
                        try:
                            if os.path.exists(old_path):
                                os.remove(old_path)
                                logger.debug(f"removido segmento antigo: {old_path}")
                        except OSError as e:
                            logger.warning(f"não foi possível remover o segmento antigo {old_path}: {e}")
                    
                    self.segments.append(self.segment_counter)
                    logger.debug(f"segmento {self.segment_counter} adicionado ao buffer")
                    
                    self.segment_counter += 1
                else:
                    logger.error(f"falha ao gravar segmento {self.segment_counter}. FFmpeg retornou código {process.returncode}")
                    if process.returncode != 0:
                        logger.error(f"FFmpeg stderr: {process.stderr.decode()}")
                    time.sleep(1) # pequeno atraso em caso de falha para evitar loop rápido
                    
            except Exception as e:
                logger.error(f"erro inesperado na gravação de segmento {self.segment_counter}: {e}")
                time.sleep(1)  # aguarda antes de tentar novamente
    
    def start_recording(self):
        """inicia a gravação contínua do buffer"""
        if self.is_recording:
            logger.warning("buffer já está gravando")
            return True
            
        try:
            self.is_recording = True
            
            # inicia a thread de gravação
            self.recording_thread = threading.Thread(target=self._record_segments, daemon=True)
            self.recording_thread.start()
            
            logger.info("gravação do buffer circular iniciada com sucesso")
            
            # aguarda um pouco para garantir que pelo menos um segmento foi criado
            time.sleep(self.segment_duration + 1)
            
            return True
            
        except Exception as e:
            logger.error(f"erro ao iniciar gravação do buffer: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self):
        """para a gravação do buffer"""
        if not self.is_recording:
            return
            
        try:
            self.is_recording = False
            
            # aguarda a thread terminar
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5)
            
            logger.info("gravação do buffer circular encerrada")
            
        except Exception as e:
            logger.error(f"erro ao parar gravação: {e}")
    
    def save_replay(self, output_path):
        """salva os últimos N segundos do buffer como replay"""
        if not self.is_recording:
            logger.error("buffer não está gravando")
            return False
            
        if len(self.segments) == 0:
            logger.error("nenhum segmento disponível no buffer")
            return False
        
        try:
            # cria lista de arquivos de entrada para concatenação
            segment_files = []
            for segment_id in self.segments:
                segment_path = self._get_segment_path(segment_id)
                if os.path.exists(segment_path):
                    segment_files.append(segment_path)
            
            if not segment_files:
                logger.error("nenhum arquivo de segmento encontrado")
                return False
            
            # cria arquivo temporário com lista de segmentos
            concat_file = os.path.join(self.output_dir, "concat_list.txt")
            with open(concat_file, 'w') as f:
                for segment_file in segment_files:
                    f.write(f"file '{segment_file}'\n")
            
            # comando FFmpeg para concatenar segmentos
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",
                output_path
            ]
            
            logger.info(f"salvando replay: {output_path}")
            logger.debug(f"comando FFmpeg: {' '.join(ffmpeg_cmd)}")
            
            # executa a concatenação
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # remove arquivo temporário
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"replay salvo com sucesso: {output_path}")
                return True
            else:
                logger.error(f"erro ao salvar replay: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"erro ao salvar replay: {e}")
            return False
    
    def get_buffer_info(self):
        """retorna informações sobre o estado atual do buffer"""
        return {
            "is_recording": self.is_recording,
            "segments_count": len(self.segments),
            "max_segments": self.max_segments,
            "buffer_duration": self.buffer_duration,
            "segment_duration": self.segment_duration,
            "total_duration": len(self.segments) * self.segment_duration
        }
    
    def get_available_duration(self):
        """retorna a duração disponível no buffer em segundos"""
        return len(self.segments) * self.segment_duration


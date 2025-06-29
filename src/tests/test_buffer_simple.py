# teste temporário que criei (28/06/2025)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.circular_buffer import CircularVideoBuffer
import time

def test_buffer():
    """
    teste simples do buffer circular
    """
    print("🎥 Testando Buffer Circular")
    print("=" * 50)
    
    # cria buffer com câmera USB real
    buffer = CircularVideoBuffer(
        buffer_duration=10,  # 10 segundos para teste rápido
        video_source="USB CAMERA",  # Usa câmera USB real
        output_dir="test_buffer"
    )
    
    try:
        print("▶️ Iniciando gravação...")
        buffer.start_recording()
        
        # aguarda um pouco para o buffer começar a gravar
        print("⏱️ Aguardando 15 segundos para acumular conteúdo...")
        time.sleep(15)
        
        # verifica status
        status = buffer.get_status()
        print(f"📊 Status do buffer:")
        print(f"   - Gravando: {status['is_recording']}")
        print(f"   - Arquivo existe: {status['buffer_exists']}")
        print(f"   - Tamanho: {status['buffer_size'] / 1024 / 1024:.2f} MB")
        
        if status['buffer_exists'] and status['buffer_size'] > 0:
            print("✅ Buffer está funcionando!")
            
            # testa salvar replay
            test_output = os.path.join("test_buffer", "test_replay.mp4")
            print(f"💾 Salvando replay teste em: {test_output}")
            
            success = buffer.save_replay(test_output)
            if success and os.path.exists(test_output):
                size_mb = os.path.getsize(test_output) / 1024 / 1024
                print(f"✅ Replay salvo com sucesso! ({size_mb:.2f} MB)")
            else:
                print("❌ Falha ao salvar replay")
        else:
            print("❌ Buffer não está funcionando corretamente")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    finally:
        print("⏹️ Parando gravação...")
        buffer.stop_recording()
        print("🏁 Teste finalizado")

if __name__ == "__main__":
    test_buffer()

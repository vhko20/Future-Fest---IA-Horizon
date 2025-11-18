from openai import OpenAI
import os
from config import OPENAI_API_KEY, OPENAI_ORGANIZATION

# Conexão com a API da OpenAI
client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORGANIZATION
)

def gerar_audio_personalizado():
    """Gera áudio personalizado: 'Olá, [NOME], como você imagina o mundo perfeito?'"""
    
    # Pedir o nome do usuário
    nome = input("Digite o nome para personalizar o áudio: ")
    
    # Criar pasta audios se não existir
    if not os.path.exists('audios'):
        os.makedirs('audios')
    
    # Texto personalizado
    texto = f"Olá, {nome}, como você imagina o mundo perfeito?"
    
    # Gerar áudio
    resposta = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=texto
    )
    
    # Salvar arquivo com nome personalizado
    nome_arquivo = f"audios/audio_{nome.lower().replace(' ', '_')}.mp3"
    with open(nome_arquivo, 'wb') as f:
        f.write(resposta.read())
    
    print(f"Audio salvo: {nome_arquivo}")

if __name__ == "__main__":
    gerar_audio_personalizado()

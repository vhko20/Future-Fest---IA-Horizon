from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from openai import OpenAI
import os
import uuid
import base64
from urllib.parse import unquote
from config import OPENAI_API_KEY, OPENAI_ORGANIZATION

#arquivo de chaves da API arquivo config.py
client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORGANIZATION
)

app = Flask(__name__)
CORS(app)

# Rota principal - página inicial do index
@app.route("/")
def index():
    """Página inicial"""
    return send_file('index.html')

# Rota para pergunta do nome  - qual o seu nome ? 
@app.route("/pergunta_nome.html")
def pergunta_nome():
    """Página de pergunta do nome"""
    return send_file('pergunta_nome.html')

# Rota para descrição do mundo perfeito
@app.route("/mundo_perfeito.html")
def mundo_perfeito():
    """Página de descrição do mundo perfeito"""
    nome = request.args.get('nome', '')
    return send_file('mundo_perfeito.html')

# Rota para resultado final que mostra a imagem gerada
@app.route("/resultado.html")
def resultado():
    """Página de resultado final"""
    nome = request.args.get('nome', '')
    mundo_perfeito = request.args.get('mundo_perfeito', '')
    return send_file('resultado.html')

# Servir arquivos estáticos
@app.route("/imagem/<filename>")
def servir_imagem(filename):
    """Servir imagem local"""
    try:
        return send_file(f'imagens/{filename}')
    except Exception as e:
        return f"Erro ao carregar imagem: {str(e)}", 404

@app.route("/audio/<filename>")
def servir_audio(filename):
    """Servir áudio local"""
    try:
        return send_file(f'audios/{filename}')
    except Exception as e:
        return f"Erro ao carregar áudio: {str(e)}", 404
    
@app.route("/video/<filename>")
def servir_video(filename):
    try:
        return send_file(f'{filename}')
    except Exception as e:
        return f"Erro ao carregar vídeo: {str(e)}", 404

# ÁUDIO FIXO - QUAL o seu nome ? que é reproduzido na tela de pergunta nome
@app.route("/audio_pergunta")
def audio_pergunta():
    """Servir áudio fixo da pergunta do nome"""
    try:
        return send_file('audios/audio_pergunta_nome.mp3')
    except Exception as e:
        return f"Erro ao carregar áudio: {str(e)}", 404

# ÁUDIO PERSONALIZADO - que é gerado quando vc coloca teu nome, ola nome digitado como vc imagina o mundo ?
@app.route("/audio_personalizado/<nome>")
def audio_personalizado(nome):
    """Servir áudio personalizado com nome - gera automaticamente se não existir"""
    try:
        # Decodificar o nome da URL
        nome_decodificado = unquote(nome)
        
        # Criar pasta audios se não existir
        if not os.path.exists('audios'):
            os.makedirs('audios')
        
        # Criar nome do arquivo sanitizado
        nome_arquivo_sanitizado = nome_decodificado.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        nome_arquivo = f"audios/audio_{nome_arquivo_sanitizado}.mp3"
        
        # Se o arquivo não existe, gerar automaticamente
        if not os.path.exists(nome_arquivo):
            texto = f"Olá, {nome_decodificado}, como você imagina o mundo perfeito?"
            
            resposta = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=texto
            )
            
            with open(nome_arquivo, 'wb') as f:
                f.write(resposta.read())
        
        return send_file(nome_arquivo)
    except Exception as e:
        return f"Erro ao carregar áudio: {str(e)}", 404

# Listar imagens
@app.route("/imagens")
def listar_imagens():
    """Listar todas as imagens salvas"""
    try:
        imagens = []
        if os.path.exists('imagens'):
            for filename in os.listdir('imagens'):
                if filename.endswith('.png'):
                    imagens.append({
                        'nome': filename,
                        'url': f'http://127.0.0.1:5000/imagem/{filename}'
                    })
        return jsonify({'imagens': imagens})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Gerar imagem 
@app.route("/gerar", methods=["POST"])
def gerar():
    data = request.json
    nome = data.get("nome")
    mundo_perfeito = data.get("mundo_perfeito")

    if not nome:
        return jsonify({"erro": "Informe o nome"}), 400

    if not mundo_perfeito:
        return jsonify({"erro": "Informe como você imagina o mundo perfeito"}), 400

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Você é um especialista em prompts para geração de imagens. Crie prompts concisos e diretos (máximo 20 palavras) para imagens realistas. Responda APENAS com o prompt melhorado, sem explicações."},
                {"role": "user",
                 "content": f"Enriqueça este prompt de forma concisa para imagem realista: 'mundo perfeito com {mundo_perfeito}'. Adicione apenas detalhes essenciais de iluminação e realismo. Máximo 20 palavras. e não gere coisas que não poderam existir, que fuja da realidade, quando isso acontecer retire da imagem."}
            ]
        )

        prompt_enriquecido = resposta.choices[0].message.content

        # Criar pasta imagens se não existir
        if not os.path.exists('imagens'):
            os.makedirs('imagens')

        # aqui Gerar imagem
        imagem = client.images.generate(
            model="dall-e-3",
            prompt=f"Photorealistic: {prompt_enriquecido}. High quality, realistic lighting, detailed.",
            size="1024x1024",
            response_format="b64_json"
        )

        b64_imagem = imagem.data[0].b64_json
        img_bytes = base64.b64decode(b64_imagem)

        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join("imagens", filename)

        with open(filepath, "wb") as f:
            f.write(img_bytes)

        local_url = f"http://127.0.0.1:5000/imagem/{filename}"

        return jsonify({
            "nome": nome,
            "mundo_perfeito": mundo_perfeito,
            "imagem_url": local_url
        })

    except Exception as e:
        return jsonify({"erro": f"Erro ao gerar conteúdo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

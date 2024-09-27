import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import time
import cohere  # Importa o SDK da Cohere

# Inicializa o mixer do pygame
pygame.mixer.init()

# Configurações da Cohere
COHERE_API_KEY = "hNhznmkv2pHhFJkw9466LOxRJeFHmtdGcY62x6Wa"  # Substitua pela sua chave API da Cohere
LANGUAGE_CODE = "pt"  # Código de idioma para gTTS

# Inicializa o cliente da Cohere
co = cohere.Client(COHERE_API_KEY)

# Função que grava o áudio e transforma em texto
def grava_e_transforma_texto():
    r = sr.Recognizer()
    r.pause_threshold = 0.5
    r.energy_threshold = 300

    with sr.Microphone() as source:
        print("Aguardando fala...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

        try:
            texto = r.recognize_google(audio, language='pt-BR')
            print(f"Você disse: {texto}")
            return texto
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
            return None
        except sr.RequestError as e:
            print(f"Erro no serviço de reconhecimento de fala: {e}")
            return None

# Função que envia o texto para a Cohere e recebe a resposta da Nina
def envia_para_cohere(texto_usuario):
    try:
        # Prompt para definir o comportamento e personalidade da Nina
        prompt_nina = f"""
        O nome dela é Nina. Ela é uma assistente virtual dócil, gentil, e sempre responde com carinho e paciência.
        Ela é muito educada e prestativa.
        Usuário: {texto_usuario}
        Nina:"""

        response = co.generate(
            model='command-xlarge-nightly',  # Escolha o modelo apropriado
            prompt=prompt_nina,
            max_tokens=100,
            temperature=0.7,
            stop_sequences=["--"],
        )

        resposta = response.generations[0].text.strip()
        return resposta
    except Exception as e:
        print(f"Erro ao se comunicar com a Cohere: {e}")
        return "Desculpe, ocorreu um erro ao conversar com a Nina."

# Função que converte o texto em áudio usando gTTS
def converte_texto_para_audio(texto):
    tts = gTTS(texto, lang=LANGUAGE_CODE)
    arquivo_audio = "audio_temp.mp3"
    tts.save(arquivo_audio)
    return arquivo_audio

# Função que reproduz o áudio gerado
def reproduz_audio(arquivo_audio):
    print("Reproduzindo áudio...")
    pygame.mixer.music.load(arquivo_audio)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.music.unload()

# Função que apaga o arquivo de áudio temporário
def apaga_arquivo(arquivo):
    if os.path.exists(arquivo):
        os.remove(arquivo)
        print(f"Arquivo {arquivo} apagado com sucesso.")
    else:
        print(f"Arquivo {arquivo} não encontrado.")

# Loop contínuo para gravar e processar áudio
while True:
    texto = grava_e_transforma_texto()
    
    if texto:
        resposta_ia = envia_para_cohere(texto)
        print(f"Resposta da Nina: {resposta_ia}")
        
        arquivo_audio = converte_texto_para_audio(resposta_ia)
        reproduz_audio(arquivo_audio)
        
        time.sleep(1)
        apaga_arquivo(arquivo_audio)

        if not os.path.exists(arquivo_audio):
            print("Pronto para a próxima gravação.")
        else:
            print("Erro: o arquivo ainda existe.")
    
    time.sleep(3)

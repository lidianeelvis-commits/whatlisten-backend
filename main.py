from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Configuração de CORS para permitir que a Vercel acesse o Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search_youtube(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Termo de busca vazio.")
    
    # Configura o yt-dlp para buscar apenas os 5 primeiros resultados sem baixar
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True, # Não baixa o vídeo, apenas extrai os metadados rápidos
    }
    
    try:
        # Usa o prefixo ytsearch5: para trazer 5 resultados do YouTube
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            entries = info.get('entries', [])
            
            resultados = []
            for entry in entries:
                if entry:
                    resultados.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'author': entry.get('uploader', 'Canal Desconhecido')
                    })
            return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
async def download_audio(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="ID da música obrigatória.")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '-',
        'logtostderr': True,
        'noplaylist': True,
        'quiet': True
    }
    
    try:
        url = f"https://www.youtube.com/watch?v={id}"
        def stream_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        return StreamingResponse(stream_audio(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

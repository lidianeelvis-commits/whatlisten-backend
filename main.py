from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# Permissões de CORS totalmente liberadas para evitar bloqueios na Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/search")
async def search_youtube(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Termo de busca vazio.")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{q}", download=False)
            entries = info.get('entries', [])
            
            resultados = []
            for entry in entries:
                if entry:
                    resultados.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'author': entry.get('uploader', 'Canal YouTube')
                    })
            return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
async def download_audio(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="ID obrigatória.")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }
    
    try:
        url = f"https://www.youtube.com/watch?v={id}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url')
            if not stream_url:
                raise HTTPException(status_code=404, detail="Stream não encontrada.")
            return RedirectResponse(url=stream_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

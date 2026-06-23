from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

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
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
        # Adiciona cabeçalhos comuns para evitar blocos automáticos na busca
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
        raise HTTPException(status_code=400, detail="ID da música obrigatória.")
    
    # OPÇÃO ULTRA-ESTÁVEL: Extrai a URL direta do fluxo de áudio do YouTube 
    # e faz o navegador do usuário buscar direto dos servidores do Google, contornando o erro 500 do Render.
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        url = f"https://www.youtube.com/watch?v={id}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Pegamos o link direto do servidor de streaming do YouTube
            stream_url = info.get('url')
            
            if not stream_url:
                raise HTTPException(status_code=404, detail="Não foi possível extrair a stream de áudio.")
            
            # Redireciona o player de áudio direto para a fonte oficial que funciona!
            return RedirectResponse(url=stream_url)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

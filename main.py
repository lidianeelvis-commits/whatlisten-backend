from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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

@app.get("/download")
async def download_audio(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="ID do vídeo é obrigatória.")
    
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
                info = ydl.extract_info(url, download=False)
                # Retorna os dados diretamente do processo de download do yt-dlp
                ydl.download([url])
                
        return StreamingResponse(stream_audio(), media_type="audio/mpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

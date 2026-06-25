# app.py
import os
import asyncio
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

from mail_account import creer_mail, attendre_verification
from eset_account import creer_compte_eset

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Le bot est en ligne. Utilisez /generate pour lancer une clé."}

@app.get("/generate")
async def generate_key():
    try:
        async with async_playwright() as playwright:
            browser_mail, page_mail, email = await creer_mail(playwright)
            
            taches = await asyncio.gather(
                creer_compte_eset(playwright, email),
                attendre_verification(page_mail),
                return_exceptions=True
            )

            await browser_mail.close()
            
            cle = taches[0]
            if isinstance(cle, Exception):
                raise cle
                
            return {"email": email, "cle": cle}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Récupère le port attribué par Render dynamiquement
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
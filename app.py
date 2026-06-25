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
            # 1. Connexion unique à Browserless
            token = os.environ.get("BROWSERLESS_TOKEN", "2UlhDbObUX6gvHZc97b815c9c73ee1cb06b7260c79d8557b7")
            endpoint_url = f"wss://production-sfo.browserless.io/chromium?token={token}"
            
            print("[Workflow] Connexion unique au navigateur distant...")
            browser = await playwright.chromium.connect(endpoint_url)
            context = await browser.new_context()

            # 2. Étape Mail : On ouvre un onglet pour le mailer
            page_mail = await context.new_page()
            email = await creer_mail(page_mail)
            print(f"[Workflow] E-mail généré : {email}")
            
            # 3. Étape ESET : On ouvre un deuxième onglet dans le même navigateur
            page_eset = await context.new_page()
            print("[Workflow] Inscription sur ESET en cours...")
            cle_licence = await creer_compte_eset(page_eset, email)
            
            # 4. Attente du mail de validation sur le premier onglet
            print("[Workflow] Inscription soumise. Attente du mail de confirmation...")
            verification_reussie = await attendre_verification(page_mail)
            
            # Fermeture propre de la session
            await browser.close()
            
            if not verification_reussie:
                raise Exception("La vérification de l'e-mail a échoué ou a expiré.")
                
            return {
                "status": "success",
                "email": email,
                "cle": cle_licence
            }
            
    except Exception as e:
        print(f"[ERREUR SCRIPT] -> {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
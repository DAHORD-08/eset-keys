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
            # ÉTAPE 1 : On génère d'abord l'e-mail temporaire
            print("[Workflow] Génération de l'e-mail temporaire...")
            browser_mail, page_mail, email = await creer_mail(playwright)
            print(f"[Workflow] E-mail généré : {email}")
            
            # ÉTAPE 2 : On lance la création ESET de manière SÉQUENTIELLE (pas de gather)
            # Cette fonction va remplir les champs, cliquer sur s'inscrire et s'arrêter au moment où elle attend le mail
            print("[Workflow] Inscription sur ESET en cours...")
            cle_licence = await creer_compte_eset(playwright, email)
            
            # ÉTAPE 3 : Maintenant que le formulaire ESET est soumis, l'email a été envoyé.
            # On peut lancer l'attente de vérification sur notre page de mail
            print("[Workflow] Inscription soumise. Attente du mail de confirmation...")
            verification_reussie = await attendre_verification(page_mail)
            
            # Fermeture propre du navigateur de mail
            await browser_mail.close()
            
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
# api/index.py
import os
import sys
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright
import asyncio

# Ajoute le dossier racine au chemin de recherche Python pour trouver vos scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importations de vos modules modifiés pour le cloud
from mail_account import creer_mail, attendre_verification
from eset_account import creer_compte_eset  # Utilise la version cloud eset_account

app = FastAPI()

# (Le reste du code de votre fichier index.py reste identique)

async def generer_cle_workflow(playwright):
    browser_mail, page_mail, email = await creer_mail(playwright)
    
    # Exécution du flow
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

@app.get("/api/generate")
async def generate_key():
    try:
        async with async_playwright() as playwright:
            resultat = await generer_cle_workflow(playwright)
            return resultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
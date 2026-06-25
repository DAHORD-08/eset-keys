# app.py
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

MOT_DE_PASSE = "singe@JUNGLE369"

# Variables globales pour maintenir l'état de la connexion unique
playwright_instance = None
browser_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le cycle de vie de l'application : la connexion au navigateur distant
    est établie une seule fois au démarrage et coupée proprement à l'arrêt.
    """
    global playwright_instance, browser_instance
    print("[Lifespan] Initialisation de Playwright et connexion à Browserless...")
    
    token = os.environ.get("BROWSERLESS_TOKEN", "2UlhDbObUX6gvHZc97b815c9c73ee1cb06b7260c79d8557b7")
    endpoint_url = f"wss://production-sfo.browserless.io/chromium?token={token}"
    
    playwright_instance = await async_playwright().start()
    browser_instance = await playwright_instance.chromium.connect(endpoint_url)
    print("[Lifespan] Connexion WebSocket établie avec succès.")
    
    yield
    
    print("[Lifespan] Fermeture des connexions...")
    if browser_instance:
        await browser_instance.close()
    if playwright_instance:
        await playwright_instance.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"status": "Le bot est en ligne. Utilisez /generate pour lancer une clé."}

@app.get("/generate")
async def generate_key():
    global browser_instance
    if not browser_instance:
        raise HTTPException(status_code=500, detail="Le navigateur distant n'est pas initialisé.")
        
    context = None
    try:
        # Création d'un contexte isolé pour cette requête spécifique
        context = await browser_instance.new_context()
        page = await context.new_page()

        # --- ÉTAPE 1 : RÉCUPÉRATION DU MAIL ---
        print("[Workflow] 1/4 - Récupération de l'e-mail temporaire...")
        await page.goto("https://dahord-08.github.io/DAHORD-Mailer/")
        await page.wait_for_load_state("networkidle")
        
        champ_affichage_mail = page.locator('input#email-display')
        await champ_affichage_mail.wait_for(state="visible", timeout=15000)
        email = await champ_affichage_mail.input_value()
        nom = email.split("@")[0]
        print(f"[Workflow] E-mail récupéré : {email}")

        # --- ÉTAPE 2 : INSCRIPTION ESET ---
        print("[Workflow] 2/4 - Navigation vers ESET...")
        await page.goto("https://login.eset.com/register")
        await page.wait_for_load_state("networkidle")

        print("[Workflow] Acceptation des cookies...")
        bouton_cookies = page.locator('button#cc-accept')
        await bouton_cookies.wait_for(state="visible", timeout=10000)
        await bouton_cookies.click()

        print("[Workflow] Remplissage du formulaire d'inscription...")
        await page.locator('input#email').fill(email)
        await page.locator('input#password').fill(MOT_DE_PASSE)

        print("[Workflow] Soumission du formulaire...")
        await page.click('[data-label="register-create-account-button"][type=\"submit\"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)

        if "login.eset.com/login" in page.url:
            print("[Workflow] Redirection détectée, connexion en cours...")
            await page.locator('[data-label="browser-email-input-input"]').fill(email)
            await page.locator('[data-label="browser-password-input-input"]').fill(MOT_DE_PASSE)
            await page.click('[data-label="browser-log-in-button"]')
            await page.wait_for_load_state("networkidle")

        # --- ÉTAPE 3 : VÉRIFICATION DU MAIL ---
        print("[Workflow] 3/4 - Retour sur le mailer pour validation...")
        await page.goto("https://dahord-08.github.io/DAHORD-Mailer/")
        await page.wait_for_load_state("networkidle")

        print("[Workflow] Attente de l'indicateur de mail reçu...")
        indicateur_mail = page.locator('[data-label="mail-indice-for-bot-use"]')
        await indicateur_mail.wait_for(state="visible", timeout=120000)
        await indicateur_mail.click()
        await asyncio.sleep(4)

        print("[Workflow] Recherche du lien de confirmation dans l'iFrame...")
        lien_clique = False
        for frame in page.frames:
            lien = await frame.query_selector('a.clickable-blue-button')
            if lien:
                await lien.click()
                print("[Workflow] Lien de vérification cliqué !")
                lien_clique = True
                break
        
        if not lien_clique:
            raise Exception("Impossible de trouver ou de cliquer sur le lien de validation dans le mail.")

        await asyncio.sleep(5)

        # --- ÉTAPE 4 : CONNEXION ESET ET RÉCUPÉRATION DE LA CLÉ ---
        print("[Workflow] 4/4 - Retour sur ESET pour l'onboarding et la clé...")
        await page.goto("https://login.eset.com/")
        await page.wait_for_load_state("networkidle")

        await page.locator('[data-label="browser-email-input-input"]').fill(email)
        await page.locator('[data-label="browser-password-input-input"]').fill(MOT_DE_PASSE)
        await page.click('[data-label="browser-log-in-button"]')
        await page.wait_for_load_state("networkidle")

        bouton_onboarding = page.locator('[data-label="onboarding-welcome-skip-introduction-btn"][type="button"]')
        await bouton_onboarding.wait_for(state="visible", timeout=30000)
        await bouton_onboarding.click()
        await page.wait_for_load_state("networkidle")

        await page.locator('[data-label="onboarding-add-subscription-protect-card-trial"]').click()
        await asyncio.sleep(1)
        await page.click('button.css-wfkctl[type="button"]')
        await page.wait_for_load_state("networkidle")

        await page.locator('[data-label="onboarding-trial-protect-card-148"]').click()
        await asyncio.sleep(1)
        await page.click('button.css-wfkctl[type="button"]')
        await page.wait_for_load_state("networkidle")

        await page.click('button.css-wfkctl[type="button"]')
        await page.wait_for_load_state("networkidle")
        await page.locator('input#name').fill(nom)
        await page.click('[data-label="onboarding-members-continue-btn"]')
        await asyncio.sleep(1)
        await page.click('button.css-wfkctl[type="button"]')
        await page.wait_for_load_state("networkidle")

        await page.locator('[data-label="onboarding-members-me-option"]').click()
        await asyncio.sleep(1)
        await page.click('button.css-wfkctl[type="button"]')
        await page.wait_for_load_state("networkidle")

        await page.locator('button.css-93cvbk[type="button"]').click()
        
        await page.locator('[data-label="dashboard-subscriptions-card-button"]').click()
        await page.wait_for_load_state("networkidle")
        
        await page.locator('[data-label="license-list-open-detail-page-btn"]').click()
        await page.wait_for_load_state("networkidle")

        cle_element = await page.wait_for_selector('[data-label="license-detail-license-key"]', timeout=20000)
        cle = await cle_element.text_content()

        await context.close()
        return {"status": "success", "email": email, "cle": cle.strip()}
        
    except Exception as e:
        print(f"[ERREUR] -> {str(e)}")
        if context:
            await context.close()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# mail_account.py
import asyncio
from playwright.async_api import Page

async def creer_mail(page: Page) -> str:
    print("[Mail] Ouverture de la page mail temporaire...")
    await page.goto("https://dahord-08.github.io/DAHORD-Mailer/")
    await page.wait_for_load_state("networkidle")

    # Remplacement par un Locator et une attente explicite de visibilité
    champ_affichage_mail = page.locator('input#email-display')
    await champ_affichage_mail.wait_for(state="visible", timeout=10000)
    mail = await champ_affichage_mail.input_value()

    print(f"[Mail] Adresse générée : {mail}")
    return mail

async def attendre_verification(page: Page) -> bool:
    print("[Mail] En attente de l'email de vérification...")
    try:
        indicateur_mail = page.locator('[data-label="mail-indice-for-bot-use"]')
        # Attente robuste de la réception du mail
        await indicateur_mail.wait_for(state="visible", timeout=300000)
        print("[Mail] Email de vérification reçu !")
        
        await indicateur_mail.click()
        await asyncio.sleep(3) # Laisse le temps au contenu de l'iFrame de se charger

        for frame in page.frames:
            lien = await frame.query_selector('a.clickable-blue-button')
            if lien:
                await lien.click()
                print("[Mail] Lien de vérification cliqué avec succès.")
                return True
        
        print("[Mail] Bouton de confirmation introuvable dans les frames.")
    except Exception as e:
        print(f"[Erreur Mail] {e}")
    return False
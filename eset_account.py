import os
import asyncio
from playwright.async_api import async_playwright

MOT_DE_PASSE = "singe@JUNGLE369"

async def creer_compte_eset(playwright, email: str):
    nom = email.split("@")[0]

    # Connexion au navigateur distant (Browserless) pour contourner les limites de Vercel
    # BROWSERLESS_TOKEN sera configuré dans l'interface de Vercel
    token = os.environ.get("BROWSERLESS_TOKEN", "2UlhDbObUX6gvHZc97b815c9c73ee1cb06b7260c79d8557b7")
    endpoint_url = f"wss://production-sfo.browserless.io/chromium/playwright?token={token}"
    
    print("[ESET] Connexion au navigateur distant...")
    browser = await playwright.chromium.connect_over_cdp(endpoint_url)
    
    # Le reste de votre code reste identique
    context = await browser.new_context()
    page = await context.new_page()
    
    # ... (Conservez votre logique fonctionnelle ici)

    print(f"\n[ESET] Ouverture de la page d'inscription pour : {email}")
    await page.goto("https://login.eset.com/register")
    await page.wait_for_load_state("networkidle")

    # --- Acceptation des cookies ---
    print("[1.5/10] Acceptation des cookies...")
    bouton_cookies = page.locator('button#cc-accept')
    await bouton_cookies.wait_for(state="visible", timeout=10000)
    await bouton_cookies.click()

    # --- Remplissage simultané (Formulaire classique) ---
    print("[2/10] Remplissage de l'email et du mot de passe...")
    
    # Saisie de l'email
    champ_email = page.locator('input#email')
    await champ_email.wait_for(state="visible", timeout=15000)
    await champ_email.fill(email)
    
    # Saisie immédiate du mot de passe
    champ_password = page.locator('input#password')
    await champ_password.wait_for(state="visible", timeout=15000)
    await champ_password.fill(MOT_DE_PASSE)

    print("[3/10] Clic sur le bouton de soumission...")
    # Remplacez le sélecteur ci-dessous par le bon bouton de validation finale
    await page.click('[data-label="register-create-account-button"][type="submit"]')
    await page.wait_for_load_state("networkidle")

    await asyncio.sleep(5)

    # --- Cas : redirigé vers /login au lieu de l'onboarding ---
    if "login.eset.com/login" in page.url:
        print("[!] Redirigé vers la page de connexion, on se connecte...")
        
        champ_login_email = page.locator('[data-label="browser-email-input-input"]')
        await champ_login_email.wait_for(state="visible")
        await champ_login_email.fill(email)
        
        champ_login_pass = page.locator('[data-label="browser-password-input-input"]')
        await champ_login_pass.wait_for(state="visible")
        await champ_login_pass.fill(MOT_DE_PASSE)
        
        await page.click('[data-label="browser-log-in-button"]')
        await page.wait_for_load_state("networkidle")
        print("[!] Connexion effectuée, reprise du flow...")

    # --- Attente de la vérification email ---
    print("[4/10] En attente de vérification email par le client...")
    bouton_onboarding = page.locator('[data-label="onboarding-welcome-skip-introduction-btn"][type="button"]')
    
    # Attente explicite que l'état de la page change après validation du mail
    await bouton_onboarding.wait_for(state="visible", timeout=300000)
    print("       Email vérifié ! On continue...")
    await bouton_onboarding.click()
    await page.wait_for_load_state("networkidle")

    # --- Sélection de l'option "Trial" ---
    print("[5/10] Sélection du mode essai gratuit...")
    carte_trial = page.locator('[data-label="onboarding-add-subscription-protect-card-trial"]')
    await carte_trial.wait_for(state="visible")
    await carte_trial.click()
    
    await asyncio.sleep(1)
    await page.click('button.css-wfkctl[type="button"]')
    await page.wait_for_load_state("networkidle")

    # --- Sélection du produit (id 148) ---
    print("[6/10] Sélection du produit...")
    carte_produit = page.locator('[data-label="onboarding-trial-protect-card-148"]')
    await carte_produit.wait_for(state="visible")
    await carte_produit.click()
    
    await asyncio.sleep(1)
    await page.click('button.css-wfkctl[type="button"]')
    await page.wait_for_load_state("networkidle")

    # --- Première étape suivante + saisie du nom ---
    print("[7/10] Saisie du nom du client...")
    await page.click('button.css-wfkctl[type="button"]')
    await page.wait_for_load_state("networkidle")
    
    champ_nom = page.locator('input#name')
    await champ_nom.wait_for(state="visible")
    await champ_nom.fill(nom)
    
    bouton_membres = page.locator('[data-label="onboarding-members-continue-btn"]')
    await bouton_membres.click()
    
    await asyncio.sleep(1)
    await page.click('button.css-wfkctl[type="button"]')
    await page.wait_for_load_state("networkidle")

    # --- Étape continuer + sélection soi-même ---
    print("[8/10] Sélection de l'option finale...")
    option_me = page.locator('[data-label="onboarding-members-me-option"]')
    await option_me.wait_for(state="visible")
    await option_me.click()
    
    await asyncio.sleep(1)
    await page.click('button.css-wfkctl[type="button"]')
    await page.wait_for_load_state("networkidle")

    # --- Bouton de confirmation ---
    print("[9/10] Confirmation...")
    bouton_confirmer = page.locator('button.css-93cvbk[type="button"]')
    await bouton_confirmer.wait_for(state="visible")
    await bouton_confirmer.click()

    # --- Accès au tableau de bord et récupération de l'abonnement ---
    bouton_dashboard = page.locator('[data-label="dashboard-subscriptions-card-button"]')
    await bouton_dashboard.wait_for(state="visible")
    await bouton_dashboard.click()
    
    await page.wait_for_load_state("networkidle")
    
    bouton_details = page.locator('[data-label="license-list-open-detail-page-btn"]')
    await bouton_details.wait_for(state="visible")
    await bouton_details.click()
    
    await page.wait_for_load_state("networkidle")

    # --- Récupération de la clé ---
    print("[10/10] Récupération de la clé de licence...")
    cle_element = await page.wait_for_selector(
        '[data-label="license-detail-license-key"]',
        timeout=15000
    )
    cle = await cle_element.text_content()

    await browser.close()
    return cle.strip()
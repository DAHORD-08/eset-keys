import asyncio
from playwright.async_api import async_playwright
from mail_account import creer_mail, attendre_verification
from eset_account import creer_compte_eset


async def generer_une_cle(playwright, numero: int, total: int) -> tuple[str, str]:
    print(f"\n{'='*40}")
    print(f"  CLÉ {numero}/{total}")
    print(f"{'='*40}")

    browser_mail, page_mail, email = await creer_mail(playwright)
    print(f">>> Email : {email}")

    taches = await asyncio.gather(
        creer_compte_eset(playwright, email),
        attendre_verification(page_mail),
        return_exceptions=True
    )

    await browser_mail.close()

    cle = taches[0]
    if isinstance(cle, Exception):
        print(f"[Erreur clé {numero}] {cle}")
        cle = "ÉCHEC"

    return email, cle


async def main():
    nb = int(input("Combien de clés voulez-vous générer ? ").strip())
    resultats = []

    async with async_playwright() as playwright:
        for i in range(1, nb + 1):
            email, cle = await generer_une_cle(playwright, i, nb)
            resultats.append((email, cle))

            if i < nb:
                print(f"\n[Système] Pause 5s avant la clé suivante...")
                await asyncio.sleep(5)

    print(f"\n\n{'='*40}")
    print(f"  RÉSUMÉ — {nb} CLÉ(S) GÉNÉRÉE(S)")
    print(f"{'='*40}")
    for i, (email, cle) in enumerate(resultats, 1):
        print(f"  [{i}] {email}")
        print(f"       → {cle}")
    print(f"{'='*40}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Système] Interruption par l'utilisateur.")
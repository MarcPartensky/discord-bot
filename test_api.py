#!/usr/bin/env python
"""Tests pour l'API HTTP du bot Discord."""

import requests
import time
import sys

API_BASE = "http://localhost:8050"

def test_server_running():
    """Vérifie que le serveur répond."""
    try:
        response = requests.get(f"{API_BASE}/live", timeout=5)
        print(f"✓ Serveur actif - Status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Serveur non accessible")
        return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_send_channel():
    """Test d'envoi de message dans un channel."""
    data = {
        "id": 1548552725808283748,  # CHANNEL_ID_NOTIF
        "message": "Test API - Message de test automatique"
    }
    try:
        response = requests.post(f"{API_BASE}/send/channel", json=data, timeout=5)
        if response.status_code == 200:
            print(f"✓ send/channel - {response.json()}")
            return True
        else:
            print(f"✗ send/channel - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ send/channel - Erreur: {e}")
        return False

def test_debug_bot():
    """Test de l'endpoint debug."""
    try:
        response = requests.get(f"{API_BASE}/debug/bot", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ debug/bot - Bot ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"✗ debug/bot - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ debug/bot - Erreur: {e}")
        return False

def main():
    """Lance tous les tests."""
    print("=" * 50)
    print("Tests API Discord Bot")
    print("=" * 50)

    tests = [
        ("Serveur actif", test_server_running),
        ("Debug bot", test_debug_bot),
        ("Send channel", test_send_channel),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        result = test_func()
        results.append((name, result))
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Résumé:")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print(f"\nRésultat: {passed}/{total} tests réussis")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

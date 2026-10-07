"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - SUITE DE PRUEBAS AUTOMATIZADAS
=============================================================================
Validación integral de:
1. Enrutador Omni-IA y detección de contextos
2. Captura y percepción de pantalla en tiempo real
3. Motor Meta-Creador de Apps (construcción y servidor HTTP local)
4. Memoria Semántica Vectorial y Perfil de Edwin
5. Mecánica vehicular y Finanzas con exportación a Excel
6. Validación sintáctica AST de auto-reparación y evolución
=============================================================================
"""

import os
import sys
import time
import unittest
import urllib.request
from pathlib import Path

# Añadir ruta raíz al path para importar módulos
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import config
from modules.omni_ai_router import omni_router, AIContext
from modules.live_screen_vision import screen_vision
from modules.app_builder_engine import app_builder
from modules.vector_memory import vector_memory
from modules.mechanics_tracker import mechanics_tracker
from modules.finance_manager import finance_manager
from modules.self_evolution import evolution_engine
from modules.self_healing import self_healer
from modules.device_telemetry import device_telemetry


class TestOmniSupreme(unittest.TestCase):

    def test_01_omni_router_context_detection(self):
        """Verifica la correcta clasificación de intenciones en el Enrutador Multi-IA."""
        ctx_code = omni_router.detect_context("Escribe una función en Python para ordenar una lista")
        self.assertEqual(ctx_code, AIContext.CODE)

        ctx_voice = omni_router.detect_context("Dime rápido la respuesta con voz")
        self.assertEqual(ctx_voice, AIContext.FAST_VOICE)

        ctx_web = omni_router.detect_context("Investiga las noticias de hoy en internet")
        self.assertEqual(ctx_web, AIContext.WEB_SEARCH)

    def test_02_omni_router_harmonization(self):
        """Verifica que el armonizador adapte la voz para Edwin."""
        raw = "El sistema está configurado."
        harmonized = omni_router.harmonize_response(raw)
        self.assertIn(config.USER_TITLE, harmonized)

    def test_03_screen_vision_capture(self):
        """Verifica que la percepción de pantalla capture un fotograma válido."""
        frame_path = screen_vision.capture_frame()
        self.assertIsNotNone(frame_path)
        self.assertTrue(frame_path.exists())
        self.assertGreater(frame_path.stat().st_size, 100)

        app_name = screen_vision.detect_active_application()
        self.assertIsInstance(app_name, str)

    def test_04_app_builder_and_local_server(self):
        """Valida la creación completa de una aplicación y su respuesta HTTP 200 en localhost."""
        app_name = "Cyber Test Suite"
        app_desc = "Aplicación de prueba generada automáticamente por tests"
        result = app_builder.build_application(app_name, app_desc, auto_launch=False)

        self.assertTrue(result["success"])
        slug = result["slug"]
        app_dir = config.APPS_DIR / slug

        self.assertTrue((app_dir / "index.html").exists())
        self.assertTrue((app_dir / "style.css").exists())
        self.assertTrue((app_dir / "app.js").exists())
        self.assertTrue((app_dir / "manifest.json").exists())

        # Probar que el servidor web local responde HTTP 200
        port = app_builder.active_port
        test_url = f"http://127.0.0.1:{port}/{slug}/index.html"
        try:
            req = urllib.request.Request(test_url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.assertEqual(resp.status, 200)
                content = resp.read().decode("utf-8")
                self.assertIn("Cyber Test Suite", content)
        except Exception as e:
            self.fail(f"El servidor HTTP local en {test_url} falló: {e}")

    def test_05_vector_memory_and_profile(self):
        """Verifica la persistencia de datos de perfil y la búsqueda de similitud coseno."""
        vector_memory.set_profile_fact("hobby_favorito", "Robótica de vanguardia")
        fact = vector_memory.get_profile_fact("hobby_favorito")
        self.assertEqual(fact, "Robótica de vanguardia")

        # Almacenar memoria y buscar similitud
        mem_id = vector_memory.store_memory("A Edwin le encanta montar en moto los fines de semana", category="vehiculos")
        self.assertGreater(mem_id, 0)

        similar = vector_memory.search_similar("moto de fin de semana", top_k=2)
        self.assertGreater(len(similar), 0)
        self.assertIn("moto", similar[0]["content"].lower())

    def test_06_mechanics_and_finance(self):
        """Valida el cálculo preventivo mecánico y la exportación de finanzas a Excel."""
        # Mecánica
        rep = mechanics_tracker.get_vehicle_report("EDW-001")
        self.assertIn("diagnostics", rep)
        self.assertEqual(rep["plate"], "EDW-001")

        # Finanzas
        parsed = finance_manager.parse_natural_language_expense("Gasté 45 mil pesos en gasolina")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["amount"], 45000.0)
        self.assertIn("Combustible", parsed["category"])

        # Registro y Exportación
        finance_manager.add_expense(45000.0, "Transporte", "Prueba de combustible")
        excel_path = finance_manager.export_to_excel()
        self.assertTrue(excel_path.exists())
        self.assertGreater(excel_path.stat().st_size, 200)

    def test_07_self_evolution_safety_check(self):
        """Valida que el motor de auto-programación rechace código inválido o peligroso."""
        valid_code = "x = 42\ndef test(): return x"
        is_safe, _ = evolution_engine.validate_code_safety(valid_code)
        self.assertTrue(is_safe)

        invalid_code = "def syntax_error(:"
        is_safe_inv, err_msg = evolution_engine.validate_code_safety(invalid_code)
        self.assertFalse(is_safe_inv)
        self.assertIn("sintaxis", err_msg.lower())

    def test_08_device_telemetry(self):
        """Verifica la recolección de métricas de telemetría."""
        metrics = device_telemetry.get_metrics()
        self.assertIn("battery", metrics)
        self.assertIn("memory", metrics)
        self.assertIn("storage", metrics)
        summary = device_telemetry.format_hud_summary()
        self.assertIn("BATERÍA", summary)


if __name__ == "__main__":
    unittest.main()

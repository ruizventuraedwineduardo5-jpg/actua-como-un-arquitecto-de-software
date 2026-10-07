"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - RASTREADOR DE MECÁNICA Y MANTENIMIENTO DE VEHÍCULOS
=============================================================================
Gestión integral de kilometraje, servicios, repuestos y alertas preventivas
para motocicletas y automóviles de Edwin (aceite, cadena, frenos, filtros).
=============================================================================
"""

import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

import config


class MechanicsTracker:
    """
    Sistema de telemetría y mantenimiento vehicular basado en SQLite.
    """

    SERVICE_INTERVALS = {
        "cambio_aceite": {"km": 3000, "label": "Cambio de Aceite de Motor"},
        "mantenimiento_cadena": {"km": 1000, "label": "Limpieza y Lubricación de Cadena"},
        "filtro_aire": {"km": 6000, "label": "Filtro de Aire"},
        "pastillas_freno": {"km": 10000, "label": "Pastillas de Freno"},
        "bujia": {"km": 12000, "label": "Bujía de Encendido"},
        "liquido_frenos": {"km": 15000, "label": "Líquido de Frenos"},
    }

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self._init_db()
        self._seed_default_vehicle()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    plate TEXT UNIQUE NOT NULL,
                    vehicle_type TEXT DEFAULT 'moto',
                    current_km INTEGER NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS maintenance_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id INTEGER NOT NULL,
                    service_type TEXT NOT NULL,
                    km_at_service INTEGER NOT NULL,
                    cost REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at REAL NOT NULL,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
                )
            """)
            conn.commit()

    def _seed_default_vehicle(self):
        """Asegura la existencia de la moto principal de Edwin."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM vehicles LIMIT 1")
            if not c.fetchone():
                c.execute("""
                    INSERT INTO vehicles (name, plate, vehicle_type, current_km, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (f"Moto Principal de {config.USER_NAME}", "EDW-001", "moto", 14500, time.time()))
                # Log inicial de cambio de aceite
                c.execute("""
                    INSERT INTO maintenance_logs (vehicle_id, service_type, km_at_service, cost, notes, created_at)
                    VALUES (1, 'cambio_aceite', 13500, 45000.0, 'Aceite 10W-40 Full Sintético', ?)
                """, (time.time(),))
                conn.commit()

    # -------------------------------------------------------------------------
    # GESTIÓN DE KILOMETRAJE Y VEHÍCULOS
    # -------------------------------------------------------------------------
    def update_mileage(self, plate: str, new_km: int) -> Dict[str, Any]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("UPDATE vehicles SET current_km = ?, updated_at = ? WHERE plate = ?", (new_km, time.time(), plate.upper()))
            conn.commit()
        return self.get_vehicle_report(plate)

    def log_service(self, plate: str, service_type: str, km: int, cost: float = 0.0, notes: str = "") -> bool:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM vehicles WHERE plate = ?", (plate.upper(),))
            row = c.fetchone()
            if not row:
                return False
            vehicle_id = row["id"]
            c.execute("""
                INSERT INTO maintenance_logs (vehicle_id, service_type, km_at_service, cost, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (vehicle_id, service_type, km, cost, notes, time.time()))
            # Actualizar kilometraje si el reportado es mayor
            c.execute("UPDATE vehicles SET current_km = MAX(current_km, ?), updated_at = ? WHERE id = ?", (km, time.time(), vehicle_id))
            conn.commit()
            return True

    # -------------------------------------------------------------------------
    # REPORTE PREVENTIVO Y ALERTAS DE MANTENIMIENTO
    # -------------------------------------------------------------------------
    def get_vehicle_report(self, plate: Optional[str] = None) -> Dict[str, Any]:
        with self._get_conn() as conn:
            c = conn.cursor()
            if plate:
                c.execute("SELECT * FROM vehicles WHERE plate = ?", (plate.upper(),))
            else:
                c.execute("SELECT * FROM vehicles LIMIT 1")
            v_row = c.fetchone()
            if not v_row:
                return {"error": "No se encontraron vehículos registrados"}

            v_id = v_row["id"]
            current_km = v_row["current_km"]

            # Obtener último mantenimiento por cada tipo
            diagnostics = []
            for s_key, s_data in self.SERVICE_INTERVALS.items():
                c.execute("""
                    SELECT km_at_service FROM maintenance_logs
                    WHERE vehicle_id = ? AND service_type = ?
                    ORDER BY km_at_service DESC LIMIT 1
                """, (v_id, s_key))
                last_log = c.fetchone()
                last_km = last_log["km_at_service"] if last_log else 0
                km_elapsed = current_km - last_km
                km_remaining = s_data["km"] - km_elapsed

                status = "ÓPTIMO"
                if km_remaining <= 0:
                    status = "¡VENCIDO / URGENTE!"
                elif km_remaining < 400:
                    status = "PRÓXIMO A VENCER"

                diagnostics.append({
                    "service": s_data["label"],
                    "interval_km": s_data["km"],
                    "km_since_last": km_elapsed,
                    "km_remaining": km_remaining,
                    "status": status,
                })

            return {
                "vehicle": v_row["name"],
                "plate": v_row["plate"],
                "current_km": current_km,
                "diagnostics": diagnostics,
            }

    def format_report_speech(self, plate: Optional[str] = None) -> str:
        """Sintetiza el estado mecánico en lenguaje natural para la voz de Jarvis."""
        rep = self.get_vehicle_report(plate)
        if "error" in rep:
            return f"{config.USER_TITLE}, no tengo registros vehiculares activos."

        lines = [f"{config.USER_TITLE}, informe técnico de su vehículo {rep['vehicle']} (Placa: {rep['plate']}):"]
        lines.append(f"Kilometraje actual: {rep['current_km']:,} km.")

        urgent = [d for d in rep["diagnostics"] if "URGENTE" in d["status"] or "PRÓXIMO" in d["status"]]
        if urgent:
            lines.append("Alertas de atención inmediata:")
            for u in urgent:
                lines.append(f"• {u['service']}: Restan {u['km_remaining']} km ({u['status']}).")
        else:
            lines.append("Todos los sistemas mecánicos se encuentran dentro de sus rangos óptimos de operación.")

        return "\n".join(lines)


# Instancia singleton predeterminada
mechanics_tracker = MechanicsTracker()

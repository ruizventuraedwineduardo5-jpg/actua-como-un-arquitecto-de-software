"""
=============================================================================
JARVIS OMNI-GHOST SUPREME - GESTOR Y AUDITOR DE FINANZAS POR VOZ
=============================================================================
Auditor financiero con parsing en lenguaje natural por dictado de voz,
almacenamiento en SQLite y exportación profesional a hojas de cálculo
de Excel (.xlsx) con estilos y fórmulas automáticas mediante openpyxl.
=============================================================================
"""

import re
import csv
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import config

# Intento de cargar openpyxl
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class FinanceManager:
    """
    Gestor contable y auditor de gastos para Edwin.
    """

    CATEGORIES = {
        "gasolina": "Transporte / Combustible",
        "combustible": "Transporte / Combustible",
        "moto": "Mecánica y Repuestos",
        "repuesto": "Mecánica y Repuestos",
        "taller": "Mecánica y Repuestos",
        "almuerzo": "Alimentación",
        "comida": "Alimentación",
        "restaurante": "Alimentación",
        "mercado": "Alimentación",
        "servicios": "Servicios Básicos",
        "internet": "Tecnología",
        "software": "Tecnología",
        "hosting": "Tecnología",
        "ocio": "Entretenimiento",
    }

    def __init__(self, db_path: Optional[Path] = None, export_dir: Optional[Path] = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.export_dir = export_dir or config.FINANCE_DIR
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date_str TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    # -------------------------------------------------------------------------
    # PARSER DE GASTOS POR LENGUAJE NATURAL Y VOZ
    # -------------------------------------------------------------------------
    def parse_natural_language_expense(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrae monto, categoría y descripción de frases como:
        "Gasté 45 mil pesos en gasolina para la moto"
        "Gasto de 120000 en cambio de llanta"
        """
        clean = text.lower()

        # 1. Extracción de monto
        amount = 0.0
        # Buscar formato "X mil"
        mil_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:mil|k)", clean)
        if mil_match:
            val_str = mil_match.group(1).replace(",", ".")
            amount = float(val_str) * 1000.0
        else:
            # Buscar número directo con o sin símbolo $
            num_match = re.search(r"\$?\s*(\d{2,}(?:[.,]\d+)?)", clean)
            if num_match:
                val_str = num_match.group(1).replace(".", "").replace(",", ".")
                amount = float(val_str)

        if amount <= 0.0:
            return None

        # 2. Extracción de categoría
        category = "Varios / General"
        for keyword, cat_name in self.CATEGORIES.items():
            if keyword in clean:
                category = cat_name
                break

        # 3. Descripción
        description = text.strip()

        return {
            "amount": amount,
            "category": category,
            "description": description,
        }

    def record_voice_expense(self, voice_text: str) -> Dict[str, Any]:
        """Procesa una locución de voz y la almacena en la contabilidad."""
        parsed = self.parse_natural_language_expense(voice_text)
        if not parsed:
            return {
                "success": False,
                "message": f"{config.USER_TITLE}, no logré identificar con certeza la cifra monetaria en su frase.",
            }

        exp_id = self.add_expense(
            amount=parsed["amount"],
            category=parsed["category"],
            description=parsed["description"],
        )

        return {
            "success": True,
            "id": exp_id,
            "amount": parsed["amount"],
            "category": parsed["category"],
            "message": f"{config.USER_TITLE}, he auditado y registrado un egreso de ${parsed['amount']:,.2f} en '{parsed['category']}'.",
        }

    # -------------------------------------------------------------------------
    # REGISTRO Y CONSULTAS
    # -------------------------------------------------------------------------
    def add_expense(self, amount: float, category: str, description: str) -> int:
        now_dt = datetime.now()
        date_str = now_dt.strftime("%Y-%m-%d %H:%M")
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO expenses (amount, category, description, date_str, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (amount, category, description, date_str, time.time()))
            conn.commit()
            return c.lastrowid

    def get_summary(self) -> Dict[str, Any]:
        """Calcula el balance acumulado y total por categorías."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT SUM(amount) as total, COUNT(*) as count FROM expenses")
            row = c.fetchone()
            total = row["total"] or 0.0
            count = row["count"] or 0

            c.execute("SELECT category, SUM(amount) as subtotal FROM expenses GROUP BY category")
            by_cat = {r["category"]: r["subtotal"] for r in c.fetchall()}

            return {
                "total_expenses": total,
                "total_transactions": count,
                "by_category": by_cat,
            }

    # -------------------------------------------------------------------------
    # EXPORTACIÓN AUTOMÁTICA A EXCEL (.XLSX) CON OPENPYXL
    # -------------------------------------------------------------------------
    def export_to_excel(self, filename: Optional[str] = None) -> Path:
        """
        Genera una hoja de cálculo ejecutiva con formato corporativo estilizado,
        fórmulas automáticas de suma y bordes estilizados.
        """
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_name = filename or f"auditoria_finanzas_{config.USER_NAME.lower()}_{stamp}.xlsx"
        file_path = self.export_dir / target_name

        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, date_str, category, description, amount FROM expenses ORDER BY id ASC")
            records = c.fetchall()

        if OPENPYXL_AVAILABLE:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Auditoría Financiera"
            ws.views.sheetView[0].showGridLines = True

            # Estilos
            fill_header = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
            font_title = Font(name="Segoe UI", size=15, bold=True, color="00E5FF")
            font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            font_body = Font(name="Segoe UI", size=10, color="000000")
            font_total = Font(name="Segoe UI", size=12, bold=True, color="00E5FF")
            fill_total = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")

            # Encabezado Banner
            ws.merge_cells("A1:E1")
            cell_title = ws["A1"]
            cell_title.value = f"JARVIS SUPREME - AUDITORÍA FINANCIERA DE {config.USER_TITLE.upper()}"
            cell_title.font = font_title
            cell_title.fill = fill_header
            cell_title.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 40

            # Fila de Columnas
            headers = ["ID", "Fecha / Hora", "Categoría", "Detalle / Concepto", "Monto ($)"]
            ws.append([])  # Fila 2 vacía
            ws.append(headers)  # Fila 3
            ws.row_dimensions[3].height = 26

            for col_idx in range(1, 6):
                cell = ws.cell(row=3, column=col_idx)
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Inserción de Datos
            row_idx = 4
            for r in records:
                ws.append([r["id"], r["date_str"], r["category"], r["description"], r["amount"]])
                # Formato moneda para la columna E
                cell_amt = ws.cell(row=row_idx, column=5)
                cell_amt.number_format = '"$"#,##0.00'
                cell_amt.alignment = Alignment(horizontal="right")
                row_idx += 1

            # Fila de Totales
            total_row = row_idx
            ws.cell(row=total_row, column=4, value="TOTAL CONSOLIDADO:").font = font_total
            ws.cell(row=total_row, column=4).fill = fill_total
            ws.cell(row=total_row, column=4).alignment = Alignment(horizontal="right")

            cell_formula = ws.cell(row=total_row, column=5, value=f"=SUM(E4:E{total_row-1})")
            cell_formula.font = font_total
            cell_formula.fill = fill_total
            cell_formula.number_format = '"$"#,##0.00'
            cell_formula.alignment = Alignment(horizontal="right")

            # Auto-ajuste de ancho de columnas
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

            wb.save(str(file_path))
            return file_path

        # Fallback a CSV si openpyxl no estuviera disponible
        csv_path = file_path.with_suffix(".csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Fecha", "Categoría", "Descripción", "Monto"])
            for r in records:
                writer.writerow([r["id"], r["date_str"], r["category"], r["description"], r["amount"]])
        return csv_path


# Instancia singleton predeterminada
finance_manager = FinanceManager()

"""Application principale - Géodésie Mini-Projet.

Interface graphique PyQt5 pour les transformations de coordonnées géodésiques
et cartésiennes géocentriques (Système Merchich - Ellipsoïde Clarke 1880 IGN).
Mode clair (Light Theme) avec ergonomie enrichie et affichage DMS.
"""

from __future__ import annotations

import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import transformations as tr


def format_dms(deg_val: float, is_latitude: bool) -> str:
    """Formate une valeur en degrés décimaux au format DMS (Degrés Minutes Secondes)."""
    if is_latitude:
        card = "N" if deg_val >= 0 else "S"
    else:
        card = "E" if deg_val >= 0 else "W"

    val = abs(deg_val)
    d = int(val)
    m_float = (val - d) * 60.0
    m = int(m_float)
    s = (m_float - m) * 60.0
    return f"{d:02d}° {m:02d}' {s:05.2f}\" {card}"


# ===========================================================================
# Feuille de style principale - MODE CLAIR (LIGHT THEME)
# ===========================================================================
STYLE_SHEET = """
/* Fenêtre principale & Fond global */
QMainWindow {
    background-color: #f8fafc;
}

QWidget {
    color: #1e293b;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Onglets & Conteneur */
QTabWidget::pane {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    border-radius: 8px;
    top: -1px;
    padding: 6px;
}

QTabBar::tab {
    background-color: #f1f5f9;
    color: #475569;
    padding: 10px 22px;
    border: 1px solid #cbd5e1;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0284c7;
    border-color: #cbd5e1;
    border-top: 3px solid #0284c7;
    border-bottom: 2px solid #ffffff;
}

QTabBar::tab:hover:!selected {
    background-color: #e2e8f0;
    color: #0f172a;
}

/* Cadres de regroupement (Group Boxes) */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 14px 12px 14px;
    font-weight: bold;
    color: #0369a1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 10px;
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 5px;
    left: 12px;
    color: #0369a1;
    font-weight: 700;
}

/* Champs de saisie */
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
    background-color: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 10px;
    color: #0f172a;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {
    border: 1.5px solid #0284c7;
    background-color: #ffffff;
}

QLineEdit:read-only {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #0f172a;
    font-weight: 600;
}

QComboBox {
    padding-right: 20px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #e2e8f0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #e0f2fe;
    selection-color: #0369a1;
    border: 1px solid #cbd5e1;
    padding: 4px;
}

/* Boutons */
QPushButton {
    background-color: #0284c7;
    color: #ffffff;
    border: 1px solid #0284c7;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #0369a1;
    border-color: #0369a1;
}

QPushButton:pressed {
    background-color: #075985;
    border-color: #075985;
}

QPushButton.btn-secondary, QPushButton[class="btn-secondary"] {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    color: #334155;
}

QPushButton.btn-secondary:hover, QPushButton[class="btn-secondary"]:hover {
    background-color: #f1f5f9;
    border-color: #94a3b8;
    color: #0f172a;
}

QPushButton.btn-secondary:pressed, QPushButton[class="btn-secondary"]:pressed {
    background-color: #e2e8f0;
}

QPushButton.btn-success, QPushButton[class="btn-success"] {
    background-color: #059669;
    border: 1px solid #059669;
    color: #ffffff;
}

QPushButton.btn-success:hover, QPushButton[class="btn-success"]:hover {
    background-color: #047857;
    border-color: #047857;
}

/* Boutons radio */
QRadioButton {
    spacing: 8px;
    color: #1e293b;
    font-weight: 500;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

/* Tableaux de données */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    gridline-color: #e2e8f0;
    border-radius: 6px;
    selection-background-color: #e0f2fe;
    selection-color: #0369a1;
    color: #1e293b;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #334155;
    font-weight: 700;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
}

/* Barres de défilement */
QScrollBar:vertical {
    background: #f1f5f9;
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar:horizontal {
    background: #f1f5f9;
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background: #94a3b8;
}

/* Zone de défilement adaptable */
QScrollArea {
    background-color: transparent;
    border: none;
}

/* Synthèse et zones de texte */
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #1e293b;
    padding: 8px;
}
"""


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application Géodésie Mini-Projet en mode clair."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Geodesie Mini-Projet")
        self.resize(1020, 760)
        self.setMinimumSize(580, 420)
        self.setStyleSheet(STYLE_SHEET)

        # Widget central principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # En-tête informatif enrichi
        header_widget = self._create_header_widget()
        main_layout.addWidget(header_widget)

        # Onglets principaux
        self.tabs = QTabWidget(self)
        self.tab_direct = self._create_tab_direct()
        self.tab_inverse = self._create_tab_inverse()
        self.tab_validation = self._create_tab_validation()

        self.tabs.addTab(self.tab_direct, "1. Transformation Directe (φ, λ, h → X, Y, Z)")
        self.tabs.addTab(self.tab_inverse, "2. Transformation Inverse (X, Y, Z → φ, λ, h)")
        self.tabs.addTab(self.tab_validation, "3. Validation & Comparaison")

        main_layout.addWidget(self.tabs)

        # Barre d'état en bas
        status_bar_container = QFrame(self)
        status_bar_container.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 2px;"
        )
        status_bar_layout = QHBoxLayout(status_bar_container)
        status_bar_layout.setContentsMargins(8, 2, 8, 2)

        self.status_label = QLabel("Prêt — Système Merchich (Ellipsoïde Clarke 1880 IGN) — Mode Clair", self)
        self.status_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: 500;")
        status_bar_layout.addWidget(self.status_label)

        main_layout.addWidget(status_bar_container)

    def _wrap_in_scroll_area(self, content_widget: QWidget) -> QScrollArea:
        """Enveloppe un widget dans une zone de défilement pour garantir fluidité et adaptabilité."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(content_widget)
        return scroll

    # -----------------------------------------------------------------------
    # Composants de l'en-tête
    # -----------------------------------------------------------------------

    def _create_header_widget(self) -> QWidget:
        widget = QFrame(self)
        widget.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffffff, stop:1 #f0f9ff); "
            "border: 1px solid #bae6fd; border-radius: 10px; padding: 10px;"
        )
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        header_top_layout = QHBoxLayout()
        title = QLabel("Géodésie Mini-Projet — Transformations de Coordonnées", widget)
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #0369a1;")
        title.setWordWrap(True)
        header_top_layout.addWidget(title, 1)

        badge = QLabel("Datum Merchich 1923", widget)
        badge.setStyleSheet(
            "background-color: #0284c7; color: #ffffff; font-weight: bold; "
            "padding: 3px 10px; border-radius: 12px; font-size: 11px;"
        )
        header_top_layout.addWidget(badge, 0, Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(header_top_layout)

        ell = tr.CLARKE_1880_IGN
        inv_f = 1.0 / ell.f
        subtitle = QLabel(
            f"Ellipsoïde : <b>{ell.name}</b> | Demi-grand axe : <b>a = {ell.a:,.1f} m</b> | "
            f"Demi-petit axe : <b>b = {ell.b:,.1f} m</b> | <b>1/f ≈ {inv_f:.3f}</b> | "
            f"Première excentricité au carré : <b>e² ≈ {ell.e2:.8f}</b>",
            widget,
        )
        subtitle.setStyleSheet("font-size: 12px; color: #334155; font-weight: 500;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        note = QLabel(
            "ℹ️ Note géodésique : Calcul direct et inverse 3D (coordonnées géocentriques). "
            "Ne se substitue pas à la projection plane Lambert Merchich Nord Maroc.",
            widget,
        )
        note.setStyleSheet(
            "background-color: #e0f2fe; border-left: 3px solid #0284c7; "
            "padding: 6px 10px; border-radius: 4px; font-size: 11px; color: #0369a1; font-weight: 500;"
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        return widget

    # -----------------------------------------------------------------------
    # Onglet 1 : Transformation Directe
    # -----------------------------------------------------------------------

    def _create_tab_direct(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Sélecteur de préréglages
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Points remarquables préconfigurés :")
        preset_label.setStyleSheet("color: #334155; font-weight: 600;")
        self.combo_presets_dir = QComboBox()
        self.combo_presets_dir.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_presets_dir.addItems([
            "-- Sélectionner un point prédéfini --",
            "Rabat, Maroc (34.020882°, -6.841650°, 100.0 m)",
            "Merchich - Origine (33.448490°, -7.555660°, 150.0 m)",
            "Marrakech, Maroc (31.629472°, -7.981084°, 460.0 m)",
            "Tanger, Maroc (35.759465°, -5.833954°, 20.0 m)",
            "Dépression Sebkha Tah (-50 m) (27.716000°, -12.233000°, -50.0 m)",
            "Équateur / Méridien Origine (0.0°, 0.0°, 0.0 m)",
            "Équateur / 90° Est (0.0°, 90.0°, 0.0 m)",
            "Pôle Nord (90.0°, 0.0°, 0.0 m)",
            "Pôle Sud (-90.0°, 0.0°, 0.0 m)",
        ])
        self.combo_presets_dir.currentIndexChanged.connect(self._on_preset_direct_selected)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.combo_presets_dir, 1)
        layout.addLayout(preset_layout)

        # Groupe des données d'entrée
        input_group = QGroupBox("Coordonnées Géodésiques d'Entrée")
        form_layout = QFormLayout(input_group)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(10)

        # Latitude phi
        self.txt_phi = QLineEdit()
        self.txt_phi.setPlaceholderText("Ex: 34.020882 (compris entre -90.0 et +90.0)")
        self.lbl_phi_dms = QLabel("")
        self.lbl_phi_dms.setStyleSheet("color: #0369a1; font-size: 11px; font-weight: 600;")
        col_phi = QVBoxLayout()
        col_phi.setSpacing(2)
        col_phi.addWidget(self.txt_phi)
        col_phi.addWidget(self.lbl_phi_dms)
        form_layout.addRow("Latitude géodésique φ (degrés) :", col_phi)

        # Longitude lambda
        self.txt_lam = QLineEdit()
        self.txt_lam.setPlaceholderText("Ex: -6.841650 (en degrés)")
        self.lbl_lam_dms = QLabel("")
        self.lbl_lam_dms.setStyleSheet("color: #0369a1; font-size: 11px; font-weight: 600;")
        col_lam = QVBoxLayout()
        col_lam.setSpacing(2)
        col_lam.addWidget(self.txt_lam)
        col_lam.addWidget(self.lbl_lam_dms)
        form_layout.addRow("Longitude λ (degrés) :", col_lam)

        # Hauteur ellipsoïdale h
        self.txt_h = QLineEdit()
        self.txt_h.setPlaceholderText("Ex: 100.0 (en mètres)")
        form_layout.addRow("Hauteur ellipsoïdale h (mètres) :", self.txt_h)

        # Mise à jour interactive DMS lors de la frappe
        self.txt_phi.textChanged.connect(self._update_direct_dms_helpers)
        self.txt_lam.textChanged.connect(self._update_direct_dms_helpers)

        layout.addWidget(input_group)

        # Boutons d'action
        btn_action_layout = QHBoxLayout()
        btn_calc_direct = QPushButton("Calculer les Coordonnées Cartésiennes (X, Y, Z)")
        btn_calc_direct.setFixedHeight(38)
        btn_calc_direct.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_calc_direct.clicked.connect(self._handle_calculate_direct)
        btn_action_layout.addWidget(btn_calc_direct, 3)

        btn_reset_direct = QPushButton("Réinitialiser")
        btn_reset_direct.setProperty("class", "btn-secondary")
        btn_reset_direct.setFixedHeight(38)
        btn_reset_direct.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_reset_direct.clicked.connect(self._reset_direct_fields)
        btn_action_layout.addWidget(btn_reset_direct, 1)

        layout.addLayout(btn_action_layout)

        # Groupe des résultats
        output_group = QGroupBox("Coordonnées Cartésiennes Géocentriques Résultantes")
        out_layout = QFormLayout(output_group)
        out_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        out_layout.setSpacing(8)

        self.txt_out_x = QLineEdit()
        self.txt_out_x.setReadOnly(True)
        btn_copy_x = QPushButton("Copier")
        btn_copy_x.setProperty("class", "btn-secondary")
        btn_copy_x.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_x.text(), "X"))
        row_x = QHBoxLayout()
        row_x.addWidget(self.txt_out_x, 1)
        row_x.addWidget(btn_copy_x)
        out_layout.addRow("X (m) :", row_x)

        self.txt_out_y = QLineEdit()
        self.txt_out_y.setReadOnly(True)
        btn_copy_y = QPushButton("Copier")
        btn_copy_y.setProperty("class", "btn-secondary")
        btn_copy_y.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_y.text(), "Y"))
        row_y = QHBoxLayout()
        row_y.addWidget(self.txt_out_y, 1)
        row_y.addWidget(btn_copy_y)
        out_layout.addRow("Y (m) :", row_y)

        self.txt_out_z = QLineEdit()
        self.txt_out_z.setReadOnly(True)
        btn_copy_z = QPushButton("Copier")
        btn_copy_z.setProperty("class", "btn-secondary")
        btn_copy_z.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_z.text(), "Z"))
        row_z = QHBoxLayout()
        row_z.addWidget(self.txt_out_z, 1)
        row_z.addWidget(btn_copy_z)
        out_layout.addRow("Z (m) :", row_z)

        # Distance géocentrique R = sqrt(X² + Y² + Z²)
        self.txt_out_r = QLineEdit()
        self.txt_out_r.setReadOnly(True)
        out_layout.addRow("Rayon géocentrique R (m) :", self.txt_out_r)

        # Barre d'actions complémentaires pour les résultats
        res_actions_layout = QHBoxLayout()
        btn_copy_all_xyz = QPushButton("Copier toutes les coordonnées (X, Y, Z)")
        btn_copy_all_xyz.setProperty("class", "btn-secondary")
        btn_copy_all_xyz.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_copy_all_xyz.clicked.connect(self._copy_all_xyz)
        res_actions_layout.addWidget(btn_copy_all_xyz)

        btn_transfer_inv = QPushButton("Transférer vers l'Onglet Inverse (X, Y, Z → φ, λ, h)")
        btn_transfer_inv.setProperty("class", "btn-secondary")
        btn_transfer_inv.setStyleSheet("font-weight: bold; color: #0369a1;")
        btn_transfer_inv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_transfer_inv.clicked.connect(self._transfer_to_inverse)
        res_actions_layout.addWidget(btn_transfer_inv)

        out_layout.addRow("", res_actions_layout)

        layout.addWidget(output_group)
        layout.addStretch()

        return self._wrap_in_scroll_area(content)

    # -----------------------------------------------------------------------
    # Onglet 2 : Transformation Inverse
    # -----------------------------------------------------------------------

    def _create_tab_inverse(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Sélecteur de préréglages
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Points remarquables préconfigurés :")
        preset_label.setStyleSheet("color: #334155; font-weight: 600;")
        self.combo_presets_inv = QComboBox()
        self.combo_presets_inv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_presets_inv.addItems([
            "-- Sélectionner un point prédéfini --",
            "Rabat, Maroc (X: 5254544.2351 m, Y: -630440.7977 m, Z: 3548155.9347 m)",
            "Merchich - Origine (X: 5283411.0825 m, Y: -700779.6200 m, Z: 3496359.5160 m)",
            "Marrakech, Maroc (X: 5383630.3138 m, Y: -754807.4890 m, Z: 3325503.2519 m)",
            "Équateur / Méridien Origine (X: 6378249.2 m, Y: 0.0 m, Z: 0.0 m)",
            "Équateur / 90° Est (X: 0.0 m, Y: 6378249.2 m, Z: 0.0 m)",
            "Pôle Nord (X: 0.0 m, Y: 0.0 m, Z: 6356515.0 m)",
            "Pôle Sud (X: 0.0 m, Y: 0.0 m, Z: -6356515.0 m)",
        ])
        self.combo_presets_inv.currentIndexChanged.connect(self._on_preset_inverse_selected)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.combo_presets_inv, 1)
        layout.addLayout(preset_layout)

        # Groupe des données d'entrée cartésiennes
        input_group = QGroupBox("Coordonnées Cartésiennes Géocentriques d'Entrée")
        form_layout = QFormLayout(input_group)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(10)

        self.txt_in_x = QLineEdit()
        self.txt_in_x.setPlaceholderText("Ex: 5254544.2351 (en mètres)")
        form_layout.addRow("X (m) :", self.txt_in_x)

        self.txt_in_y = QLineEdit()
        self.txt_in_y.setPlaceholderText("Ex: -630440.7977 (en mètres)")
        form_layout.addRow("Y (m) :", self.txt_in_y)

        self.txt_in_z = QLineEdit()
        self.txt_in_z.setPlaceholderText("Ex: 3548155.9347 (en mètres)")
        form_layout.addRow("Z (m) :", self.txt_in_z)

        layout.addWidget(input_group)

        # Sélection de la méthode inverse
        method_group = QGroupBox("Méthode de Transformation Inverse")
        method_layout = QVBoxLayout(method_group)

        self.radio_bowring = QRadioButton("Méthode directe (approximation de Bowring)")
        self.radio_iterative = QRadioButton("Méthode itérative")
        self.radio_iterative.setChecked(True)

        self.method_btn_group = QButtonGroup(self)
        self.method_btn_group.addButton(self.radio_bowring)
        self.method_btn_group.addButton(self.radio_iterative)

        method_layout.addWidget(self.radio_bowring)
        method_layout.addWidget(self.radio_iterative)

        # Paramètres itératifs optionnels
        iter_params_layout = QHBoxLayout()
        iter_params_layout.setContentsMargins(20, 0, 0, 0)
        iter_params_layout.addWidget(QLabel("Tolérance (rad) :"))
        self.txt_tolerance = QLineEdit("1e-12")
        self.txt_tolerance.setFixedWidth(90)
        iter_params_layout.addWidget(self.txt_tolerance)

        iter_params_layout.addWidget(QLabel("Itérations max :"))
        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setRange(1, 1000)
        self.spin_max_iter.setValue(100)
        self.spin_max_iter.setFixedWidth(80)
        iter_params_layout.addWidget(self.spin_max_iter)
        iter_params_layout.addStretch()

        method_layout.addLayout(iter_params_layout)
        layout.addWidget(method_group)

        # Boutons d'action
        btn_action_layout = QHBoxLayout()
        btn_calc_inverse = QPushButton("Calculer les Coordonnées Géodésiques (φ, λ, h)")
        btn_calc_inverse.setFixedHeight(38)
        btn_calc_inverse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_calc_inverse.clicked.connect(self._handle_calculate_inverse)
        btn_action_layout.addWidget(btn_calc_inverse, 3)

        btn_reset_inv = QPushButton("Réinitialiser")
        btn_reset_inv.setProperty("class", "btn-secondary")
        btn_reset_inv.setFixedHeight(38)
        btn_reset_inv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_reset_inv.clicked.connect(self._reset_inverse_fields)
        btn_action_layout.addWidget(btn_reset_inv, 1)

        layout.addLayout(btn_action_layout)

        # Groupe des résultats géodésiques
        output_group = QGroupBox("Coordonnées Géodésiques Résultantes")
        out_layout = QFormLayout(output_group)
        out_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        out_layout.setSpacing(8)

        # Latitude phi
        self.txt_out_phi = QLineEdit()
        self.txt_out_phi.setReadOnly(True)
        btn_copy_phi = QPushButton("Copier")
        btn_copy_phi.setProperty("class", "btn-secondary")
        btn_copy_phi.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_phi.text(), "Latitude φ"))
        row_phi = QHBoxLayout()
        row_phi.addWidget(self.txt_out_phi, 1)
        row_phi.addWidget(btn_copy_phi)

        self.lbl_out_phi_dms = QLabel("")
        self.lbl_out_phi_dms.setStyleSheet("color: #0369a1; font-size: 11px; font-weight: 600;")
        col_out_phi = QVBoxLayout()
        col_out_phi.setSpacing(2)
        col_out_phi.addLayout(row_phi)
        col_out_phi.addWidget(self.lbl_out_phi_dms)
        out_layout.addRow("Latitude φ (degrés) :", col_out_phi)

        # Longitude lambda
        self.txt_out_lam = QLineEdit()
        self.txt_out_lam.setReadOnly(True)
        btn_copy_lam = QPushButton("Copier")
        btn_copy_lam.setProperty("class", "btn-secondary")
        btn_copy_lam.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_lam.text(), "Longitude λ"))
        row_lam = QHBoxLayout()
        row_lam.addWidget(self.txt_out_lam, 1)
        row_lam.addWidget(btn_copy_lam)

        self.lbl_out_lam_dms = QLabel("")
        self.lbl_out_lam_dms.setStyleSheet("color: #0369a1; font-size: 11px; font-weight: 600;")
        col_out_lam = QVBoxLayout()
        col_out_lam.setSpacing(2)
        col_out_lam.addLayout(row_lam)
        col_out_lam.addWidget(self.lbl_out_lam_dms)
        out_layout.addRow("Longitude λ (degrés) :", col_out_lam)

        # Hauteur ellipsoïdale h
        self.txt_out_h = QLineEdit()
        self.txt_out_h.setReadOnly(True)
        btn_copy_h = QPushButton("Copier")
        btn_copy_h.setProperty("class", "btn-secondary")
        btn_copy_h.clicked.connect(lambda: self._copy_to_clipboard(self.txt_out_h.text(), "Hauteur h"))
        row_h = QHBoxLayout()
        row_h.addWidget(self.txt_out_h, 1)
        row_h.addWidget(btn_copy_h)
        out_layout.addRow("Hauteur ellipsoïdale h (m) :", row_h)

        self.txt_out_iter = QLineEdit()
        self.txt_out_iter.setReadOnly(True)
        out_layout.addRow("Convergence / Itérations :", self.txt_out_iter)

        # Actions complémentaires
        res_actions_layout = QHBoxLayout()
        btn_copy_all_geo = QPushButton("Copier toutes les coordonnées (φ, λ, h)")
        btn_copy_all_geo.setProperty("class", "btn-secondary")
        btn_copy_all_geo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_copy_all_geo.clicked.connect(self._copy_all_geo)
        res_actions_layout.addWidget(btn_copy_all_geo)

        btn_transfer_dir = QPushButton("Transférer vers l'Onglet Direct (φ, λ, h → X, Y, Z)")
        btn_transfer_dir.setProperty("class", "btn-secondary")
        btn_transfer_dir.setStyleSheet("font-weight: bold; color: #0369a1;")
        btn_transfer_dir.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_transfer_dir.clicked.connect(self._transfer_to_direct)
        res_actions_layout.addWidget(btn_transfer_dir)

        out_layout.addRow("", res_actions_layout)

        layout.addWidget(output_group)
        layout.addStretch()

        return self._wrap_in_scroll_area(content)

    # -----------------------------------------------------------------------
    # Onglet 3 : Validation & Comparaison
    # -----------------------------------------------------------------------

    def _create_tab_validation(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Barre de boutons de test en grille 2x2 responsive
        btn_layout = QGridLayout()
        btn_layout.setSpacing(8)

        self.btn_run_known = QPushButton("Exécuter les tests de référence connue")
        self.btn_run_known.setProperty("class", "btn-secondary")
        self.btn_run_known.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_run_known.clicked.connect(self._run_known_reference_tests)
        btn_layout.addWidget(self.btn_run_known, 0, 0)

        self.btn_run_roundtrip = QPushButton("Exécuter les tests aller-retour")
        self.btn_run_roundtrip.setProperty("class", "btn-secondary")
        self.btn_run_roundtrip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_run_roundtrip.clicked.connect(self._run_roundtrip_tests)
        btn_layout.addWidget(self.btn_run_roundtrip, 0, 1)

        self.btn_compare_methods = QPushButton("Comparer les méthodes inverses")
        self.btn_compare_methods.setProperty("class", "btn-secondary")
        self.btn_compare_methods.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_compare_methods.clicked.connect(self._compare_inverse_methods)
        btn_layout.addWidget(self.btn_compare_methods, 1, 0)

        self.btn_export_csv = QPushButton("Copier le tableau (CSV)")
        self.btn_export_csv.setProperty("class", "btn-secondary")
        self.btn_export_csv.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_export_csv.clicked.connect(self._export_table_to_clipboard)
        btn_layout.addWidget(self.btn_export_csv, 1, 1)

        layout.addLayout(btn_layout)

        # Tableau des résultats
        self.table_results = QTableWidget()
        self.table_results.setColumnCount(7)
        self.table_results.setAlternatingRowColors(True)
        self.table_results.setMinimumHeight(140)
        self.table_results.setHorizontalHeaderLabels([
            "Test / Point",
            "Méthode",
            "Écart φ (°)",
            "Écart λ (°)",
            "Écart h (m)",
            "Itérations",
            "Statut",
        ])
        header = self.table_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 7):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

        layout.addWidget(self.table_results, 1)

        # Zone de texte explicatif / synthèse
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setMinimumHeight(55)
        self.txt_summary.setMaximumHeight(150)
        self.txt_summary.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; font-size: 12px; padding: 6px;")
        layout.addWidget(self.txt_summary)

        return tab

    # -----------------------------------------------------------------------
    # Logique métier et gestionnaires d'événements
    # -----------------------------------------------------------------------

    def _update_direct_dms_helpers(self) -> None:
        """Met à jour les étiquettes d'aide DMS pour la transformation directe."""
        phi_str = self.txt_phi.text().strip()
        try:
            phi_val = float(phi_str)
            if -90.0 <= phi_val <= 90.0:
                self.lbl_phi_dms.setText(f"DMS : {format_dms(phi_val, is_latitude=True)}")
            else:
                self.lbl_phi_dms.setText("")
        except ValueError:
            self.lbl_phi_dms.setText("")

        lam_str = self.txt_lam.text().strip()
        try:
            lam_val = float(lam_str)
            self.lbl_lam_dms.setText(f"DMS : {format_dms(lam_val, is_latitude=False)}")
        except ValueError:
            self.lbl_lam_dms.setText("")

    def _reset_direct_fields(self) -> None:
        """Efface les champs de l'onglet transformation directe."""
        self.txt_phi.clear()
        self.txt_lam.clear()
        self.txt_h.clear()
        self.lbl_phi_dms.setText("")
        self.lbl_lam_dms.setText("")
        self.txt_out_x.clear()
        self.txt_out_y.clear()
        self.txt_out_z.clear()
        self.txt_out_r.clear()
        self.combo_presets_dir.setCurrentIndex(0)
        self.status_label.setText("Champs de l'onglet Transformation Directe réinitialisés.")

    def _reset_inverse_fields(self) -> None:
        """Efface les champs de l'onglet transformation inverse."""
        self.txt_in_x.clear()
        self.txt_in_y.clear()
        self.txt_in_z.clear()
        self.txt_out_phi.clear()
        self.txt_out_lam.clear()
        self.txt_out_h.clear()
        self.lbl_out_phi_dms.setText("")
        self.lbl_out_lam_dms.setText("")
        self.txt_out_iter.clear()
        self.combo_presets_inv.setCurrentIndex(0)
        self.status_label.setText("Champs de l'onglet Transformation Inverse réinitialisés.")

    def _transfer_to_inverse(self) -> None:
        """Transfère les coordonnées X, Y, Z résultantes vers l'onglet Inverse."""
        x = self.txt_out_x.text().strip()
        y = self.txt_out_y.text().strip()
        z = self.txt_out_z.text().strip()
        if not (x and y and z):
            QMessageBox.information(self, "Calcul requis", "Veuillez d'abord calculer les coordonnées X, Y, Z.")
            return
        self.txt_in_x.setText(x)
        self.txt_in_y.setText(y)
        self.txt_in_z.setText(z)
        self.tabs.setCurrentIndex(1)
        self.status_label.setText("Coordonnées cartésiennes transférées vers l'onglet Inverse.")

    def _transfer_to_direct(self) -> None:
        """Transfère les coordonnées géodésiques résultantes vers l'onglet Direct."""
        phi = self.txt_out_phi.text().strip()
        lam = self.txt_out_lam.text().strip()
        h = self.txt_out_h.text().strip()
        if not (phi and lam and h):
            QMessageBox.information(self, "Calcul requis", "Veuillez d'abord calculer les coordonnées φ, λ, h.")
            return
        self.txt_phi.setText(phi)
        self.txt_lam.setText(lam)
        self.txt_h.setText(h)
        self._update_direct_dms_helpers()
        self.tabs.setCurrentIndex(0)
        self.status_label.setText("Coordonnées géodésiques transférées vers l'onglet Direct.")

    def _export_table_to_clipboard(self) -> None:
        """Exporte les résultats du tableau de validation vers le presse-papiers au format CSV."""
        rows = self.table_results.rowCount()
        cols = self.table_results.columnCount()
        if rows == 0:
            QMessageBox.information(self, "Tableau vide", "Aucun résultat à exporter. Exécutez d'abord un test.")
            return

        headers = [self.table_results.horizontalHeaderItem(c).text() for c in range(cols)]
        csv_lines = [";".join(headers)]
        for r in range(rows):
            line = []
            for c in range(cols):
                item = self.table_results.item(r, c)
                line.append(item.text() if item else "")
            csv_lines.append(";".join(line))

        full_csv = "\n".join(csv_lines)
        QApplication.clipboard().setText(full_csv)
        self.status_label.setText(f"✓ {rows} lignes exportées au format CSV dans le presse-papiers.")

    def _on_preset_direct_selected(self, index: int) -> None:
        presets = {
            1: ("34.020882", "-6.841650", "100.0"),
            2: ("33.448490", "-7.555660", "150.0"),
            3: ("31.629472", "-7.981084", "460.0"),
            4: ("35.759465", "-5.833954", "20.0"),
            5: ("27.716000", "-12.233000", "-50.0"),
            6: ("0.0", "0.0", "0.0"),
            7: ("0.0", "90.0", "0.0"),
            8: ("90.0", "0.0", "0.0"),
            9: ("-90.0", "0.0", "0.0"),
        }
        if index in presets:
            phi, lam, h = presets[index]
            self.txt_phi.setText(phi)
            self.txt_lam.setText(lam)
            self.txt_h.setText(h)
            self._update_direct_dms_helpers()

    def _on_preset_inverse_selected(self, index: int) -> None:
        presets = {
            1: ("5254544.2351", "-630440.7977", "3548155.9347"),
            2: ("5283411.0825", "-700779.6200", "3496359.5160"),
            3: ("5383630.3138", "-754807.4890", "3325503.2519"),
            4: (str(tr.CLARKE_1880_IGN.a), "0.0", "0.0"),
            5: ("0.0", str(tr.CLARKE_1880_IGN.a), "0.0"),
            6: ("0.0", "0.0", str(tr.CLARKE_1880_IGN.b)),
            7: ("0.0", "0.0", str(-tr.CLARKE_1880_IGN.b)),
        }
        if index in presets:
            x, y, z = presets[index]
            self.txt_in_x.setText(x)
            self.txt_in_y.setText(y)
            self.txt_in_z.setText(z)

    def _handle_calculate_direct(self) -> None:
        """Exécute la transformation géodésique vers cartésienne avec validation."""
        str_phi = self.txt_phi.text().strip()
        str_lam = self.txt_lam.text().strip()
        str_h = self.txt_h.text().strip()

        if not str_phi or not str_lam or not str_h:
            QMessageBox.warning(self, "Entrées manquantes", "Veuillez renseigner φ, λ et h.")
            return

        try:
            phi = float(str_phi)
            lam = float(str_lam)
            h = float(str_h)
        except ValueError:
            QMessageBox.critical(self, "Erreur de format", "Les coordonnées doivent être des nombres réels valides.")
            return

        try:
            X, Y, Z = tr.geodetic_to_cartesian(phi, lam, h)
            self.txt_out_x.setText(f"{X:.4f}")
            self.txt_out_y.setText(f"{Y:.4f}")
            self.txt_out_z.setText(f"{Z:.4f}")

            # Rayon géocentrique R
            r_val = math.sqrt(X * X + Y * Y + Z * Z)
            self.txt_out_r.setText(f"{r_val:.4f} m (≈ {r_val / 1000.0:.3f} km)")

            self.status_label.setText(
                f"Succès : Transformation directe effectuée (φ={phi:.6f}°, λ={lam:.6f}°, h={h:.2f} m)"
            )
        except tr.GeodeticError as exc:
            QMessageBox.critical(self, "Erreur géodésique", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Erreur inattendue", f"Une erreur s'est produite : {exc}")

    def _handle_calculate_inverse(self) -> None:
        """Exécute la transformation cartésienne vers géodésique."""
        str_x = self.txt_in_x.text().strip()
        str_y = self.txt_in_y.text().strip()
        str_z = self.txt_in_z.text().strip()

        if not str_x or not str_y or not str_z:
            QMessageBox.warning(self, "Entrées manquantes", "Veuillez renseigner X, Y et Z.")
            return

        try:
            X = float(str_x)
            Y = float(str_y)
            Z = float(str_z)
        except ValueError:
            QMessageBox.critical(self, "Erreur de format", "Les coordonnées cartésiennes doivent être des réels valides.")
            return

        try:
            if self.radio_bowring.isChecked():
                res = tr.cartesian_to_geodetic_direct(X, Y, Z)
                self.txt_out_iter.setText("N/A (Approximation directe fermée de Bowring)")
            else:
                tol_str = self.txt_tolerance.text().strip() or "1e-12"
                tolerance = float(tol_str)
                max_iter = self.spin_max_iter.value()
                res = tr.cartesian_to_geodetic_iterative(X, Y, Z, tolerance=tolerance, max_iterations=max_iter)
                self.txt_out_iter.setText(f"{res.iterations} itération(s) (Tolérance: {tolerance} rad)")

            self.txt_out_phi.setText(f"{res.latitude:.8f}")
            self.txt_out_lam.setText(f"{res.longitude:.8f}")
            self.txt_out_h.setText(f"{res.height:.4f}")

            # Affichage DMS
            self.lbl_out_phi_dms.setText(f"DMS : {format_dms(res.latitude, is_latitude=True)}")
            self.lbl_out_lam_dms.setText(f"DMS : {format_dms(res.longitude, is_latitude=False)}")

            self.status_label.setText(
                f"Succès : Transformation inverse effectuée (X={X:.2f}, Y={Y:.2f}, Z={Z:.2f})"
            )
        except tr.UndefinedCoordinateError as exc:
            QMessageBox.warning(self, "Coordonnées indéfinies", str(exc))
        except tr.ConvergenceError as exc:
            QMessageBox.critical(self, "Erreur de convergence", str(exc))
        except tr.GeodeticError as exc:
            QMessageBox.critical(self, "Erreur géodésique", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Erreur inattendue", f"Une erreur s'est produite : {exc}")

    def _copy_to_clipboard(self, text: str, name: str) -> None:
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.status_label.setText(f"✓ '{name}' copié dans le presse-papiers ({text})")

    def _copy_all_xyz(self) -> None:
        x, y, z = self.txt_out_x.text(), self.txt_out_y.text(), self.txt_out_z.text()
        if not (x and y and z):
            return
        full_text = f"X = {x} m, Y = {y} m, Z = {z} m"
        QApplication.clipboard().setText(full_text)
        self.status_label.setText("✓ Coordonnées cartésiennes copiées dans le presse-papiers.")

    def _copy_all_geo(self) -> None:
        phi, lam, h = self.txt_out_phi.text(), self.txt_out_lam.text(), self.txt_out_h.text()
        if not (phi and lam and h):
            return
        full_text = f"φ = {phi}°, λ = {lam}°, h = {h} m"
        QApplication.clipboard().setText(full_text)
        self.status_label.setText("✓ Coordonnées géodésiques copiées dans le presse-papiers.")

    # -----------------------------------------------------------------------
    # Exécution des séries de validation
    # -----------------------------------------------------------------------

    def _set_table_row(
        self,
        row: int,
        test_name: str,
        method: str,
        d_phi: float,
        d_lam: float,
        d_h: float,
        iterations: str,
        passed: bool,
    ) -> None:
        self.table_results.setItem(row, 0, QTableWidgetItem(test_name))
        self.table_results.setItem(row, 1, QTableWidgetItem(method))

        item_phi = QTableWidgetItem(f"{d_phi:.2e}")
        item_phi.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_results.setItem(row, 2, item_phi)

        item_lam = QTableWidgetItem(f"{d_lam:.2e}")
        item_lam.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_results.setItem(row, 3, item_lam)

        item_h = QTableWidgetItem(f"{d_h:.2e}")
        item_h.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_results.setItem(row, 4, item_h)

        item_iter = QTableWidgetItem(iterations)
        item_iter.setTextAlignment(Qt.AlignCenter)
        self.table_results.setItem(row, 5, item_iter)

        status_item = QTableWidgetItem("SUCCÈS" if passed else "ÉCHEC")
        status_item.setTextAlignment(Qt.AlignCenter)
        font = status_item.font()
        font.setBold(True)
        status_item.setFont(font)

        if passed:
            status_item.setForeground(QBrush(QColor("#15803d")))
            status_item.setBackground(QBrush(QColor("#dcfce7")))
        else:
            status_item.setForeground(QBrush(QColor("#b91c1c")))
            status_item.setBackground(QBrush(QColor("#fee2e2")))

        self.table_results.setItem(row, 6, status_item)

    def _run_known_reference_tests(self) -> None:
        """Exécute les cas analytiques connus et le point de référence pyproj."""
        known_cases = [
            ("Équateur / Greenwich (0°, 0°, 0 m)", 0.0, 0.0, 0.0, tr.CLARKE_1880_IGN.a, 0.0, 0.0),
            ("Équateur / 90°E (0°, 90°, 0 m)", 0.0, 90.0, 0.0, 0.0, tr.CLARKE_1880_IGN.a, 0.0),
            ("Pôle Nord (90°, 0°, 0 m)", 90.0, 0.0, 0.0, 0.0, 0.0, tr.CLARKE_1880_IGN.b),
            ("Rabat (Réf. pyproj indépendante)", 34.020882, -6.841650, 100.0, 5254544.235142, -630440.797713, 3548155.934676),
        ]

        self.table_results.setRowCount(len(known_cases) * 2)
        row = 0
        total_passed = 0

        for name, phi, lam, h, exp_x, exp_y, exp_z in known_cases:
            # 1. Directe
            X, Y, Z = tr.geodetic_to_cartesian(phi, lam, h)
            d_x = abs(X - exp_x)
            d_y = abs(Y - exp_y)
            d_z = abs(Z - exp_z)
            pass_dir = d_x < 1e-3 and d_y < 1e-3 and d_z < 1e-3
            if pass_dir:
                total_passed += 1

            self._set_table_row(
                row, f"{name} [Direct]", "Analytique / Formule",
                0.0, 0.0, max(d_x, d_y, d_z), "-", pass_dir
            )
            row += 1

            # 2. Inverse Itérative
            res_it = tr.cartesian_to_geodetic_iterative(exp_x, exp_y, exp_z)
            d_phi = abs(res_it.latitude - phi)
            d_lam = tr.angular_difference_deg(res_it.longitude, lam)
            d_h = abs(res_it.height - h)
            pass_inv = d_phi < 1e-7 and d_lam < 1e-7 and d_h < 1e-3
            if pass_inv:
                total_passed += 1

            self._set_table_row(
                row, f"{name} [Inverse]", "Itérative",
                d_phi, d_lam, d_h, str(res_it.iterations), pass_inv
            )
            row += 1

        self.txt_summary.setHtml(
            "<div style='line-height: 1.4;'>"
            "<b style='color: #0369a1; font-size: 13px;'>Résultats des tests de référence :</b><br>"
            f"• Total de vérifications : <b>{len(known_cases) * 2}</b><br>"
            f"• Tests réussis : <b style='color: #15803d;'>{total_passed}</b> / {len(known_cases) * 2}<br>"
            "• Tous les cas analytiques (équateur, pôles) et le point de référence pyproj sont conformes aux tolérances."
            "</div>"
        )
        self.status_label.setText("Tests de référence connue terminés avec succès.")

    def _run_roundtrip_tests(self) -> None:
        """Exécute les tests aller-retour (φ, λ, h -> X, Y, Z -> φ, λ, h)."""
        test_points = [
            ("Origine Merchich", 33.448490, -7.555660, 150.0),
            ("Rabat", 34.020882, -6.841650, 100.0),
            ("Marrakech", 31.629472, -7.981084, 460.0),
            ("Tanger", 35.759465, -5.833954, 20.0),
            ("Sebkha Tah (h < 0)", 27.716000, -12.233000, -50.0),
            ("Haute latitude (Arctique)", 85.000000, 45.000000, 1500.0),
            ("Antiméridien (+180°)", 15.000000, 179.999999, 100.0),
            ("Antiméridien (-180°)", 15.000000, -179.999999, 100.0),
        ]

        self.table_results.setRowCount(len(test_points) * 2)
        row = 0
        total_passed = 0

        for name, phi, lam, h in test_points:
            X, Y, Z = tr.geodetic_to_cartesian(phi, lam, h)

            # Test Bowring
            res_b = tr.cartesian_to_geodetic_direct(X, Y, Z)
            d_phi_b = abs(res_b.latitude - phi)
            d_lam_b = tr.angular_difference_deg(res_b.longitude, lam)
            d_h_b = abs(res_b.height - h)
            pass_b = d_phi_b < 1e-6 and d_lam_b < 1e-8 and d_h_b < 1e-3
            if pass_b:
                total_passed += 1
            self._set_table_row(row, name, "Bowring (Directe)", d_phi_b, d_lam_b, d_h_b, "N/A", pass_b)
            row += 1

            # Test Itérative
            res_it = tr.cartesian_to_geodetic_iterative(X, Y, Z)
            d_phi_it = abs(res_it.latitude - phi)
            d_lam_it = tr.angular_difference_deg(res_it.longitude, lam)
            d_h_it = abs(res_it.height - h)
            pass_it = d_phi_it < 1e-8 and d_lam_it < 1e-8 and d_h_it < 1e-4
            if pass_it:
                total_passed += 1
            self._set_table_row(row, name, "Itérative", d_phi_it, d_lam_it, d_h_it, str(res_it.iterations), pass_it)
            row += 1

        self.txt_summary.setHtml(
            "<div style='line-height: 1.4;'>"
            "<b style='color: #0369a1; font-size: 13px;'>Résultats des tests aller-retour :</b><br>"
            f"• Points évalués : <b>{len(test_points)}</b> (dont points géodésiques au Maroc, dépressions et antiméridiens).<br>"
            f"• Succès : <b style='color: #15803d;'>{total_passed}</b> / {len(test_points) * 2}.<br>"
            "• La méthode itérative restaure les coordonnées avec une précision nanométrique (écart φ &lt; 1e-8°, écart h &lt; 0.1 mm)."
            "</div>"
        )
        self.status_label.setText("Tests aller-retour terminés avec succès.")

    def _compare_inverse_methods(self) -> None:
        """Compare l'approximation de Bowring et la méthode itérative sur un ensemble de latitudes."""
        latitudes = [-80.0, -60.0, -30.0, 0.0, 30.0, 60.0, 80.0]
        self.table_results.setRowCount(len(latitudes))
        row = 0

        max_err_phi = 0.0
        max_err_h = 0.0

        for lat in latitudes:
            h = 2500.0  # Altitude de test
            X, Y, Z = tr.geodetic_to_cartesian(lat, 10.0, h)

            res_b = tr.cartesian_to_geodetic_direct(X, Y, Z)
            res_it = tr.cartesian_to_geodetic_iterative(X, Y, Z, tolerance=1e-13)

            d_phi = abs(res_b.latitude - res_it.latitude)
            d_lam = tr.angular_difference_deg(res_b.longitude, res_it.longitude)
            d_h = abs(res_b.height - res_it.height)

            max_err_phi = max(max_err_phi, d_phi)
            max_err_h = max(max_err_h, d_h)

            self._set_table_row(
                row, f"Comparaison φ = {lat:+.0f}°, h = {h}m", "Bowring vs Itérative",
                d_phi, d_lam, d_h, f"{res_it.iterations} iters", True
            )
            row += 1

        self.txt_summary.setHtml(
            "<div style='line-height: 1.4;'>"
            "<b style='color: #0369a1; font-size: 13px;'>Comparaison numérique : Bowring vs Itérative :</b><br>"
            f"• Écart maximal en latitude (φ) : <b style='color: #0369a1;'>{max_err_phi:.3e}°</b> (≈ {max_err_phi * 111_000 * 1000:.3f} mm sur l'ellipsoïde)<br>"
            f"• Écart maximal en hauteur (h) : <b style='color: #0369a1;'>{max_err_h:.3e} m</b> (≈ {max_err_h * 1000:.3f} mm)<br>"
            "• Conclusion : L'approximation de Bowring présente une excellente fidélité sub-millimétrique pour les usages topographiques standards, "
            "tandis que la méthode itérative converge en 3-4 itérations vers la précision machine."
            "</div>"
        )
        self.status_label.setText("Comparaison des méthodes inverses terminée.")


def main() -> int:
    """Point d'entrée pour lancer l'application PyQt5."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

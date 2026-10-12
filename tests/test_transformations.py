"""Suite de tests automatisés pour le module transformations géodésiques.

Vérifications incluses :
1. Cas de référence analytiques connus (équateur, pôles, méridiens).
2. Point non trivial validé indépendamment avec pyproj (coordonnées fixées).
3. Tests aller-retour (Direct -> Inverse) pour plusieurs points (notamment au Maroc).
4. Prise en compte du repliement circulaire des longitudes.
5. Points à hauteur négative, hautes latitudes et limites.
6. Gestion rigoureuse des quadrants de longitude.
7. Détection des entrées invalides et non finies (NaN, inf).
8. Traitement du géocentre et des pôles géographiques.
9. Gestion des limites de convergence et de la tolérance d'itération.
10. Quantification des écarts entre l'approximation de Bowring et la méthode itérative.
"""

from __future__ import annotations

import pytest

import transformations as tr


# ===========================================================================
# 1. Tests de valeurs de référence connues (analytiques et pyproj)
# ===========================================================================


class TestKnownReferenceValues:
    """Tests des points aux valeurs analytiques exactes et points de référence pyproj.

    Justification des tolérances numériques appliquées :
    - Pour les cas analytiques exacts (équateur, pôles), la tolérance est fixée à `abs=1e-9 m`
      pour les coordonnées cartésiennes et `abs=1e-9°` pour les coordonnées angulaires,
      ce qui correspond à la limite de précision des flottants 64 bits (IEEE 754).
    - Pour la comparaison avec la bibliothèque indépendante externe pyproj, la tolérance
      est de `1e-4 m` (0.1 mm) sur X, Y, Z, et `1e-7°` (0.01 mm) sur la latitude.
    """

    def test_case_a_equator_prime_meridian(self):
        """Cas A : Équateur (φ=0°), méridien de Greenwich (λ=0°), surface de l'ellipsoïde (h=0m).

        Attendu : X = a, Y = 0, Z = 0.
        """
        X, Y, Z = tr.geodetic_to_cartesian(0.0, 0.0, 0.0)
        assert X == pytest.approx(tr.CLARKE_1880_IGN.a, abs=1e-9)
        assert Y == pytest.approx(0.0, abs=1e-9)
        assert Z == pytest.approx(0.0, abs=1e-9)

        # Inverse directe Bowring
        phi_b, lam_b, h_b = tr.cartesian_to_geodetic_direct(tr.CLARKE_1880_IGN.a, 0.0, 0.0)
        assert phi_b == pytest.approx(0.0, abs=1e-9)
        assert lam_b == pytest.approx(0.0, abs=1e-9)
        assert h_b == pytest.approx(0.0, abs=1e-9)

        # Inverse itérative
        phi_it, lam_it, h_it = tr.cartesian_to_geodetic_iterative(tr.CLARKE_1880_IGN.a, 0.0, 0.0)
        assert phi_it == pytest.approx(0.0, abs=1e-9)
        assert lam_it == pytest.approx(0.0, abs=1e-9)
        assert h_it == pytest.approx(0.0, abs=1e-9)

    def test_case_b_equator_90_east(self):
        """Cas B : Équateur (φ=0°), 90° Est (λ=90°), surface de l'ellipsoïde (h=0m).

        Attendu : X = 0, Y = a, Z = 0.
        """
        X, Y, Z = tr.geodetic_to_cartesian(0.0, 90.0, 0.0)
        assert X == pytest.approx(0.0, abs=1e-9)
        assert Y == pytest.approx(tr.CLARKE_1880_IGN.a, abs=1e-9)
        assert Z == pytest.approx(0.0, abs=1e-9)

        # Inverses
        phi_b, lam_b, h_b = tr.cartesian_to_geodetic_direct(0.0, tr.CLARKE_1880_IGN.a, 0.0)
        assert phi_b == pytest.approx(0.0, abs=1e-9)
        assert lam_b == pytest.approx(90.0, abs=1e-9)
        assert h_b == pytest.approx(0.0, abs=1e-9)

        phi_it, lam_it, h_it = tr.cartesian_to_geodetic_iterative(0.0, tr.CLARKE_1880_IGN.a, 0.0)
        assert phi_it == pytest.approx(0.0, abs=1e-9)
        assert lam_it == pytest.approx(90.0, abs=1e-9)
        assert h_it == pytest.approx(0.0, abs=1e-9)

    def test_case_c_north_pole(self):
        """Cas C : Pôle Nord (φ=90°), surface de l'ellipsoïde (h=0m).

        Attendu : X = 0, Y = 0, Z = b.
        """
        X, Y, Z = tr.geodetic_to_cartesian(90.0, 0.0, 0.0)
        assert X == pytest.approx(0.0, abs=1e-9)
        assert Y == pytest.approx(0.0, abs=1e-9)
        assert Z == pytest.approx(tr.CLARKE_1880_IGN.b, abs=1e-9)

        # Inverses
        phi_b, lam_b, h_b = tr.cartesian_to_geodetic_direct(0.0, 0.0, tr.CLARKE_1880_IGN.b)
        assert phi_b == pytest.approx(90.0, abs=1e-9)
        assert h_b == pytest.approx(0.0, abs=1e-9)

        phi_it, lam_it, h_it = tr.cartesian_to_geodetic_iterative(0.0, 0.0, tr.CLARKE_1880_IGN.b)
        assert phi_it == pytest.approx(90.0, abs=1e-9)
        assert h_it == pytest.approx(0.0, abs=1e-9)

    def test_nontrivial_point_rabat_pyproj_independent_reference(self):
        """Point non-trivial au Maroc (Rabat) comparé à une référence pyproj précalculée.

        Ellipsoïde : Clarke 1880 (IGN), a = 6378249.2 m, b = 6356515.0 m.
        Coordonnées géodésiques d'entrée :
            φ = 34.020882° N
            λ = -6.841650° W
            h = 100.0 m

        Valeurs cartésiennes de référence obtenues indépendamment via pyproj
        (CRS : +proj=latlong +a=6378249.2 +b=6356515.0 vers +proj=geocent +a=6378249.2 +b=6356515.0) :
            X_REF = 5254544.235142349 m
            Y_REF = -630440.797713274 m
            Z_REF = 3548155.934675958 m
        """
        phi_in = 34.020882
        lam_in = -6.841650
        h_in = 100.0

        EXPECTED_X = 5254544.235142349
        EXPECTED_Y = -630440.797713274
        EXPECTED_Z = 3548155.934675958

        # 1. Vérification directe
        X, Y, Z = tr.geodetic_to_cartesian(phi_in, lam_in, h_in)
        assert X == pytest.approx(EXPECTED_X, abs=1e-4)
        assert Y == pytest.approx(EXPECTED_Y, abs=1e-4)
        assert Z == pytest.approx(EXPECTED_Z, abs=1e-4)

        # 2. Vérification inverse de Bowring contre les coordonnées de référence
        phi_b, lam_b, h_b = tr.cartesian_to_geodetic_direct(EXPECTED_X, EXPECTED_Y, EXPECTED_Z)
        assert phi_b == pytest.approx(phi_in, abs=1e-7)
        assert lam_b == pytest.approx(lam_in, abs=1e-7)
        assert h_b == pytest.approx(h_in, abs=1e-3)

        # 3. Vérification inverse itérative contre les coordonnées de référence
        phi_it, lam_it, h_it = tr.cartesian_to_geodetic_iterative(EXPECTED_X, EXPECTED_Y, EXPECTED_Z)
        assert phi_it == pytest.approx(phi_in, abs=1e-9)
        assert lam_it == pytest.approx(lam_in, abs=1e-9)
        assert h_it == pytest.approx(h_in, abs=1e-5)


# ===========================================================================
# 2. Tests aller-retour (Round-trip) pour plusieurs points (Maroc et globe)
# ===========================================================================


TEST_POINTS = [
    # Nom, φ (°), λ (°), h (m)
    ("Origine Merchich", 33.44849, -7.55566, 150.0),
    ("Rabat", 34.020882, -6.841650, 100.0),
    ("Marrakech", 31.629472, -7.981084, 460.0),
    ("Tanger", 35.759465, -5.833954, 20.0),
    ("Dépression Sebkha Tah (hauteur négative)", 27.716000, -12.233000, -50.0),
    ("Haute latitude Arctique", 85.000000, 45.000000, 1500.0),
    ("Haute latitude Antarctique", -82.500000, -110.000000, 2800.0),
    ("Antiméridien positif", 12.345678, 179.999999, 50.0),
    ("Antiméridien négatif", 12.345678, -179.999999, 50.0),
]


class TestRoundTripTransformations:
    """Tests d'aller-retour complets : Géodésique -> Cartésien -> Géodésique."""

    @pytest.mark.parametrize("name, phi_in, lam_in, h_in", TEST_POINTS)
    def test_round_trip_iterative(self, name, phi_in, lam_in, h_in):
        """Vérifie que la méthode itérative restaure fidèlement les coordonnées d'origine."""
        X, Y, Z = tr.geodetic_to_cartesian(phi_in, lam_in, h_in)
        res = tr.cartesian_to_geodetic_iterative(X, Y, Z)

        phi_rec, lam_rec, h_rec = res

        # Écarts
        d_phi = abs(phi_rec - phi_in)
        d_lam = tr.angular_difference_deg(lam_rec, lam_in)
        d_h = abs(h_rec - h_in)

        # Tolérances strictes pour la méthode itérative
        assert d_phi < 1e-8, f"[{name}] Erreur de latitude itérative trop grande: {d_phi}°"
        assert d_lam < 1e-8, f"[{name}] Erreur de longitude itérative trop grande: {d_lam}°"
        assert d_h < 1e-4, f"[{name}] Erreur de hauteur itérative trop grande: {d_h} m"
        assert res.iterations is not None and res.iterations > 0

    @pytest.mark.parametrize("name, phi_in, lam_in, h_in", TEST_POINTS)
    def test_round_trip_bowring(self, name, phi_in, lam_in, h_in):
        """Vérifie que l'approximation de Bowring restaure les coordonnées avec une précision sub-millimétrique."""
        X, Y, Z = tr.geodetic_to_cartesian(phi_in, lam_in, h_in)
        phi_rec, lam_rec, h_rec = tr.cartesian_to_geodetic_direct(X, Y, Z)

        d_phi = abs(phi_rec - phi_in)
        d_lam = tr.angular_difference_deg(lam_rec, lam_in)
        d_h = abs(h_rec - h_in)

        # Bowring est une approximation : précision attendue ~ 1e-6° sur φ et ~ 1 mm sur h
        assert d_phi < 1e-6, f"[{name}] Erreur de latitude Bowring: {d_phi}°"
        assert d_lam < 1e-8, f"[{name}] Erreur de longitude Bowring: {d_lam}°"
        assert d_h < 1e-3, f"[{name}] Erreur de hauteur Bowring: {d_h} m"

    def test_iterative_superiority_over_bowring(self):
        """Vérifie que la méthode itérative atteint une précision supérieure à celle de Bowring."""
        phi_in, lam_in, h_in = 45.0, 10.0, 5000.0
        X, Y, Z = tr.geodetic_to_cartesian(phi_in, lam_in, h_in)

        res_bowring = tr.cartesian_to_geodetic_direct(X, Y, Z)
        res_iter = tr.cartesian_to_geodetic_iterative(X, Y, Z, tolerance=1e-13)

        d_phi_bowring = abs(res_bowring.latitude - phi_in)
        d_phi_iter = abs(res_iter.latitude - phi_in)

        d_h_bowring = abs(res_bowring.height - h_in)
        d_h_iter = abs(res_iter.height - h_in)

        # L'erreur résiduelle itérative est inférieure ou égale à celle de Bowring
        assert d_phi_iter <= d_phi_bowring + 1e-15
        assert d_h_iter <= d_h_bowring + 1e-10


# ===========================================================================
# 3. Tests des cas limites, pôles, géocentre et quadrants
# ===========================================================================


class TestEdgeCasesAndValidation:
    """Tests des quadrants, cas limites, exceptions et erreurs de convergence."""

    @pytest.mark.parametrize(
        "lam_deg",
        [45.0, 135.0, -135.0, -45.0, 0.0, 90.0, 180.0, -180.0, -90.0],
    )
    def test_longitude_quadrants(self, lam_deg):
        """Vérifie que les 4 quadrants trigonométriques de longitude sont correctement résolus via atan2."""
        phi_deg = 20.0
        h = 50.0
        X, Y, Z = tr.geodetic_to_cartesian(phi_deg, lam_deg, h)

        # Méthode Bowring
        res_b = tr.cartesian_to_geodetic_direct(X, Y, Z)
        assert tr.angular_difference_deg(res_b.longitude, lam_deg) < 1e-9

        # Méthode Itérative
        res_it = tr.cartesian_to_geodetic_iterative(X, Y, Z)
        assert tr.angular_difference_deg(res_it.longitude, lam_deg) < 1e-9

    def test_south_pole(self):
        """Vérifie la gestion spécifique du pôle Sud (φ = -90°)."""
        X, Y, Z = tr.geodetic_to_cartesian(-90.0, 0.0, 100.0)
        assert X == pytest.approx(0.0, abs=1e-9)
        assert Y == pytest.approx(0.0, abs=1e-9)
        assert Z == pytest.approx(-(tr.CLARKE_1880_IGN.b + 100.0), abs=1e-9)

        # Inverses
        res_b = tr.cartesian_to_geodetic_direct(X, Y, Z)
        assert res_b.latitude == pytest.approx(-90.0, abs=1e-9)
        assert res_b.height == pytest.approx(100.0, abs=1e-9)

        res_it = tr.cartesian_to_geodetic_iterative(X, Y, Z)
        assert res_it.latitude == pytest.approx(-90.0, abs=1e-9)
        assert res_it.height == pytest.approx(100.0, abs=1e-9)

    def test_geocentre_undefined_behavior(self):
        """Vérifie que le géocentre (0, 0, 0) lève bien UndefinedCoordinateError."""
        with pytest.raises(tr.UndefinedCoordinateError):
            tr.cartesian_to_geodetic_direct(0.0, 0.0, 0.0)

        with pytest.raises(tr.UndefinedCoordinateError):
            tr.cartesian_to_geodetic_iterative(0.0, 0.0, 0.0)

    def test_invalid_latitudes(self):
        """Vérifie le rejet des latitudes hors limites (>90° ou <-90°)."""
        with pytest.raises(tr.InvalidCoordinateError):
            tr.geodetic_to_cartesian(90.001, 0.0, 0.0)

        with pytest.raises(tr.InvalidCoordinateError):
            tr.geodetic_to_cartesian(-90.001, 0.0, 0.0)

    def test_non_finite_inputs(self):
        """Vérifie le rejet des entrées non finies (NaN, inf)."""
        nan = float("nan")
        inf = float("inf")

        with pytest.raises(tr.InvalidCoordinateError):
            tr.geodetic_to_cartesian(nan, 0.0, 0.0)

        with pytest.raises(tr.InvalidCoordinateError):
            tr.geodetic_to_cartesian(0.0, inf, 0.0)

        with pytest.raises(tr.InvalidCoordinateError):
            tr.cartesian_to_geodetic_direct(nan, 100.0, 100.0)

        with pytest.raises(tr.InvalidCoordinateError):
            tr.cartesian_to_geodetic_iterative(100.0, 100.0, inf)

    def test_convergence_limit_error(self):
        """Vérifie que ConvergenceError est levée si max_iterations est trop faible avec une tolérance stricte."""
        X, Y, Z = tr.geodetic_to_cartesian(45.0, 10.0, 100.0)
        with pytest.raises(tr.ConvergenceError):
            # 1 itération ne suffit pas pour converger à 1e-15 rad
            tr.cartesian_to_geodetic_iterative(X, Y, Z, tolerance=1e-15, max_iterations=1)

    def test_invalid_iteration_parameters(self):
        """Vérifie le rejet des paramètres d'itération aberrants (tolérance négative ou itérations <= 0)."""
        X, Y, Z = tr.geodetic_to_cartesian(45.0, 10.0, 100.0)
        with pytest.raises(ValueError):
            tr.cartesian_to_geodetic_iterative(X, Y, Z, tolerance=-1e-5)

        with pytest.raises(ValueError):
            tr.cartesian_to_geodetic_iterative(X, Y, Z, max_iterations=0)


# ===========================================================================
# 4. Tests d'intégration de l'interface graphique PyQt5 (MainWindow)
# ===========================================================================


class TestGuiIntegration:
    """Vérifications de l'interface utilisateur PyQt5."""

    @pytest.fixture(autouse=True)
    def setup_gui(self):
        """Initialise QApplication pour l'exécution des tests d'interface."""
        from PyQt5.QtWidgets import QApplication
        import main
        self.app = QApplication.instance() or QApplication([])
        self.win = main.MainWindow()
        yield
        self.win.close()

    def test_window_title_and_tabs(self):
        """Vérifie le titre de la fenêtre et la présence des 3 onglets requis."""
        assert self.win.windowTitle() == "Geodesie Mini-Projet"
        assert self.win.tabs.count() == 3

    def test_gui_direct_and_inverse_calculation(self):
        """Vérifie le flux de calcul complet via les champs de l'interface."""
        # 1. Remplissage direct
        self.win.txt_phi.setText("34.020882")
        self.win.txt_lam.setText("-6.841650")
        self.win.txt_h.setText("100.0")
        self.win._handle_calculate_direct()

        assert float(self.win.txt_out_x.text()) == pytest.approx(5254544.2351, abs=1e-3)
        assert float(self.win.txt_out_y.text()) == pytest.approx(-630440.7977, abs=1e-3)
        assert float(self.win.txt_out_z.text()) == pytest.approx(3548155.9347, abs=1e-3)

        # 2. Transfert vers inverse itératif
        self.win.txt_in_x.setText(self.win.txt_out_x.text())
        self.win.txt_in_y.setText(self.win.txt_out_y.text())
        self.win.txt_in_z.setText(self.win.txt_out_z.text())
        self.win.radio_iterative.setChecked(True)
        self.win._handle_calculate_inverse()

        assert float(self.win.txt_out_phi.text()) == pytest.approx(34.020882, abs=1e-5)
        assert float(self.win.txt_out_lam.text()) == pytest.approx(-6.841650, abs=1e-5)
        assert float(self.win.txt_out_h.text()) == pytest.approx(100.0, abs=1e-2)
        assert "itération" in self.win.txt_out_iter.text()

    def test_gui_validation_tab_actions(self):
        """Vérifie que les trois boutons de test de l'onglet Validation s'exécutent sans erreur."""
        self.win._run_known_reference_tests()
        assert self.win.table_results.rowCount() == 8

        self.win._run_roundtrip_tests()
        assert self.win.table_results.rowCount() == 16

        self.win._compare_inverse_methods()
        assert self.win.table_results.rowCount() == 7

    def test_gui_dms_formatting_and_helpers(self):
        """Vérifie le formatage DMS et la mise à jour dynamique des étiquettes d'aide."""
        import main
        assert "34° 01' 15.18\" N" in main.format_dms(34.020882, is_latitude=True)
        assert "06° 50' 29.94\" W" in main.format_dms(-6.841650, is_latitude=False)

        self.win.txt_phi.setText("34.020882")
        self.win.txt_lam.setText("-6.841650")
        assert "DMS" in self.win.lbl_phi_dms.text()
        assert "DMS" in self.win.lbl_lam_dms.text()

    def test_gui_transfer_and_reset_workflow(self):
        """Vérifie le transfert bidirectionnel des résultats et la réinitialisation des champs."""
        # Calcul direct
        self.win.txt_phi.setText("34.020882")
        self.win.txt_lam.setText("-6.841650")
        self.win.txt_h.setText("100.0")
        self.win._handle_calculate_direct()

        # Transfert vers onglet inverse
        self.win._transfer_to_inverse()
        assert self.win.tabs.currentIndex() == 1
        assert self.win.txt_in_x.text() == self.win.txt_out_x.text()

        # Calcul inverse
        self.win._handle_calculate_inverse()

        # Transfert vers onglet direct
        self.win._transfer_to_direct()
        assert self.win.tabs.currentIndex() == 0
        assert float(self.win.txt_phi.text()) == pytest.approx(34.020882, abs=1e-5)

        # Réinitialisation
        self.win._reset_direct_fields()
        assert self.win.txt_phi.text() == ""
        assert self.win.txt_out_x.text() == ""

    def test_gui_resizing_flexibility(self):
        """Vérifie l'adaptabilité de la fenêtre : réduction (compacte) et agrandissement (large)."""
        # Test réduction (mode compact)
        self.win.resize(600, 450)
        self.app.processEvents()
        assert self.win.width() <= 650
        assert self.win.height() <= 500

        # Test agrandissement (mode étendu / grand écran)
        self.win.resize(1600, 1000)
        self.app.processEvents()
        assert self.win.width() >= 1500
        assert self.win.height() >= 950

        # Vérification de l'intégrité de tous les onglets lors des changements de dimensions
        for tab_idx in range(3):
            self.win.tabs.setCurrentIndex(tab_idx)
            self.app.processEvents()
            assert self.win.tabs.currentIndex() == tab_idx



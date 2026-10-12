"""Module de calcul et de transformations de coordonnées géodésiques tridimensionnelles.

Ce module met en œuvre les formules mathématiques rigoureuses pour :
1. La transformation directe :
   (latitude φ, longitude λ, hauteur ellipsoïdale h)
   vers les coordonnées cartésiennes géocentriques (X, Y, Z).
2. La transformation inverse :
   (X, Y, Z) vers (φ, λ, h) selon deux méthodes complémentaires :
   - Méthode A : Approximation directe en forme fermée de Bowring (1976).
   - Méthode B : Méthode itérative de convergence (Heiskanen & Moritz, 1967).

Système géodésique de référence :
- Ellipsoïde : Clarke 1880 (IGN) associé au datum géodésique Merchich (Maroc).
- Demi-grand axe : a = 6 378 249.200 m
- Demi-petit axe : b = 6 356 515.000 m
- Aplatissement : f = (a - b) / a ≈ 1 / 293.46602
- Première excentricité au carré : e² = 1 - b²/a² ≈ 0.0068034876
- Deuxième excentricité au carré : e'² = (a² - b²) / b² ≈ 0.0068500854

Distinctions géodésiques fondamentales :
- Le datum Merchich définit le système de référence géodésique 3D. Ce module
  transforme les coordonnées curvilignes (φ, λ, h) en coordonnées cartésiennes
  géocentriques (X, Y, Z) et réciproquement.
- Il ne met PAS en œuvre la projection plane cartographique Lambert
  (telle que Merchich / Nord Maroc, EPSG:26191 ou Sud Maroc, EPSG:26192)
  qui projette la surface ellipsoïdale sur un plan (E, N).
- Il n'applique PAS de transformation de datum (ex: transformation de Helmert
  à 7 paramètres) pour convertir Merchich vers le système mondial WGS 84 (EPSG:4326).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple, Union

if TYPE_CHECKING:
    import pyproj


class GeodeticError(Exception):
    """Exception de base pour les erreurs géodésiques."""


class InvalidCoordinateError(GeodeticError, ValueError):
    """Exception levée en cas de coordonnées invalides ou non finies (NaN, infini, hors bornes)."""


class UndefinedCoordinateError(GeodeticError, ValueError):
    """Exception levée pour les coordonnées géométriquement indéfinies (ex: géocentre X=Y=Z=0)."""


class ConvergenceError(GeodeticError, RuntimeError):
    """Exception levée si la méthode itérative n'atteint pas la convergence après le nombre max d'itérations."""


@dataclass(frozen=True)
class Ellipsoid:
    """Paramètres géométriques d'un ellipsoïde de révolution de référence.

    Un ellipsoïde de révolution aplati aux pôles est engendré par la rotation
    d'une ellipse autour de son petit axe (axe polaire de rotation terrestre).

    Attributs :
        name : Désignation de l'ellipsoïde (ex: "Clarke 1880 (IGN)").
        a : Demi-grand axe équatorial en mètres (rayon équatorial).
        b : Demi-petit axe polaire en mètres (rayon polaire).
    """

    name: str
    a: float  # Demi-grand axe équatorial (mètres)
    b: float  # Demi-petit axe polaire (mètres)

    @property
    def e2(self) -> float:
        """Première excentricité au carré e² = 1 - b²/a² = (a² - b²) / a².

        Grandeur adimensionnelle fondamentale gouvernant la géométrie mérienne
        et intervenant dans le calcul du rayon de courbure de la grande normale N(φ).
        """
        return 1.0 - (self.b * self.b) / (self.a * self.a)

    @property
    def ep2(self) -> float:
        """Deuxième excentricité au carré e'² = (a² - b²) / b² = e² / (1 - e²).

        Intervient directement dans la formulation fermée de Bowring pour le calcul
        de la latitude paramétrique réduite θ.
        """
        return (self.a * self.a - self.b * self.b) / (self.b * self.b)

    @property
    def f(self) -> float:
        """Aplatissement géométrique f = (a - b) / a.

        Mesure l'écart relatif entre la sphère équatoriale et l'ellipsoïde polaire.
        """
        return (self.a - self.b) / self.a


# Ellipsoïde Clarke 1880 (IGN) associé au datum historique Merchich (Maroc)
CLARKE_1880_IGN = Ellipsoid(
    name="Clarke 1880 (IGN)",
    a=6378249.2,
    b=6356515.0,
)


class CartesianPoint(NamedTuple):
    """Coordonnées cartésiennes géocentriques tridimensionnelles (X, Y, Z) en mètres.

    Repère cartésien géocentrique :
    - Origine (0, 0, 0) au centre de masse de l'ellipsoïde (géocentre).
    - Axe Z orienté vers le pôle Nord moyen (axe de rotation terrestre).
    - Axe X dirigé vers l'intersection du plan équatorial et du méridien origine (Greenwich, λ = 0°).
    - Axe Y orienté à 90° Est dans le plan équatorial, formant un trièdre direct (dextrogyre).
    """

    X: float
    Y: float
    Z: float


class GeodeticPoint(tuple):
    """Coordonnées géodésiques (latitude_deg, longitude_deg, hauteur_m).

    Hérite de tuple pour permettre un déballage direct transparent :
        phi, lam, h = point
    Tout en exposant des attributs nommés pour la clarté pédagogique :
        point.latitude, point.longitude, point.height, point.iterations
    """

    def __new__(
        cls,
        latitude: float,
        longitude: float,
        height: float,
        iterations: int | None = None,
    ) -> GeodeticPoint:
        return super().__new__(cls, (latitude, longitude, height))

    def __init__(
        self,
        latitude: float,
        longitude: float,
        height: float,
        iterations: int | None = None,
    ) -> None:
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.iterations = iterations

    @property
    def phi(self) -> float:
        """Latitude géodésique φ en degrés décimaux."""
        return self.latitude

    @property
    def lambda_(self) -> float:
        """Longitude géodésique λ en degrés décimaux."""
        return self.longitude

    @property
    def h(self) -> float:
        """Hauteur ellipsoïdale h en mètres (distance le long de la normale à l'ellipsoïde)."""
        return self.height

    def __repr__(self) -> str:
        iter_str = f", iterations={self.iterations}" if self.iterations is not None else ""
        return (
            f"GeodeticPoint(latitude={self.latitude:.8f}°, "
            f"longitude={self.longitude:.8f}°, height={self.height:.4f} m{iter_str})"
        )


def validate_geodetic_inputs(
    phi_deg: float,
    lambda_deg: float,
    h: float,
    min_height: float = -100_000.0,
    max_height: float = 100_000_000.0,
) -> None:
    """Valide les coordonnées géodésiques en entrée.

    Règles de validation :
    1. Valeurs finies requises : les types invalides, NaN et valeurs infinies (+inf, -inf)
       sont systématiquement rejetés pour éviter les instabilités numériques.
    2. Latitude géodésique φ : bornée dans l'intervalle strict [-90.0°, +90.0°].
       Les pôles correspondent à exactement ±90°.
    3. Longitude géodésique λ : doit être une valeur réelle finie.
    4. Hauteur ellipsoïdale h : doit être physiquement admissible [-100 km, +100 000 km].
       Remarque : les hauteurs négatives (ex: Sebkha Tah à -50 m, Mer Morte à -430 m)
       sont parfaitement valides et acceptées.
    """
    for name, val in [("Latitude φ", phi_deg), ("Longitude λ", lambda_deg), ("Hauteur h", h)]:
        if not isinstance(val, (int, float)) or not math.isfinite(val):
            raise InvalidCoordinateError(f"La valeur de '{name}' doit être un nombre réel fini, obtenu: {val}")

    if not (-90.0 <= phi_deg <= 90.0):
        raise InvalidCoordinateError(
            f"La latitude géodésique doit être comprise entre -90° et +90°, obtenu: {phi_deg}°"
        )

    if not (min_height <= h <= max_height):
        raise InvalidCoordinateError(
            f"La hauteur ellipsoïdale h doit être comprise entre {min_height} m et {max_height} m, obtenu: {h} m"
        )


def validate_cartesian_inputs(X: float, Y: float, Z: float) -> None:
    """Valide les coordonnées cartésiennes géocentriques en entrée.

    Règles de validation :
    - X, Y, Z doivent être des nombres réels finis (non NaN, non infinis).
    """
    for name, val in [("X", X), ("Y", Y), ("Z", Z)]:
        if not isinstance(val, (int, float)) or not math.isfinite(val):
            raise InvalidCoordinateError(f"La coordonnée cartésienne '{name}' doit être un nombre réel fini, obtenu: {val}")


def angular_difference_deg(deg1: float, deg2: float) -> float:
    """Calcule l'écart angulaire absolu minimal entre deux angles en degrés.

    Prend rigoureusement en compte la périodicité circulaire sur [-180°, +180°].
    Exemple : l'écart entre -179.999999° et +179.999999° est de 0.000002°,
    et non de 359.999998°.
    """
    diff = (deg1 - deg2 + 180.0) % 360.0 - 180.0
    return abs(diff)


def geodetic_to_cartesian(
    phi_deg: float,
    lambda_deg: float,
    h: float,
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
) -> CartesianPoint:
    """Transformation directe : Coordonnées géodésiques vers coordonnées cartésiennes (X, Y, Z).

    Raisonnement mathématique :
    1. Conversion angulaire degrés -> radians :
       Les fonctions trigonométriques standard de la bibliothèque Python (`math.sin`, `math.cos`)
       opèrent exclusivement sur des angles exprimés en radians. Les degrés décimaux saisis
       par l'utilisateur doivent donc impérativement être convertis via `math.radians()`.
    2. Rayon de courbure de la grande normale N(φ) (premier vertical) :
       N(φ) représente la distance, mesurée le long de la normale à l'ellipsoïde au point de
       latitude φ, entre la surface de l'ellipsoïde et son intersection avec l'axe polaire Z :
           N(φ) = a / sqrt(1 - e² * sin²(φ))
       À l'équateur (φ = 0°), N = a. Aux pôles (φ = ±90°), N = a / sqrt(1 - e²) = a² / b.
    3. Projection cartésienne 3D :
       Le point physique P se situe à une hauteur ellipsoïdale h au-dessus de la surface le long
       de la normale. La projection sur le plan équatorial a pour rayon :
           p = (N + h) * cos(φ)
       D'où :
           X = p * cos(λ) = (N + h) * cos(φ) * cos(λ)
           Y = p * sin(λ) = (N + h) * cos(φ) * sin(λ)
       Le long de l'axe Z, la composante intègre le facteur de réduction ellipsoïdale (1 - e²) :
           Z = (N * (1 - e²) + h) * sin(φ)

    Paramètres :
        phi_deg : Latitude géodésique en degrés [-90°, +90°].
        lambda_deg : Longitude géodésique en degrés [-180°, +180°].
        h : Hauteur ellipsoïdale en mètres.
        ellipsoid : Ellipsoïde de référence (par défaut Clarke 1880 IGN).

    Retourne :
        CartesianPoint(X, Y, Z) en mètres.
    """
    validate_geodetic_inputs(phi_deg, lambda_deg, h)

    a = ellipsoid.a
    e2 = ellipsoid.e2

    # Conversion essentielle degrés décimaux -> radians
    phi = math.radians(phi_deg)
    lam = math.radians(lambda_deg)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    # Grande normale N(φ) le long du premier vertical
    N = a / math.sqrt(1.0 - e2 * (sin_phi * sin_phi))

    # Équations directes fondamentales
    X = (N + h) * cos_phi * cos_lam
    Y = (N + h) * cos_phi * sin_lam
    Z = (N * (1.0 - e2) + h) * sin_phi

    return CartesianPoint(X, Y, Z)


def cartesian_to_geodetic_direct(
    X: float,
    Y: float,
    Z: float,
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
) -> GeodeticPoint:
    """Transformation inverse méthode A : Approximation fermée directe de Bowring (1976).

    Fondement mathématique et analyse de l'algorithme :
    La transformation inverse (X, Y, Z) -> (φ, λ, h) est non linéaire car l'inconnue φ
    apparaît simultanément dans la fonction N(φ) et dans les équations cartésiennes.

    B. R. Bowring (1976) a proposé une solution analytique directe remarquable en introduisant
    la latitude paramétrique réduite θ de l'ellipse méridienne :
        p = sqrt(X² + Y²)                  (distance à l'axe des pôles Z)
        θ = atan2(Z * a, p * b)             (angle paramétrique initial)

    À partir de θ, la latitude géodésique φ est obtenue directement par la formule fermée :
        φ = atan2(Z + e'² * b * sin³(θ), p - e² * a * cos³(θ))
    où :
        e²  = (a² - b²) / a²  (première excentricité au carré)
        e'² = (a² - b²) / b²  (deuxième excentricité au carré)

    La hauteur ellipsoïdale h est ensuite déduite par :
        N = a / sqrt(1 - e² * sin²(φ))
        h = p / cos(φ) - N   (si |cos(φ)| > 1e-10, formule équatoriale/moyenne)
        h = Z / sin(φ) - N * (1 - e²)   (aux hautes latitudes pour éviter division par zéro)

    Gestion de la longitude λ :
    λ = atan2(Y, X). L'utilisation de `math.atan2(Y, X)` est mathématiquement indispensable :
    contrairement à `math.atan(Y / X)` qui est indéterminée en X = 0 et perd le signe du quadrant,
    `atan2` discrimine automatiquement les 4 quadrants sur l'intervalle complet ]-π, +π].

    Cas particuliers :
    - Géocentre (X=0, Y=0, Z=0) : p = 0 et Z = 0. La normale à la surface et la longitude
      sont géométriquement indéterminées. Lève `UndefinedCoordinateError`.
    - Pôles géographiques (p < 1e-12) : φ = ±90°, λ = 0° (convention), h = |Z| - b.

    Précision :
    Pour toutes les altitudes terrestres (|h| < 10 000 m), l'erreur de l'approximation
    de Bowring est inférieure à 1e-7 degré (écart spatial sub-millimétrique sur l'ellipsoïde).
    """
    validate_cartesian_inputs(X, Y, Z)

    p = math.sqrt(X * X + Y * Y)

    # 1. Gestion rigoureuse de la singularité au géocentre
    if p == 0.0 and Z == 0.0:
        raise UndefinedCoordinateError(
            "Les coordonnées géodésiques (latitude et longitude) sont indéfinies au géocentre (X=0, Y=0, Z=0)."
        )

    a = ellipsoid.a
    b = ellipsoid.b
    e2 = ellipsoid.e2
    ep2 = ellipsoid.ep2

    # 2. Gestion rigoureuse des pôles géographiques (axe polaire Z, p ≈ 0)
    if p < 1e-12:
        phi_deg = 90.0 if Z > 0 else -90.0
        lambda_deg = 0.0
        h = abs(Z) - b
        return GeodeticPoint(phi_deg, lambda_deg, h)

    # 3. Formule paramétrique directe de Bowring (1976)
    theta = math.atan2(Z * a, p * b)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)

    numerator = Z + ep2 * b * (sin_theta**3)
    denominator = p - e2 * a * (cos_theta**3)
    phi = math.atan2(numerator, denominator)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)

    # Rayon de courbure de la grande normale pour le φ calculé
    N = a / math.sqrt(1.0 - e2 * (sin_phi * sin_phi))

    # 4. Calcul numériquement stable de la hauteur ellipsoïdale h
    # Lorsque φ est proche de ±90°, cos(φ) tend vers zéro, ce qui rend p / cos(φ) instable.
    # On bascule alors sur la formulation polaire : Z / sin(φ) - N * (1 - e²).
    if abs(cos_phi) > 1e-10:
        h = p / cos_phi - N
    else:
        h = Z / sin_phi - N * (1.0 - e2)

    # 5. Longitude via atan2 (gestion rigoureuse des 4 quadrants)
    lam = math.atan2(Y, X)

    # Conversion finale radians -> degrés décimaux pour restitution utilisateur
    phi_deg = math.degrees(phi)
    lambda_deg = math.degrees(lam)

    return GeodeticPoint(phi_deg, lambda_deg, h)


def cartesian_to_geodetic_iterative(
    X: float,
    Y: float,
    Z: float,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
    return_iterations: bool = False,
) -> Union[GeodeticPoint, tuple[float, float, float, int]]:
    """Transformation inverse méthode B : Méthode itérative de convergence (Heiskanen & Moritz).

    Raisonnement mathématique et déroulement de l'algorithme :
    Contrairement à la forme fermée approchée de Bowring, cette méthode résout le système
    non linéaire par approximations successives jusqu'à ce que la variation angulaire
    entre deux itérations soit inférieure à la tolérance spécifiée (par défaut 1e-12 rad,
    soit environ 0.006 mm à la surface de la Terre).

    Algorithme :
    1. Distance équatoriale : p = sqrt(X² + Y²)
    2. Longitude géodésique : λ = atan2(Y, X)  (calculée exactement au départ)
    3. Initialisation de la latitude (approximation sphérique initiale) :
       φ₀ = atan2(Z, p * (1 - e²))
    4. Boucle d'itération k (k = 1, 2, ..., max_iterations) :
       a. Grande normale : N_k = a / sqrt(1 - e² * sin²(φ_k))
       b. Hauteur approchée : h_k = p / cos(φ_k) - N_k
       c. Mise à jour de la latitude selon la relation géométrique exacte :
          φ_(k+1) = atan2(Z, p * [1 - e² * N_k / (N_k + h_k)])
       d. Test d'arrêt de convergence :
          Si |φ_(k+1) - φ_k| < tolerance :
              Convergence atteinte ! Calcul final de haute précision pour h et sortie.
          Sinon :
              φ_k = φ_(k+1)
    5. Si k dépasse max_iterations sans converger, lève une `ConvergenceError`.

    Paramètres :
        X, Y, Z : Coordonnées cartésiennes géocentriques en mètres.
        tolerance : Critère de convergence angulaire sur φ en radians (par défaut 1e-12 rad).
        max_iterations : Nombre maximal d'itérations autorisées (par défaut 100).
        ellipsoid : Ellipsoïde de référence (par défaut Clarke 1880 IGN).
        return_iterations : Si True, renvoie un tuple (phi_deg, lambda_deg, h, nb_iter).

    Retourne :
        GeodeticPoint(latitude_deg, longitude_deg, height_m, iterations=k)
        ou tuple (phi, lambda, h, k) si return_iterations=True.
    """
    validate_cartesian_inputs(X, Y, Z)

    if tolerance <= 0.0 or not math.isfinite(tolerance):
        raise ValueError(f"La tolérance doit être un nombre réel positif strictement supérieur à 0, obtenu: {tolerance}")
    if max_iterations <= 0:
        raise ValueError(f"Le nombre max d'itérations doit être supérieur à 0, obtenu: {max_iterations}")

    p = math.sqrt(X * X + Y * Y)

    # 1. Gestion du géocentre (indétermination mathématique)
    if p == 0.0 and Z == 0.0:
        raise UndefinedCoordinateError(
            "Les coordonnées géodésiques (latitude et longitude) sont indéfinies au géocentre (X=0, Y=0, Z=0)."
        )

    a = ellipsoid.a
    b = ellipsoid.b
    e2 = ellipsoid.e2

    # 2. Gestion des pôles géographiques (axe Z pur)
    if p < 1e-12:
        phi_deg = 90.0 if Z > 0 else -90.0
        lambda_deg = 0.0
        h = abs(Z) - b
        if return_iterations:
            return phi_deg, lambda_deg, h, 0
        return GeodeticPoint(phi_deg, lambda_deg, h, iterations=0)

    # 3. Longitude exacte
    lam = math.atan2(Y, X)

    # 4. Initialisation de la latitude géodésique φ₀
    phi = math.atan2(Z, p * (1.0 - e2))

    # 5. Processus itératif de convergence
    for iteration in range(1, max_iterations + 1):
        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)

        N = a / math.sqrt(1.0 - e2 * (sin_phi * sin_phi))

        if abs(cos_phi) > 1e-10:
            h = p / cos_phi - N
        else:
            h = Z / sin_phi - N * (1.0 - e2)

        # Mise à jour de la latitude via le rapport de courbure
        denom_ratio = 1.0 - e2 * (N / (N + h))
        phi_new = math.atan2(Z, p * denom_ratio)

        # Vérification du critère d'arrêt
        if abs(phi_new - phi) < tolerance:
            # Calcul final de haute précision pour h avec la latitude convergée phi_new
            sin_phi_final = math.sin(phi_new)
            cos_phi_final = math.cos(phi_new)
            N_final = a / math.sqrt(1.0 - e2 * (sin_phi_final * sin_phi_final))
            if abs(cos_phi_final) > 1e-10:
                h_final = p / cos_phi_final - N_final
            else:
                h_final = Z / sin_phi_final - N_final * (1.0 - e2)

            phi_deg = math.degrees(phi_new)
            lambda_deg = math.degrees(lam)

            if return_iterations:
                return phi_deg, lambda_deg, h_final, iteration
            return GeodeticPoint(phi_deg, lambda_deg, h_final, iterations=iteration)

        phi = phi_new

    # Si la boucle se termine sans satisfaire le critère de tolérance
    raise ConvergenceError(
        f"La méthode itérative n'a pas convergé après {max_iterations} itérations (tolérance: {tolerance} rad)."
    )


# ---------------------------------------------------------------------------
# Module d'indépendance de validation avec pyproj
# ---------------------------------------------------------------------------


def get_pyproj_transformer(
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
    inverse: bool = False,
):
    """Initialise un transformateur pyproj basé strictement sur les paramètres
    de l'ellipsoïde spécifié (ex: Clarke 1880 IGN pour Merchich).

    ATTENTION : Utilisé EXCLUSIVEMENT comme référence indépendante de validation externe
    afin de certifier la rigueur des algorithmes développés en pur Python.
    """
    import pyproj

    # Définition Proj explicite des CRS géodésique 3D et cartésien géocentrique
    proj_geo = f"+proj=latlong +a={ellipsoid.a} +b={ellipsoid.b} +no_defs"
    proj_geocent = f"+proj=geocent +a={ellipsoid.a} +b={ellipsoid.b} +units=m +no_defs"

    crs_geo = pyproj.CRS.from_proj4(proj_geo)
    crs_geocent = pyproj.CRS.from_proj4(proj_geocent)

    if not inverse:
        return pyproj.Transformer.from_crs(crs_geo, crs_geocent, always_xy=True)
    return pyproj.Transformer.from_crs(crs_geocent, crs_geo, always_xy=True)


def pyproj_reference_geodetic_to_cartesian(
    phi_deg: float,
    lambda_deg: float,
    h: float,
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
) -> tuple[float, float, float]:
    """Calcul de référence indépendant via pyproj pour la transformation directe."""
    transformer = get_pyproj_transformer(ellipsoid, inverse=False)
    # always_xy=True : x=longitude, y=latitude, z=hauteur
    x, y, z = transformer.transform(lambda_deg, phi_deg, h)
    return float(x), float(y), float(z)


def pyproj_reference_cartesian_to_geodetic(
    X: float,
    Y: float,
    Z: float,
    ellipsoid: Ellipsoid = CLARKE_1880_IGN,
) -> tuple[float, float, float]:
    """Calcul de référence indépendant via pyproj pour la transformation inverse."""
    transformer = get_pyproj_transformer(ellipsoid, inverse=True)
    lam, phi, h = transformer.transform(X, Y, Z)
    return float(phi), float(lam), float(h)

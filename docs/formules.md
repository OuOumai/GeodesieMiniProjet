# Formulaire Géodésique et Dérivations Mathématiques

Ce document constitue la référence mathématique détaillée pour le mini-projet de géodésie dédié aux transformations tridimensionnelles de coordonnées sur le système géodésique marocain **Merchich** (Ellipsoïde **Clarke 1880 IGN**).

---

## 1. Définitions des Notations et Unités

| Grandeur | Symbole | Unité SI / Pratique | Définition géométrique et physique |
| :--- | :---: | :---: | :--- |
| **Latitude géodésique** | $\varphi$ | Degrés décimaux ($^\circ$) / rad | Angle entre la normale à l'ellipsoïde au point considéré et le plan de l'équateur. Plage : $[-90^\circ, +90^\circ]$. |
| **Longitude géodésique** | $\lambda$ | Degrés décimaux ($^\circ$) / rad | Angle dièdre entre le plan méridien origine (Greenwich) et le plan méridien du point. Plage : $[-180^\circ, +180^\circ]$. |
| **Hauteur ellipsoïdale** | $h$ | Mètres ($\text{m}$) | Distance algébrique mesurée le long de la normale à l'ellipsoïde entre la surface de référence et le point physique $P$. |
| **Latitude géocentrique** | $\psi$ | Degrés décimaux ($^\circ$) / rad | Angle entre le rayon vecteur reliant le géocentre au point et le plan équatorial. $\tan\psi = (1 - e^2)\tan\varphi$. |
| **Latitude paramétrique (réduite)** | $\theta$ | Radians ($\text{rad}$) | Angle au centre du cercle principal circonscrit à l'ellipse méridienne, tel que $\tan\theta = \frac{b}{a}\tan\varphi$. |
| **Coordonnées géocentriques** | $X, Y, Z$ | Mètres ($\text{m}$) | Coordonnées dans le repère cartésien orthonormé direct centré au géocentre $O(0,0,0)$. |
| **Distance à l'axe des pôles** | $p$ | Mètres ($\text{m}$) | Rayon cylindrique $p = \sqrt{X^2 + Y^2}$ dans le plan parallèle à l'équateur. |
| **Grande normale (premier vertical)** | $N(\varphi)$ | Mètres ($\text{m}$) | Rayon de courbure de la section normale perpendiculaire au méridien (premier vertical). |
| **Demi-grand axe équatorial** | $a$ | Mètres ($\text{m}$) | Rayon de l'ellipsoïde dans le plan équatorial ($a = 6\,378\,249{,}200\text{ m}$). |
| **Demi-petit axe polaire** | $b$ | Mètres ($\text{m}$) | Rayon de l'ellipsoïde selon l'axe de rotation ($b = 6\,356\,515{,}000\text{ m}$). |

---

## 2. Paramètres et Constantes de l'Ellipsoïde Clarke 1880 (IGN)

Le système géodésique national marocain Merchich adopte les paramètres géométriques officiels de l'ellipsoïde de Clarke 1880 tels que définis par l'IGN :

$$
a = 6\,378\,249{,}200\text{ m}
$$

$$
b = 6\,356\,515{,}000\text{ m}
$$

### 2.1. Aplatissement géométrique ($f$)
L'aplatissement caractérise la déformation polaire de l'ellipsoïde par rapport à une sphère de rayon $a$ :
$$
f = \frac{a - b}{a} = \frac{6\,378\,249{,}2 - 6\,356\,515{,}0}{6\,378\,249{,}2} \approx 0{,}0034075495 \approx \frac{1}{293{,}46602}
$$

### 2.2. Première excentricité au carré ($e^2$)
Intervient dans toutes les équations de courbure et les transformations directes :
$$
e^2 = \frac{a^2 - b^2}{a^2} = 1 - \frac{b^2}{a^2} = 2f - f^2 \approx 0{,}0068034876
$$

### 2.3. Deuxième excentricité au carré ($e'^2$)
Intervient spécifiquement dans la formule de Bowring pour la latitude paramétrique :
$$
e'^2 = \frac{a^2 - b^2}{b^2} = \frac{a^2}{b^2} - 1 = \frac{e^2}{1 - e^2} \approx 0{,}0068500854
$$

---

## 3. Transformation Directe : $(\varphi, \lambda, h) \to (X, Y, Z)$

### 3.1. Conversion angulaire préalable
Dans l'implémentation Python, les angles $\varphi$ et $\lambda$ saisis en degrés décimaux sont convertis en radians avant tout appel aux fonctions trigonométriques :
$$
\varphi_{\text{rad}} = \varphi_{\text{deg}} \times \frac{\pi}{180}, \quad \lambda_{\text{rad}} = \lambda_{\text{deg}} \times \frac{\pi}{180}
$$

### 3.2. Rayon de courbure de la grande normale $N(\varphi)$
La grande normale représente la longueur du segment porté par la normale à l'ellipsoïde entre le point de la surface et l'intersection avec l'axe polaire $Z$ :
$$
N(\varphi) = \frac{a}{\sqrt{1 - e^2 \sin^2\varphi}}
$$

*Propriétés remarquables :*
- À l'équateur ($\varphi = 0$) : $N(0) = a = 6\,378\,249{,}200\text{ m}$.
- Aux pôles ($\varphi = \pm 90^\circ$) : $N(\pm 90^\circ) = \frac{a}{\sqrt{1 - e^2}} = \frac{a^2}{b} \approx 6\,400\,057{,}300\text{ m}$.

### 3.3. Équations de passage cartésien
Pour un point $P$ situé à une hauteur ellipsoïdale $h$ le long de la normale :
$$
\begin{cases}
X = (N(\varphi) + h) \cos\varphi \cos\lambda \\
Y = (N(\varphi) + h) \cos\varphi \sin\lambda \\
Z = [N(\varphi)(1 - e^2) + h] \sin\varphi
\end{cases}
$$

*Rayon géocentrique résultant :*
$$
R = \sqrt{X^2 + Y^2 + Z^2}
$$

---

## 4. Transformation Inverse : $(X, Y, Z) \to (\varphi, \lambda, h)$

La transformation inverse présente une non-linéarité fondamentale car la latitude $\varphi$ apparaît simultanément dans le terme de courbure $N(\varphi)$ et dans les expressions de $p$ et $Z$ :
$$
p = \sqrt{X^2 + Y^2} = (N(\varphi) + h)\cos\varphi
$$
$$
Z = [N(\varphi)(1 - e^2) + h]\sin\varphi
$$

### 4.1. Calcul exact de la longitude ($\lambda$)
La longitude géodésique se déduit directement par le rapport $Y / X$ :
$$
\lambda = \operatorname{atan2}(Y, X)
$$

> **Justification du choix de `atan2`** :  
> La fonction classique $\arctan(Y/X)$ présente une indétermination pour $X = 0$ (méridiens $\pm 90^\circ$) et est incapable de distinguer les quadrants opposés (par exemple $(+X, +Y)$ dans le 1er quadrant et $(-X, -Y)$ dans le 3e quadrant ont le même quotient $Y/X$).  
> La fonction `math.atan2(Y, X)` évalue le signe de $X$ et de $Y$ indépendamment et fournit l'angle unique sur l'intervalle complet $]-\pi, +\pi]$, évitant tout risque d'ambiguïté de quadrant.

---

### 4.2. Méthode A : Approximation directe de Bowring (1976)

La méthode de Bowring est une solution analytique en forme fermée non itérative.

1. **Calcul de la distance à l'axe polaire** :
   $$
   p = \sqrt{X^2 + Y^2}
   $$

2. **Estimation de la latitude paramétrique réduite ($\theta$)** :
   Bowring introduit l'angle paramétrique $\theta$ calculé par :
   $$
   \theta = \operatorname{atan2}(Z \cdot a,\, p \cdot b)
   $$

3. **Formule fermée pour la latitude géodésique ($\varphi$)** :
   En utilisant les puissances troisièmes $\sin^3\theta$ et $\cos^3\theta$, la courbure de l'ellipsoïde est compensée avec une fidélité sub-millimétrique :
   $$
   \varphi = \operatorname{atan2}\left(Z + e'^2 \cdot b \cdot \sin^3\theta,\; p - e^2 \cdot a \cdot \cos^3\theta\right)
   $$

4. **Calcul de la hauteur ellipsoïdale ($h$)** :
   $$
   N(\varphi) = \frac{a}{\sqrt{1 - e^2 \sin^2\varphi}}
   $$
   - En zone générale ($|\cos\varphi| > 10^{-10}$) :
     $$
     h = \frac{p}{\cos\varphi} - N(\varphi)
     $$
   - En zone polaire ($|\cos\varphi| \le 10^{-10}$) pour éviter une division par un cosinus quasi-nul :
     $$
     h = \frac{Z}{\sin\varphi} - N(\varphi)(1 - e^2)
     $$

**Nature de la méthode :** Il s'agit d'une approximation fermée. Pour toute altitude terrestre usuelle ($-100\text{ m} \le h \le 10\,000\text{ m}$), l'erreur maximale en latitude est inférieure à $10^{-7\circ}$ (environ $0{,}01\text{ mm}$ sur l'ellipsoïde).

---

### 4.3. Méthode B : Méthode itérative de convergence (Heiskanen & Moritz, 1967)

Cette méthode résout le problème par approximations successives jusqu'à ce que la solution converge à la précision machine.

1. **Initialisation ($\varphi_0$)** :
   La première approximation néglige la hauteur et prend la forme :
   $$
   \varphi_0 = \operatorname{atan2}(Z,\, p(1 - e^2))
   $$

2. **Équations de mise à jour à l'itération $k$ ($k \ge 1$)** :
   $$
   N_k = \frac{a}{\sqrt{1 - e^2 \sin^2\varphi_k}}
   $$
   $$
   h_k = \frac{p}{\cos\varphi_k} - N_k \quad (\text{ou formulation polaire si } |\cos\varphi_k| \le 10^{-10})
   $$
   $$
   \varphi_{k+1} = \operatorname{atan2}\left(Z,\, p\left[1 - e^2 \frac{N_k}{N_k + h_k}\right]\right)
   $$

3. **Critère d'arrêt et tolérance** :
   L'algorithme s'arrête dès que :
   $$
   |\varphi_{k+1} - \varphi_k| < \varepsilon
   $$
   Par défaut, $\varepsilon = 10^{-12}\text{ rad}$ (correspondant à environ $0{,}006\text{ mm}$ à la surface terrestre).

4. **Calcul final de $h$** :
   Lorsque le critère d'arrêt est satisfait, un calcul final de $N(\varphi_{\text{final}})$ et $h_{\text{final}}$ est exécuté avec la latitude convergée.

5. **Gestion de la non-convergence** :
   Si le nombre d'itérations atteint $k = \text{max\_iterations}$ (défaut : 100) sans satisfaire le critère, une exception `ConvergenceError` est explicitement levée. En pratique, pour des coordonnées terrestres réelles, la méthode converge en 3 à 4 itérations.

---

## 5. Traitement des Singularités et Cas Limites

### 5.1. Pôles géographiques ($p \to 0$)
Sur l'axe polaire $Z$, $X = 0$ et $Y = 0$, donc $p < 10^{-12}\text{ m}$ :
- La latitude vaut exactement $\varphi = +90^\circ$ si $Z > 0$ et $\varphi = -90^\circ$ si $Z < 0$.
- La longitude $\lambda$ est conventionnellement fixée à $0^\circ$.
- La hauteur ellipsoïdale vaut exactement :
  $$
  h = |Z| - b
  $$
L'algorithme détecte cette condition immédiatement sans division par zéro.

### 5.2. Géocentre ($X = 0, Y = 0, Z = 0$)
Au centre de masse de l'ellipsoïde, la normale à la surface et la longitude sont géométriquement indéfinies. Le code intercepte ce cas et lève une exception dédiée `UndefinedCoordinateError`.

### 5.3. Hauteurs négatives ($h < 0$)
Les dépressions terrestres naturelles (ex: Sebkha Tah au Maroc à $-50\text{ m}$, Mer Morte à $-430\text{ m}$) ont une hauteur ellipsoïdale négative. Les formules de Bowring et itérative sont mathématiquement valables pour $h < 0$, tant que $N + h > 0$.

### 5.4. Franchissement de l'antiméridien ($\lambda \approx \pm 180^\circ$)
La fonction `angular_difference_deg` prend en compte la discontinuité à $\pm 180^\circ$ par réduction modulaire :
$$
\Delta\lambda = \left[(\lambda_1 - \lambda_2 + 180^\circ) \bmod 360^\circ\right] - 180^\circ
$$
$$
|\Delta\lambda_{\text{circulaire}}| = |\Delta\lambda|
$$

---

## 6. Synthèse Comparative Numérique

| Critère | Méthode A : Bowring (1976) | Méthode B : Itérative (Heiskanen & Moritz) |
| :--- | :--- | :--- |
| **Type de méthode** | Forme fermée approchée | Résolution itérative exacte |
| **Nombre d'itérations** | 0 (calcul direct) | 3 à 4 itérations typiques |
| **Complexité temporelle** | $\mathcal{O}(1)$ déterministe | $\mathcal{O}(k)$ avec $k \le 4$ |
| **Précision en latitude** | Erreur $< 10^{-7\circ}$ ($\approx 0{,}01\text{ mm}$) | Précision machine ($\approx 10^{-12}\text{ rad}$) |
| **Précision en hauteur** | Erreur $< 1\text{ mm}$ pour $|h| < 10\text{ km}$ | Précision machine ($\approx 10^{-5}\text{ mm}$) |
| **Usage recommandé** | Topographie standard, SIG, temps réel | Géodésie spatiale, étalonnage de référence |

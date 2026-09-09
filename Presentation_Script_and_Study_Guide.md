# Průvodce a scénář k obhajobě: Analýza časových řad cestovního ruchu (20-25 minut)

Tento dokument slouží jako detailní scénář pro vaši obhajobu. Je strukturován tak, abyste krok za krokem logicky a sebevědomě prošli celou prací, vysvětlili **co** děláte, **proč** to děláte a přidali odborné zdůvodnění každého kroku. Dokument obsahuje i vizualizace z vašeho notebooku pro snazší orientaci.

---

## 1. Úvod a představení dat (cca 2-3 minuty)

**Co říct:**
"Dobrý den, vítám vás u obhajoby své semestrální práce. Cílem mé práce bylo najít optimální prediktivní model pro časovou řadu měsíčního počtu přenocování turistů v České republice (`nights_CZ_total`). Tato řada je z analytického hlediska nesmírně zajímavá, protože obsahuje silnou roční sezónnost, dlouhodobý růstový trend a především masivní strukturální zlom způsobený pandemií COVID-19."

**Odborné zdůvodnění (Proč?):**
* **Strukturální zlom:** Pandemie není jen běžný "šum" nebo anomálie. Změnila chování celého systému. Proto ji nesmíme ignorovat nebo data jen "smazat" (čímž bychom narušili časovou kontinuitu nezbytnou pro modely jako ARIMA). Místo toho ji budeme explicitně modelovat pomocí dummy proměnné.
* Data jsme stáhli přímo z Eurostat API a chybějící hodnoty u doplňkových řad jsme vyřešili lineární časovou interpolací, abychom nenarušili spojitost řad.

![Původní časová řada](./images/plot_1.png)

---

## 2. Grafická analýza a dekompozice (cca 4 minuty)

**Co říct:**
"Než přistoupím k modelování, musel jsem pochopit základní chování dat. Provedl jsem analýzu sezónnosti a robustní dekompozici pomocí metody STL a 12měsíčního klouzavého průměru."

![STL Dekompozice](./images/plot_3.png)

**Odborné zdůvodnění (Co a Proč?):**
* **Boxploty a sezónní profil:** Odhalily obrovské letní špičky (červenec/srpen) a zimní propady. Tvar není dokonalá sinusoida (letní špička je moc ostrá), což mě vedlo k myšlence použít v regresi více Fourierových členů.
* **STL (Seasonal and Trend decomposition using Loess):** Použil jsem robustní variantu STL, která je odolná vůči extrémům. Díky tomu pandemický propad nerozhodil odhad základní sezónní složky a plně se propsal do "reziduí" (zbytkové složky v grafech).
* **Klouzavý průměr:** Pro vyhlazení jsem použil klouzavý průměr s délkou okna 12, abych odstranil roční sezónnost. Protože je okno sudé a střed by padl mezi 6. a 7. měsíc, výpočet funguje jako **centrovaný 2×12 klouzavý průměr**.

---

## 3. Deterministické modelování - Fourierova regrese (cca 4 minuty)

**Co říct:**
"V prvním kroku modelování jsem zkusil popsat data čistě matematicky jako deterministickou funkci času. Zkoušel jsem lineární i kvadratický trend a pro složitý tvar sezónnosti jsem zvolil Fourierovy řady."

![Fourierova Regrese](./images/plot_5.png)

**Odborné zdůvodnění (Proč?):**
* **COVID Dummy:** Zavedl jsem proměnnou (0 a 1) pro období březen 2020 – prosinec 2021.
* **Fourierovy členy:** Místo 11 dummy proměnných pro měsíce jsem použil 5 harmonických složek (sinus a kosinus různých frekvencí). Je to elegantnější a flexibilnější způsob, jak zachytit onu ostrou letní špičku.
* **Proč model odmítáme jako finální?**
  I když model opticky krásně sedí (vysoké $R^2$), podíváme-li se na autokorelační funkci (ACF) reziduí a Ljung-Boxův test, vidíme problém:

![ACF Fourierových reziduí](./images/plot_6.png)

V ACF vidíme obrovský pozitivní pík u zpoždění 1 ($r \approx 0.68$) a další významný pík u sezónního zpoždění 12. To znamená, že rezidua nejsou bílý šum. Model nevysvětlil krátkodobou paměť dat a část sezónnosti.

---

## 4. Model SARIMA (cca 4 minuty)

**Co říct:**
"Protože rezidua deterministického modelu byla silně autokorelovaná, přešel jsem na stochastické modelování pomocí SARIMA modelu, který tuto 'paměť' dokáže zachytit."

**Odborné zdůvodnění (Co a Proč?):**
* **Volba parametrů pomocí auto.arima:** Pro výběr řádů p, d, q, P, D, Q jsem použil balíček `pmdarima` s parametrem `stepwise=True`, aby byl výpočet rychlý a efektivní.
* **Rovnice modelu:** Model vybral řád $SARIMA(2,0,0)(0,0,2)_{12}$. Výsledek byl mnohem lepší než u regrese, ale ACF reziduí ukázalo, že u vyšších sezónních zpoždění pořád zůstává určitá nezachycená závislost. 

![SARIMA Forecast](./images/plot_8.png)

---

## 5. Kroskorelace a SARIMAX (cca 5 minut)

**Co říct:**
"Jelikož samotná česká data nestačila k úplnému vysvětlení variability, rozhodl jsem se zapojit externí proměnné z okolních států (počet příjezdů a přenocování z DE, PL, SK). Přistoupil jsem k modelu SARIMAX."

**Odborné zdůvodnění (Co a Proč?):**
* **Kroskorelační funkce (CCF):** Abych předešel zdánlivé korelaci (spurious correlation) způsobené společným trendem a sezónností, neočišťoval jsem původní řady, ale prováděl jsem kroskorelaci na jejich *reziduích* (po odstranění deterministické složky a COVIDu).
* **Lag 0:** Kroskorelace ukázala, že největší závislost je u zpoždění 0. Ekonomicky to dává smysl – turistická sezóna v Německu a Polsku vrcholí ve stejných měsících jako u nás. Přebytek turistů se přelévá okamžitě v daném měsíci.
* **Finální SARIMAX Model:** Použil jsem model se 3 externími regresory (přenocování v DE, PL, SK).

---

## 6. Diagnostika a Periodogram (cca 2 minuty)

**Co říct:**
"Abych potvrdil, že jsou mé předpoklady správné, provedl jsem sérii diagnostických testů."

![Periodogram](./images/plot_16.png)

**Odborné zdůvodnění:**
* **Periodogram:** Očekával jsem roční sezónnost. Transformací dat do frekvenční domény jsem získal periodogram, kde absolutně největší výkon leží přesně na periodě 12 měsíců. Toto je objektivní matematický důkaz.
* **Kritéria kvality:** Náš finální SARIMAX model dosáhl nejnižší hodnoty Akaikeho informačního kritéria (AIC $\approx$ 3663) a měl absolutně nejnižší RMSE (chybu).

---

## 7. Závěr a Predikce (cca 3 minuty)

**Co říct:**
"V posledním kroku jsem pomocí všech tří hlavních modelů odhadl vývoj na 10 budoucích měsíců a modely vizuálně porovnal."

![Porovnání Predikcí](./images/plot_20.png)

**Odborné zdůvodnění:**
* Na společném grafu jasně vidíme, proč je SARIMAX vítězem. 
* Fourierova regrese má zavádějící intervaly spolehlivosti kvůli ignorování autokorelace.
* Čistá SARIMA modeluje pouze z historie a její predikce měla velmi široké intervaly.
* **SARIMAX** naopak dokázal zkombinovat historickou paměť řady a extra znalosti z okolních zemí (DE, PL, SK). Výsledná predikce je nejrealističtější a má výrazně užší intervaly spolehlivosti. 

"Tímto považuji cíl práce, tedy nalezení optimálního modelu pro vybranou časovou řadu, za splněný. Děkuji za pozornost a jsem připraven na vaše otázky."

---

## 8. Otázky a Odpovědi na specifické dotazy vedoucí (Příprava na obhajobu)

Zde jsou přesné a vyčerpávající odpovědi na konkrétní dotazy vaší vedoucí, připravené ke čtení/odpovědi u komise.

### i) Šířka okna klouzavých průměrů (12 vs liché číslo)
**Otázka vedoucí:** *Při vyhlazování dat pomocí klouzavých průměrů používáte šířku okna 12. Na hodinách jsem Vám říkala, že většinou se používá okno liché délky. Dokážete vysvětlit proč a jak byste tento požadavek řešil ve Vašem případě?*
**Odpověď:** Liché okno (např. 3, 5, 7) se používá proto, že průměr přirozeně padne přesně na prostřední pozorování (na konkrétní měsíc). U sudého okna jako je 12 (které ale potřebujeme k vyhlazení roční sezónnosti) padne střed "mezi" 6. a 7. měsíc. V praxi se tento požadavek řeší tzv. **centrovaným klouzavým průměrem (např. 2x12)**. To znamená, že nejprve spočítáme 12měsíční klouzavý průměr a následně na tyto výsledky aplikujeme 2měsíční klouzavý průměr. Tím dojde k polovičnímu posunu a hodnota "dosadne" přesně na daný měsíc. V mém kódu v Pythonu to řeší parametr `center=True`, který toto centrování algoritmicky zajišťuje.

### ii) Exponenciální vyrovnání (Proč chybí a jaké by bylo nejlepší)
**Otázka vedoucí:** *Mezi vyzkoušené postupy jste nezařadil žádný model exponenciálního vyrovnání? Jaký by byl pro Vaše data nejlepší? Zkuste si jeden spočítat a podívat se, jak mu vyšly parametry a co znamenají.*
**Odpověď:** Pro má data, která mají trend i sezónnost, by byl nejlepší model **Holt-Winters (Trojité exponenciální vyrovnání)** v aditivní podobě.
Pro zajímavost jsem ho na data zpětně napasoval a vyšly následující vyhlazovací parametry:
* **Úroveň ($\alpha \approx 1.0$):** Extrémně vysoká hodnota. Model dává téměř 100% váhu nejnovějším datům, aby mohl okamžitě zareagovat na obrovský pandemický propad.
* **Trend ($\beta \approx 0.035$):** Velmi nízká hodnota. Znamená to, že sklon trendu se v čase mění jen velmi pozvolna.
* **Sezónnost ($\gamma \approx 0.0$):** Blíží se nule. Sezónní výkyvy (léto/zima) jsou v čase extrémně stabilní a nepotřebují dynamicky upravovat.
**Proč jsem ho nezařadil:** Hodnota AIC u Holt-Wintersova modelu byla cca 4251, což je výrazně horší (vyšší) než u mého SARIMAX modelu (AIC cca 3663).

### iii) Vylepšení modelování pandemie u regresních modelů (Blok 5)
**Otázka vedoucí:** *V bloku 5 jste velice pěkně volil proměnné. Přesto má výsledný model v oblasti pandemie mírné nedostatky. Napadne Vás, jak by bylo možné je ještě trochu vylepšit?*
**Odpověď:** Ano, pandemii jsem modeloval pomocí jediné "dummy" proměnné (hodnota 1 pro celé období březen 2020 – prosinec 2021). To vytvoří v grafu jednoduchý schod, tedy obdélníkový jednorázový propad. Ve skutečnosti měla pandemie více vln (jarní lockdown, letní rozvolnění, zimní uzávěry).
Model bych mohl vylepšit dvěma způsoby:
1. Použitím **více dummy proměnných** pro jednotlivé vlny pandemie (např. covid_wave1, covid_wave2).
2. Profesionálnější by bylo využití **Intervenční analýzy**, kde bych šok definoval jako "Pulse" (náhlý propad) s následným "Decay" efektem (pozvolné zotavování turistického ruchu).

### v) ACF reziduí modelu z bloku 5
**Otázka vedoucí:** *Co všechno vidíte v autokorelační funkci reziduí modelu z bloku 5?*
**Odpověď:** V grafu ACF jsou vidět dva naprosto zásadní problémy:
1. Obrovský pozitivní pík u **zpoždění 1** ($r \approx 0.68$). To znamená, že deterministický model nevysvětlil krátkodobou paměť (AR proces) dat.
2. Další významný pík u **sezónního zpoždění 12** ($r \approx 0.30$). To znamená, že i přes použití Fourierových členů tam zbyla určitá sezónní dynamika, kterou model nepokryl.
Závěr z toho plyne jasný: chyby nejsou "bílým šumem", jsou závislé, což porušuje předpoklady OLS regrese a je to pádný argument pro přechod na SARIMA modely.

### vi) Rovnice odhadnutého SARIMA modelu
**Otázka vedoucí:** *Zkuste, prosím, napsat rovnici odhadnutého SARIMA modelu s využitím konkrétních odhadů jednotlivých koeficientů?*
**Odpověď:** Model `auto.arima` vybral strukturu $SARIMA(2,0,0)(0,0,2)_{12}$. Odhadnuté koeficienty byly zhruba: $AR_1 = 1.183$, $AR_2 = -0.254$, $SMA_1 = 0.773$, $SMA_2 = 0.598$.
Rovnice (kde $Y_t$ jsou data a $\epsilon_t$ je chybový bílý šum) vypadá takto:
$$ Y_t = 1.183 Y_{t-1} - 0.254 Y_{t-2} + \epsilon_t + 0.773 \epsilon_{t-12} + 0.598 \epsilon_{t-24} $$

### vii) Připomínka k odhadnutým koeficientům SARIMAX modelu
**Otázka vedoucí:** *U výpisu nejlepšího SARIMAX modelu bych měla jednu připomínku k odhadnutým koeficientům, odhadnete jakou?*
**Odpověď:** Jde o takový malý chyták v summary tabulce modelu. Všechny naše externí proměnné (přenocování v DE, PL, SK) a většina zpoždění měly $p-hodnotu \approx 0.000$ (byly plně signifikantní). 
Pokud se ale podíváte na koeficient pro **AR(2)** člen, jeho hodnota je $-0.0071$ a jeho **p-hodnota je 0.949**. To znamená, že tento člen je statisticky naprosto nevýznamný. Připomínka spočívá v tom, že ačkoliv tento složitější model vyhrál díky AIC kritériu, z hlediska tzv. pravidla parsimonie (úspornosti) bychom mohli člen AR(2) z modelu bez obav vyřadit a používat jednodušší chybovou strukturu $ARIMA(1,0,0)(0,0,2)_{12}$ se zachováním stejné kvality predikce.

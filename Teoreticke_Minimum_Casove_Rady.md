# Teoretické minimum a Vizuální tahák: Analýza časových řad

Tento dokument spojuje podrobné lidské vysvětlení teorie s rychlým vizuálním tahákem. Je navržen tak, abyste pochopil všechny pojmy do hloubky a zároveň měl po ruce rychlý přehled pro obhajobu.

---

# ČÁST 1: TEORETICKÉ MINIMUM (Podrobné vysvětlení)

## 1. Základní stavební kameny

### Co je to časová řada?
Časová řada (Time Series) je zkrátka posloupnost hodnot měřených postupně v čase (např. každý den, měsíc nebo rok). Hlavním cílem analýzy je pochopit minulost a na jejím základě **predikovat budoucnost**.

Každá časová řada se skládá ze tří (až čtyř) základních složek:
1. **Trend ($T_t$):** Dlouhodobý vývoj. Znamená to, že data dlouhodobě rostou (vzkvétající turismus) nebo klesají.
2. **Sezónnost ($S_t$):** Pravidelně se opakující kolísání s pevnou periodou. U vás je to 12 měsíců (v létě je hodně turistů, v zimě málo).
3. **Cyklická složka ($C_t$):** Kolísání, které nemá pevnou délku (např. hospodářské krize). Často se spojuje s trendem.
4. **Šum / Rezidua ($R_t$):** Náhodná, nevysvětlitelná složka. To, co zbyde, když z dat odečteme trend a sezónnost.

### Důležité pojmy: Stacionarita a Bílý šum
* **Stacionarita (Stationarity):** Říkáme, že řada je stacionární, pokud se její chování v čase nemění. Nemá trend (nepadá ani neroste) a nemá sezónnost. Její průměr a rozptyl jsou konstantní. Většina modelů vyžaduje, aby data byla stacionární. Pokud nejsou (mají trend), musíme je tzv. "diferencovat" (odečítat hodnoty od sebe).
* **Bílý šum (White Noise):** Ideální stav reziduí (zbytků). Jde o čistě náhodné hodnoty, které nemají žádný trend, žádnou sezónnost a **nejsou na sobě nijak závislé**. Cílem každého dobrého modelu je, aby to, co model "neodhadne" (chyby), byl čistý bílý šum.

## 2. Metody vyhlazování a dekompozice

### Klouzavý průměr (Moving Average - MA)
* **Co to je:** Technika na "vyhlazení" rozskákaných dat. Spočítá průměr z několika sousedních hodnot (např. 12 měsíců).
* **Proč 12 měsíců?** Tím, že zprůměrujeme celý rok, se vymaže sezónnost.
* **Problém sudého okna:** 12 měsíců nemá přesný střed (je mezi 6. a 7. měsícem). Proto děláme **2x12 (centrovaný) klouzavý průměr** – průměrujeme ještě jednou dvěma měsíci, aby výsledek sedl přesně na jeden měsíc.

### STL Dekompozice
* **Co to je:** Rozkládá data na Trend, Sezónnost a Rezidua pomocí robustní lokální regrese (Loess). 
* **Proč je lepší?** Je velmi odolná vůči extrémním výkyvům. Když přišel COVID-19, obyčejný průměr by se zbláznil, STL propad vyhodí do reziduí a nezničí odhad běžné sezónnosti.

## 3. Diagnostické nástroje: Jak model kontrolovat?

### ACF a PACF (Autokorelační funkce)
* **ACF (Autocorrelation Function):** Měří, jak moc je dnešní hodnota závislá na minulé (např. před 1 měsícem, před 2 měsíci...). Pokud máme v ACF reziduí čáru nad kritickou mezí, znamená to, že v datech zbyla nevyužitá informace a chyby nejsou nezávislé.
* **PACF (Partial ACF):** Měří "čistý" vliv. (Odfiltruje zprostředkovaný vliv vnitřních kroků a řekne nám, jaký je *přímý* vliv např. 2 měsíců zpět na dnešek).

### Ljung-Boxův test
* **K čemu slouží:** Statistický test, který zkoumá ACF jako celek. Ptá se: *"Jsou tato rezidua jen náhodný bílý šum?"*
* **Interpretace:** Hledáme **vysokou p-hodnotu (p > 0.05)**. Pokud je p < 0.05, rezidua jsou závislá (model je špatný, unikla mu nějaká informace).

### Periodogram
* **Co to je:** Převádí data z "osy času" na "osu frekvencí". Není-li zřejmé, jakou mají data sezónnost, periodogram najde dominantní "cyklus". (U vás pík na frekvenci $\frac{1}{12}$ jasně dokazuje 12měsíční periodu).

## 4. Přístupy k modelování

### A. Deterministické modelování (Regrese s Fourierovými členy)
* **Přístup:** Snažíme se popsat data pevnou matematickou funkcí času (např. $Y = a + b \cdot čas$).
* **Fourierovy řady:** K popisu ročních vln se místo dummy proměnných použije součet funkcí Sinus a Kosinus různých frekvencí.
* **Problém:** Deterministický model nepočítá s tím, že se chyba z minulého měsíce přenese do dalšího. U turismu to tak funguje, proto deterministický model propadl u Ljung-Boxova testu.

### B. Stochastické modelování (SARIMA)
Zkratka pro **Seasonal AutoRegressive Integrated Moving Average**. Modeluje data na základě vlastní minulosti a chyb. Skládá se z:
* **AR (p, P) - Autoregrese:** Dnešní hodnota se vypočítá jako procento včerejší hodnoty.
* **I (d, D) - Integrace:** Udává, kolikrát musíme data odečíst (diferencovat), abychom se zbavili trendu a získali stacionární řadu.
* **MA (q, Q) - Moving Average (chyb):** Dnešní hodnota je ovlivněna náhodnými šoky (chybami) z minulosti.
* **Velká písmena (P, D, Q)** znamenají to samé, ale pro sezónní složku (např. o 12 měsíců zpět).

### C. SARIMAX (SARIMA + eXogenní proměnné)
* **Proč vylepšovat SARIMU?** SARIMA je "slepá" vůči vnějšímu světu. Kouká jen na vlastní historii.
* **Exogenní proměnné (X):** Vnější vlivy (Německo, Polsko, Slovensko). SARIMAX dokáže započítat vnější nával turistů a zbytek nevysvětlených chyb modeluje klasickou SARIMOU.
* **Kroskorelační funkce (CCF):** Abychom věděli, jestli použít data z Německa s nějakým zpožděním, použili jsme CCF. Vám vyšel nejvyšší Lag 0 (reagují okamžitě ve stejném měsíci).

## 4.5 Rozdíly mezi ARIMA, SARIMA a SARIMAX (Kdy a jaký použít)

| Model | Zkratka znamená | Kdy jej použít | Nevýhody / Omezení |
|---|---|---|---|
| **ARIMA** | AutoRegressive Integrated Moving Average | Pokud data **nemají** žádnou roční/pravidelnou sezónnost, ale mají trend a paměť (např. denní ceny akcií). | Naprosto selže, pokud se v datech opakují pravidelné cykly (např. letní turismus). |
| **SARIMA** | **Seasonal** ARIMA | Pokud data mají **i trend, i sezónnost**. K predikci jí stačí jen samotná historie dané řady (např. počet turistů letos počítá z loňska). | Je "slepá" vůči okolnímu světu. Nedokáže reagovat na vnější vlivy (např. státní svátky, ekonomické šoky v cizině). |
| **SARIMAX** | SARIMA s e**X**ogenními proměnnými | Když chceme model vylepšit o vnější vlivy (např. vliv počasí, německých turistů, inflace). | Nejtěžší na modelování. K předpovědi budoucnosti ČR musíme znát/umět odhadnout i budoucnost těch externích X proměnných (Německa). |

## 4.6 Jak najít nejlepší parametry (p, d, q, P, D, Q)?
Při hledání správných čísel do závorky (např. $SARIMA(2,0,0)(0,0,2)_{12}$) existují v praxi dva hlavní přístupy:

1. **Manuální hledání (tzv. Box-Jenkinsova metodologie):**
   * **Hledání d, D:** Odstraníme trend a sezónnost pomocí "diferenciace" (odečítání hodnot od sebe), dokud řada nevypadá jako stacionární (rozlítaný šum kolem nuly). Tím určíme $d$ a $D$.
   * **Hledání p, q z grafů:** Vykreslíme si ACF a PACF na již diferencovaných (stacionárních) datech. Podle toho, kolik sloupců trčí z PACF, určíme $p$. Podle ACF určíme $q$.
   * *Výhoda/Nevýhoda:* Máte plnou kontrolu, ale je to extrémně pracné, dost subjektivní a často se v interpretaci grafů člověk splete.

2. **Automatické hledání (Grid Search / auto.arima):**
   * Moderní přístup, **který jste použili ve své práci**. Funkce vyzkouší spoustu kombinací parametrů a pro každou spočítá AIC kritérium. Vybere tu vítěznou.
   * **Stepwise vyhledávání (Hyndman-Khandakar algoritmus):** Abyste nečekal hodiny, než se spočítají *všechny* možné kombinace, použil jste parametr `stepwise=True`. Algoritmus postupuje chytře – vezme základní model, zkusí k němu sousední (přidá/ubere 1 k $p$ nebo $q$) a jde jako po schodech tím směrem, kde se snižuje AIC. Výpočet zkrátí z hodin na vteřiny.

## 5. Hodnocení modelů (Jak poznat vítěze)
1. **RMSE (Root Mean Squared Error):** Udává průměrnou odchylku modelu od reality. Čím nižší, tím lepší predikce. SARIMAX měl nejnižší RMSE.
2. **AIC (Akaike Information Criterion):** Metrika vyvažující přesnost a složitost. Dává modelu trestné body za každou zbytečnou proměnnou (aby nedošlo k "přeucení" neboli overfittingu). **Nejnižší AIC vyhrává**.

---

# ČÁST 2: VIZUÁLNÍ TAHÁK (Rychlý přehled s grafy)

## 1. Zlatá pravidla časových řad v praxi
Aby fungovala ARIMA, musíme se zbavit trendu a sezónnosti. Na původních datech vidíme oboje, navíc obří propad.

![Původní nestacionární data](./images/plot_1.png)

---

## 2. Anatomie modelu: $ARIMA(p, d, q)$

### 🟢 AR = AutoRegressive (parametr $p$)
* **Lidsky:** Dnešní hodnota počítána z minulých hodnot (např. $p=1$ znamená závislost jen na včerejšku).
* **Jak se hledá:** Podle grafu **PACF** (vpravo).

### 🔵 I = Integrated (parametr $d$)
* **Lidsky:** Diferenciace. Kolikrát musím data odečíst, abych zabil trend. U stacionární řady $d=0$.

### 🔴 MA = Moving Average chyb (parametr $q$)
* **Lidsky:** Závislost na minulých chybách (šocích).
* **Jak se hledá:** Podle grafu **ACF** (vlevo).

*(Vlevo: ACF extrémně závislá; Vpravo: PACF)*
![ACF a PACF](./images/plot_7.png)

### 🔎 Jak správně číst ACF a PACF grafy (Návod k interpretaci)
Pokud se vás u obhajoby zeptají, co vlastně ty "modré čáry" znamenají, řiďte se tímto:
1. **Osa X (Lags / Zpoždění):** Čísla dole představují "počet měsíců do minulosti". Jednička znamená minulý měsíc, dvanáctka znamená stejný měsíc loni. První čára u nuly (která je vždycky 1.0) se ignoruje – je to závislost dnešku na dnešku.
2. **Osa Y (Korelace):** Čím vyšší sloupec (směrem nahoru nebo dolů), tím silnější je závislost na daném minulém měsíci.
3. **Modrá stínovaná zóna:** Toto je hranice "šumu" (interval spolehlivosti, obvykle 95%). Cokoliv leží **uvnitř** této zóny, je statisticky zanedbatelné (nula). Cokoliv trčí **ven ze zóny**, má na dnešek prokazatelný matematický vliv.
4. **Určení $p$ a $q$:** 
   * Pokud z grafu PACF trčí ven jen první dva sloupce a zbytek spadne do modré zóny, parametr $p = 2$.
   * Pokud z grafu ACF trčí ven první sloupec a pak to "usekne", parametr $q = 1$.
5. **Jak číst váš graf nahoře:** Na obrázku vlevo (ACF) vidíte, že sloupce klesají extrémně pomalu a vlní se. To je učebnicový důkaz, že řada **není stacionární** a má obrovskou sezónnost (silné píky na 12, 24, 36). Abychom mohli odhadnout $p$ a $q$, musíme data nejprve diferencovat (vymazat trend a sezónnost), což dělá právě parametr $d$ a $D$.

---

## 3. SARIMA: Přidání sezónnosti

### $SARIMA (p,d,q) \times (P,D,Q)_{12}$
* **Sezónní AR ($P$):** Jak moc dnešní červenec závisí na červenci loňského roku?
* **Sezónní I ($D$):** Odečtení celého roku k zabití sezónnosti.
* **Sezónní MA ($Q$):** Chyba z loňského léta ovlivní i to letošní.

**Váš model:** $SARIMA (2,0,0)(0,0,2)_{12}$
* Dnešek závisí na 2 minulých měsících ($p=2$).
* Náhodný šok z loňska a předloňska ovlivňuje letošek ($Q=2$).
* Diferencovat nebylo pro kód nutné ($d=0, D=0$).

![Předpověď pomocí SARIMA modelu](./images/plot_8.png)

---

## 4. Rychlá Diagnostika z grafů

1. **Ljung-Boxův test:** Má být nad 0.05. Testuje, jestli už je to konečně "Bílý šum".
2. **ACF reziduí:** Sloupce by neměly trčet ven z modré stínované zóny.
   *Zde je ukázka špatného modelu (Deterministická regrese). Všimněte si píků na 1 a 12, což znamená, že v datech zbyla informace:*
   ![Špatné ACF - Zůstala informace](./images/plot_6.png)
3. **Periodogram:** Osuje absolutně největší pík u 12. To je neprůstřelný matematický důkaz sezónnosti.
   ![Periodogram](./images/plot_16.png)

---
*Tento dokument používejte jako odrazový můstek pro vaši obhajobu. Pokud chápete, co je napsáno zde, máte problematiku dokonale pod kontrolou.*

import json
import os

notebook_path = r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\seminarni_prace.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'markdown':
        if len(cell['source']) > 0 and 'auto_arima' in cell['source'][0] and 'Finální srovnávací tabulky' in cell['source'][0]:
            # This is cell 30
            original_text = cell['source'][0]
            
            # The new text that adds the justification for auto.arima
            new_text = "Následující blok použije `auto_arima` (z balíčku `pmdarima`) pro nalezení optimálního řádu SARIMA modelu. " \
                       "Aby se předešlo známému problému, kdy může být automatické hledání výpočetně velmi náročné a zdlouhavé, " \
                       "je využit parametr `stepwise=True`. Ten místo vyčerpávajícího (exhaustive) prohledávání všech kombinací " \
                       "implementuje efektivní Hyndman-Khandakarův algoritmus, který dramaticky šetří výpočetní čas i výkon. " \
                       "Navíc se nespoléháme na automatický výběr slepě – samotnou periodu (12) i povahu dat jsme již ověřili " \
                       "graficky, přes ACF/PACF a periodogram. Vybraný model se následně znovu odhadne ve `statsmodels`, " \
                       "aby finální srovnávací tabulky používaly hodnoty AIC/BIC ze stejného nástroje jako ostatní modely.\n"
            
            cell['source'] = [new_text]
            print("Updated Cell 30!")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

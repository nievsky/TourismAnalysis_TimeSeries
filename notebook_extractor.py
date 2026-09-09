import json

def main():
    with open(r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\seminarni_prace.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    with open(r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\notebook_content.txt', 'w', encoding='utf-8') as f_out:
        for i, cell in enumerate(nb.get('cells', [])):
            c_type = cell.get('cell_type', 'unknown')
            f_out.write(f"\n--- Cell {i} ({c_type}) ---\n")
            source = cell.get('source', [])
            if isinstance(source, list):
                f_out.write(''.join(source))
            else:
                f_out.write(source)
            f_out.write("\n")

if __name__ == '__main__':
    main()

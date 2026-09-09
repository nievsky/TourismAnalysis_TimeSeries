import json
import os
import base64

notebook_path = r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\seminarni_prace.ipynb'
image_dir = r'C:\Users\alecs\My Drive\UJEP\CAS\Seminar\images'

if not os.path.exists(image_dir):
    os.makedirs(image_dir)

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

img_idx = 1
for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        for output in cell.get('outputs', []):
            if output.get('output_type') in ['display_data', 'execute_result']:
                data = output.get('data', {})
                if 'image/png' in data:
                    img_data = data['image/png']
                    img_path = os.path.join(image_dir, f'plot_{img_idx}.png')
                    with open(img_path, 'wb') as img_f:
                        img_f.write(base64.b64decode(img_data))
                    print(f'Saved {img_path}')
                    img_idx += 1

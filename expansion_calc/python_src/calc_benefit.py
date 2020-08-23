import futsu.csv
import futsu.json
import math
import os
import re

LV_FORMAT = 'Lv\\.(\\d+)(\\.(\\d+))?([KMBT]?)'
LV_FORMAT_RE = re.compile(LV_FORMAT)
LVUP_FORMAT = 'Lv\\.UPx(\\d+)(\\.(\\d+))?([KMBT]?)'
LVUP_FORMAT_RE = re.compile(LVUP_FORMAT)

dirname = os.path.dirname
PROJECT_ROOT = dirname(dirname(dirname(os.path.abspath(__file__))))

OUTPUT_FOLDER_PATH = os.path.join(PROJECT_ROOT,'expansion_calc','output')

res_data_path = os.path.join(PROJECT_ROOT,'expansion_calc','res','data.json')
res_data = futsu.json.path_to_data(res_data_path)

expansion_data_list_fn = os.path.join(OUTPUT_FOLDER_PATH, 'expansion_data_list.csv')
expansion_data_list = futsu.csv.read_csv(expansion_data_list_fn)[0]

expansion_calc_data_list = []
for expansion_data in expansion_data_list:
    icon_id = expansion_data['ICON_ID']
    lv_txt = expansion_data['LV']
    lvup_txt = expansion_data['LVUP']
    
    icon_id_int = int(icon_id)
    
    m = LV_FORMAT_RE.fullmatch(lv_txt)
    v_txt = '{}.{}'.format(m.group(1),m.group(3)) if m.group(3) != None else \
            m.group(1)
    v_mult_txt = m.group(4)
    v_mult = 1             if v_mult_txt == '' else \
             1000          if v_mult_txt == 'K' else \
             1000000       if v_mult_txt == 'M' else \
             1000000000    if v_mult_txt == 'B' else \
             1000000000000 if v_mult_txt == 'T' else \
             0
    v_num = float(v_txt) * v_mult
    lv_num = v_num

    m = LVUP_FORMAT_RE.fullmatch(lvup_txt)
    v_txt = '{}.{}'.format(m.group(1),m.group(3)) if m.group(3) != None else \
            m.group(1)
    v_mult_txt = m.group(4)
    v_mult = 1             if v_mult_txt == '' else \
             1000          if v_mult_txt == 'K' else \
             1000000       if v_mult_txt == 'M' else \
             1000000000    if v_mult_txt == 'B' else \
             1000000000000 if v_mult_txt == 'T' else \
             0
    v_num = float(v_txt) * v_mult
    lvup_num = v_num
    
    lvm = (lv_num+lvup_num)/lv_num
    log_lvm = math.log(lvm,10)
    effect = log_lvm * res_data['ICON_DATA_LIST'][icon_id_int]['EFFECT']
    
    expansion_calc_data_list.append({
        'ICON_ID':icon_id,
        'LABEL':res_data['ICON_DATA_LIST'][icon_id_int]['LABEL']['ZH'],
        'LV':lv_txt,
        'LVUP':lvup_txt,
        'EFFECT':effect
    })

csv_path = os.path.join(OUTPUT_FOLDER_PATH,'expansion_calc_data_list.csv')
futsu.csv.write_csv(
    csv_path, expansion_calc_data_list,
    col_name_list = ['LABEL','EFFECT','LV','LVUP'],
    sort_key_list = ['ICON_ID']
)

import PIL.Image
import futsu.csv
import futsu.fs
import numpy
import os
import pytesseract

dirname = os.path.dirname
PROJECT_ROOT = dirname(dirname(dirname(os.path.abspath(__file__))))

OUTPUT_FOLDER_PATH = os.path.join(PROJECT_ROOT,'expansion_calc','output')
futsu.fs.reset_dir(OUTPUT_FOLDER_PATH)

def image_to_string(v_np_hwc):
    v_np_hw = v_np_hwc.mean(2)
    v_np_hw = v_np_hw.astype(numpy.double)
    v_min = v_np_hw.min()
    v_max = v_np_hw.max()
    v_np_hw = v_np_hw - v_min
    v_np_hw = v_np_hw/(v_max-v_min)
    v_np_hw = 1-v_np_hw # better result when background white text black
    v_np_hw = v_np_hw*255
    v_np_hw = numpy.maximum(v_np_hw,0)
    v_np_hw = numpy.minimum(v_np_hw,255)
    v_img = PIL.Image.fromarray(numpy.uint8(v_np_hw))
    v_txt = pytesseract.image_to_string(v_img, config="--psm 7 -c 'tessedit_char_whitelist=Lv.UPx1234567890KMBTe'")
    v_txt = v_txt.strip()
    return v_txt

def save_img(fn,v_np_hwc):
    v_img = PIL.Image.fromarray(numpy.uint8(v_np_hwc))
    v_img.save(fn,'PNG')

# get icon
icon_folder_path = os.path.join(PROJECT_ROOT,'expansion_calc','res','icon')
icon_data_list = []
for img_path in sorted(futsu.fs.find_file(icon_folder_path)):
    fn = os.path.relpath(img_path,icon_folder_path)
    icon_id = fn[:-4]
    icon_img = PIL.Image.open(img_path)
    icon_np_hwc = numpy.asarray(icon_img)
    icon_data_list.append({
        'ICON_ID':icon_id,
        'NP_HWC':icon_np_hwc,
    })

box_data_list = []

img_folder_path = os.path.join(PROJECT_ROOT,'expansion_calc','input')
#icon_id = 0
for img_path in sorted(futsu.fs.find_file(img_folder_path)):
    fn = os.path.relpath(img_path,img_folder_path)
    #print(fn)

    img_img = PIL.Image.open(img_path)
    assert(img_img.size==(1440, 2560))
    
    img_np_hwc = numpy.asarray(img_img)
    assert(img_np_hwc.shape==(2560,1440,3))
    
    # chop data area
    img_np_hwc = img_np_hwc[255:2195,:,:]
    assert(img_np_hwc.shape==(1940,1440,3))
    
    # detect item box
    t_np_hwc = img_np_hwc[:,998:1411,:]
    assert(t_np_hwc.shape==(1940,413,3))
    t_np_h = t_np_hwc.max((1,2))
    assert(t_np_h.shape==(1940,))
    t_list = list(t_np_h)
    #print(t_list)
    box_start_y_list = []
    tmp_box_start_y = None
    for i in range(len(t_list)+1):
        v = t_list[i] if (i < len(t_list)) else 0
        if v > 181:
            if tmp_box_start_y == None:
                tmp_box_start_y = i
        else:
            if tmp_box_start_y != None:
                if i-tmp_box_start_y >= 180:
                    box_start_y_list.append(tmp_box_start_y)
                tmp_box_start_y = None
    t_np_hwc = None
    t_np_h = None
    t_list = None
    tmp_box_start_y = None

    #print(box_start_y_list)
    for i in range(len(box_start_y_list)):
        box_start_y = box_start_y_list[i]
    
        box_np_hwc = img_np_hwc[box_start_y:box_start_y+180,25:1411,:]
        assert(box_np_hwc.shape==(180,1386,3))
        
        # detect img
        v_np_hwc = box_np_hwc[0:180,0:180,:]
        # save_img('{}.png'.format('000{}'.format(icon_id)[-3:]),v_np_hwc)
        # icon_id+=1
        min_diff = float("inf")
        icon_id = None
        for icon_data in icon_data_list:
            tmp_icon_id = icon_data['ICON_ID']
            tmp_np_hwc = icon_data['NP_HWC']
            icon_diff = tmp_np_hwc - v_np_hwc
            icon_diff = numpy.absolute(icon_diff)
            icon_diff = numpy.sum(icon_diff)
            if icon_diff > min_diff: continue
            min_diff = icon_diff
            icon_id = tmp_icon_id
        
        # detect lv
        v_np_hwc=box_np_hwc[50:84,200:450,:]
        lv_txt = image_to_string(v_np_hwc)
        #save_img('{}.{}.lv.png'.format(fn,i),v_np_hwc)
        #print('{} {} lv_txt={}'.format(fn,i,lv_txt))
    
        # todo: detect lv up
        v_np_hwc=box_np_hwc[83:147,980:1380,:]
        lvup_txt = image_to_string(v_np_hwc)
        #print(lvup_txt)

        box_data_list.append({
            'filename':fn,
            'idx':i,
            'ICON_ID':icon_id,
            'LV':lv_txt,
            'LVUP':lvup_txt,
        })

csv_path = os.path.join(OUTPUT_FOLDER_PATH,'expansion_data_list.csv')
futsu.csv.write_csv(
    csv_path, box_data_list,
    col_name_list = ['ICON_ID','LV','LVUP','filename','idx'],
    sort_key_list = ['ICON_ID']
)

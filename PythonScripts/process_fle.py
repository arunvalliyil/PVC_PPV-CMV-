import os, fnmatch, csv
import __main__

global tiles , path
tiles = 1
path = r"C:\PythonSV\articsound\toolext\bootscript\fusefiles\ATS\A0\SFO\PPV"

def _return_missing_dff(file):
    dffs=[]
    with open (file) as f:
        for line in f:
            if "DFF" in line:
                splitline=line.rsplit(",")
                for item in splitline:
                    if "DFF:" in item:
                        dffs.append(item)
    return dffs

def _read_column_from_csv(file, columnName):
    result = None
    with open(file) as f:
        reader = csv.DictReader(f)  # read rows into a dictionary format
        for row in reader:  # read a row as {column1: value1, column2: value2,...}
            for (k, v) in row.items():  # go over each column name and value
                if k == columnName:
                    result = v
    return result

def _write_string_to_file(string,file):
    with open(file,'w') as f:
        f.write(string)

def override_fle(ULT):
    print ("Number of tiles: {}".format(tiles))
    if tiles == 1:
        missing_dff=_return_missing_dff(find_csv_file_from_ULT(block="",ULT=ULT,path=path))
        print(missing_dff)
        if len(missing_dff) > 2:
            return ("More than 2 DFFs are missing! Expecting only Unique_ID and Phantom_Creek DFF to be missing!")
        fusestrfile=generate_fusestr_txt_file(find_csv_file_from_ULT(block="",ULT=ULT,path=path))
        __main__.sv.gfxcard0.tile0.fuses.import_string(fusestrfile)
    if tiles == 2:
        missing_dff=_return_missing_dff(find_csv_file_from_ULT(block="CPU00",ULT=ULT,path=path))
        print(missing_dff)
        if len(missing_dff) > 2:
            return ("More than 2 DFFs are missing! Expecting only Unique_ID and Phantom_Creek DFF to be missing!")
        missing_dff=_return_missing_dff(find_csv_file_from_ULT(block="CPU01",ULT=ULT,path=path))
        print(missing_dff)
        if len(missing_dff) > 2:
            return ("More than 2 DFFs are missing! Expecting only Unique_ID and Phantom_Creek DFF to be missing!")
            
        fusestrfile0=generate_fusestr_txt_file(find_csv_file_from_ULT(block="CPU00",ULT=ULT,path=path))
        fusestrfile1=generate_fusestr_txt_file(find_csv_file_from_ULT(block="CPU01",ULT=ULT,path=path))
        __main__.sv.gfxcard0.tile0.fuses.import_string(fusestrfile0)
        __main__.sv.gfxcard0.tile0.fuses.import_string(fusestrfile1)

def generate_fusestr_txt_file(file):
    with open(file) as f:
        filepath = os.path.realpath(f.name)
        path,filename=os.path.split(filepath)
        filename,extension = filename.rsplit(".")
        print (path)
        print (filename)
        print (extension)
    fusestr=_read_column_from_csv(file,"Dynamic String")
    if fusestr == 0 or len(fusestr) != 147456:
        return ("ERROR: Dynamic String is ZERO or is not 147456 bits in length!")
    txtfilepath = path+"\\"+filename+".txt"
    _write_string_to_file(fusestr,txtfilepath)
    if os.path.exists(txtfilepath):
        print ("TXT file generated: {}".format(txtfilepath))
    else:
        print ("Failed to create TXT file: {}".format(txtfilepath))
    return (txtfilepath)

def find_file_from_string(string,extension,path):
    if extension:
        pattern = "*"+string+"*"+extension
    else:
        pattern = "*"+string+"*"
    print ("Pattern to match: {}".format(pattern))
    return(_find(pattern,path))

def find_csv_file_from_ULT(block,ULT,path):
    ULT1,ULT2 = _reconstruct_ULT(ULT)
    try:
        csvfile=find_file_from_string("*"+block+"*"+ULT1,"csv",path)
        print ("Found CSV file: {}".format(csvfile))
        return csvfile
    except Exception as e:
        print ("Unable to find CSV file with {} at {}. Will try a different format.".format(ULT1,path))
        try:
            csvfile=find_file_from_string("*"+block+"*"+ULT2,"csv",path)
            print ("Found CSV file: {}".format(csvfile))
            return csvfile
        except Exception as e:
            print ("Unable to find CSV file with {} at {}".format(ULT2,path))
            return "Failed"
         

def _find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                print ("Found: {}".format(name))
                result.append(os.path.join(root, name))
        break #remove this break if recursive search is preferred
    return result[0] #return first result
    
def _get_eu_group(obj):
    dss_csv = r"C:\PythonSV\articsound\toolext\bootscript\toolbox\ATS_EU_Configs.csv"
    with open(dss_csv, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:  # read a row as {column1: value1, column2: value2,...}
            # sku, meml3_en, gt_compute_dss_en, gt_geometry_dss_en, gt_sfc_en, gt_vdbox_en, gt_vebox_en   
            if obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_meml3_en").get_value() == int(row["FUSE_GT_MEML3_EN"][3:], 2) and \
            obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_compute_dss_en").get_value() == int(row["FUSE_GT_COMPUTE_DSS_EN"][4:], 16) and \
            obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_geometry_dss_en").get_value() == int(row["FUSE_GT_GEOMETRY_DSS_EN"][4:], 16) and \
            obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_sfc_en").get_value() == int(row["FUSE_GT_SFC_EN"][3:], 2) and \
            obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_vdbox_en").get_value() == int(row["FUSE_GT_VDBOX_EN"][3:], 2) and \
            obj.getbypath("fuses.gt_merged_gfx_gt_c0_r3.cnlgt2_fuse_gt_vebox_en").get_value() == int(row["FUSE_GT_VEBOX_EN"][3:], 2):
                print("Fuses match EUGROUP: {}".format(row["SKU"]))
                return row["SKU"]
            else:
                continue
    print('Could not find a matching EU Config with these fuses')
    return "Failed"
    
def _split_ULT(ULT):
    lot,wafer,x,y = ULT.rsplit("_")
    if int(x) < 0: 
        x_polarity = "-"
    else: 
        x_polarity = "+"
    if int(y) < 0:
        y_polarity = "-"
    else:
        y_polarity = "+"
    #print (x_polarity)
    #print (y_polarity)
    return lot,wafer,x_polarity,str(abs(int(x))),y_polarity,str(abs(int(y)))
    
def _reconstruct_ULT(ULT):
    lot,wafer,x_polarity,x,y_polarity,y = _split_ULT(ULT)
    ULT1 = lot+"_"+str(wafer).zfill(3)+"_"+ x_polarity + x + "_"+ y_polarity + y
    ULT2 = lot+"_"+str(wafer).zfill(3)+"_"+ x_polarity + x.zfill(2) + "_"+ y_polarity + y.zfill(2)
    #print (ULT1)
    #print (ULT2)
    return ULT1,ULT2
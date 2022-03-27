from matplotlib import pyplot as plt
from PIL import ImageFile, Image
from rembg.bg import remove
import numpy as np
import re, io, cv2, os
from sys import argv
from os import path

ImageFile.LOAD_TRUNCATED_IMAGES = True

input_path = ""
temp_path = "./Temp/"
output_path = f"{temp_path}Output/"
rembg_output=f"{temp_path}rembg/out.png"
img_to_gcode_output = f"{temp_path}img2gcode/out.txt"

img_to_gcode_threshold = 80


def normalize_filled(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    im, _ = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # fill shape
    cv2.fillPoly(img, pts=im, color=(255,255,255))
    bounding_rect = cv2.boundingRect(im[0])
    img_cropped_bounding_rect = img[bounding_rect[1]:bounding_rect[1] + bounding_rect[3], bounding_rect[0]:bounding_rect[0] + bounding_rect[2]]
    return cv2.resize(img_cropped_bounding_rect, (300, 300))

def countour_similarity():
    calculated = normalize_filled(cv2.imread(f"{output_path}calculated.png"))
    extracted = normalize_filled(cv2.imread(f"{output_path}extracted.png"))
    score = cv2.matchShapes(extracted, calculated, cv2.CONTOURS_MATCH_I2, 0.0)
    return str((1-score)*10000)[:4]

def ImgToGcode(img):
    def removeBackGround(name):
        f = np.fromfile(name)
        result = remove(f)
        img = Image.open(io.BytesIO(result)).convert("RGBA")
        img.save(rembg_output)
        
    def readFile(name):
        x = []
        y = []
        with open(name) as f:
            for line in f:
                x1,y1 = re.findall('[XY]-?[0-9]{0,3}\.?[0-9]{0,6}', line)
                x.append(float(x1[1:]))
                y.append(float(y1[1:]))
        return x,y

    removeBackGround(input_path+img)
    #extractGCODE(rembg_output,img_to_gcode_output,img_to_gcode_threshold)
    os.system(
        "python3 ./ImgToGcode/image_to_gcode.py --input {} --output {} --threshold {}"
        .format(rembg_output,img_to_gcode_output,img_to_gcode_threshold)
    )
    return readFile(img_to_gcode_output)

def createImage(x,y, name):
    def normalize(array):
        #!normalize array from 0 to 1
        m = min(array)
        M = max(array)
        return [ (i-m)/(M-m) for i in array]

    #!Normalize points to have the same scale
    x = normalize(x)
    y = normalize(y)
    #!Setting resolution, background color and removing axis
    #plt.gcf().set_size_inches(5.12,5.12)
    plt.style.use('dark_background')
    plt.axis('off')
    #!Image creation
    plt.plot(x,y,c='w')
    plt.savefig(f'{output_path}{name}', dpi=1000)
    plt.close()

def extract_layer_gcode(gco, layer):
    x = []
    y = []
    with open(input_path+gco) as gcode:
        start = False
        for line in gcode:
            if ";LAYER:{}".format(layer) in line:
                start = True
            if start and (coord := re.findall('[XY]-?[0-9]{0,3}\.?[0-9]{0,6}', line)) and (len(coord)==2):
                x.append(float(coord[0][1:]))
                y.append(float(coord[1][1:]))
            if ";LAYER:{}".format(layer+1) in line:
                start = False
                break
    return x,y

def cleanTemp():
    if (path.isfile(rembg_output)):
        os.remove(rembg_output)
        
    if (path.isfile(img_to_gcode_output)):
        os.remove(img_to_gcode_output)
        
    if (path.isfile(f'{output_path}calculated.png')):
        os.remove(f'{output_path}calculated.png')
        
    if (path.isfile(f'{output_path}extracted.png')):
        os.remove(f'{output_path}extracted.png')

def calculate(snapshot,gcode,layer):
    cleanTemp()
    x,y = ImgToGcode(snapshot)
    createImage(x,y,"extracted.png")
    
    x,y=extract_layer_gcode(gcode,int(layer))
    createImage(x,y,"calculated.png")
    return countour_similarity()

def main():
    if (len(argv) == 4):
        if (path.isfile(argv[1]) and path.isfile(argv[2])):
            print(calculate(argv[1],argv[2],argv[3]))
            
    else:
        print(-1)


if __name__=="__main__":
    main()
    #calculate("20220211_124928.jpg","CE6_cubettino.gcode",42)
    #main()
    """     
    def readFile(name):
        x = []
        y = []
        with open(name) as f:
            for line in f:
                coord = re.findall('[XY]-?[0-9]{0,3}\.?[0-9]{0,6}', line)
                if coord and len(coord)==2:
                    x.append(float(coord[0][1:]))
                    y.append(float(coord[1][1:]))
        return x,y

    x,y=readFile("test")
    createImage(x,y,"prova") """
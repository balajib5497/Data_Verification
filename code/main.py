import cv2
import sys
import os

import pyocr
import pyocr.builders
from PIL import Image

from dateutil.parser import parse
from dateparser.search import search_dates

from util import values

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)

tool = tools[0]
lang = 'eng'
img_resize_ratio = 3

def find_coordinates_of_number(ocr_result, number):
    coordinates = []
    words = []
    
    for box in ocr_result:
        if number in box.content:
            words.append(box.content)
            coordinates.append(box.position)
            
    return words, coordinates
    
def find_coordinates_of_date(ocr_result, date):
    coordinates = []
    words = []
    
    text = ' '.join([box.content for box in ocr_result])
    dates_in_text = search_dates(text)
    
    if dates_in_text:
        for (s, dt) in dates_in_text:
            if dt == date:
                date_in_s = s.split()
                m = len(date_in_s)
                n = len(ocr_result)
                
                for i in range(m-1, n):
                    k = m-1
                    for j in range(i, i-m, -1):
                       if ocr_result[j].content != date_in_s[k]:
                           break
                       k -= 1
                       
                    if k == -1:
                       words.append(s) 
                       coordinates.append((ocr_result[i-m+1].position[0], ocr_result[i].position[1]))
                        
#    for box in ocr_result:
#        dates_in_text = search_dates(box.content)
#        if dates_in_text:
#            print(dates_in_text)
#            for (s, dt) in dates_in_text:
#                if dt == date:
#                    words.append(box.content)
#                    coordinates.append(box.position)
    
    return words, coordinates
        
def extract_text_from_image(image):
    image = cv2.resize(image, None, fx=img_resize_ratio,
                       fy=img_resize_ratio, interpolation = cv2.INTER_CUBIC)
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    text = tool.image_to_string(Image.fromarray(image), lang=lang, builder=pyocr.builders.WordBoxBuilder())
    return text

path = '../samples'
for filename in os.listdir(path):    
    print('file:', filename)
    image = cv2.imread(os.path.join(path, filename), 0)
    
    key = filename.split('.')[0]
    number = values[key]['number']
    date = parse(values[key]['date'])
    
    ocr_result = extract_text_from_image(image)
    
    res_img = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
    words, coordinates =  find_coordinates_of_number(ocr_result, number)
    for (word, position) in zip(words, coordinates):
        print(word, '\t', position)
        cv2.rectangle(res_img,(position[0][0]//img_resize_ratio, position[0][1]//img_resize_ratio)
                            ,(position[1][0]//img_resize_ratio, position[1][1]//img_resize_ratio),(0,0,255),2)    

    
    words, coordinates =  find_coordinates_of_date(ocr_result, date)
    for (word, position) in zip(words, coordinates):
        print(word, '\t', position)    
        cv2.rectangle(res_img,(position[0][0]//img_resize_ratio, position[0][1]//img_resize_ratio)
                            ,(position[1][0]//img_resize_ratio, position[1][1]//img_resize_ratio),(0,255,0),2)
    print('-'*60)
    
    res_img = cv2.resize(res_img, (600, 700))
    cv2.imshow('res_img',  res_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
'''
coordinate - ((x1, y1), (x2, y2)) or ((x, y), (x+w, y+h))
Accuracy (Recognition rate)

For Number = 100 % (10/10)
For Date   = 90 % (9/10)
    Total  = 95 % (19/20)
'''

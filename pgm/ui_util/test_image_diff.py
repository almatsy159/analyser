from PIL import Image
import numpy as np
import os 

"""
naming of tests images :
    M masks
    C capture (E ecran <=> screen)
    C0X => All x are the same series
    sYX => serie Y number X (vertical scrool (y axis))
    swYX => same but x axis scroll !
"""

img_dict = {}

def extract_name_from_filename(filename):
    name = ""
    for c in filename:
        if c == ".":
            break
        else :
            name += c
    return name

img_dir = "./pgm/ui_util/test_img/"
img_dir_content = os.listdir(img_dir)
#img_names = [extract_name_from_filename(img_filename) for img_filename in img_dir_content]

for img_filename in img_dir_content:
    name = extract_name_from_filename(img_filename)
    file_path = img_dir + img_filename
    img = Image.open(file_path).convert("RGB")
    arr = np.array(img,dtype=np.uint8)
    img_dict[img_filename] = {"name":name,"img_arr":arr}


#print(img_dict["CE1.png"]["img_arr"])
#for c in img_dict["CE1.png"]["img_arr"]:
#    print(c)
"""
def compare_img(arr1,arr2):
    if arr1.shape == arr2.shape:
        mask = np.zeros_like(arr1)
        for i,c in enumerate(arr1):
            for j,l in enumerate(c):
                if np.all(arr1[i][j] == arr2[i][j]):
                    mask[i][j] = [1,1,1]

    return mask

def compare_img2(arr1,arr2):
    if arr1.shape == arr2.shape:
        mask = np.zeros_like(arr1)
        for i,c in enumerate(arr1):
            for j,l in enumerate(c):
                if np.all(arr1[i][j] != arr2[i][j]):
                    mask[i][j] = arr1[i][j]

    return mask
"""

"""  
# here it is about click appened and then a change occur within the window , not the actual issue of aggregating must see that later !          
mask_CE1_CE2 = compare_img2(img_dict["CE1.png"]["img_arr"],img_dict["CE2.png"]["img_arr"])
#print(mask_CE1_CE2)
mask_img_CE1_CE2 = Image.fromarray(mask_CE1_CE2*255)
mask_ce1_ce2_path = img_dir + "mask_img2_CE1_CE2.png"
mask_img_CE1_CE2.save(mask_ce1_ce2_path)

mask_CE2_CE1 = compare_img2(img_dict["CE2.png"]["img_arr"],img_dict["CE1.png"]["img_arr"])
#print(mask_CE1_CE2)
mask_img_CE2_CE1 = Image.fromarray(mask_CE2_CE1*255)
mask_ce2_ce1_path = img_dir + "mask_img2_CE2_CE1.png"
mask_img_CE2_CE1.save(mask_ce2_ce1_path)
"""

"""
def compare_image_scroll_y(arr1,arr2):
    print("arr 1 : ",arr1.shape," and arr 2 : ",arr2.shape)
    if arr1.shape == arr2.shape:
        flag_same = False
        idx = 0
        indices = []
        #idx2 = None
        for i,c in enumerate(arr1):
            for i2,c2 in range(idx,len(arr2)):
                if np.all(c == arr2[i2]):
                    flag_same = True
                    if idx == None:
                        #idx = i2
                        indices.append((i,i2))

                    
    print(idx,indices)

compare_image_scroll_y(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"])

"""

test_scroll1 = [1,3,1,7,1,3,1,5,1,3,1,7,1,3]
test_scroll2 = [1,3,1,5,1,3,1,7,1,3,1,9]

"""
i=0
idx = 0
eof = False
cpt = 0
k=0
print(len(test_scroll1))
while eof == False:

    for j in range(i,len(test_scroll1)):
        
        print(f"L1[{j}] : {test_scroll1[j]} ==  {test_scroll2[k]} : L2[{k}]" if test_scroll1[j] == test_scroll2[k] else f"L1[{j}] : {test_scroll1[j]} !=  {test_scroll2[k]} : L2[{k}]")
        if test_scroll1[j] == test_scroll2[k]:
            k=k+1
        else :
            i = i+1
            k=0
            break
    else :
        idx = i
        eof = True

print(test_scroll1[i:])
print(test_scroll2[:len(test_scroll2)-i])

"""

def compare_sequences(sqc1,sqc2):

    i=0
    idx = 0
    eof = False
    cpt = 0
    k=0
    print(len(sqc1))
    while eof == False:

        for j in range(i,len(sqc1)):
        
            print(f"L1[{j}] : {sqc1[j]} ==  {sqc2[k]} : L2[{k}]" if sqc1[j] == sqc2[k] else f"L1[{j}] : {sqc1[j]} !=  {sqc2[k]} : L2[{k}]")
            if sqc1[j] == sqc2[k]:
                k=k+1
            else :
                i = i+1
                k=0
                break
        else :
            idx = i
            eof = True

    return idx


i = compare_sequences(test_scroll1,test_scroll2)
print(i)
# overlap
print(test_scroll1[i:])
# identical part from scroll 1
print(test_scroll2[:len(test_scroll1)-i])
# identical part from scroll 2
new_sqc = []*(len(test_scroll1)+i)
# initialize new_sequence of length scroll i + overlap
print(new_sqc)
new_sqc[:len(test_scroll1)] = test_scroll1
print(new_sqc)
new_sqc[len(test_scroll1):] = test_scroll2[len(new_sqc)-i:]
print(new_sqc)



    
def compare_image_scroll_y(arr1,arr2):

    i=0
    idx = 0
    eof = False

    k=0
    print(arr1.shape[0])
    while eof == False:

        for j in range(i,arr1.shape[0]):
            if i == 0 and j==0:
                print(f"L1[{j}] : {arr1[j,:,:]} ==  {arr2[k,:,:]} : L2[{k}]" if np.all(arr1[j,:,:] == arr2[k,:,:]) else f"L1[{j}] : {arr1[j,:,:]} !=  {arr2[k,:,:]} : L2[{k}]")
            if np.all(arr1[j,:,:] == arr2[k,:,:]):
                k=k+1
            else :
                i = i+1
                k=0
                break
        else :
            idx = i
            eof = True

    return idx


#compare_image_scroll_y(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"])

def delta_y_between_images(arr1, arr2):
    """
    Compute vertical shift (delta Y) between two images of same shape.
    Returns the delta Y such that shifting arr2 by deltaY matches arr1 best.
    """
    H, W, C = arr1.shape
    max_match = 0
    best_dy = 0

    # Try all possible shifts
    for dy in range(-H + 1, H):
        if dy >= 0:
            # arr2 shifted down
            overlap_arr1 = arr1[dy:H]
            overlap_arr2 = arr2[0:H-dy]
        else:
            # arr2 shifted up
            overlap_arr1 = arr1[0:H+dy]
            overlap_arr2 = arr2[-dy:H]

        # Count number of fully matching rows
        match_count = np.sum(np.all(overlap_arr1 == overlap_arr2, axis=(1,2)))

        if match_count > max_match:
            max_match = match_count
            best_dy = dy

    return best_dy

"""
dy = delta_y_between_images(img_dict["s11.png"]["img_arr"], 
                            img_dict["s12.png"]["img_arr"])
print("Vertical offset (delta Y):", dy)
"""

def merge_images_simple(arr1, arr2, delta_y):
    H1, W, C = arr1.shape
    H2, _, _ = arr2.shape

    # Height of the new merged array
    #new_H = H1 + (H2 - delta_y)
    new_H = H1 + delta_y
    merged = np.zeros((new_H, W, C), dtype=arr1.dtype)

    # Put first image at the top
    merged[0:H1, :, :] = arr1

    # Put the non-overlapping part of the second image
    #merged[H1:H1 + (H2 - delta_y), :, :] = arr2[delta_y:, :, :]
    merged[H1:H1 + delta_y, :, :] = arr2[H2-delta_y:, :, :]

    return merged
"""
merged = merge_images_simple(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"],dy)
s11_s12_merged = Image.fromarray(merged)
s11_12_path =img_dir + "s11_12.png"
s11_s12_merged.save(s11_12_path)
"""

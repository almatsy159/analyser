import numpy as np  
from PIL import Image
# only for type hint ! 
from capture import Capture

# copied from test_image_diff.py

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


def delta_between_y2(arr1,arr2):
    if np.all(arr1[0]==arr2[-1]):
        print("same last and first")


"""
merged = merge_images_simple(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"],dy)
s11_s12_merged = Image.fromarray(merged)
s11_12_path =img_dir + "s11_12.png"
s11_s12_merged.save(s11_12_path)
"""

"""
def process(cap1:Capture,cap2:Capture):
    img1 = Image.open(cap1.f_path).convert("RGB")
    arr1 = np.array(img1,dtype=np.uint8)
    img2 = Image.open(cap2.f_path).convert("RGB")
    arr2 = np.array(img2,dtype=np.uint8)
    dy = delta_y_between_images(arr1,arr2)
    merged = merge_images_simple(arr1,arr2,dy)
    res = Image.fromarray(merged)

    return res

def process(cap1:Capture,cap2:Capture):
    img1 = Image.open(cap1.f_path).convert("RGB")
    arr1 = np.array(img1,dtype=np.uint8)
    img2 = Image.open(cap2.f_path).convert("RGB")
    arr2 = np.array(img2,dtype=np.uint8)
    dy = delta_y_between_images(arr1,arr2)
    merged = merge_images_simple(arr1,arr2,dy)
    res = Image.fromarray(merged)

    return res  
"""


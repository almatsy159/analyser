# why replace last readme ?

the last readme_file (readme_v3) comes up to be pretty long and so doesn't gave a qucik overview of the project.
so instead of one huge readme file, there will be shortly one readme by module all linked here.

# what can i see on this one ?

in this reamdme file you can see : 

- the description of the app
- the global architecture of the app
- the user guide
- links to others readme files for more advanced research on a module/ functionnality
- advancement on the app


# app description



# architecture


# user guide


# notes


# links


# app advancement


## last update

- changed sender by sender_feed

## to do

- add connector for message (and add it to displaywidget):

    1. "recording ctrl+alt then s to stop"

    2. "capturing feed => scroll up to stop"

    3. "error : server/script"

    4. ""

- handle state of overlay

## bugs

- bug while aggregating images :

    1. first capture

    2. last capture

    3. naming capture (time.now => f_path = ./.../<session>_<user>_<y_m_d_m_s>.<ms>.<ext>) : double point => extract_name regex get out the wrong file name
    
    ### notes

    - collab to test aggregation

    - aggregation in capture (for using type hint on capture, it avoid circular import)

    - test_image_diff.py

    - trt_img.py


- display info bugs : (since overlay_test7.py (ignore ...6.py))

    1. error while actualising context : {analyser:{app...,context:...,...}} => {app:...,context:...,...} and deleting previous content

    2. probably while changing window too for "app"


# -*- encoding=utf-8 -*-
# @Time:31/7/2019
# @Author: Sanjun
# """ remove the redundant images """
import os
import sys
import math
import glob
import copy
import cv2
import shutil
import random
import itertools

# get the two images similary
def img_similarity(img1_path,img2_path):
    try:
        img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

        # init ORB detector
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)

        # get the feature points
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)

        # knn filters
        matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)

        # get the max matching points number
        good = [m for (m, n) in matches if m.distance < 0.75 * n.distance]
        #print(len(good))
        #print(len(matches))
        similary = len(good) / len(matches)
        #print("the similary is: %s" % similary)
        return similary

    except:
        print('error: cannot calculate the two images similary')
        return '0'

if __name__ == '__main__':

    inImgsRoot = './tmp'
    out_imgs_root = './output'
    internal_size = 10
    similary_threshold = 0.2
    if len(sys.argv) == 3:
        inImgsRoot = sys.argv[1]
        out_imgs_root = sys.argv[2]
    if not os.path.isdir(out_imgs_root):
        os.makedirs(out_imgs_root)
    else:
        print('Please remove {} first'.format(out_imgs_root))
        sys.exit(2)
    file_paths = glob.glob(os.path.join(inImgsRoot, '**/*.jpg'), recursive=True)
    #print('file_paths', file_paths)
    num_image = len(file_paths)
    tmp_paths = copy.deepcopy(file_paths)
    list_pairs = []
    ## separate the images by internal_size to num_bin, and calculate each pair similary
    internal_size = 10 ### to change based on your datasets
    num_bin = int(num_image/internal_size)
    for i in range(num_bin - 1):
        tmp_file_path = file_paths[i*internal_size:(i+1)*internal_size]
        list_bin = list(itertools.combinations(tmp_file_path, 2))
        list_pairs += list_bin
    tmp_file_path = file_paths[(num_bin - 1)*internal_size:num_image]
    list_bin = list(itertools.combinations(tmp_file_path, 2))
    list_pairs += list_bin
    #print('list pairs', list_pairs)

    rm_lists = []
    for i in range(len(list_pairs)):
        list_pair = list_pairs[i]
        #print(list_pair[0], list_pair[1])
        print('processing {}/{}'.format(i, len(list_pairs)))
        if list_pair[0] in rm_lists or list_pair[1] in rm_lists:
            continue
        similary = img_similarity(list_pair[0], list_pair[1])
        if similary >= similary_threshold:
            #print('tmp_path', tmp_paths)
            if list_pair[1] in tmp_paths:
                print('rm item', list_pair[1],similary)
                tmp_paths.remove(str(list_pair[1]))
                rm_lists.append(list_pair)
    #print('save list', tmp_paths)
    # save the results
    for file_path in tmp_paths:
        shutil.copy(file_path,  out_imgs_root)

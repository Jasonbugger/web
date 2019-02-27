import subprocess
import os
import re
import time
import queue
from multiprocessing.pool import Pool
import shutil
import copy
from info_parse import user_info_get, tweet_location_get

# 源文件路径获取单元
def source_path_getter(root_path):
    file_list = [root_path]
    counter = 0
    while counter<= len(file_list):
        b = file_list[counter]
        if os.path.isdir(b):
            file_list.remove(counter)
            for a in [b +'\\' +  os.listdir()]:
                file_list.append(a)
        else:
            counter += 1
    return file_list

#目标文件路径生成器
def dst_path_getter(source_path, dst_root_path, source_root):
    x = source_path[len(source_root):]
    dst_path = dst_root_path  +"\\" + x
    return dst_path

def dst_path_list_getter(source_path_list, dst_root_path, source_root):
    dst_path_list = []
    for i in source_path_list:
        dst_path_list.append(dst_path_getter(i, dst_root_path, source_root))
    return dst_path_list

# 并行单元
def parallel_process(program_to_run, source_file_list, dst_path_list, process_number):
    if len(source_file_list)!=len(dst_path_list):
        raise ValueError
    args = []
    for i in range(len(source_file_list)):
        args.append((source_file_list[i], dst_path_list[i]))
    
    with Pool(processes=process_number) as pool:
        for arg in args:
            pool.apply_async(program_to_run, arg)
        pool.close()
        pool.join()

# 合并单元(合并的临时文件怎么处理)
def merge_files(dst_path_list, process_number, final_path, merge_func, dst_root, batch = 5):
    # 这里路径还能优化一下
    temp1_path = 'G:\\temp1'
    temp2_path = 'G:\\temp2'
    path_list = copy.deepcopy(dst_path_list)
    switch = 0
    # 迭代合并过程
    while True:
        args = []
        batch_left = 0
        batch_right = 5
        if len(path_list) == 1:
            shutil.copyfile(path_list[0], final_path+ "\\"+ path_list[0].split("\\")[-1])
            return
        # 单次划分
        while batch_left<len(path_list):
            source = path_list[batch_left:batch_right]
            if switch == 0:
                dst = dst_path_list_getter(source, temp1_path, dst_root)
            elif switch == 1:
                dst = dst_path_list_getter(source, temp2_path, temp1_path)
            elif switch == 2:
                dst = dst_path_list_getter(source, temp1_path, temp2_path)
            args.append((source, dst))
            batch_left += batch
            batch_right += batch
            
        with Pool(process_number) as pool:
            for arg in args:
                pool.apply_async(merge_func, arg)
            pool.close()
            pool.join()
        if switch == 1:
            path_list = source_path_getter(temp2_path)
            shutil.rmtree(temp1_path)
            os.mkdir(temp1_path)
            switch = 2
        else:
            path_list = source_path_getter(temp1_path)
            shutil.rmtree(temp2_path)
            os.mkdir(temp2_path)
            switch = 1

def main(source_root_path, dst_root_path, process_number, final_path, program_to_run, merge_func):
    source_path_list = source_path_getter(source_root_path)
    dst_path_list = dst_path_list_getter(source_path_list, dst_root_path, source_root_path)
    parallel_process(program_to_run, source_path_list, dst_path_list, process_number)
    merge_files(dst_path_list, process_number, final_path, merge_func, source_root_path)

if __name__ == '__main__':
    source_root_path = ''
    dst_root_path = ''
    process_number = 4
    final_path = ''
    program_to_run = ''
    merge_func = ''


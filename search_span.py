from multiprocessing import managers
from multiprocessing.context import get_spawning_popen
from pathlib import Path
import queue
from fuzzysearch import find_near_matches
from seg_data import search_Seg
import numpy as np
import os
import time
import multiprocessing
from verse_tokenizer import tokenize_verse


def get_seg_obj(text):
    obj = search_Seg()
    splitted_chunks = tokenize_verse(text)
    for chunk in splitted_chunks:
        obj.push(chunk)
    return obj


def fuzzy_search(search_text,target_text):
    matches = find_near_matches(search_text,target_text,max_l_dist=int(len(search_text)*0.2))
    return matches


def get_spans(target_text):
    spans = []
    middle_node = search_obj.getMiddle(search_obj.first_node,search_obj.last_node)
    mid_matches = fuzzy_search(middle_node.data,target_text)
    if mid_matches:
        for mid_match in mid_matches:
            span = search_in_expand_window(middle_node,mid_match,target_text)
            if span:
                spans.append(span)
    return spans


def search_in_expand_window(middle_node,mid_match,target_text):
    start_span = search_in_left_window(middle_node,mid_match,target_text)
    end_span = search_in_right_window(middle_node,mid_match,target_text)
    if start_span is not None and end_span is not None:
        return (start_span,end_span)
    return


def search_in_left_window(middle_node,mid_match,target_text):
    prev_node = middle_node.prev
    prev_match = mid_match
    while(prev_node != None):
        len_of_seg = len(prev_node.data)
        cur_matches = find_near_matches(prev_node.data,target_text,max_l_dist=int(len_of_seg*0.2))
        print(prev_node.data)
        if not cur_matches:
            return
        nearest_match = get_nearest_match(prev_match,cur_matches)
        if not nearest_match:
            return 
        prev_node = prev_node.prev
        prev_match = nearest_match
    return prev_match.start


def search_in_right_window(middle_node,mid_match,target_text):
    next_node = middle_node.next
    prev_match = mid_match
    while(next_node != None):
        len_of_seg = len(next_node.data)
        print(next_node.data)
        cur_matches = find_near_matches(next_node.data,target_text,max_l_dist=int(len_of_seg*0.2))
        if not cur_matches:
            return
        nearest_match = get_nearest_match(prev_match,cur_matches)
        if not nearest_match:
            return
        next_node = next_node.next
        prev_match = nearest_match
    
    return prev_match.end


def get_nearest_match(prev_match,cur_matches):
    spans = []
    for match in cur_matches:
        spans.append((match.start,match.end))
    spans = np.array(spans)
    target_span = np.array((prev_match.start,prev_match.end))
    distances = np.linalg.norm(spans - target_span, axis=1)
    min_index = np.argmin(distances)

    return cur_matches[min_index]


def search(search_chunk,target_text):
    global search_obj
    search_obj = get_seg_obj(search_chunk)
    spans = get_spans(target_text)
    return spans


def filter(text_dir):
    target_text = Path(text_dir).read_text(encoding="utf-8")
    first_node = search_obj.first_node.data
    middle_node = search_obj.getMiddle(search_obj.first_node,search_obj.last_node).data
    last_node = search_obj.last_node.data 
    param = [(first_node,target_text),(middle_node,target_text),(last_node,target_text)]
    with multiprocessing.Pool(processes=3) as pool:
        results = pool.starmap(fuzzy_search,param)
    first_match,mid_match,last_match = results
    if first_match and mid_match and last_match:
        return True
    return False

def index(home_dir):
    plausible_files = []
    for root, dirs, files in os.walk(home_dir):
        for file in files:
            if file.endswith(".txt"):
                txt_dir = os.path.join(root, file)
                print(txt_dir)
                is_present = filter(txt_dir)
                if is_present:
                    plausible_files.append(txt_dir)

    return plausible_files

if __name__ == "__main__":
    st = time.time()
    search_chunk = Path("O96FB467A/O96FB467A/O96FB467A.opf/base/03EC.txt").read_text(encoding="utf-8")
    target_text = Path("./FE32B.txt").read_text(encoding="utf-8")
    spans = search(search_chunk,target_text)
    print(spans)
    en = time.time()
    print("time taken =",en-st)
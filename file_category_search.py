from important_functions import *
import numpy as np


# Function that searches words from the text extracted from a file
def main_categorization(cats_df, file_path, file_text, search_whole_word):
    in_main_cats = []
    for index, row in cats_df.iterrows():
        main_cat_dir = row['CategoryChq']
        search_text = row['Keywords_cat']
        sub_txt = row['Keywords_sub']
        sub2_txt = row['Keywords_lvl1']
        new_dict = {}

        if search_text is not np.nan and os.path.exists(file_path):
            possible_path = row['CategoryChq']
            path_list = [get_file_path_string(k) for k in in_main_cats if k]
            if (possible_path and possible_path not in path_list) and search_word_in_given_text(file_text, search_text,
                                                                                                search_whole_word):
                print("Found Level One Key {} Dir {} Search Text {} ".format(index, main_cat_dir, search_text))
                new_dict.update({'key': index, 'level_one_dir': main_cat_dir, 'level_one_found': True,
                                 'level_two_dir': 'NOT_FOUND', 'level_two_found': False,
                                 'level_three_dir': 'NOT_FOUND', 'level_three_found': False, 'search_term': search_text,
                                 'file_path': file_path})

        if sub_txt is not np.nan and os.path.exists(file_path):
            sub_cats = sub_txt.split(", ")
            possible_path = '{}/{}'.format(row['CategoryChq'], row['SubCategoryChq'])
            path_list = [get_file_path_string(k) for k in in_main_cats if k]
            if possible_path and possible_path not in path_list and check_if_all_search_text_are_hit(file_text,
                                                                                                     sub_cats,
                                                                                                     search_whole_word):
                print("Found subcategory Dir {} Search Text {} ".format(row['SubCategoryChq'], sub_txt))
                new_dict.update({'key': index, 'level_one_dir': main_cat_dir, 'level_one_found': True,
                                 'level_two_dir': row['SubCategoryChq'], 'level_two_found': True,
                                 'level_three_dir': 'NOT_FOUND', 'level_three_found': False, 'search_term': sub_txt,
                                 'file_path': file_path})

        if sub2_txt is not np.nan and os.path.exists(file_path):
            sub2_cats = sub2_txt.split(", ")
            possible_path = '{}/{}/{}'.format(row['CategoryChq'], row['SubCategoryChq'], row['Level1Chq'])
            path_list = [get_file_path_string(k) for k in in_main_cats if k]
            if possible_path and possible_path not in path_list and check_if_all_search_text_are_hit(file_text,
                                                                                                     sub2_cats,
                                                                                                     search_whole_word):
                print("Found level 2 subcategory Dir {} Search Text {} ".format(row['Level1Chq'], sub2_txt))
                new_dict.update({'key': index, 'level_one_dir': main_cat_dir, 'level_one_found': True,
                                 'level_two_dir': row['SubCategoryChq'], 'level_two_found': True,
                                 'level_three_dir': row['Level1Chq'], 'level_three_found': True,
                                 'search_term': sub2_txt,
                                 'file_path': file_path})

        if new_dict: in_main_cats.append(new_dict)
    return in_main_cats


# If a sub-directory search texts are more than one, this is the function to traverse all of them
def check_if_all_search_text_are_hit(file_text, search_text_array, search_whole_word):
    for search_text in search_text_array:
        if not search_word_in_given_text(file_text, search_text, search_whole_word):
            return False
    return True

from os.path import expanduser
import pandas as pd
from file_category_search import *
from text_extraction import *
from important_functions import delete_dir
import argparse

source_path = expanduser('~') + '/Downloads/Kabana/source'
categories_excel_source_path = expanduser('~') + '/Downloads/Kabana/Doc_Category_SubCategory_sample.xlsx'
output_path = expanduser('~') + "/Downloads/Kabana/output"

parser = argparse.ArgumentParser()
parser.add_argument("--as_word", help="1 Indicates you want to search a text as a whole word or else search any appearance", type=int, required=False)
args = parser.parse_args()


def process_files(excel_cats_df, source_directory, output_directory, pdf_splitter_directory, search_whole_word, tess_dir):

    # Check if source folder and output folder both exist.
    if not os.path.exists(source_directory) or not os.path.exists(output_directory):
        print("Source folder {} or/and destination folder {} does not exist".format(source_directory, output_directory))
    else:
        count = 1
        f_list = os.listdir(source_directory)
        number_files = len(f_list)
        for file_path in os.listdir(source_directory):
            if os.path.isdir(f'{source_directory}/{file_path}'):
                count2 = 1
                f_list2 = os.listdir(f'{source_directory}/{file_path}')
                number_files2 = len(f_list2)
                for file_ in os.listdir(f'{source_directory}/{file_path}'):
                    if allowed_file(file_):
                        # Create TEMP folders used for processing files
                        create_folder(output_directory, 'SPLITTER')
                        print(f'{str(count)}/{str(number_files)}-{str(count2)}/{str(number_files2)} Processing {source_directory}/{file_path}/{file_}')

                        # Extract Text from the file
                        # custom_config = r'--oem 3 -l '+str(file_path)+' --psm 6 --tessdata-dir "'+tess_dir+'"'
                        custom_config = r'-l ' + str(file_path) + ' --tessdata-dir "' + tess_dir + '"'
                        file_full_text = extract_text_in_file(f'{source_directory}/{file_path}/{file_}',
                                                              pdf_splitter_directory, custom_config)
                        # Remove Splitter folder
                        delete_dir(f'{output_path}/SPLITTER')
                        # Check if text was extracted
                        if not re.search('[a-zA-Z]+', file_full_text):
                            create_folder(output_directory, 'FAILED')
                            move_file(f'{source_directory}/{file_path}/{file_}', f'{output_directory}/FAILED')
                        else:
                            level_one_lt = main_categorization(excel_cats_df, f'{source_directory}/{file_path}/{file_}',
                                                               file_full_text, search_whole_word)
                            if len(level_one_lt) > 1:
                                sel = [(str(k['key']) + ' to move to ' + get_file_path_string(k) + ' Search Text->'
                                        + k['search_term']) for k in level_one_lt]
                                int_choices = [(int(k['key'])) for k in level_one_lt]
                                choice = get_int_choice(int_choices, sel)
                                level_one_lt = [dic for dic in level_one_lt if dic['key'] == choice]

                            if len(level_one_lt) < 1:
                                create_folder(output_directory, 'UNDEFINED')
                                move_file(f'{source_directory}/{file_path}/{file_}',
                                          f'{output_directory}/UNDEFINED')
                                create_file_text(f'{source_directory}/{file_path}/{file_}',
                                                 f'{output_directory}/UNDEFINED', file_full_text)
                            else:
                                categorize_file(output_directory, level_one_lt, file_full_text)
                    else:
                        print("{} not allowed. Only pdf, jpg, jpeg and  png".format(file_path))
                    count2 += 1
            else:
                if allowed_file(file_path):
                    # Create TEMP folders used for processing files
                    create_folder(output_directory, 'SPLITTER')
                    print(f'{str(count)}/{str(number_files)} Processing {source_directory}/{file_path} ')

                    # Extract Text from the file
                    custom_config = r' --tessdata-dir "' + tess_dir + '"'
                    file_full_text = extract_text_in_file(f'{source_directory}/{file_path}', pdf_splitter_directory, custom_config)
                    delete_dir(f'{output_path}/SPLITTER')
                    # Check if text was extracted
                    if not re.search('[a-zA-Z]+', file_full_text):
                        create_folder(output_directory, 'FAILED')
                        move_file(f'{source_directory}/{file_path}', f'{output_directory}/FAILED')
                    else:
                        level_one_lt = main_categorization(excel_cats_df, f'{source_directory}/{file_path}',
                                                           file_full_text, search_whole_word)
                        if len(level_one_lt) > 1:
                            sel = [(str(k['key']) + ' to move to ' + get_file_path_string(k) + ' Search Text->' + k[
                                'search_term']) for k in level_one_lt]
                            int_choices = [(int(k['key'])) for k in level_one_lt]
                            choice = get_int_choice(int_choices, sel)
                            level_one_lt = [dic for dic in level_one_lt if dic['key'] == choice]

                        if len(level_one_lt) < 1:
                            create_folder(output_directory, 'UNDEFINED')
                            move_file(f'{source_directory}/{file_path}', f'{output_directory}/UNDEFINED')
                            create_file_text(f'{source_directory}/{file_path}', f'{output_directory}/UNDEFINED', file_full_text)
                        else:
                            categorize_file(output_directory, level_one_lt, file_full_text)
                else:
                    print("{} not allowed. Only pdf, jpg, jpeg and  png".format(file_path))
            count += 1


if __name__ == "__main__":
    """ Run script in this folder as it depends on other scripts """
    print("\n\n**************************     File Categorization from {} to {}      *************".format(source_path,
                                                                                                           output_path))
    # Decide whether you want to search text as whole word or no.
    search_whole_word = False
    if args.as_word == 1:
        search_whole_word = True

    # Read the category excel file with pandas
    cats_df = pd.read_excel(categories_excel_source_path)
    cats_df['Keywords_cat'] = cats_df['Keywords_cat'].fillna(method='ffill')

    process_files(cats_df, source_path, output_path, f'{output_path}/SPLITTER', search_whole_word, f'tessdata')






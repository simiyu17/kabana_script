import os
import re
import shutil
from pdf2image import convert_from_path

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}


# Check that file being processed is valid for this script
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Move file to another directory
def move_file(file_path, dst_dir):
    '''
    :param file_path: Path for Document to be moved
    :param dst_dir: Destination directory
    '''
    try:
        shutil.move(file_path, dst_dir)
    except OSError:
        shutil.move(file_path, f'{dst_dir}/{os.path.basename(get_nonexistant_path(file_path))}')
        # print("Moving of the file %s failed" % file_path)
    else:
        print("{} File Moved to: {}".format(file_path, dst_dir))


def get_nonexistant_path(fname_path):
    """
    Get the path to a filename which does not exist by incrementing path.
    """
    if not os.path.exists(fname_path):
        return fname_path
    filename, file_extension = os.path.splitext(fname_path)
    i = 1
    new_fname = "{}_{}{}".format(filename, i, file_extension)
    while os.path.exists(new_fname):
        i += 1
        new_fname = "{}_{}{}".format(filename, i, file_extension)
    return new_fname


# Delete file
def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError:
        print("Deleting of the file %s failed" % file_path)


# Delete Directory
def delete_dir(dir_path):
    delete_files = []
    delete_dirs = []
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            delete_files.append(os.path.join(root, f))
        for d in dirs:
            delete_dirs.append(os.path.join(root, d))
    for f in delete_files:
        os.remove(f)
    for d in delete_dirs:
        os.rmdir(d)
    os.rmdir(dir_path)


# Create a directory inside another directory
def create_folder(parent_dir, dir_to_create):
    '''
    :param parent_dir: Directory inside which we want to create another Directory
    :param dir_to_create: Directory To be created
    '''
    if os.path.exists(parent_dir) and not os.path.exists(f'{parent_dir}/{dir_to_create}'):
        try:
            os.makedirs(f'{parent_dir}/{dir_to_create}')
        except OSError:
            print(f'Creation of the directory {parent_dir}/{dir_to_create} failed')
        else:
            print(f'Successfully created the directory {parent_dir}/{dir_to_create}')


# Search a WHOLE word in a given text
def search_word_in_given_text(file_text, search_text, search_whole_word):
    '''
    :param file_text: Text extracted from a document
    :param search_text: The keyword to be searched in the text
    :param search_whole_word: Whether to search words as whole or any appearance otherwise
    :return:
    '''
    res_search = re.search(search_text, file_text, flags=re.IGNORECASE)
    if search_whole_word:
        res_search = re.search(r'\b{}\b'.format(search_text), file_text, flags=re.IGNORECASE)
    if res_search:
        return True
    return False


# a function used to show a folder to be created
def get_file_path_string(file_dic):
    if file_dic['level_three_found']:
        result = '{}/{}/{}'.format(file_dic['level_one_dir'], file_dic['level_two_dir'], file_dic['level_three_dir'])
    elif file_dic['level_two_found']:
        result = '{}/{}'.format(file_dic['level_one_dir'], file_dic['level_two_dir'])
    elif file_dic['level_one_found']:
        result = file_dic['level_one_dir']
    else:
        result = ''
    return result


# Main function that does the directory creation and file movement
def categorize_file(destination_dir, path_dictionaries, file_full_text):
    for file_dic in path_dictionaries:
        level_three = file_dic['level_three_found']
        if level_three and os.path.exists(file_dic['file_path']):
            # create level one folder
            create_folder(destination_dir, file_dic['level_one_dir'])
            # create level two folder
            create_folder('{}/{}'.format(destination_dir, file_dic['level_one_dir']), file_dic['level_two_dir'])
            # create level three folder
            create_folder('{}/{}/{}'.format(destination_dir, file_dic['level_one_dir'], file_dic['level_two_dir']),
                          file_dic['level_three_dir'])
            # move file
            move_file(file_dic['file_path'],
                      '{}/{}/{}/{}'.format(destination_dir, file_dic['level_one_dir'], file_dic['level_two_dir'],
                                           file_dic['level_three_dir']))
            create_file_text(file_dic['file_path'],
                             '{}/{}/{}/{}'.format(destination_dir, file_dic['level_one_dir'], file_dic['level_two_dir'],
                                                  file_dic['level_three_dir']), file_full_text)
            return

        for file_dic_two in path_dictionaries:
            level_two = file_dic_two['level_two_found']
            if level_two and os.path.exists(file_dic_two['file_path']):
                # create level one folder
                create_folder(destination_dir, file_dic_two['level_one_dir'])
                # create level two folder
                create_folder('{}/{}'.format(destination_dir, file_dic_two['level_one_dir']),
                              file_dic_two['level_two_dir'])
                # move file
                move_file(file_dic_two['file_path'],
                          '{}/{}/{}'.format(destination_dir, file_dic_two['level_one_dir'],
                                            file_dic_two['level_two_dir']))
                create_file_text(file_dic['file_path'],
                                 '{}/{}/{}'.format(destination_dir, file_dic_two['level_one_dir'],
                                                   file_dic_two['level_two_dir']), file_full_text)
                return

        for file_dic_one in path_dictionaries:
            level_one = file_dic_one['level_one_found']
            if level_one and os.path.exists(file_dic_one['file_path']):
                # create level one folder
                create_folder(destination_dir, file_dic_one['level_one_dir'])
                # move file
                move_file(file_dic_one['file_path'], '{}/{}'.format(destination_dir, file_dic_one['level_one_dir']))
                create_file_text(file_dic['file_path'],
                                 '{}/{}'.format(destination_dir, file_dic_two['level_one_dir']), file_full_text)
                return

        for file_dic_undefined in path_dictionaries:
            if os.path.exists(file_dic_undefined['file_path']):
                # create undefined folder
                create_folder(destination_dir, 'UNDEFINED')
                # move file
                move_file(file_dic_undefined['file_path'], f'{destination_dir}/UNDEFINED')
                create_file_text(file_dic['file_path'],
                                 f'{destination_dir}/UNDEFINED', file_full_text)
                return


# a function to enable user to make a choice in case a file can be move to more than one possible destination
def get_int_choice(int_choices_list, selection_texts):
    while True:
        try:
            choice = int(input("More than one Categories Were found. Select One {}  : ".format(selection_texts)))
        except ValueError:
            print("Expected a number !!!!!!!!!")
        else:  # got integer, check range
            if choice in int_choices_list:
                break
            print('Invalid Choice. Please select a number from the given choices !!!!!!!!!!')
    return choice


# Create a .txt file for each processed file for verification
def create_file_text(file_path, destination_dir, file_text):
    file_name = os.path.basename(file_path).split('.')[0]
    f = open(f'{destination_dir}/{file_name}.txt', 'w+')
    f.write(file_text)
    f.close()


# Convert PDF file to Image
def convert_pdf_to_image_and_save(file_path, save_directory):
    pages = convert_from_path(file_path)
    for page in pages:
        page.save(f'{save_directory}/output.jpg', 'JPEG')

import menu_to_tp_converter
import ner
import os
root_dir_path = os.path.expanduser("~/Smarter.Codes/src")


def generate_questions():
    """
    generate questions after cuisine selection
    """
    open(root_dir_path+'/question.txt', 'a').close()
    try:
        menu_to_tp_converter.menu_converter()
        ner.NER_plain_text()
    except Exception as e:
        print e

    os.remove(root_dir_path+'/question.txt')

    return {'process': 'Process Complete'}
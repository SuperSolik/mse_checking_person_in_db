import _pickle
import glob
import os
import re

import face_recognition
from app.model import Persons


def insert_many_persons(path_to_train_dir):  # change path
    train_dir = os.listdir(path_to_train_dir)
    count_persons = len(train_dir)
    person_counter = 0
    train_dir = os.listdir(path_to_train_dir)
    print(f'0/{count_persons} of people have been processed (0%)')

    for path_to_person_dir in train_dir:
        person_counter += 1
        print(f'{person_counter}/{count_persons} '
              f'of people have been processed ({person_counter / count_persons * 100:.0f}%) ', end=' ')
        insert_one_person(path_to_person_dir, path_to_train_dir + path_to_person_dir)


def insert_one_person(name, path_to_person_dir):
    if not os.path.exists(path_to_person_dir) or not os.path.isdir(path_to_person_dir):
        print(f'No such file or directory: {path_to_person_dir}')
        return

    pattern = '|'.join(['.jpg', '.png'])
    paths_to_person_imgs = glob.glob(f'{path_to_person_dir}/*[{pattern}]')

    if not paths_to_person_imgs:
        print(f'{path_to_person_dir} doesn\'t contain images with supported formats: .jpg, .png')
        return

    persons = Persons.objects(name=name)
    encodings = _pickle.loads(persons[0].face_encodings) if persons else []

    for path_to_person_img in paths_to_person_imgs:
        face = face_recognition.load_image_file(path_to_person_img)
        face_bounding_boxes = face_recognition.face_locations(face)

        if len(face_bounding_boxes) == 1:
            face_enc = face_recognition.face_encodings(face)[0]
            encodings.append(face_enc)

    person = Persons(name=name, face_encodings=_pickle.dumps(encodings, protocol=2))
    person.save()
    print(f'{name} successfully added')


def delete_person(name=''):
    regex = re.compile('.*' + name)
    person = Persons.objects(name=regex)
    if person:
        person.delete()
        print(f'All {name} data was deleted')
    else:
        print('No such person in db')


def show_persons():
    names = [person.name for person in Persons.objects]
    if names:
        for name in sorted(names):
            print(name)
    else:
        print("No persons in db")


if __name__ == '__main__':
    # delete_person()
    show_persons()
    # delete_person('Elon_Musk')
    # insert_one_person('Elon_Musk', '../resources/train/Elon_Musk')
    # insert_many_persons('../resources/train/')
    # show_persons()

import os
import shelve
import sys
import random
import datetime
import pandas
import barcode as bc
from barcode.writer import ImageWriter
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from os import listdir


'''Author: kamar baraka'''

'''class to store update and manipulate file based database
:Date:06/07/2023'''


class DatabaseApi:
    __container_number = 1
    __total_reuse = 0
    __total_kgs = 0.0
    __register_count = 0
    count = 0

    '''constructor to initialize the class
    :param database the database to reference
    :param barcode_image_storage the path to the generated barcode images folder'''

    '''singleton class'''
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(DatabaseApi, cls).__new__(cls)
        return cls.instance

    def __init__(self, database, barcode_path=None):
        try:
            file = open(f'{database}.dat', 'x')
            self.__class_count = 0
            file.close()
            os.remove(f'{database}.dat')
        except FileExistsError:
            self.__class_count = 1

        try:
            self.database = shelve.open(database, writeback=True)
        except FileExistsError:
            print("database exists")
        if barcode_path is not None:
            self.barcode_image_storage = barcode_path
        self.barcode_image_storage = barcode_path

    """input data from an excel sheet and save it in the database
    the excel sheet must have two columns 'Barcodes' and 'Weight(kgs)'
    :param excel_doc the path to the excel input file"""
    def parse_excel(self, excel_doc):
        database = self.database
        sheet = pandas.read_excel(excel_doc, sheet_name='Sheet1')
        record = sheet.to_dict(orient='records')
        key_list = [str(each_dict['Barcode']) for each_dict in record]
        value_list = [each_dict['Weight(kgs)'] for each_dict in record]

        item_dict = dict(zip(key_list, value_list))

        for k, v in item_dict.items():
            if k in database.keys():
                if float(v) != 0.00:
                    self.set_kg(int(k), v)
                    continue
            self.parse(k)
            if float(v) != 0.00:
                self.set_kg(int(k), v)
                continue
        return f'ok'

    """generate a report on the items in the database and save it to an excel sheet
    :param output_file (str) the path where to save the generated excel sheet
    :returns 'ok' when successful"""
    def report(self, output_file):
        database_shelve = self.database
        record = database_shelve['report']
        data_frame = pandas.DataFrame.from_dict(record)
        data_frame.to_excel(output_file)
        return 'ok'

    """input a barcode into the database
    :param barcode (int) the barcode to save in the database
    :returns 'ok' when successful"""
    def parse(self, barcode):
        if self.__class_count == 0:
            self.database['report'] = []
            report = {'Barcode': str(barcode), 'Reuse Count': 0, 'Weight(kg)': 0.0, 'Total Weight Saved': 0.0}
            self.database['report'].append(report)
            self.__class_count += 1
            self.database['__class_count'] = self.__class_count
            self.database[str(barcode)] = dict(barcode=barcode, count=0, name=self.__container_number,
                                               month=datetime.datetime.now().month, kg=0.0)
            self.__container_number += 1
            self.database['monthly_reuse'] = 0
            self.database['total_reuse'] = self.__total_reuse
            self.database['total_kgs_saved'] = self.__total_kgs
            return 'ok'

        if 'report' not in self.database:
            self.database['report'] = []
        if str(barcode) in self.database:
            return 'data exists'
        self.database[str(barcode)] = dict(barcode=barcode, count=0, name=self.__container_number,
                                           month=datetime.datetime.now().month, kg=0.0)
        report = {'Barcode': str(barcode), 'Reuse Count': 0, 'Weight(kg)': 0.0, 'Total Weight Saved': 0.0}
        self.database['report'].append(report)
        self.__container_number += 1
        self.database['monthly_reuse'] = 0
        self.database['total_reuse'] = self.__total_reuse
        self.database['total_kgs_saved'] = self.__total_kgs
        return 'ok'

    """sets the weight of an item in the database
    :param barcode (int) the barcode of the item to set the weight
    :param kg (float) the float weight you wish to set on the item
    :returns 'ok' when successful"""
    def set_kg(self, barcode, kg):
        database = self.database
        database[str(barcode)]['kg'] = float(kg)
        database['total_kgs_saved'] += (float(database[str(barcode)]['count']) * float(database[str(barcode)]['kg']))
        for dic in database['report']:
            if dic['Barcode'] == str(barcode):
                dic['Weight(kg)'] = kg
                if dic['Total Weight Saved'] != (float(dic['Weight(kg)']) * float(dic['Reuse Count'])):
                    dic['Total Weight Saved'] = (float(dic['Weight(kg)']) * float(dic['Reuse Count']))
        return 'ok'

    """get the data of a particular item in the database
    :param barcode (int) the barcode of the item
    :returns dictionary (dict) containing the items data when successful"""
    def fetch(self, barcode):
        database = self.database
        if str(barcode) not in database:
            return "no such data"
        database[str(barcode)]['count'] += 1
        for dic in database['report']:
            if dic['Barcode'] == str(barcode):
                dic['Reuse Count'] += 1
                dic['Total Weight Saved'] += float(database[str(barcode)]['kg'])
        if database[str(barcode)]['month'] != datetime.datetime.now().month:
            database['monthly_reuse'] = 0
        database['monthly_reuse'] += 1
        database['total_reuse'] += 1
        database['total_kgs_saved'] += float(database[str(barcode)]['kg'])
        barcode_data = {str(barcode): database.get(str(barcode)), 'monthly_reuse': database.get('monthly_reuse'),
                        'total_reuse': database.get('total_reuse'), 'total_kgs_saved': database['total_kgs_saved']}
        return barcode_data

    """generates barcodes and save them in the database
    :param count (int) the number of barcodes to generate
    :keyword kgs (float) the optional weight you wish to associate with each barcode. Can be left blank. If left blank,
    an excel sheet will be generated in the path you provided containing all barcodes without associated weights
    :keyword path (str) the optional path to the directory to save the resulting barcode images
    :keyword image_format (str) the format of the image to be generated. Can be 'png', 'jpeg', 'tiff' or left blank.
    :returns (list) list of successfully generated barcodes."""
    def generate(self, count, kgs=0.0, path=None, image_format="png"):
        self.count = count
        if kgs == 0.0:
            export = True
        else:
            export = False
        lis_of_codes = self.__generator(path, image_format, export)
        for code in lis_of_codes:
            self.parse(code)
            self.set_kg(str(code), kgs)
        return 'ok'

    def __generator(self, path, image_format, export):
        database = self.database
        if path is None:
            if self.barcode_image_storage is None:
                print("please provide a path to save the barcodes")
                raise NotADirectoryError
            path = self.barcode_image_storage
        if self.__class_count == 0:
            database['imagecount'] = 0
            print(f'if {database["imagecount"]}')
        else:
            if database.get('imagecount') is None:
                database['imagecount'] = 0
            database['imagecount'] = self.database['imagecount']
            print(f'else {database["imagecount"]}')
        codes = []
        for counts in range(1, self.count+1):
            random_number = random.randint(100000000000, 999999999999)
            bark = bc.EAN13(str(random_number), writer=ImageWriter(format=image_format))
            bark.save(f'{path}/qrcode{database["imagecount"]}')
            database['imagecount'] += 1
            codes.append(random_number)

        # export_dict = {}
        # if export:
        #     for barcode in codes:
        #         export_dict.update({"Barcodes": str(barcode)})
        #
        #     dataframe = pandas.DataFrame.from_dict(export_dict)
        #     dataframe.to_excel(path)
        return codes

    """register a user in the system
    :param user_profile (dict) a dictionary containing all the user details. The dictionary MUST contain the following
    keys;
    :key 'username' the unique username of the user.
    :key 'firstname' the first name of the user.
    :key 'lastname' the last name of the user.
    :key 'role' the role of the user in the system.
    :key 'password' the password of the user.
    :returns 'ok' (str) upon successful registration"""
    def register(self, user_profile):
        database = self.database
        if self.__register_count == 0:
            database['users'] = {
                user_profile['username']: {
                    'password': user_profile['password'],
                    'firstname': user_profile['firstname'],
                    'lastname': user_profile['lastname'],
                    'role': user_profile['role']
                }
            }
            self.__register_count += 1
            return 'ok'
        if user_profile['username'] in database['users']:
            return 'user exists'
        if 'users' not in database:
            database['users'] = {
                user_profile['username']: {
                    'password': user_profile['password'],
                    'firstname': user_profile['firstname'],
                    'lastname': user_profile['lastname'],
                    'role': user_profile['role']
                }
            }

        database['users'].update(
            {
                user_profile['username']: {
                    'password': user_profile['password'],
                    'firstname': user_profile['firstname'],
                    'lastname': user_profile['lastname'],
                    'role': user_profile['role']
                }
            }
        )
        return 'ok'

    """enables a user to login.
    :param profile (dict) a dictionary containing the user details. It must have the keys;
    :key 'username' the username of the user.
    :key 'password' the password of the user."""
    def login(self, profile):
        database = self.database

        if (
            profile['username'] in database['users'] and
            profile['password'] == database['users'][profile['username']]['password']
        ):
            return 'ok'

    """converts an svg image to png.
    :param path_to_svg (str) the path to the svg file.
    :param path_to_png (str) the path to save the png file.
    :returns 'ok' (str) upon successful conversion."""
    @staticmethod
    def convert_svg_to_png(path_to_svg, path_to_png):
        drawing = svg2rlg(path_to_svg)
        renderPM.drawToFile(drawing, path_to_png, fmt="PNG")
        return 'ok'

    """converts bulk svg images to png.
    :param dir_path_to_svg (str) the path to the directory containing the svg images.
    :param dir_path_to_png (str) the path to the directory you wish to save the png images.
    :returns 'ok' upon successful conversion"""
    @staticmethod
    def bulk_convert_svg_png(dir_path_to_svg, dir_path_to_png):
        no = 0
        svg_files = listdir(dir_path_to_svg)
        for svg_file in svg_files:
            drawing = svg2rlg(f"{dir_path_to_svg}/{svg_file}")
            renderPM.drawToFile(drawing, f"{dir_path_to_png}/conv_png{no}.png", fmt="PNG")
            no += 1
        return 'ok'

    """
    generate excel report of weightless items.
     :param path (str) the path to the location you wish to save the report.
     :returns 'ok' (str) upon successful generation"""
    def report_weightless(self, path):
        database = self.database
        keys = database.keys()
        weightless_bars = []
        for key in keys:

            if key.isnumeric() and database[key]['kg'] == 0.0:
                weightless_bars_dict = {}
                weightless_bars_dict.update(Barcode=key)
                weightless_bars.append(weightless_bars_dict)

        dataframe = pandas.DataFrame.from_dict(weightless_bars)
        dataframe.to_excel(path)
        return 'ok'


"""
test cases"""
if __name__ == '__main__':
    db = DatabaseApi('../../resources/database/database')
    # db1 = DatabaseApi('../../resources/database/database', '../../resources/images/barcodeImages')
    # print(db is db1)
    # print(db1.parse(123456))
    # print(db.fetch(123456))
    # print(db is db1)

    #

    # print(db.generate(205, kgs=0.71))
    # print(db.generate(2300, kgs=0.62))
    # print(db.generate(625, kgs=0.21))
    # print(db.generate(4632, kgs=0.84))
    # print(db.generate(12, 0.68, '../../resources/images/barcodeImages'))
    # print(db.generate(6))
    print(db.generate(2, path='../../resources/images/barcodeImages'))
    # print(db.generate(2, 0.86, '../../resources/images/barcodeImages'))
    # db.generate(2, 0.86)
    # print(db.parse_excel('input.xlsx'))
    # print(db.report('out_test.xlsx'))

    db.report_weightless('weightless.xlsx')

    # print(db.register({'username': 'kamar', 'password': '1234', 'firstname': 'kamar', 'lastname': 'baraka'}))
    # print('done register')
    # print(db.register({'username': 'kahindi', 'password': '1234', 'firstname': 'kahindi', 'lastname': 'baraka'}))
    # print('done register')
    # print(db.register({'username': 'kamori', 'password': '1234', 'firstname': 'kamori', 'lastname': 'baraka'}))
    # print('done register')
    # print(db.register({'username': 'evans', 'password': '1234', 'firstname': 'evans', 'lastname': 'murunga'}))
    # print('done register')
    # print(db.register({'username': 'makena', 'password': '1234', 'firstname': 'makena', 'lastname': 'wachira'}))
    # print('done register')
    #
    # print(db.login({'username': 'kamar', 'password': '1234'}))
    # print('done login')
    # print(db.login({'username': 'kahindi', 'password': '1234'}))
    # print('done login')
    # print(db.login({'username': 'kamori', 'password': '1234'}))
    # print('done login')
    # print(db.login({'username': 'evans', 'password': '1234'}))
    # print('done login')
    # print(db.login({'username': 'makena', 'password': '1234'}))
    # print('done login')

    print("done")
    sys.exit(25)

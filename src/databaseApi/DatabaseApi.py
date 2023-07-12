import os
import shelve
import sys
import random
import datetime
import pandas
import barcode as bc


'''author: kamar baraka'''

'''class to store update and manipulate file based database
:since:06/07/2023'''


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

    def report(self, output_file):
        database_shelve = self.database
        record = database_shelve['report']
        data_frame = pandas.DataFrame.from_dict(record)
        data_frame.to_excel(output_file)
        return 'ok'

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

    def fetch(self, barcode):
        database = self.database
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

    def generate(self, count, kgs=0.0, path=None):
        self.count = count
        lis_of_codes = self.__generator(path)
        for code in lis_of_codes:
            self.parse(code)
            self.set_kg(str(code), kgs)
        return 'ok'

    def __generator(self, path):
        database = self.database
        if path is None:
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
            bark = bc.EAN13(str(random_number))
            bark.save(f'{path}/qrcode{database["imagecount"]}')
            database['imagecount'] += 1
            codes.append(random_number)
        return codes

    def register(self, user_profile):
        database = self.database
        if self.__register_count == 0:
            database['users'] = {
                user_profile['username']: {
                    'password': user_profile['password'],
                    'firstname': user_profile['firstname'],
                    'lastname': user_profile['lastname']
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
                    'lastname': user_profile['lastname']
                }
            }

        database['users'].update(
            {
                user_profile['username']: {
                    'password': user_profile['password'],
                    'firstname': user_profile['firstname'],
                    'lastname': user_profile['lastname']
                }
            }
        )
        return 'ok'

    def login(self, profile):
        database = self.database

        if (
            profile['username'] in database['users'] and
            profile['password'] == database['users'][profile['username']]['password']
        ):
            return 'ok'


if __name__ == '__main__':
    db = DatabaseApi('../../resources/database/database')
    db1 = DatabaseApi('../../resources/database/database', '../../resources/images/barcodeImages')
    print(db is db1)
    print(db1.parse(123456))
    print(db.fetch(123456))
    print(db is db1)

    # while True:
    #     inp = input('scan barcode to save, type "do" when done \n')
    #     if inp == 'do':
    #         break
    #     print(db.parse(str(inp)))
    # while True:
    #     inpt = input('scan barcodes, type "exit" to exit or "kgs" to input kgs \n')
    #     if inpt == 'exit':
    #         break
    #     if inpt == 'kgs':
    #         while True:
    #             input_code = input('scan the item to insert kgs, type "do" when done\n')
    #             if input_code == 'do':
    #                 break
    #             input_kg = input('enter the kg to input, type "do" when done \n')
    #             if input_kg == 'do':
    #                 break
    #             print(db.set_kg(input_code, input_kg))
    #     try:
    #         print(db.fetch(inpt))
    #     except KeyError:
    #         print('scan again')
    #         continue

    # print(db.generate(205, kgs=0.71))
    # print(db.generate(2300, kgs=0.62))
    # print(db.generate(625, kgs=0.21))
    # print(db.generate(4632, kgs=0.84))
    # print(db.generate(12, 0.68, '../../resources/images/barcodeImages'))
    # print(db.generate(6, 0.72))
    # print(db.generate(2, 0.58))
    # print(db.generate(2, 0.86))
    # db.generate(2, 0.86)
    # print(db.parse_excel('input.xlsx'))
    # print(db.report('out_test.xlsx'))

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

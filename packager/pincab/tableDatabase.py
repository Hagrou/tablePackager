import logging
import json

class TableDatabase:
    def __init__(self):
        self.__data = None

        with open('tools/pincab.json', 'r') as file:
            self.__data = json.load(file)

    def search(self, name):
        for table in self.__data:
            if table.get('Table Name (Manufacturer Year)') == name:
                return table

    def search_fuzzy(self, name):
        min = 1000
        tableFound = None
        for table in self.__data:
            value = self.levenshtein(name, table.get('Table Name (Manufacturer Year)'))
            if value <= min:
                min = value
                tableFound = table

        print("Levenshtein: %d [%s] [%s]" % (min, tableFound.get('Table Name (Manufacturer Year)'), name))
        return tableFound

    def get_directBS2_url(self, table):
        return table.get('VisualPinball').get('DirectBS2').get('URL')

    def get_native_rom_url(self, table):
        return table.get('VisualPinball').get('Rom').get('native').get('URL')

    def get_colored_rom_url(self, table):
        return table.get('VisualPinball').get('Rom').get('colored').get('URL')

    def is_rom_required(self, table):
        return  table.get('VisualPinball').get('Rom').get('colored').get('ROM') or table.get('VisualPinball').get('Rom').get('native').get('Name')

    def search_table(self, name):
        dbTable = self.__database.search(name)
        if dbTable is not None:
            return dbTable

        dbTable = self.__database.search_fuzzy(name)
        logging.info(
            'Table %s not found in database, try with %s' % (name, dbTable.get('Table Name (Manufacturer Year)')))
        return dbTable

    #https: // stackabuse.com / levenshtein - distance - and -text - similarity - in -python /
    def levenshtein(self, seq1, seq2):
        size_x = len(seq1) + 1
        size_y = len(seq2) + 1
        matrix = np.zeros ((size_x, size_y))
        for x in range(size_x):
            matrix [x, 0] = x
        for y in range(size_y):
            matrix [0, y] = y

        for x in range(1, size_x):
            for y in range(1, size_y):
                if seq1[x-1] == seq2[y-1]:
                    matrix [x,y] = min(
                        matrix[x-1, y] + 1,
                        matrix[x-1, y-1],
                        matrix[x, y-1] + 1
                    )
                else:
                    matrix [x,y] = min(
                        matrix[x-1,y] + 1,
                        matrix[x-1,y-1] + 1,
                        matrix[x,y-1] + 1
                    )
        #print (matrix)
        return (matrix[size_x - 1, size_y - 1])


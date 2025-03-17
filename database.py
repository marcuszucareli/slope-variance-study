import sqlite3


# Class to interact with database
class database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
    

    def test_db(self):
        print('working')


    def create_table(self, table_name, columns):
        columns_string = ''
        for i, (column, c_type) in enumerate(columns.items()):
            columns_string += column + ' ' + c_type
            if i == len(columns) - 1:
                continue
            else:
                columns_string += ', '
        
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                        ({columns_string})
                        ''')
    

    def add(self, table_name, values):
        columns_string = ''
        values_string = ''
        for i, (column, value) in enumerate(values.items()):
            columns_string += f"{column}"
            values_string += f"{value}"
            if i == len(values) - 1:
                continue
            else:
                columns_string += ', '
                values_string += ', '

        self.c.execute(f'''INSERT INTO {table_name} ({columns_string}) VALUES
                    ({values_string})
                    ''')
        
        self.conn.commit()
        

    def get(self, table_name, columns, condition):
        res = self.c.execute(f'''SELECT {columns} FROM {table_name} WHERE {condition}''')
        return res.fetchone()


# Create our results database table
if __name__=='__main__':

    results = {
        'id': 'INTEGER PRIMARY KEY',
        'height': 'INTEGER',
        'length': 'INTEGER',
        'cohesion': 'INTEGER',
        'friction': 'INTEGER',
        'weight': 'INTEGER',
        'fs': 'REAL',
        'id_combinations': 'INTEGER' 
    }

    db = database()
    db.create_table('results', results)






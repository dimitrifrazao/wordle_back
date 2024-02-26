import sys
import database

def main(argv):
    kwargs = {}
    if len(argv) > 0:
        kwargs['user'] =argv[0]
    if len(argv) > 1:
        kwargs['password'] =argv[1]
    if len(argv) > 2:
        kwargs['host'] =argv[2]

    kwargs['database'] = ''

    db = database.DataBase(**kwargs)
    db.connect()
    if not db.databaseExists():
        db.createDatabase()
        if db.databaseExists():
            db.close()
            kwargs['database'] = 'wordDB'
            db = database.DataBase(**kwargs)
            db.connect()
            db.createTables()
            if db.hasTables():
                db.addWordsFromFile(file_name="sgb-words.txt")
                if db.getAllWords():
                    print("database setup complete!")
                else:
                    print("failed adding words")
            else:
                print("failed adding tables")            
        else:
            print("failed adding database, please check your setup arguments")
    else:
        print("database already exists")
    db.close()

if __name__ == "__main__":
   main(sys.argv[1:])
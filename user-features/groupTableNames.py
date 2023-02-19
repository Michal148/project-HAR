import pyodbc
import os

def groupTables():

    # read database credentials
    driver = os.environ['DBDriver']
    server = os.environ['DBServer']
    database = os.environ['DBDb']
    username = os.environ['DBUser']
    password = os.environ['DBPass']

    # prepare list used to store data returned by the database
    nameList = []

    # connect to database and retrieve tabl names
    with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select schema_name(t.schema_id) as schema_name, \
                            t.name as table_name, \
                            t.create_date, \
                            t.modify_date \
                            from sys.tables t")
            row = cursor.fetchone()
            while row:
                nameList.append(str(row[1]))
                row = cursor.fetchone()

    # prepare empty lists to store accelerometer, gyroscope and magnetometer table names
    aList = []
    gList = []
    mList = []
    groupedList = []

    # run first loop to put the names in the same order
    for word in sorted(nameList):
        if 'Accelerometer' in word:
            aList.append(word)

        elif 'Gyroscope' in word:
            gList.append(word)

        elif 'Magnetometer' in word:
            mList.append(word)

    # append corresponding names to final list
    for id_ in range(len(aList)):
        groupedList.append([aList[id_], gList[id_], mList[id_]])

    return groupedList
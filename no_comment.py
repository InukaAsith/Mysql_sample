import subprocess
import sys
import re
import time
try:
    from pick import pick
except:
    subprocess.check_call([sys.executable,"-m","pip","install","pick"])
    from pick import pick
import mysql.connector as mysql
from mysql.connector import errorcode
list1=[]
Create=False
tablecre=[]
Back=False

def create_database(cursr, db_name):
    """Creates a database with the specified name."""
    try:
        cursr.execute("CREATE DATABASE {}".format(db_name))
    except mysql.Error as e:
        print("Database Creation Error: {}".format(e))
        exit(1)

def create_table(cursr, tablen):
    """Creates a table with the specified name and columns."""
    tableval = input("Enter table columns seperate a column by , : ").strip()
    tablecre = ",".join([col + " VARCHAR(255)" for col in re.split(",",tableval)])
    tablecre = "id INT PRIMARY KEY AUTO_INCREMENT, {}, Edited VARCHAR(255)".format(tablecre)
    cursr.execute("CREATE TABLE IF NOT EXISTS {}({})".format(tablen,tablecre))
    print("Log: Table {} Created Successfully".format(tablen))

def show_record(rcname, rcid, tablen, cursr, colindexmax, columns, db):
    """Displays the details of a specific record."""
    print(f"record {rcname} from {tablen}")
    sql= "SELECT * FROM {} WHERE id = {}".format(tablen,rcid+1)
    try:
        cursr.execute(sql)
    except mysql.errors.ProgrammingError as e:
        try:
            cursr.execute("ALTER TABLE {} ADD id INT PRIMARY KEY AUTO_INCREMENT".format(tablen))
            cursr.execute(sql)
        except mysql.errors.ProgrammingError as e:
            re1=columns[0]
            cursr.execute("SELECT * FROM {} WHERE {} = {}".format(tablen,re1,rcid+1))        
    results=cursr.fetchone()
    print("Details for record {}".format(rcname))
    list=[]
    for f in range(colindexmax):
        list.append(f" -{columns[f]}: {results[f]}")
    list1=["Add new field","Delete this Record","Edit record", "Delete a Feild","Export this record","Back"]
    title="\n".join(list)        #Info as a list for pick
    option, index=pick(list1,title)
    if index==0:
        add_field(tablen,db,cursr,rcid,columns)
    if index==1:
        delete_record(tablen,rcid,rcname,cursr,db)
    if index==2:
        edit_record(tablen,cursr,columns,rcid,db)
    if index==3:
        delete_field(tablen,cursr,columns)
    if index==4:
        export_record(rcname,columns,results,colindexmax)
    if len(list1)-1 == index:
        return True

def add_record(tablen, columns, colindexmax, db,cursr):
    """Adds a new record to the specified table."""
    list1.clear()
    Datetime= False
    if "Edited".lower() in [f.lower() for f in columns]:
        colindexmax, Datetime = colindexmax-2 , True
    list1.append("NULL")
    for r in range(colindexmax):
        list1.append(input("Enter {} :".format(columns[r+1])))
    if Datetime:    
        list1.append(time.ctime())
    sql="INSERT INTO {} VALUES{}".format(tablen,(str(tuple(list1)).replace("'NULL'","NULL"))) 
    try:
        cursr.execute(sql)
    except:
        print("Log : Database Error")
    db.commit()
    print(f"Log: Successfully inserted record {list1[0]} to {tablen}")
    return True

def add_field(tablen,db,cursr,rcid,columns):
    """Adds a new field to current table"""
    if list1:
        list1.clear()

    fnme=input("Enter a field name :")
    fname = str(fnme) + " VARCHAR(255)"
    default=input("Enter a default value :")
    if default:
        default = str(default)
    else:
        print("Error: No value given")
    sql="ALTER TABLE {} ADD {} DEFAULT '{}'".format(tablen,fname,default)
    cursr.execute(sql)
    db.commit()
    print("Log: Created new field with default value {}".format(default))
    sql="UPDATE {} SET {} = '{}' WHERE id = {}".format(tablen,fnme,str(input("Enter a value for current field")),rcid+1)
    if "Edited" in columns: 
        sql2 = "UPDATE {} SET Edited = '{}' WHERE id = {}".format(tablen,time.ctime(),rcid+1)
        cursr.execute(sql)
        cursr.execute(sql2)
    else:
        cursr.execute(sql)
    db.commit()
    print("Log: Value of field updated {}".format(default))
    return True
    
def delete_record(tablen,rcid,rcname,cursr,db):
    """Deletes the record"""
    sql = "DELETE FROM {} WHERE id ={}".format(tablen,rcid+1)
    cursr.execute(sql)
    db.commit()
    print("Log :",rcname, "Deleted Successfully")
    return True

def delete_field(tablen,cursr,columns):
    """Deletes a feild"""
    title="Select a feild to drop"
    columns=[x for x in columns if x != "id"] #same as columns.remove("id")
    option,index=pick(columns,title)
    sql = "ALTER TABLE {} DROP COLUMN {}".format(tablen,option)
    if "Edited" in columns:  
        sql2 = "UPDATE {} SET Edited = '{}'".format(tablen,time.ctime())
        cursr.execute(sql)
        cursr.execute(sql2)
    else:
        cursr.execute(sql)
    print("Deleted feild {}".format(option))
    return True
    
def edit_record(tablen,cursr,columns,rcid,db):
    Updated=False
    """Edit the current record"""
    while True:
        title="Select a column to edit"
        if Updated: title = title+Updated 
        column=[x for x in columns if x != "id" and x!="Edited" and x!="Back"]
        column.append("Back")
        option,index=pick(column,title)
        if option== "Back":
            break
        val=str(input("Enter a new value for {} :".format(option)))
        sql= "UPDATE {} SET {} = '{}' WHERE id = {}".format(tablen,option,val,rcid+1)
        if "Edited" in columns: 
            sql2 = "UPDATE {} SET Edited = '{}' WHERE id = {}".format(tablen,time.ctime(),rcid+1)
            cursr.execute(sql)
            cursr.execute(sql2)
        else:
            cursr.execute(sql)
        Updated= "\nUpdated {} of {} with {}".format(option,tablen,val)
        
        db.commit()
    return True

def export_record(rcname,columns,results,colindexmax):    
    out=f"\n\nDetails for the record {rcname}\n"
    for f in range(colindexmax):
        out=out+f"\n  -{columns[f]} : {results[f]}" #same implementation as list.append(f"-{columns[f]} : {results[f]}") and then joining it with "\n".join()
    with open("export.txt","a+") as file:
        file.write(out) #same as list.append(f"-{columns[f]} : {results[f]}") then file.writelines(list)   
    print("Log : File Exported Successfully")
    return True
    
    
def main(list1,Create):
    """Main function that handles the user interaction and database operations."""
    # Establish database connection
    db=mysql.connect(host="localhost",username="root",passwd="root")
    if db.is_connected: print("Log: Database connection Success")
    cursr=db.cursor()

    # Select or create a database
    sql="SHOW DATABASES"
    cursr.execute(sql)
    results=cursr.fetchall()
    for i in results:
        list1.append(i)
    list1=[d[0] for d in list1]
    list1.append("Create new Database")
    DB_NAME, index= pick(list1,"Please select a databaseto work with") 
    if index==(len(list1)-1): DB_NAME,Create=input("Enter a Database Name to Create :"), True 
    if DB_NAME and Create: 
        create_database(cursr, DB_NAME) 
        print("Database {} Successfully Created".format(DB_NAME)) 
    Create=False 
 
    # Select or create a table 
    try: 
        cursr.execute("USE {}".format(DB_NAME)) 
    except mysql.Error as e: 
        print("Alert: Database {} doesn't exist".format(DB_NAME)) 
        if e.errno == errorcode.ER_BAD_DB_ERROR: 
            create_database(cursr, DB_NAME) 
            print("Log: Database {} Created Successfully".format(DB_NAME)) 
            db.database=DB_NAME 
        else: 
            print(e) 
            exit(1) 
    sql="SHOW TABLES" 
    cursr.execute(sql) 
    results=cursr.fetchall() 
    list1.clear() 
    for i in results: 
        list1.append(i) 
    list1=[d[0] for d in list1] 
    title="Please select a table to work with" 
    list1.append("Create new table") 
    options = list1 
    tablen, index=pick(options,title) 
    if index==(len(options)-1): tablen, Create=input("Enter a table noame to create :"),True 
    if tablen and Create: 
        create_table(cursr,tablen) 
     
    # Get table columns 
    sql = "SHOW COLUMNS FROM {}".format(tablen) 
    cursr.execute(sql) 
    results=cursr.fetchall() 
    columns= [f[0] for f in results] 
    results.clear() 
    colindexmax=len(columns) 
    print("Using {} ".format(tablen)) 
 
    # Main loop for user interaction 
    while True: 
        list1.clear() 
        list1=[ 
            "Show all records", 
            "Create a record", 
            "Search a record" 
        ] 
        title="Select an option" 
        option,index=pick(list1,title) 
        if index== 0: 
            # Show all records 
            sql="SELECT * FROM {}".format(tablen) 
            cursr.execute(sql) 
            results=cursr.fetchall() 
            results=([str(r[0])+f" {r[1]}" for r in results]) 
            results.append('Back') 
            title="Select a record" 
            rcname,rcid=pick(results,title) 
            if rcid==len(results)-1: 
                break 
            show_record(rcname,rcid,tablen,cursr,colindexmax,columns,db) 
            continue 
        if index==1: 
            # Create a record 
            add_record(tablen,columns,colindexmax,db,cursr) 
            continue 
        if index==2: 
            # Search a record 
            search_term = input("Enter the search term: ") 
            sql = "SELECT * FROM {} WHERE {} LIKE '%{}%'".format(tablen, columns[1], search_term) 
            cursr.execute(sql) 
            results = cursr.fetchall() 
            results=results[0]
            if not results: 
                print("No records found.") 
            else: 
                list=[]
                for f in range(colindexmax):
                    list.append(f" -{columns[f]}: {results[f]}")
                list1=["Add new field", "Edit record","Back"]
                title="\n".join(list)
                option, index=pick(list1,title)
                if index==0:
                    add_record(tablen,columns,colindexmax,db,cursr)
                if len(list1)-1 == index:
                    return True
                        
 
if __name__ == "__main__": 
    main(list1,Create)

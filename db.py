# Import the required modules
import subprocess
import sys
import re
import time
try:
     # Try to import the pick module, which allows the user to select an option from a list
    from pick import pick
except:
    # If the pick module is not installed, use pip to install it
    subprocess.check_call([sys.executable,"-m","pip","install","pick"])
    from pick import pick
# Import the mysql.connector module, which allows Python to interact with MySQL databases
import mysql.connector as mysql
# Import the errorcode module, which contains error codes for MySQL errors
from mysql.connector import errorcode
# Initialize an empty list to store the database names
list1=[]
# Initialize a boolean variable to indicate whether a new database or table needs to be created
Create=False
# Initialize an empty list to store the table columns
tablecre=[]
# Initialize a boolean variable to indicate whether the user wants to go back to the previous menu
Back=False

def create_database(cursr, db_name):
    """Creates a database with the specified name.

    Args:
        cursr: A cursor object to execute SQL statements.
        db_name: A string representing the name of the database to create.

    Raises:
        mysql.Error: If an error occurs while creating the database.
    """
    try:
        # Execute the SQL statement to create a database
        cursr.execute("CREATE DATABASE {}".format(db_name))
    except mysql.Error as e:
        # If an error occurs, print the error message and exit the program
        print("Database Creation Error: {}".format(e))
        exit(1)

def create_table(cursr, tablen):
    """Creates a table with the specified name and columns."""
    # Ask the user to enter the table columns, separated by commas
    tableval = input("Enter table columns seperate a column by , : ").strip()
    # Create a string of column names and data types, using VARCHAR(255) as the default data type
    tablecre = ",".join([col + " VARCHAR(255)" for col in re.split(",",tableval)])
    # Add an id column as the primary key with auto-increment
    tablecre = "id INT PRIMARY KEY AUTO_INCREMENT, {}, Edited VARCHAR(255)".format(tablecre)
    # Execute the SQL statement to create a table
    cursr.execute("CREATE TABLE IF NOT EXISTS {}({})".format(tablen,tablecre))
    # Print a log message to indicate the table creation was successful
    print("Log: Table {} Created Successfully".format(tablen))

def show_record(rcname, rcid, tablen, cursr, colindexmax, columns, db):
    """Displays the details of a specific record."""
    # Print the record name and table name
    print(f"record {rcname} from {tablen}")
    # Create a SQL statement to select the record by its id
    sql= "SELECT * FROM {} WHERE id = {}".format(tablen,rcid+1)
    try:
        # Execute the SQL statement
        cursr.execute(sql)
    except mysql.errors.ProgrammingError as e:
        # If a programming error occurs, it means the table does not have an id column
        try:
            # Try to add an id column to the table
            cursr.execute("ALTER TABLE {} ADD id INT PRIMARY KEY AUTO_INCREMENT".format(tablen))
            # Execute the SQL statement again
            cursr.execute(sql)
        except mysql.errors.ProgrammingError as e:
            # If another programming error occurs, it means the table does not have any records
            # Use the first column as the id column instead
            re1=columns[0]
            cursr.execute("SELECT * FROM {} WHERE {} = {}".format(tablen,re1,rcid+1))        
    # Fetch the record from the cursor
    results=cursr.fetchone()
    # Print the details of the record
    print("Details for record {}".format(rcname))
    # Initialize an empty list to store the record fields
    list=[]
    # Loop through the columns and append the field name and value to the list
    for f in range(colindexmax):
        list.append(f" -{columns[f]}: {results[f]}")
    # Create a list of options for the user to perform on the record
    list1=["Add new field","Delete this Record","Edit record", "Delete a Feild","Export this record","Back"]
    # Create a title for the pick module, using the list of record fields
    title="\n".join(list)        #Info as a list for pick
    # Use the pick module to let the user select an option
    option, index=pick(list1,title)
    # If the user chooses to add a new field, call the add_field function
    if index==0:
        add_field(tablen,db,cursr,rcid,columns)
    # If the user chooses to delete the record, call the delete_record function
    if index==1:
        delete_record(tablen,rcid,rcname,cursr,db)
    # If the user chooses to edit the record, call the edit_record function
    if index==2:
        edit_record(tablen,cursr,columns,rcid,db)
    # If the user chooses to delete a field, call the delete_field function
    if index==3:
        delete_field(tablen,cursr,columns)
    if index==4:
        export_record(rcname,columns,results,colindexmax)       
    # If the user chooses to go back, return True
    if len(list1)-1 == index:
        return True

def add_record(tablen, columns, colindexmax, db,cursr):
    """Adds a new record to the specified table."""
    # Clear the list1 variable
    list1.clear()
    # Initialize a boolean variable to indicate whether the table has an Edited column
    Datetime= False
    # Check if the table has an Edited column, which stores the timestamp of the last edit
    if "Edited".lower() in [f.lower() for f in columns]:
        # If yes, reduce the colindexmax by 2 and set Datetime to True
        colindexmax, Datetime = colindexmax-2 , True
    # Append a NULL value to the list1, which will be used as the id value
    list1.append("NULL")
    # Loop through the columns, except the id and Edited columns, and ask the user to enter the values
    for r in range(colindexmax):
        list1.append(input("Enter {} :".format(columns[r+1])))
    # If the table has an Edited column, append the current time to the list1
    if Datetime:    
        list1.append(time.ctime())
    # Create a SQL statement to insert the values into the table
    sql="INSERT INTO {} VALUES{}".format(tablen,(str(tuple(list1)).replace("'NULL'","NULL"))) 
    try:
        # Execute the SQL statement
        cursr.execute(sql)
    except:
        # If an error occurs, print a log message
        print("Log : Database Error")
    # Commit the changes to the database
    db.commit()
    # Print a log message to indicate the record insertion was successful
    print(f"Log: Successfully inserted record {list1[0]} to {tablen}")
    # Return True
    return True

def add_field(tablen,db,cursr,rcid,columns):
    """Adds a new field to current table"""
    # Clear the list1 variable
    if list1:
        list1.clear()

    # Ask the user to enter a field name
    fnme=input("Enter a field name :")
    # Create a string of the field name and data type, using VARCHAR(255) as the default data type
    fname = str(fnme) + " VARCHAR(255)"
    # Ask the user to enter a default value for the new field
    default=input("Enter a default value :")
    # If the user enters a value, convert it to a string
    if default:
        default = str(default)
    else:
        # If the user does not enter a value, print an error message
        print("Error: No value given")
    # Create a SQL statement to add the new field to the table with the default value
    sql="ALTER TABLE {} ADD {} DEFAULT '{}'".format(tablen,fname,default)
    # Execute the SQL statement
    cursr.execute(sql)
    # Commit the changes to the database
    db.commit()
    # Print a log message to indicate the new field creation was successful
    print("Log: Created new field with default value {}".format(default))
    # Create a SQL statement to update the value of the new field for the current record
    sql="UPDATE {} SET {} = '{}' WHERE id = {}".format(tablen,fnme,str(input("Enter a value for current field")),rcid+1)
    # Check if the table has an Edited column
    if "Edited" in columns: 
        # If yes, create another SQL statement to update the timestamp of the last edit
        sql2 = "UPDATE {} SET Edited = '{}' WHERE id = {}".format(tablen,time.ctime(),rcid+1)
        # Execute both SQL statements
        cursr.execute(sql)
        cursr.execute(sql2)
    else:
        # If no, execute only the first SQL statement
        cursr.execute(sql)
    # Commit the changes to the database
    db.commit()
    # Return True
    return True
def delete_record(tablen,rcid,rcname,cursr,db):
    """Deletes the record"""
    # Create a SQL statement to delete the record by its id
    sql = "DELETE FROM {} WHERE id ={}".format(tablen,rcid+1)
    # Execute the SQL statement
    cursr.execute(sql)
    # Commit the changes to the database
    db.commit()
    # Print a log message to indicate the record deletion was successful
    print("Log :",rcname, "Deleted Successfully")
    # Return True
    return True

def delete_field(tablen,cursr,columns):
    """Deletes a feild"""
    # Create a title for the pick module
    title="Select a feild to drop"
    # Remove the id column from the list of columns
    columns=[x for x in columns if x != "id"] #same as columns.remove("id")
    # Use the pick module to let the user select a column to delete
    option,index=pick(columns,title)
    # Create a SQL statement to drop the selected column from the table
    sql = "ALTER TABLE {} DROP COLUMN {}".format(tablen,option)
    # Check if the table has an Edited column
    if "Edited" in columns:  
        # If yes, create another SQL statement to update the timestamp of the last edit
        sql2 = "UPDATE {} SET Edited = '{}'".format(tablen,time.ctime())
        # Execute both SQL statements
        cursr.execute(sql)
        cursr.execute(sql2)
    else:
        # If no, execute only the first SQL statement
        cursr.execute(sql)
    # Print a log message to indicate the field deletion was successful
    print("Deleted feild {}".format(option))
    # Return True
    return True
    
def edit_record(tablen,cursr,columns,rcid,db):
    # Initialize a variable to store the update message
    Updated=False
    """Edit the current record"""
    # Start a while loop to let the user edit multiple columns
    while True:
        # Create a title for the pick module
        title="Select a column to edit"
        # If the user has already updated a column, append the update message to the title
        if Updated: title = title+Updated 
        # Create a list of columns that can be edited, excluding the id and Edited columns
        column=[x for x in columns if x != "id" and x!="Edited" and x!="Back"]
        # Add a Back option to the list of columns
        column.append("Back")
        # Use the pick module to let the user select a column to edit
        option,index=pick(column,title)
        # If the user chooses to go back, break the loop
        if option== "Back":
            break
        # Ask the user to enter a new value for the selected column
        val=str(input("Enter a new value for {} :".format(option)))
        # Create a SQL statement to update the value of the selected column for the current record
        sql= "UPDATE {} SET {} = '{}' WHERE id = {}".format(tablen,option,val,rcid+1)
        # Check if the table has an Edited column
        if "Edited" in columns: 
            # If yes, create another SQL statement to update the timestamp of the last edit
            sql2 = "UPDATE {} SET Edited = '{}' WHERE id = {}".format(tablen,time.ctime(),rcid+1)
            # Execute both SQL statements
            cursr.execute(sql)
            cursr.execute(sql2)
        else:
            # If no, execute only the first SQL statement
            cursr.execute(sql)
        # Update the update message with the column name, table name, and new value
        Updated= "\nUpdated {} of {} with {}".format(option,tablen,val)
        
        # Commit the changes to the database
        db.commit()
    # Return True
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
    # If the connection is successful, print a log message
    if db.is_connected: print("Log: Database connection Success")
    # Create a cursor object to execute SQL statements
    cursr=db.cursor()

    # Select or create a database
    # Create a SQL statement to show all the existing databases
    sql="SHOW DATABASES"
    # Execute the SQL statement
    cursr.execute(sql)
    # Fetch the results from the cursor
    results=cursr.fetchall()
    # Loop through the results and append the database names to the list1
    for i in results:
        list1.append(i)
    # Convert the list of tuples to a list of strings
    list1=[d[0] for d in list1]
    # Add an option to create a new database to the list1
    list1.append("Create new Database")
    # Use the pick module to let the user select a database to work with
    DB_NAME, index= pick(list1,"Please select a databaseto work with") 
    # If the user chooses to create a new database, ask them to enter a database name and set Create to True
    if index==(len(list1)-1): DB_NAME,Create=input("Enter a Database Name to Create :"), True 
    # If the user enters a database name and Create is True, call the create_database function
    if DB_NAME and Create: 
        create_database(cursr, DB_NAME) 
        # Print a log message to indicate the database creation was successful
        print("Database {} Successfully Created".format(DB_NAME)) 
    # Set Create to False
    Create=False 
 
    # Select or create a table 
    # Try to use the selected database
    try: 
        cursr.execute("USE {}".format(DB_NAME)) 
    # If an error occurs, it means the database does not exist
    except mysql.Error as e: 
        print("Alert: Database {} doesn't exist".format(DB_NAME)) 
        # Check the error code
        if e.errno == errorcode.ER_BAD_DB_ERROR: 
            # If the error code is ER_BAD_DB_ERROR, it means the database name is invalid
            # Call the create_database function to create a new database
            create_database(cursr, DB_NAME) 
            # Print a log message to indicate the database creation was successful
            print("Log: Database {} Created Successfully".format(DB_NAME)) 
            # Set the database attribute of the connection object to the new database name
            db.database=DB_NAME 
        else: 
            # If the error code is not ER_BAD_DB_ERROR, it means there is another problem
            # Print the error message and exit the program
            print(e) 
            exit(1) 
    # Create a SQL statement to show all the existing tables in the database
    sql="SHOW TABLES" 
    # Execute the SQL statement
    cursr.execute(sql) 
    # Fetch the results from the cursor
    results=cursr.fetchall() 
    # Clear the list1 variable
    list1.clear() 
    # Loop through the results and append the table names to the list1
    for i in results: 
        list1.append(i) 
    # Convert the list of tuples to a list of strings
    list1=[d[0] for d in list1] 
    # Create a title for the pick module
    title="Please select a table to work with" 
    # Add an option to create a new table to the list1
    list1.append("Create new table") 
    # Create a list of options for the user to select a table
    options = list1 
    # Use the pick module to let the user select a table
    tablen, index=pick(options,title) 
    # If the user chooses to create a new table, ask them to enter a table name and set Create to True
    if index==(len(options)-1): tablen, Create=input("Enter a table noame to create :"),True 
    # If the user enters a table name and Create is True, call the create_table function
    if tablen and Create: 
        create_table(cursr,tablen) 
     
    # Get table columns 
    # Create a SQL statement to show the columns of the selected table
    sql = "SHOW COLUMNS FROM {}".format(tablen) 
    # Execute the SQL statement
    cursr.execute(sql) 
    # Fetch the results from the cursor
    results=cursr.fetchall() 
    # Create a list of column names from the results
    columns= [f[0] for f in results] 
    # Clear the results variable
    results.clear() 
    # Get the number of columns
    colindexmax=len(columns) 
    # Print a log message to indicate the table selection was successful
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

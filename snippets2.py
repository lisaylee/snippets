import psycopg2
import logging # will allow you to track what happens in the application, and identify problems with the code
import argparse
import sys

# set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")

# connect to database from python
connection = psycopg2.connect(
    database = "drinkwater",
    user = "postgres",
    password = "lawncare"
    )

logging.debug("Database connection established.")


def put(name,snippet,hide=False):
    """Store a snippet with an associated name."""
    # import pdb; pdb.set_trace()
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))

    with connection.cursor() as cursor:
        try:
            command = "insert into snippets values (%s, %s, %s)"
            cursor.execute(command, (name, snippet, hide))
        except psycopg2.IntegrityError:
            connection.rollback()
            command = "update snippets set message=%s, hidden=%s where keyword=%s"
            cursor.execute(command, (snippet,hide,name))
        connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet

# connection.cursor method: creating a cursor object - allows us to run SQL
# commands in Postgres session insert into statement: constructing a string
# which contains insert into, with two placeholders for keyword and message
# (%s) cursor.execute: running the command on the database, substituting the
# snippet keyword and message by passing them as a tuple connection.commit:
# saving changes to the database

### GET CHALLENGE ###
# Try to implement the get() function
# Construct a select statement to retrieve the snippet with a given keyword 
# Run the statement on the database 
# Fetch the corresponding row from the database
# Run the message from the row

def get(name):
    """Retrieve the snippet with a given keyword"""
    logging.info("Retrieving snippet {!r}".format(name))

    with connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    if not row:
        # If no snippet was found with that name
        logging.debug("Snippet does not exist")
        return "404: Snippet Not Found"
    else:
        logging.debug("Snippet retrieved successfully.")
    return row[0]

# Snippets Catalog
# Create Catalog function: Provides list of keywords to select from
def catalog():
    """Query keywords from snippets table"""
# import pdb; pdb.set_trace()
    logging.info("Querying the database")
    with connection.cursor() as cursor:
        command = "select keyword, message from snippets where hidden=False \
        order by keyword ASC"
        cursor.execute(command)
        rows = cursor.fetchall()
        for x in rows:
            print("the keyworrd is: {}, the message is: {}".format(x[0], x[1]))
logging.debug("Query complete")

# Create Search function: Search for word within snippet messages

def search(word):
    """Return a list of snippets containing a given word"""
    logging.info("Searching snippets for {}".format(word))
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from snippets where hidden=False \
                and message like '%{}%'".format(word))
                       # select * from snippets where hidden=False and message like %insert%
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    logging.debug("Search complete")


def main():
    # import pdb; pdb.set_trace()
    """Main function"""             
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")


    # Subparser for the get command 
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")

    # Subparser for the catalog command
    catalog_parser = subparsers.add_parser("catalog", help = "List keywords fron snippet")

    # Subparser for the search command 
    import pdb; pdb.set_trace()
    search_parser = subparsers.add_parser("search", help = "Query snippets based on word")
    search_parser.add_argument("word", help = "word in snippet")

    arguments = parser.parse_args()

    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments) 
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        catalog()
        print("Retrieved keywords")
    # elif command == "search":
    #     string = search(**arguments)
    #     print
    #     print("Search complete")
    elif command == "search":
        word = search(**arguments)
        print()
        print("Search complete")
        print("Found {} in these messages".format(word))

if __name__ == "__main__":
   main()


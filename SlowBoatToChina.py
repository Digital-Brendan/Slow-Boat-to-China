import sqlite3
import os
import time
from columnar import columnar

clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

connection = sqlite3.connect("restaurant.db")
cursor = connection.cursor()

# Creates "Customers" table in database
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY
                       UNIQUE,
    Forename   TEXT    NOT NULL,
    Surname    TEXT    NOT NULL,
    Telephone  TEXT    UNIQUE
                       NOT NULL
)""")

# Creates "Orders" table in database
cursor.execute("""
CREATE TABLE IF NOT EXISTS Orders (
    OrderID    INTEGER NOT NULL,
    CustomerID INTEGER REFERENCES Customers (CustomerID) 
                       NOT NULL,
    ItemID     INTEGER REFERENCES Menu (ItemID) 
                       NOT NULL,
    Address    TEXT    NOT NULL,
    Postcode   TEXT    NOT NULL,
    Distance   INTEGER NOT NULL,
    MealSize   INTEGER NOT NULL,
    TotalPrice DOUBLE  NOT NULL
)""")

# Creates "Menu" table in database
cursor.execute("""
CREATE TABLE IF NOT EXISTS Menu (
    ItemID   INTEGER PRIMARY KEY
                     UNIQUE,
    ItemName TEXT    UNIQUE
                     NOT NULL,
    Price    DOUBLE  NOT NULL
)""")

cursor.execute("""
INSERT OR IGNORE INTO Menu ("ItemID", "ItemName", "Price") VALUES
(1,	"Crispy wonton", 4.5),
(2,	"Hot and sour soup", 2.9),
(3,	"Chicken with sweetcorn soup", 2.9),
(4,	"Sizzling beef with black bean sauce", 5.5),
(5, "Sizzling king prawns", 6.4),
(6,	"Sizzling chicken with ginger", 5.5),
(7,	"Beef with chilli sauce", 5.5),
(8,	"Chicken with curry sauce", 5.7),
(9,	"Chicken with cashew nuts", 5.7),
(10, "Pork with sweet and sour sauce", 5.8),
(11	, "Egg fried rice", 2.7);
""")

connection.commit()
connection.close()


# Create new order
def new_order():
    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    clear()
    print("\n" + "-"*50 + "SLOW BOAT TO CHINA" + "-"*50 + "\n")
    print("Please enter the follow order details below.\n")

    order_temp = []

    # ORDERID
    cursor.execute("SELECT COALESCE(MAX(OrderID),0) from Orders")  # Finds most recent orderID. If empty (no orders), 0 is returned instead of NULL
    orderID = cursor.fetchone()[0] + 1
    order_temp.append(orderID)
    
    # CUSTOMERID
    cursor.execute("SELECT MAX(CustomerID) from Customers")
    customerID = cursor.fetchone()
    order_temp.append(customerID[0])
    # print(order_temp[0][0])   <-- HOW TO FIND CUSTOMERID

    # ADDRESS
    address = str(input("\nAddress: ")).title()
    order_temp.append(address)

    # POSTCODE
    postcode = str(input("\nPostcode: ")).upper()
    order_temp.append(postcode)

    # DISTANCE
    distance_answer = input("\n[1] Within 2 miles\n[2] Within 5 miles\n[3] Within 10 miles\n\nDelivery Distance: ")

    if distance_answer == "1":
        distance = 2
        delivery_price = 2.5
    elif distance_answer == "2":
        distance = 5
        delivery_price = 5.0
    elif distance_answer == "3":
        distance = 10
        delivery_price = 7.5
    else:
        print("ERROR! Unrecognised character entered.")
        time.sleep(5)
        exit()
    
    order_temp.append(distance)

    # MEAL SIZE
    meal_size = int(input("\nNumber of items (1 - 7): "))

    # ITEMID AND PRICE
    if 7 < meal_size < 1:
        print("ERROR! Exceeds maximum size.")
        time.sleep(5)
        exit()
    else:
        starter_answer = int(input("\n[1] Crispy wonton\n[2] Hot and sour soup\n[3] Chicken with sweetcorn soup\n\nStarter item: "))
        
        if starter_answer not in range(1, 4):
            print("ERROR! Unrecognised character entered.")
            time.sleep(5)
            exit()
        else:
            itemID = starter_answer

            cursor.execute("SELECT Price FROM Menu WHERE ItemID = ?", [itemID,])
            price = cursor.fetchone()

            meal_item = [orderID, customerID[0], itemID, address, postcode, distance, meal_size, price[0]]
            cursor.execute("INSERT INTO Orders (OrderID, CustomerID, ItemID, Address, Postcode, Distance, MealSize, TotalPrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", meal_item)

        # Gives customer the choice of their meal size minus two items (first must be starter and last egg fried rice)
        for i in range(meal_size-2):
            food_answer = int(input("""\n[1] Crispy wonton\n[2] Hot and sour soup\n[3] Chicken with sweetcorn soup\n[4] Sizzling beef with black bean sauce\n[5] Sizzling king prawns\n[6] Sizzling chicken with ginger\n[7] Beef with chilli sauce\n[8] Chicken with curry sauce\n[9] Chicken with cashew nuts\n[10] Pork with sweet and sour sauce\n\nFood item: """))
            
            if food_answer not in range(1, 11):
                print("ERROR! Unrecognised character entered.")
                time.sleep(5)
                exit()
            else:
                itemID = food_answer

                cursor.execute("SELECT Price FROM Menu WHERE ItemID = ?", [itemID,])
                price = cursor.fetchone()

                meal_item = [orderID, customerID[0], itemID, address, postcode, distance, meal_size, price[0]]
                cursor.execute("INSERT INTO Orders (OrderID, CustomerID, ItemID, Address, Postcode, Distance, MealSize, TotalPrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", meal_item)

    meal_rice = [orderID, customerID[0], 11, address, postcode, distance, meal_size, 2.7]
    cursor.execute("INSERT INTO Orders (OrderID, CustomerID, ItemID, Address, Postcode, Distance, MealSize, TotalPrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", meal_rice)

    # Price and invoice
    cursor.execute("SELECT TotalPrice FROM Orders WHERE OrderID = ?", [orderID,])
    SumTotal = 0
    for row in cursor.fetchall():
        SumTotal += row[0]
    
    OverallTotal = SumTotal + delivery_price

    headers = ["Food", "Price"]

    # Finds the food from a particular order and the prices
    cursor.execute("SELECT Menu.ItemName, Menu.Price FROM Menu, Orders WHERE Orders.OrderID = ? AND Orders.ItemID = Menu.ItemID", [orderID,])
    print("\n~~Order Invoice~~")
    print("\n" + columnar(list(map(list, cursor.fetchall())), headers))

    print(f"\nCost of food: £{format(SumTotal, '.2f')}")
    print(f"Cost with delivery: £{format(OverallTotal, '.2f')}\n")

    connection.commit()
    connection.close()


# Searches current orders
def search_order():
    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    # Column headers for "columnar" table
    headers = ["OrderID", "CustomerID", "ItemID", "Address", "Postcode", "Delivery Distance", "Meal Size", "Price"]

    clear()
    print("\n" + "-"*50 + "SLOW BOAT TO CHINA" + "-"*50 + "\n")

    search_by = int(input("[1] Postcode\n[2] Delivery distance\n[3] Size of meal\n[4] CustomerID\n[5] Customer surname\n\nSearch by: "))

    if search_by == 1:
        postcode_search = str(input("\nEnter a postcode to search for: ")).upper
        
        cursor.execute("SELECT * FROM Orders WHERE Postcode = ?", [postcode_search,])

        # Creates a columnar table out of the rows from the fetchall(). map() returns iterables which must be converted to lists, hence outer list()
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))

    elif search_by == 2:
        distance_search = int(input("\n[1] Within 2 miles\n[2] Within 5 miles\n[3] Within 10 miles\n\nEnter a delivery distance to search for: "))

        if 5 < distance_search < 1:
            print("\nERROR! Unrecognised character entered.")
            time.sleep(5)
            exit()
        else:
            if distance_search == 1:
                distance_search = 2
            elif distance_search == 2:
                distance_search = 5
            elif distance_search == 3:
                distance_search = 10

            cursor.execute("SELECT * FROM Orders WHERE Distance = ?", [distance_search,])
            print("\n" + columnar(list(map(list, cursor.fetchall())), headers))
    
    elif search_by == 3:
        size_search = int(input("\nEnter a size of meal to search for: "))

        if 7 < size_search < 1:
            print("ERROR! Exceeds maximum size.")
            time.sleep(5)
            exit()
        else:
            cursor.execute("SELECT * from Orders WHERE MealSize = ?", [size_search,])
            print("\n" + columnar(list(map(list, cursor.fetchall())), headers))
    
    elif search_by == 4:
        customerID_search = int(input("\nEnter a customerID to search for: "))

        cursor.execute("SELECT * from Orders WHERE CustomerID = ?", [customerID_search,])
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))

    elif search_by == 5:
        surname_search = str(input("\nEnter a customer's surname to search for: ")).title()

        # Find the customerID's with specific surname, and all the orders associated with those customerID's
        cursor.execute("SELECT Orders.* FROM Customers, Orders WHERE Customers.Surname = ? AND Orders.CustomerID = Customers.CustomerID", [surname_search,])

        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))
    
    else:
        print("ERROR! Unrecognised character entered.")
        time.sleep(5)
        exit()

    connection.commit()
    connection.close()


# Creates new customer
def new_customer():
    clear()
    print("\n" + "-"*50 + "SLOW BOAT TO CHINA" + "-"*50 + "\n")

    print("Please enter the following customer details below.\n")

    customer_temp = []

    forename = str(input("Forename: ").title())
    customer_temp.append(forename.strip())

    surname = str(input("Surname: ").title())
    customer_temp.append(surname.strip())

    telephone = str(input("Telephone number: "))
    customer_temp.append(telephone.strip())

    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    # Check if customer already exists
    cursor.execute("SELECT EXISTS(SELECT 1 FROM customers WHERE Forename = ? AND Surname = ? AND Telephone = ?)", (forename, surname, telephone))
    if cursor.fetchone() == (0,):
        cursor.execute("INSERT INTO Customers (Forename, Surname, Telephone) VALUES (?, ?, ?)", customer_temp)
    else:
        print("ERROR! Customer already exists.\nPlease wait...")
        time.sleep(5)
        new_customer()

    connection.commit()
    connection.close()

    if (input("\nCreate an order for this customer? [YES] or [NO]\n")).upper() == "YES":
        new_order()
    else:
        exit()


# Search current customers
def search_customer():
    connection = sqlite3.connect("restaurant.db")
    cursor = connection.cursor()

    # Column headers for "columnar" table
    headers = ["CustomerID", "Forename", "Surname", "Telephone"]

    clear()
    print("\n" + "-"*50 + "SLOW BOAT TO CHINA" + "-"*50 + "\n")

    search_by = int(input("[1] CustomerID\n[2] Forename\n[3] Surname\n[4] Telephone\n\nSearch by: "))

    if search_by == 1:
        customerID_search = int(input("\nEnter a customerID to search for: "))

        cursor.execute("SELECT * from Customers WHERE CustomerID = ?", [customerID_search,])
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))

    elif search_by == 2:
        forename_search = str(input("\nEnter a forename to search for: ")).title()

        cursor.execute("SELECT * FROM Customers WHERE Forename = ?", [forename_search,])
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))
    
    elif search_by == 3:
        surname_search = str(input("\nEnter a surname to search for: ")).title()

        cursor.execute("SELECT * FROM Customers WHERE Surname = ?", [surname_search,])
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))

    elif search_by == 4:
        telephone_search = str(input("\nEnter a telephone number to search for: ")).title()

        cursor.execute("SELECT * FROM Customers WHERE Telephone = ?", [telephone_search,])
        print("\n" + columnar(list(map(list, cursor.fetchall())), headers))
    
    else:
        print("ERROR! Unrecognised character entered.")
        time.sleep(5)
        exit()

    connection.commit()
    connection.close()


# Introduction
print("\n" + "-"*50 + "SLOW BOAT TO CHINA" + "-"*50 + "\n")

menu_response = input("Press 1 to create a new customer.\nPress 2 to search for a customer\nPress 3 to search for an order.\n\n")
if menu_response == "1":
    new_customer()
elif menu_response == "2":
    search_customer()
elif menu_response == "3":
    search_order()
else:
    print("ERROR! Unrecognised character entered.")
    time.sleep(5)
    exit()

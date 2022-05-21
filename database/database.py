import sqlite3
from model.Product import Product
import model.Product


class REIClothingDatabase:

    REI_CLOTHING_DATABASE_PATH = "database/rei_clothing.db"
    db = None

    def __init__(self, database_path):
        try:
            self.db = sqlite3.connect(database_path)
        except Exception as e:
            print(f"Failed to connect to database (path: {database_path}). Reason:")
            print(e)

    
    def insert_product(self, product):
        # Determine which columns
        insert_sql = "INSERT INTO PRODUCT(product_id"
        if product.name is not None:
            insert_sql += ", name"
        if product.type is not None:
            insert_sql += ", type"
        insert_sql += ") "

        # Append values
        insert_sql += f"VALUES({product.product_id}"
        if product.name is not None:
            insert_sql += f", \"{product.name}\""
        if product.type is not None:
            insert_sql += f", \"{product.type}\""
        insert_sql += ");"

        # Insert product
        try:
            self.db.execute(insert_sql)
            self.db.commit()
        except Exception as e:
            print(f"Failed to insert product (product_id: {product.product_id}). Reason:")
            print(e)


    def delete_product(self, product_id):
        delete_sql = f"DELETE FROM product WHERE product_id={product_id};"
        try:
            self.db.execute(delete_sql)
            self.db.commit()
        except Exception as e:
            print(f"Failed to delete product (product_id: {product_id}). Reason:")
            print(e)


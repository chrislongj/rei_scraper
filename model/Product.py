class Product:
    product_id = None
    name = None
    type = None

    def __init__(self, product_id, name=None, type=None):
        self.product_id = product_id
        self.name = name
        self.type = type

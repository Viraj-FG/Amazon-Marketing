# relay_bot.py - Handles user-approved product data

approved_products = []  # Simulates a storage for approved product data

def approve_product(product):
    """Add a user-approved product to the storage."""
    if product not in approved_products:
        approved_products.append(product)
        return f"Product '{product}' approved and added to the workflow."
    else:
        return f"Product '{product}' is already approved."

def list_approved_products():
    """List all approved products."""
    return approved_products

if __name__ == "__main__":
    print(approve_product("Cool Gadget 1"))
    print(approve_product("Cool Gadget 2"))
    print(approve_product("Cool Gadget 1"))  # Duplicate test
    print("Approved Products:", list_approved_products())
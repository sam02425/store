from ..models.database import Inventory, Product
from ..utils.kafka_utils import KafkaConsumer
from ..utils.db_utils import get_db_session

class InventoryManagementService:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer('checkout_verified', 'inventory_update')
        self.db_session = get_db_session()

    def update_inventory(self, product_id, quantity_change, aisle_id=None):
        inventory_item = self.db_session.query(Inventory).filter_by(product_id=product_id, aisle_id=aisle_id).first()
        if inventory_item:
            inventory_item.quantity += quantity_change
            if inventory_item.quantity < 0:
                inventory_item.quantity = 0
        else:
            new_item = Inventory(product_id=product_id, quantity=max(0, quantity_change), aisle_id=aisle_id)
            self.db_session.add(new_item)
        self.db_session.commit()

    def run(self):
        for message in self.kafka_consumer:
            if message.topic == 'checkout_verified':
                customer_id = message.value['customer_id']
                cart_items = self.db_session.query(CartItem).filter_by(customer_id=customer_id).all()
                for item in cart_items:
                    self.update_inventory(item.product_id, -item.quantity)
                # Clear the customer's cart after checkout
                self.db_session.query(CartItem).filter_by(customer_id=customer_id).delete()
                self.db_session.commit()
            elif message.topic == 'inventory_update':
                self.update_inventory(
                    message.value['product_id'],
                    message.value['quantity_change'],
                    message.value.get('aisle_id')
                )

if __name__ == "__main__":
    service = InventoryManagementService()
    service.run()
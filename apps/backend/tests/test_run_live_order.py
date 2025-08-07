from logzero import logger

from src.algomin.sessions.angelone_session import AngelOneSession
from src.algomin.config_loader import BrokerConfigLoader
from src.algomin.brokers.order_client_factory import OrderClientFactory
from src.algomin.utils.order_builder import OrderBuilder

def main():
		print("🚀 Starting Live Order Placement Test for AngelOne")

		# Step 1: Load credentials & order config
		config_loader = BrokerConfigLoader()
		credentials = config_loader.load_credentials()
		order_config = config_loader.load_order_config()

		# Step 2: Create AngelOne session
		session = AngelOneSession(credentials)

		client = OrderClientFactory.create("smart_connect", session)
		# Step 3: Create broker-agnostic order client
		print('+++ smart connect client ', client )
		# Step 4: Build and validate order
		builder = OrderBuilder(order_config)
		valid, reason = builder.validate()

		if not valid:
				logger.error(f"❌ Invalid order: {reason}")
				return

		order = builder.build()


		# Step 5: Place the order
		print("📤 Placing order:", order)
		result = client.place_order(order)

		# Step 6: Show result
		if result.get("status") == "success":
				print("✅ Order placed successfully! Order ID:", result["orderid"])
		elif result.get("reason"):
				print("⚠️", result["reason"])
		else:
				print("❌ Failed to place order:", result)

if __name__ == "__main__":
		main()
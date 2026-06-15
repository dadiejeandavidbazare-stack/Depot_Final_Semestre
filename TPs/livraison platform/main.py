# =========================================================
# LIVRAISON PLATFORM - MAIN SIMULATION CLEAN
# =========================================================

import threading
import time

from service.order_service import OrderService
from broker.mini_broker import MiniBroker
from producers.event_producer import EventProducer
from producers.partitioner import Partitioner
from contracts.order import Order

from consumers.consumer_a import ConsumerA
from consumers.consumer_b import ConsumerB

from dashboard.dashboard import Dashboard


# =========================================================
# INIT SYSTEM
# =========================================================

print("\n================ SYSTEM INIT ================\n")

broker = MiniBroker(num_partitions=3)

service = OrderService(broker)
producer = EventProducer(broker)
partitioner = Partitioner(3)


# =========================================================
# PARTIE E - PARTITIONING TEST
# =========================================================

print("\n================ PARTIE E ================\n")

cities = ["Fes", "Casablanca", "Rabat", "Marrakech", "Tanger"]

for city in cities:
    print(city, "→ partition", partitioner.get_partition(city))


# =========================================================
# PARTIE C - SERVICE TEST
# =========================================================

print("\n================ PARTIE C ================\n")

print(service.create_order({
    "customer_id": "CUST-101",
    "city": "Fes",
    "zone": "Saiss",
    "courier_id": "CRR-07",
    "amount": 250.0,
    "items_count": 2
}))

print(service.create_order({
    "customer_id": "CUST-102",
    "city": "Paris",
    "zone": "X",
    "courier_id": "CRR-09",
    "amount": -10,
    "items_count": 1
}))


# =========================================================
# PARTIE D - PRODUCER TEST
# =========================================================

print("\n================ PARTIE D ================\n")

order = Order(
    order_id="ORD-1",
    customer_id="C1",
    city="Fes",
    zone="Saiss",
    courier_id="CRR-1",
    amount=200,
    items_count=2,
    status="created"
)

offsets = producer.run_order_lifecycle(order)

print("\n[PRODUCER OFFSETS]", offsets)


# =========================================================
# PARTIE F - CONSUMERS
# =========================================================

print("\n================ PARTIE F ================\n")

consumer_a = ConsumerA(broker, partitions=[0, 1])
consumer_b = ConsumerB(broker, partitions=[2])


# threads consumers
t1 = threading.Thread(target=consumer_a.consume)
t2 = threading.Thread(target=consumer_b.consume)

t1.start()
t2.start()


# =========================================================
# PARTIE I - DASHBOARD (REAL TIME)
# =========================================================

dashboard = Dashboard(consumer_a, consumer_b)
dashboard_thread = threading.Thread(target=dashboard.start)

dashboard_thread.start()


# =========================================================
# SIMULATION TIME
# =========================================================

print("\n[MAIN] System running...\n")

time.sleep(10)


# =========================================================
# STOP SYSTEM CLEANLY
# =========================================================

print("\n💥 STOPPING SYSTEM...\n")

consumer_a.running = False
consumer_b.running = False
dashboard.running = False

t1.join()
t2.join()
dashboard_thread.join()


# =========================================================
# FINAL REPORT
# =========================================================

print("\n========= FINAL REPORT =========\n")

print("[Consumer A]", consumer_a.report())
print("[Consumer B]", consumer_b.report())

print("\n[SYSTEM STOPPED CLEANLY]")
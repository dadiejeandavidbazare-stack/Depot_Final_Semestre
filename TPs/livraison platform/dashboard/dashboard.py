import time
import os


class Dashboard:

    def __init__(self, consumer_a, consumer_b):
        self.consumer_a = consumer_a
        self.consumer_b = consumer_b

        self.running = True

    # -------------------------
    # CLEAR CONSOLE
    # -------------------------
    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    # -------------------------
    # CALCUL KPI
    # -------------------------
    def compute_metrics(self):

        cities = self.consumer_a.city_stats
        statuses = self.consumer_a.status_stats

        success = sum(self.consumer_b.courier_success.values())
        failed = sum(self.consumer_b.courier_failed.values())

        created = statuses.get("created", 0)
        delivered = statuses.get("delivered", 0)
        cancelled = statuses.get("cancelled", 0)

        total = created

        success_rate = (delivered / total * 100) if total > 0 else 0

        return {
            "created": created,
            "delivered": delivered,
            "failed": failed,
            "cancelled": cancelled,
            "success_rate": success_rate,
            "cities": dict(cities),
            "couriers_success": dict(self.consumer_b.courier_success),
            "couriers_failed": dict(self.consumer_b.courier_failed)
        }

    # -------------------------
    # DISPLAY LOOP
    # -------------------------
    def start(self):

        while self.running:

            self.clear()

            data = self.compute_metrics()

            print("\n================ DASHBOARD ================\n")

            print(f"📦 Created     : {data['created']}")
            print(f"✅ Delivered   : {data['delivered']}")
            print(f"❌ Failed      : {data['failed']}")
            print(f"🚫 Cancelled   : {data['cancelled']}")
            print(f"📈 Success rate: {data['success_rate']:.2f}%")

            print("\n🏙️ BY CITY:")
            for city, count in data["cities"].items():
                print(f" - {city}: {count}")

            print("\n🚚 BY COURIER (SUCCESS):")
            for c, v in data["couriers_success"].items():
                print(f" - {c}: {v}")

            print("\n🚚 BY COURIER (FAILED):")
            for c, v in data["couriers_failed"].items():
                print(f" - {c}: {v}")

            print("\n==========================================\n")

            time.sleep(3)
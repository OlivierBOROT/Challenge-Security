import random
from datetime import datetime, timedelta
from src.data.mariadb_client import MariaDBClient
from sqlalchemy import text

def generate_test_data(n=50):
    db = MariaDBClient()
    db.init_db()
    protocols = ['TCP', 'UDP']
    actions = ['Permit', 'Deny']
    ips = [f"192.168.1.{i}" for i in range(1, 11)] + ["10.0.0.1", "172.16.0.5"]
    
    logs = []
    start_date = datetime(2025, 11, 1) # Début de la période requise

    for i in range(n):
        logs.append({
            "log_datetime": start_date + timedelta(minutes=i*10),
            "ip_source": random.choice(ips),
            "ip_dest": "159.84.1.1", # IP simulée de l'université
            "protocol": random.choice(protocols),
            "port_dest": random.choice([22, 80, 443, 3306, 514]),
            "action": random.choice(actions),
            "rule_id": random.randint(1, 20) if i % 5 != 0 else 999,
            "iface_in": "eth0",
            "iface_out": "eth1"
        })

    query = text("""
        INSERT INTO firewall_logs (log_datetime, ip_source, ip_dest, protocol, port_dest, action, rule_id, iface_in, iface_out)
        VALUES (:log_datetime, :ip_source, :ip_dest, :protocol, :port_dest, :action, :rule_id, :iface_in, :iface_out)
    """)

    with db.get_connection() as conn:
        for log in logs:
            conn.execute(query, log)
        conn.commit()
    print(f"✅ {n} lignes de test insérées.")

if __name__ == "__main__":
    generate_test_data()
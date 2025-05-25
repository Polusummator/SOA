from clickhouse_driver import Client
from typing import List, Dict
from datetime import datetime


class StatsDB:
    def __init__(self, host: str = "stats-service-db", database: str = "default"):
        self.client = Client(user='user', password='password', host=host, database=database)
        self._init_tables()

    def _init_tables(self):
        self.client.execute("""
        CREATE TABLE IF NOT EXISTS post_events (
            event_time DateTime,
            post_id UInt64,
            user_id UInt64,
            event_type Enum8('view' = 1, 'like' = 2, 'comment' = 3)
        ) ENGINE = MergeTree()
        ORDER BY (post_id, event_time)
        """)

    def insert_event(self, event_time: datetime, post_id: int, user_id: int, event_type: str):
        self.client.execute(
            "INSERT INTO post_events (event_time, post_id, user_id, event_type) VALUES",
            [(event_time, post_id, user_id, event_type)]
        )

    def get_post_stats(self, post_id: int) -> Dict[str, int]:
        result = self.client.execute("""
            SELECT
                sum(event_type = 'view') AS views,
                sum(event_type = 'like') AS likes,
                sum(event_type = 'comment') AS comments
            FROM post_events
            WHERE post_id = %(post_id)s
        """, {'post_id': post_id})

        views, likes, comments = result[0]
        return {"views": views, "likes": likes, "comments": comments}

    def get_post_dynamics(self, post_id: int) -> List[Dict]:
        result = self.client.execute("""
            SELECT
                toDate(event_time) as ts,
                sum(event_type = 'view') AS views,
                sum(event_type = 'like') AS likes,
                sum(event_type = 'comment') AS comments
            FROM post_events
            WHERE post_id = %(post_id)s
            GROUP BY ts
            ORDER BY ts
        """, {'post_id': post_id})

        return [
            {"date": ts.isoformat(), "views": views, "likes": likes, "comments": comments}
            for ts, views, likes, comments in result
        ]

    def get_post_timeline(self, post_id: int, metric: str) -> List[Dict]:
        if metric not in ["view", "like", "comment"]:
            raise ValueError("Invalid metric")

        result = self.client.execute(f"""
            SELECT
                toDate(event_time) AS ts,
                count() AS count
            FROM post_events
            WHERE post_id = %(post_id)s AND event_type = %(metric)s
            GROUP BY ts
            ORDER BY ts
        """, {'post_id': post_id, 'metric': metric})

        return [{"date": ts.isoformat(), "count": count} for ts, count in result]

    def get_top_posts(self, metric: str, limit: int = 10) -> List[Dict]:
        if metric not in ["post_viewed", "post_liked", "post_commented"]:
            raise ValueError("Invalid metric")

        metric_map = {
            "post_viewed": "view",
            "post_liked": "like",
            "post_commented": "comment"
        }

        event = metric_map[metric]

        result = self.client.execute("""
            SELECT post_id, count() as cnt
            FROM post_events
            WHERE event_type = %(event)s
            GROUP BY post_id
            ORDER BY cnt DESC
            LIMIT %(limit)s
        """, {'event': event, 'limit': limit})

        return [{"post_id": pid, "count": cnt} for pid, cnt in result]

    def get_top_users(self, metric: str, limit: int = 10) -> List[Dict]:
        if metric not in ["post_viewed", "post_liked", "post_commented"]:
            raise ValueError("Invalid metric")

        metric_map = {
            "post_viewed": "view",
            "post_liked": "like",
            "post_commented": "comment"
        }

        event = metric_map[metric]

        result = self.client.execute("""
            SELECT user_id, count() as cnt
            FROM post_events
            WHERE event_type = %(event)s
            GROUP BY user_id
            ORDER BY cnt DESC
            LIMIT %(limit)s
        """, {'event': event, 'limit': limit})

        return [{"user_id": uid, "count": cnt} for uid, cnt in result]

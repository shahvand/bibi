#!/bin/bash
# اسکریپت نمایش لاگ‌های کانتینرها

# نمایش لاگ‌های همه کانتینرها
docker compose logs -f

# برای نمایش لاگ یک کانتینر خاص، می‌توانید از دستورات زیر استفاده کنید:
# docker compose logs -f web
# docker compose logs -f db
# docker compose logs -f nginx 
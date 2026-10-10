

import sqlite3

# اتصال به دیتابیس
conn = sqlite3.connect('todo.db')
c = conn.cursor()

# برای نگهداری کارها
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    details TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("✅ دیتابیس و جدول tasks با موفقیت ساخته شد.")

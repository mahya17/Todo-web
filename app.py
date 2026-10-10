

from flask import Flask, render_template, jsonify, request, g
import sqlite3
import os

# مسیر فایل دیتابیس
DATABASE = os.path.join(os.path.dirname(__file__), "todo.db")

app = Flask(__name__)

# تابع کمکی برای اتصال به دیتابیس
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# قطع تصال بعد هر درخواست
@app.teardown_appcontext
def close_conn(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# یه برای اجرای کوئرهایی که خروجی دارن
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# برای اجرای کوئرهایی هایی که فقط تغییر میکنه
def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id

# صفحه اصلی برنامه
@app.route("/")
def index():
    return render_template("index.html")

# گرفتن لیست تمام کارها
@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    rows = query_db("SELECT id, title, details, done, created_at FROM tasks ORDER BY created_at DESC")
    tasks = [dict(row) for row in rows]
    return jsonify({"ok": True, "tasks": tasks})

# اضافه کردن کارای جدید
@app.route("/api/tasks", methods=["POST"])
def api_add_task():
    data = request.json or {}
    title = data.get("title", "").strip()
    details = data.get("details", "").strip()
    if not title:
        return jsonify({"ok": False, "error": "عنوان الزامی است."}), 400
    task_id = execute_db("INSERT INTO tasks (title, details) VALUES (?, ?)", (title, details))
    row = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    return jsonify({"ok": True, "task": dict(row)}), 201

# تغییر وضعیت
@app.route("/api/tasks/<int:task_id>/toggle", methods=["POST"])
def api_toggle_task(task_id):
    row = query_db("SELECT done FROM tasks WHERE id = ?", (task_id,), one=True)
    if not row:
        return jsonify({"ok": False, "error": "کار پیدا نشد."}), 404
    new_done = 0 if row["done"] else 1
    execute_db("UPDATE tasks SET done = ? WHERE id = ?", (new_done, task_id))
    return jsonify({"ok": True, "done": bool(new_done)})

# ویرایش عنوان کار یا توضیحات کار
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_edit_task(task_id):
    data = request.json or {}
    title = data.get("title", "").strip()
    details = data.get("details", "").strip()
    if not title:
        return jsonify({"ok": False, "error": "عنوان الزامی است."}), 400
    execute_db("UPDATE tasks SET title = ?, details = ? WHERE id = ?", (title, details, task_id))
    row = query_db("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    return jsonify({"ok": True, "task": dict(row)})

# حذف کار
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    execute_db("DELETE FROM tasks WHERE id = ?", (task_id,))
    return jsonify({"ok": True})

# اجرای برنامه
if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        print("⚠️ دیتابیس وجود ندارد، ابتدا دستور زیر را اجرا کن:\npython db_init.py")
    app.run(host="0.0.0.0", port=5000, debug=True)

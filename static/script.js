

const tasksEl = document.getElementById("tasks");
const addBtn = document.getElementById("addBtn");
const titleInput = document.getElementById("title");
const detailsInput = document.getElementById("details");
const msgEl = document.getElementById("msg");

// برای نمایش پیام کوتاه بالای صفحه
function showMsg(text, timeout = 2000) {
  msgEl.textContent = text;
  setTimeout(() => (msgEl.textContent = ""), timeout);
}

// گرفتن و نمایش کارها از سرور
function fetchTasks() {
  fetch("/api/tasks")
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) renderTasks(data.tasks);
    });
}

// نمایش همه‌ی کارها تو صفحه
function renderTasks(tasks) {
  tasksEl.innerHTML = "";
  for (const t of tasks) {
    const li = document.createElement("li");
    li.className = "task" + (t.done ? " done" : "");
    li.dataset.id = t.id;

    const check = document.createElement("button");
    check.textContent = t.done ? "✓" : "◻";
    check.addEventListener("click", () => toggleTask(t.id));

    const title = document.createElement("div");
    title.className = "title";
    title.textContent = t.title;
    title.title = t.details || "";
    title.addEventListener("dblclick", () => editTaskPrompt(t));

    const del = document.createElement("button");
    del.textContent = "🗑";
    del.addEventListener("click", () => deleteTask(t.id));

    li.appendChild(check);
    li.appendChild(title);
    li.appendChild(del);

    tasksEl.appendChild(li);
  }
}

// اضافه کردن کار جدید
function addTask() {
  const title = titleInput.value.trim();
  const details = detailsInput.value.trim();
  if (!title) {
    showMsg("عنوان رو یادت رفت");
    return;
  }
  fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, details }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) {
        titleInput.value = "";
        detailsInput.value = "";
        fetchTasks();
      } else showMsg(data.error || "خطا در افزودن کار");
    });
}

// تغییر وضعیت انجام‌شده
function toggleTask(id) {
  fetch(`/api/tasks/${id}/toggle`, { method: "POST" })
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) fetchTasks();
      else showMsg("خطا در تغییر وضعیت");
    });
}

// حذف کار
function deleteTask(id) {
  if (!confirm("آخرین فرصت برای پشیمون شدن،واقعاً می‌خوای پاکش کنی؟")) return;
  fetch(`/api/tasks/${id}`, { method: "DELETE" })
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) fetchTasks();
      else showMsg("خطا در حذف کار");
    });
}

// ویرایش کار
function editTaskPrompt(task) {
  const newTitle = prompt("عنوان جدید:", task.title);
  if (newTitle === null) return;
  const newDetails = prompt("توضیحات جدید:", task.details || "");
  fetch(`/api/tasks/${task.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: newTitle.trim(), details: newDetails.trim() }),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data.ok) fetchTasks();
      else showMsg("خطا در ویرایش");
    });
}

// ایونت ها
addBtn.addEventListener("click", addTask);
titleInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") addTask();
});

// شروع اولیه
fetchTasks();

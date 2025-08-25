document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("container");
  const list = document.getElementById("list");
  let page = 1, loading = false, hasMore = true;

  async function loadPage() {
    if (!hasMore || loading) return;
    loading = true;
    const res = await fetch(`/api/items?page=${page}`);
    const data = await res.json();
    data.items.forEach(it => {
      const div = document.createElement("div");
      div.className = "item";
      const a = document.createElement("a");
      a.href = it.href;
      a.textContent = `Item ${it.id}`;
      div.appendChild(a);
      list.appendChild(div);
    });
    hasMore = data.has_more;
    page += 1;
    loading = false;
  }

  container.addEventListener("scroll", () => {
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 10) {
      loadPage();
    }
  });

  await loadPage(); // initial
});
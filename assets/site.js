(() => {
  const search = document.querySelector('#post-search');
  const sort = document.querySelector('#post-sort');
  const list = document.querySelector('#post-list');
  if (search && sort && list) {
    const rows = [...list.querySelectorAll('.post-row')];
    const update = () => {
      const query = search.value.trim().toLocaleLowerCase();
      const ordered = [...rows].sort((a, b) => {
        const ad = a.dataset.date || '', bd = b.dataset.date || '';
        if (!ad || !bd) return ad ? -1 : bd ? 1 : 0;
        return sort.value === 'oldest' ? ad.localeCompare(bd) : bd.localeCompare(ad);
      });
      let visible = 0;
      ordered.forEach(row => {
        row.hidden = !row.textContent.toLocaleLowerCase().includes(query);
        if (!row.hidden) visible++;
        list.append(row);
      });
      document.querySelector('#post-count').textContent = `${visible} 篇文章`;
      document.querySelector('#empty-state').hidden = visible !== 0;
    };
    search.addEventListener('input', update);
    sort.addEventListener('change', update);
    update();
  }
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  document.querySelectorAll('[data-copy-email]').forEach(button => button.addEventListener('click', async () => {
    const status = document.querySelector('[data-email-status]');
    try { await navigator.clipboard.writeText(button.dataset.copyEmail); if (status) status.textContent = '邮箱地址已复制'; }
    catch { if (status) status.textContent = button.dataset.copyEmail; }
  }));
  const share = document.querySelector('[data-copy-link]');
  if (share) share.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href); share.textContent = '链接已复制'; }
    catch { share.textContent = '请复制地址栏链接'; }
  });
})();

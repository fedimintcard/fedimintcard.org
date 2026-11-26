(() => {
  function enhance() {
    const groups = [];
    const byPane = new Map();
    const byTab = new Map();
    const isAppleMobile = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
      (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

    function fragment(hash) {
      try {
        return document.getElementById(decodeURIComponent(hash.slice(1)));
      } catch {
        return null;
      }
    }

    for (const picker of document.querySelectorAll('[data-picker]')) {
      const links = [...picker.querySelectorAll('a[href^="#"]')].filter(link => link.closest('[data-picker]') === picker);
      const items = links.map(tab => ({tab, pane: fragment(tab.hash)}));
      if (!items.length || items.some(({tab, pane}) => !tab.id || !pane?.hasAttribute('data-pane'))) continue;
      const preferred = items.find(({pane}) => pane.id === 'pos' || (isAppleMobile && pane.id.endsWith('-ios')));
      const group = {picker, items, initial: preferred || items[0], selected: null};
      groups.push(group);
      picker.setAttribute('role', 'tablist');
      if (!picker.hasAttribute('aria-label') && !picker.hasAttribute('aria-labelledby')) {
        picker.setAttribute('aria-label', picker.dataset.picker === 'product' ? 'Product' : 'Platform');
      }
      for (const item of items) {
        item.group = group;
        byTab.set(item.tab, item);
        byPane.set(item.pane, item);
        item.tab.setAttribute('role', 'tab');
        item.tab.setAttribute('aria-controls', item.pane.id);
        item.pane.setAttribute('role', 'tabpanel');
        item.pane.setAttribute('aria-labelledby', item.tab.id);
        item.pane.tabIndex = 0;
      }
    }
    if (!groups.length) return;

    function select(item) {
      const group = item.group;
      if (group.selected === item) return;
      group.selected = item;
      for (const choice of group.items) {
        const selected = choice === item;
        choice.pane.hidden = !selected;
        choice.tab.tabIndex = selected ? 0 : -1;
        choice.tab.setAttribute('aria-selected', String(selected));
      }
    }

    function reveal(target) {
      // Selecting a nested platform also selects its product. Other products keep their platform.
      let pane = byTab.get(target)?.pane || target.closest('[data-pane]');
      while (pane) {
        const item = byPane.get(pane);
        if (item) select(item);
        pane = pane.parentElement?.closest('[data-pane]');
      }
      for (let node = target; node; node = node.parentElement) {
        if (node.tagName === 'DETAILS') node.open = true;
      }
    }

    function remember(method, url) {
      const downloadsTabs = groups.map(group => group.selected.pane.id);
      history[method]({...history.state, downloadsTabs}, '', url);
    }

    function restore(event) {
      const focused = document.activeElement;
      const saved = history.state?.downloadsTabs;
      for (const [index, group] of groups.entries()) {
        select(group.items.find(({pane}) => pane.id === saved?.[index]) || group.selected || group.initial);
      }
      const target = fragment(location.hash);
      if (target) reveal(target);
      // Back/Forward can hide the panel containing keyboard focus or deselect the focused tab.
      let focusTab = byTab.get(focused)?.group.selected.tab || focused;
      if (event && byPane.has(target) && focused === target) focusTab = byPane.get(target).tab;
      let hidden = focusTab?.closest('[data-pane][hidden]');
      while (hidden && byPane.has(hidden)) {
        focusTab = byPane.get(hidden).group.selected.tab;
        hidden = focusTab.closest('[data-pane][hidden]');
      }
      if (focusTab && focusTab !== focused) focusTab.focus({preventScroll: true});
      remember('replaceState', location.href);
      return target;
    }

    function navigate(target, hash) {
      reveal(target);
      remember(location.hash === hash ? 'replaceState' : 'pushState', hash);
    }

    document.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
      const link = event.target.closest('a[href]');
      if (!(link instanceof HTMLAnchorElement) || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
      const url = new URL(link.href);
      if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search || !url.hash) return;
      const target = fragment(url.hash);
      if (!target || !(byTab.has(link) || byTab.has(target) || target.closest('[data-pane]'))) return;
      event.preventDefault();
      navigate(target, url.hash);
      if (byTab.has(link)) {
        link.focus({preventScroll: true});
      } else {
        target.scrollIntoView();
        if (!target.hasAttribute('tabindex') && target.tabIndex < 0) target.tabIndex = -1;
        target.focus({preventScroll: true});
      }
    });

    document.addEventListener('keydown', event => {
      const item = byTab.get(event.target);
      if (!item || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      const {items, picker} = item.group;
      const index = items.indexOf(item);
      const vertical = picker.getAttribute('aria-orientation') === 'vertical';
      let next;
      switch (event.key) {
        case vertical ? 'ArrowDown' : 'ArrowRight': next = items[(index + 1) % items.length]; break;
        case vertical ? 'ArrowUp' : 'ArrowLeft': next = items[(index + items.length - 1) % items.length]; break;
        case 'Home': next = items[0]; break;
        case 'End': next = items[items.length - 1]; break;
        case ' ': next = item; break;
        default: return;
      }
      event.preventDefault();
      navigate(next.pane, next.tab.hash);
      next.tab.focus({preventScroll: true});
    });

    const initialTarget = restore();
    if (initialTarget && !byPane.has(initialTarget) && initialTarget.closest('[data-pane]')) {
      initialTarget.scrollIntoView();
    }
    window.addEventListener('popstate', restore);
    window.addEventListener('hashchange', restore);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhance, {once: true});
  } else {
    enhance();
  }
})();

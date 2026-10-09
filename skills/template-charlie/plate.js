/* template-charlie: plate.js
   d3 helpers for the notebook look. Load after d3 and before the page script
   (dashboard-export: --js plate.js --js app.js). Everything hangs off window.PLATE. */
window.PLATE = (() => {
  const css = (n) => getComputedStyle(document.getElementById('dash-root')).getPropertyValue(n).trim();

  /* Range-frame axis: the line spans only the first to last tick, so the axis itself
     reports the data range. orient: 'bottom' | 'left'. */
  function rangeAxis(g, scale, orient, { ticks = 6, format = (d) => d, tickValues, size = 5, pad = 8 } = {}) {
    const vals = tickValues || scale.ticks(ticks);
    const [a, b] = [scale(vals[0]), scale(vals[vals.length - 1])];
    const bottom = orient === 'bottom';
    g.append('path').attr('class', 'axis').attr('d', bottom ? `M${a},0H${b}` : `M0,${a}V${b}`);
    const t = g.selectAll('g.tk').data(vals).join('g').attr('class', 'tk')
      .attr('transform', (d) => (bottom ? `translate(${scale(d)},0)` : `translate(0,${scale(d)})`));
    t.append('line').attr('class', 'axis').attr(bottom ? 'y2' : 'x2', bottom ? size : -size);
    t.append('text').text((d) => format(d))
      .attr(bottom ? 'y' : 'x', bottom ? size + pad + 4 : -(size + pad))
      .attr('text-anchor', bottom ? 'middle' : 'end').attr('dy', bottom ? 0 : '0.32em');
    return g;
  }

  /* Direct label: a coloured dot at the line end, the words in ink. */
  function directLabel(g, x, y, text, color, dx = 10) {
    g.append('circle').attr('cx', x).attr('cy', y).attr('r', 3.5).attr('fill', color);
    g.append('text').attr('class', 'it').attr('x', x + dx).attr('y', y).attr('dy', '0.32em').text(text);
  }

  /* Numbered badge tied to a margin note. Keep (dx, dy) off the data. */
  function badge(g, x, y, n, dx = 0, dy = -26, ring = true) {
    const b = g.append('g').attr('class', 'badge');
    if (ring) b.append('circle').attr('class', 'ring').attr('cx', x).attr('cy', y).attr('r', 6);
    const bx = x + dx, by = y + dy, len = Math.hypot(dx, dy) || 1;
    b.append('line').attr('x1', x + (dx / len) * (ring ? 6 : 0)).attr('y1', y + (dy / len) * (ring ? 6 : 0))
      .attr('x2', bx - (dx / len) * 9).attr('y2', by - (dy / len) * 9);
    b.append('circle').attr('cx', bx).attr('cy', by).attr('r', 9);
    b.append('text').attr('x', bx).attr('y', by).attr('dy', '0.35em').attr('text-anchor', 'middle').text(n);
  }

  /* Tooltip bound to a card element. tip(el) returns show(ev, text) and hide(). */
  function tooltip(tipEl, host) {
    return {
      show(ev, text) {
        const [x, y] = d3.pointer(ev, host);
        tipEl.textContent = text;
        tipEl.style.opacity = 1;
        tipEl.style.left = Math.max(0, Math.min(x + 14, host.clientWidth - tipEl.offsetWidth)) + 'px';
        tipEl.style.top = (y + 14) + 'px';
      },
      hide() { tipEl.style.opacity = 0; }
    };
  }

  return { css, rangeAxis, directLabel, badge, tooltip };
})();

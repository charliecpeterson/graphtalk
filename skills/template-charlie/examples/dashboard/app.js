/* Example notebook dashboard. Every number in the margin notes is computed from the data,
   so editing a CSV rewrites the notes instead of leaving stale claims. */
const $ = (id) => document.getElementById(id);
const fmt = d3.format(',');
const C = PLATE.css;
const DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const state = { rt: 'member' };

function setNotes(id, lines) {
  const ol = $(id);
  ol.replaceChildren();
  lines.forEach((t) => { const li = document.createElement('li'); li.textContent = t; ol.append(li); });
}

/* Run stub: what this page was built from. Counts and span come from the loaded data. */
function stub(sets, daily) {
  const span = d3.extent(daily, (r) => r.date).map(d3.timeFormat('%Y-%m-%d')).join(' to ');
  const parts = sets.map(([name, rows]) => `<b>${name}</b> ${fmt(rows)} rows`);
  $('fp-stub').innerHTML = `run ${d3.timeFormat('%Y-%m-%d')(new Date())} &middot; ${parts.join(' &middot; ')} &middot; covers ${span}`;
}

function movingMean(rows, key, n = 7) {
  return rows.map((r, i) => {
    const w = rows.slice(Math.max(0, i - n + 1), i + 1);
    return { date: r.date, v: d3.mean(w, (q) => q[key]) };
  });
}

function linePlate(daily) {
  const box = $('fp-line'), tipEl = $('tip1');
  box.querySelectorAll('svg').forEach((n) => n.remove());
  const W = box.clientWidth || 760, H = Math.round(Math.min(330, W * 0.42)), m = { l: 50, r: 104, t: 18, b: 36 };
  const svg = d3.select(box).insert('svg', '.tip').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
    .attr('aria-label', 'Daily member and casual trips with 7-day means');
  const x = d3.scaleTime(d3.extent(daily, (r) => r.date), [m.l, W - m.r]);
  const y = d3.scaleLinear([0, d3.max(daily, (r) => Math.max(r.member, r.casual)) * 1.06], [H - m.b, m.t]);
  PLATE.rangeAxis(svg.append('g').attr('transform', `translate(0,${H - m.b + 6})`), x, 'bottom',
    { tickValues: d3.timeMonths(...x.domain()), format: d3.timeFormat('%b') });
  PLATE.rangeAxis(svg.append('g').attr('transform', `translate(${m.l - 6},0)`), y, 'left', { ticks: 4, format: fmt });
  const series = [['member', C('--teal'), 'Members'], ['casual', C('--amber'), 'Casual riders']];
  series.forEach(([key, color]) => {
    svg.append('path').datum(daily).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 1).attr('opacity', .35)
      .attr('d', d3.line().x((r) => x(r.date)).y((r) => y(r[key])));
    svg.append('path').datum(movingMean(daily, key)).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 2.4)
      .attr('stroke-linecap', 'round').attr('d', d3.line().x((r) => x(r.date)).y((r) => y(r.v)));
  });
  series.forEach(([key, color, label]) => {
    const last = movingMean(daily, key).at(-1);
    PLATE.directLabel(svg.append('g'), x(last.date), y(last.v), label, color);
  });
  const peakMember = daily.reduce((a, b) => (b.member > a.member ? b : a));
  const peakCasual = daily.reduce((a, b) => (b.casual > a.casual ? b : a));
  PLATE.badge(svg.append('g'), x(peakMember.date), y(peakMember.member), 1, -28, -10);
  PLATE.badge(svg.append('g'), x(peakCasual.date), y(peakCasual.casual), 2, 26, -4);
  const dm = d3.timeFormat('%b %-d');
  const base = d3.mean(daily.filter((r) => r.date < peakMember.date && r.date.getDay() === peakMember.date.getDay()).slice(-4), (r) => r.member);
  setNotes('notes1', [
    `Members peak on ${dm(peakMember.date)} at ${fmt(peakMember.member)} trips, ${(peakMember.member / base).toFixed(1)} times the same weekday in the month before.`,
    `Casual riders peak on ${dm(peakCasual.date)} at ${fmt(peakCasual.casual)} trips, ${(peakCasual.casual / d3.median(daily, (r) => r.casual)).toFixed(1)} times their median day.`,
    `Casual riders are ${Math.round(100 * d3.sum(daily, (r) => r.casual) / d3.sum(daily, (r) => r.trips))}% of trips and swing with the weekend and the weather. Members barely move.`
  ]);
  const cross = svg.append('line').attr('y1', m.t).attr('y2', H - m.b).attr('stroke', C('--ink')).attr('stroke-width', 1).style('opacity', 0);
  const tip = PLATE.tooltip(tipEl, box), bis = d3.bisector((r) => r.date).center;
  svg.append('rect').attr('x', m.l).attr('width', W - m.l - m.r).attr('y', 0).attr('height', H).style('fill', 'transparent')
    .on('mousemove', (ev) => {
      const r = daily[bis(daily, x.invert(d3.pointer(ev)[0]))];
      cross.attr('x1', x(r.date)).attr('x2', x(r.date)).style('opacity', 1);
      tip.show(ev, `${d3.timeFormat('%a %b %-d')(r.date)}  ${fmt(r.member)} members  ${fmt(r.casual)} casual  ${r.temp.toFixed(0)}C`);
    })
    .on('mouseleave', () => { cross.style('opacity', 0); tip.hide(); });
}

function dotPlate(heat) {
  const box = $('fp-dots'), tipEl = $('tip2');
  box.replaceChildren();
  const cells = heat.filter((r) => r.rt === state.rt), vmax = d3.max(heat, (r) => r.v);
  const W = box.clientWidth || 760, m = { l: 40, r: 6, t: 4, b: 30 }, cw = (W - m.l - m.r) / 24, rh = 34, H = m.t + 7 * rh + m.b;
  const svg = d3.select(box).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
    .attr('aria-label', `Average trips per hour, ${state.rt} riders`);
  svg.selectAll('line.rule').data(d3.range(7)).join('line').attr('class', 'rule')
    .attr('x1', m.l).attr('x2', W - m.r).attr('y1', (d) => m.t + d * rh + rh / 2).attr('y2', (d) => m.t + d * rh + rh / 2);
  const rmax = Math.min(cw, rh) / 2 - 1.5, color = state.rt === 'member' ? C('--teal') : C('--amber');
  const tip = PLATE.tooltip(tipEl, box.parentNode);
  svg.selectAll('circle').data(cells).join('circle').attr('cx', (r) => m.l + r.hour * cw + cw / 2).attr('cy', (r) => m.t + r.dow * rh + rh / 2)
    .attr('r', (r) => rmax * Math.sqrt(r.v / vmax)).attr('fill', color)
    .on('mousemove', (ev, r) => tip.show(ev, `${DOW[r.dow]} ${r.hour}:00  ${r.v.toFixed(1)} trips an hour`)).on('mouseleave', () => tip.hide());
  svg.selectAll('text.d').data(DOW).join('text').attr('class', 'd').attr('x', m.l - 10).attr('y', (d, i) => m.t + i * rh + rh / 2).attr('dy', '0.32em').attr('text-anchor', 'end').text((d) => d);
  svg.selectAll('text.h').data(d3.range(0, 24, 3)).join('text').attr('class', 'h').attr('x', (h) => m.l + h * cw + cw / 2).attr('y', H - 8).attr('text-anchor', 'middle').text((h) => h + ':00');
  const peak = cells.reduce((a, b) => (b.v > a.v ? b : a));
  const wk = d3.rollup(cells, (v) => d3.mean(v.filter((r) => r.dow < 5), (r) => r.v), (r) => r.hour);
  const wkPeak = [...wk].reduce((a, b) => (b[1] > a[1] ? b : a));
  PLATE.badge(svg.append('g'), m.l + peak.hour * cw + cw / 2, m.t + peak.dow * rh + rh / 2, 1, 0, -24);
  setNotes('notes2', [
    `${state.rt === 'member' ? 'Members' : 'Casual riders'} are busiest on ${DOW[peak.dow]} in the ${peak.hour}:00 hour, at ${peak.v.toFixed(0)} trips an hour.`,
    `Weekdays peak in the ${wkPeak[0]}:00 hour at ${wkPeak[1].toFixed(0)} trips an hour on average.`,
    `Largest circle on either rider type: ${vmax.toFixed(0)} trips an hour.`
  ]);
}

function dumbPlate(eb) {
  const box = $('fp-dumb'), tipEl = $('tip3');
  box.querySelectorAll('svg').forEach((n) => n.remove());
  const hoods = eb.filter((r) => r.neighborhood !== 'All trips').sort((a, b) => (a.h2 - b.h2));
  const all = eb.find((r) => r.neighborhood === 'All trips');
  const rows = hoods.concat([all]);
  const W = box.clientWidth || 760, rh = 38, m = { l: 104, r: 20, t: 8, b: 40 }, H = m.t + rows.length * rh + m.b;
  const svg = d3.select(box).insert('svg', '.tip').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
    .attr('aria-label', 'E-bike share by neighborhood, first and second half of the year');
  const x = d3.scaleLinear([10, 66], [m.l, W - m.r]);
  const yOf = (i) => m.t + i * rh + rh / 2;
  svg.append('defs').selectAll('marker').data([['hood', C('--teal')], ['city', C('--rose')]]).join('marker')
    .attr('id', (d) => 'ar-' + d[0]).attr('viewBox', '0 0 10 10').attr('refX', 9).attr('refY', 5).attr('markerWidth', 5.5).attr('markerHeight', 5.5).attr('orient', 'auto')
    .append('path').attr('d', 'M0,0L10,5L0,10z').attr('fill', (d) => d[1]);
  PLATE.rangeAxis(svg.append('g').attr('transform', `translate(0,${m.t + rows.length * rh + 2})`), x, 'bottom',
    { tickValues: d3.range(10, 61, 10), format: (d) => d + '%' });
  svg.selectAll('line.rule').data(rows).join('line').attr('class', 'rule').attr('x1', m.l).attr('x2', W - m.r).attr('y1', (d, i) => yOf(i)).attr('y2', (d, i) => yOf(i));
  svg.append('line').attr('class', 'axis').attr('x1', m.l - 90).attr('x2', W - m.r).attr('y1', yOf(rows.length - 1) - rh / 2).attr('y2', yOf(rows.length - 1) - rh / 2).attr('stroke-width', .8);
  const tip = PLATE.tooltip(tipEl, box);
  rows.forEach((r, i) => {
    const city = r === all, col = city ? C('--rose') : C('--teal'), y = yOf(i), g = svg.append('g');
    g.append('text').attr('class', city ? 'ink' : '').attr('x', m.l - 14).attr('y', y).attr('dy', '0.32em').attr('text-anchor', 'end')
      .style('font-weight', city ? 700 : 400).text(r.neighborhood);
    if (Number.isNaN(r.h1)) {
      g.append('circle').attr('cx', x(r.h2)).attr('cy', y).attr('r', 4.5).attr('fill', col);
    } else {
      g.append('line').attr('x1', x(r.h1)).attr('x2', x(r.h2) + (r.h2 > r.h1 ? -9 : 9)).attr('y1', y).attr('y2', y)
        .attr('stroke', col).attr('stroke-width', city ? 2.4 : 1.8).attr('marker-end', `url(#ar-${city ? 'city' : 'hood'})`);
      g.append('circle').attr('cx', x(r.h1)).attr('cy', y).attr('r', 4.5).attr('fill', C('--paper')).attr('stroke', col).attr('stroke-width', 1.5);
    }
    g.append('text').attr('class', 'mono').attr('x', x(r.h2) + (r.h2 >= (r.h1 || 0) ? 14 : -14)).attr('y', y).attr('dy', '0.32em')
      .attr('text-anchor', r.h2 >= (r.h1 || 0) ? 'start' : 'end').text(r.h2.toFixed(1) + '%');
    g.append('rect').attr('x', m.l).attr('y', y - rh / 2).attr('width', W - m.l - m.r).attr('height', rh).style('fill', 'transparent')
      .on('mousemove', (ev) => tip.show(ev, Number.isNaN(r.h1) ? `${r.neighborhood}  ${r.h2.toFixed(1)}% in Jul to Dec (opened Jul 1)` :
        `${r.neighborhood}  ${r.h1.toFixed(1)}% to ${r.h2.toFixed(1)}%  (${(r.h2 - r.h1 >= 0 ? '+' : '') + (r.h2 - r.h1).toFixed(1)} pts)`))
      .on('mouseleave', () => tip.hide());
  });
  const gains = hoods.filter((r) => !Number.isNaN(r.h1)).map((r) => r.h2 - r.h1), harbor = hoods.find((r) => Number.isNaN(r.h1));
  const d = all.h2 - all.h1;
  PLATE.badge(svg.append('g'), x(all.h2) + (d < 0 ? -70 : 70), yOf(rows.length - 1), 1, 0, 0, false);
  if (harbor) PLATE.badge(svg.append('g'), x(harbor.h2) + 70, yOf(hoods.indexOf(harbor)), 3, 0, 0, false);
  PLATE.badge(svg.append('g'), x(hoods.find((r) => !Number.isNaN(r.h1)).h2) + 70, yOf(hoods.findIndex((r) => !Number.isNaN(r.h1))), 2, 0, 0, false);
  setNotes('notes3', [
    `City-wide, e-bike share went from ${all.h1.toFixed(1)}% to ${all.h2.toFixed(1)}%, a ${d < 0 ? 'fall' : 'rise'} of ${Math.abs(d).toFixed(1)} points.`,
    `Each neighborhood that existed all year gained ${d3.min(gains).toFixed(1)} to ${d3.max(gains).toFixed(1)} points.`,
    harbor ? `Harbor Flats opened on July 1 at ${harbor.h2.toFixed(1)}%, well under the city rate. New riders there pull the total down: the mix changed, not the riders.`
      : 'No neighborhood opened part-way through the year in this data.'
  ]);
}

document.querySelectorAll('.tabs button').forEach((b) => b.addEventListener('click', () => {
  state.rt = b.dataset.rt;
  document.querySelectorAll('.tabs button').forEach((o) => o.setAttribute('aria-pressed', o === b));
  draw();
}));

function draw() {
  const [d, h, e] = ['daily', 'heat', 'ebike'].map((i) => dash.data(i));
  if ([d, h, e].some((q) => q.status !== 'ok')) return;
  const daily = d.data.map((r) => ({ date: new Date(r.date + 'T00:00'), trips: +r.trips, member: +r.member_trips, casual: +r.casual_trips, temp: +r.mean_temp_c }));
  const heat = h.data.map((r) => ({ rt: r.rider_type, dow: +r.dow, hour: +r.hour, v: +r.avg_trips }));
  const eb = e.data.map((r) => ({ neighborhood: r.neighborhood, h1: r.h1 === '' ? NaN : +r.h1, h2: +r.h2 }));
  [() => stub([['daily.csv', d.data.length], ['heat.csv', h.data.length], ['ebike.csv', e.data.length]], daily),
   () => linePlate(daily), () => dotPlate(heat), () => dumbPlate(eb)].forEach((f) => {
    try { f(); } catch (err) { console.error(err); }
  });
}

dash.onData(draw);

(function () {
	var parts = location.pathname.split('/eia_proxy/');
	if (parts.length < 2) return;

	var sink = parts[0] + '/eia_table';
	var stateSink = parts[0] + '/eia_state';
	var browser = '__OBB_BROWSER__';
	function hash16(s) {
		var h1 = 0x811c9dc5;
		var h2 = 0x9e3779b9;
		for (var i = 0; i < s.length; i++) {
			var c = s.charCodeAt(i);
			h1 ^= c;
			h1 = (h1 + ((h1 << 1) + (h1 << 4) + (h1 << 7) + (h1 << 8) + (h1 << 24))) >>> 0;
			h2 = (h2 ^ ((c << 1) >>> 0)) >>> 0;
			h2 = (h2 + 0x6d2b79f5) >>> 0;
		}
		function hex(n) {
			return ('00000000' + (n >>> 0).toString(16)).slice(-8);
		}
		return hex(h1) + hex(h2);
	}
	function sanitizeUser(v) {
		if (v === null || v === undefined) return '';
		var s = String(v);
		if (!s) return '';
		return s.indexOf('@') >= 0 ? hash16(s) : s;
	}
	var user='__OBB_USER__';
	user=sanitizeUser(user);

	try {
		var _uq = new URLSearchParams(location.search).get('obb_user');
		if (_uq) {
			user = sanitizeUser(_uq);
			if (user) sessionStorage.setItem('obb_user', user);
		} else {
			var _us = sessionStorage.getItem('obb_user');
			if (_us) user = sanitizeUser(_us);
		}
	} catch (e) {}

	var up = window.parent && window.parent !== window ? window.parent : null;

	function stripObbUser(query) {
		var p = new URLSearchParams(query || '');
		p.delete('obb_user');
		var s = p.toString();
		return s ? '?' + s : '';
	}

	function stripObbUserInHash(hash) {
		var raw = hash || '';
		if (!raw) return '';
		if (raw.charAt(0) === '#') raw = raw.slice(1);
		var i = raw.indexOf('?');
		if (i < 0) return '#' + raw;
		var head = raw.slice(0, i);
		var qs = raw.slice(i + 1);
		var p = new URLSearchParams(qs);
		p.delete('obb_user');
		var tail = p.toString();
		return '#' + head + (tail ? '?' + tail : '');
	}

	function view() {
		var p = location.pathname.split('/eia_proxy/')[1] || '';
		return p + stripObbUser(location.search) + stripObbUserInHash(location.hash);
	}

	function txt(el) {
		return ((el.innerText || el.textContent || '').replace(/\s+/g, ' ')).trim();
	}

	function cell(v) {
		if (v === null || v === undefined) return null;
		if (typeof v === 'number') return isFinite(v) ? v : null;
		if (typeof v === 'object') {
			if ('value' in v) return cell(v.value);
			if ('v' in v) return cell(v.v);
			if ('y' in v) return cell(v.y);
			return null;
		}
		var s = String(v)
			.replace(/<[^>]*>/g, ' ')
			.replace(/&nbsp;/g, ' ')
			.replace(/\s+/g, ' ')
			.trim();
		if (s === '' || s === '--' || s === '-' || s === '\u2013' || s === '\u2014') {
			return null;
		}
		var n = s.replace(/,/g, '');
		if (/^-?\d*\.?\d+$/.test(n)) return parseFloat(n);
		return s;
	}

	function records(head, body) {
		var names = [];
		var used = {};
		for (var i = 0; i < head.length; i++) {
			var h = String(head[i] || '').trim();
			if (!h) h = 'category';
			if (/^\d+$/.test(h)) h = h + ' ';
			if (used[h]) {
				used[h]++;
				h = h + ' (' + used[h] + ')';
			} else {
				used[h] = 1;
			}
			names.push(h);
		}
		var out = [];
		for (var r = 0; r < body.length; r++) {
			var row = {};
			for (var c = 0; c < names.length; c++) row[names[c]] = cell(body[r][c]);
			if (Object.keys(row).length) out.push(row);
		}
		return out;
	}

	var grids = [];

	function resolve(field, item) {
		if (!field) return undefined;
		var path = String(field).split('.');
		var v = item;
		for (var i = 0; i < path.length; i++) {
			if (v === null || v === undefined) return undefined;
			v = v[path[i]];
		}
		return v;
	}

	function extract(grid, item, col) {
		var o = grid.getOptions ? grid.getOptions() : null;
		if (o && typeof o.dataItemColumnValueExtractor === 'function') {
			try {
				return o.dataItemColumnValueExtractor(item, col);
			} catch (e) {}
		}
		return resolve(col.field, item);
	}

	function value(grid, item, col, r, c) {
		var raw = extract(grid, item, col);
		if (typeof raw === 'number' && isFinite(raw)) return raw;
		var fn = col.outputFormatter || col.dataFormatter || col.formatter;
		if (typeof fn === 'function') {
			try {
				var out = fn.call(grid, r, c, raw, col, item);
				if (out !== undefined && out !== null) return out;
			} catch (e) {}
		}
		return raw === undefined ? null : raw;
	}

	function node(g) {
		try {
			return g.getContainerNode ? g.getContainerNode() : null;
		} catch (e) {
			return null;
		}
	}

	function dead(g) {
		var n = node(g);
		return !!n && !n.querySelector('.slick-viewport');
	}

	function live(g) {
		var n = node(g);
		if (!n) return true;
		if (!n.ownerDocument || !n.ownerDocument.contains(n)) return false;
		if (!n.querySelector('.slick-viewport')) return false;
		return !!(n.offsetParent || n.getClientRects().length);
	}

	function fromSlick() {
		var best = null;
		var rows = 0;
		var keep = [];
		for (var i = 0; i < grids.length; i++) {
			var g = grids[i];
			if (dead(g)) continue;
			keep.push(g);
			if (!live(g)) continue;
			try {
				var n = g.getDataLength();
				if (n > rows) {
					rows = n;
					best = g;
				}
			} catch (e) {}
		}
		grids = keep;
		if (!best || !rows) return null;

		var all = best.getColumns() || [];
		if (!all.length) return null;

		var cols = [];
		var head = [];
		for (var c = 0; c < all.length; c++) {
			var col = all[c];
			if (col.output === false || col.display === false || col.id === 'spacer' || col.iconClass) {
				continue;
			}
			var h = col.name === undefined || col.name === null ? '' : String(col.name);
			cols.push(col);
			head.push(h.replace(/<[^>]*>/g, ' '));
		}
		if (!cols.length) return null;

		function period(i) {
			var id = cols[i].id;
			id = id === null || id === undefined ? '' : String(id);
			return /^\d{4}(Q[1-4]|\d{2}|\d{4})?$/.test(id) ? id : null;
		}

		var order = [];
		for (var oi = 0; oi < cols.length; oi++) order.push(oi);
		order.sort(function (a, b) {
			var pa = period(a);
			var pb = period(b);
			if (pa === null && pb === null) return a - b;
			if (pa === null) return -1;
			if (pb === null) return 1;
			return pa < pb ? -1 : pa > pb ? 1 : a - b;
		});

		var scols = [];
		var shead = [];
		for (var oj = 0; oj < order.length; oj++) {
			scols.push(cols[order[oj]]);
			shead.push(head[order[oj]]);
		}
		cols = scols;
		head = shead;

		var body = [];
		for (var r = 0; r < rows; r++) {
			var item = best.getDataItem(r);
			if (!item) continue;
			var row = [];
			for (var f = 0; f < cols.length; f++) row.push(value(best, item, cols[f], r, f));
			body.push(row);
		}
		return body.length ? records(head, body) : null;
	}

	function wrapGrid() {
		var S = window.Slick;
		if (!S || typeof S.Grid !== 'function' || S.Grid.__obb) return;
		var G = S.Grid;
		function W() {
			var g = Object.create(G.prototype || Object.prototype);
			var r = G.apply(g, arguments);
			var inst = r && typeof r === 'object' ? r : g;
			try {
				grids.push(inst);
				if (inst.onRendered && inst.onRendered.subscribe) inst.onRendered.subscribe(schedule);
				schedule();
			} catch (e) {}
			return inst;
		}
		W.prototype = G.prototype;
		W.__obb = 1;
		for (var k in G) {
			try {
				W[k] = G[k];
			} catch (e) {}
		}
		try {
			S.Grid = W;
		} catch (e) {}
	}

	setInterval(wrapGrid, 20);

	var apis = [];

	function keep(api) {
		if (!api || typeof api.forEachNodeAfterFilterAndSort !== 'function') return;
		for (var i = 0; i < apis.length; i++) if (apis[i] === api) return;
		apis.push(api);
		schedule();
	}

	function wrapAg() {
		var A = window.agGrid;
		if (!A || A.__obb) return;
		if (typeof A.createGrid === 'function') {
			var create = A.createGrid;
			A.createGrid = function () {
				var api = create.apply(this, arguments);
				try {
					keep(api);
				} catch (e) {}
				return api;
			};
		}
		if (typeof A.Grid === 'function') {
			var G = A.Grid;
			function W(el, opts) {
				var g = Object.create(G.prototype || Object.prototype);
				var r = G.apply(g, arguments);
				var inst = r && typeof r === 'object' ? r : g;
				try {
					keep(opts && opts.api);
					keep(inst && inst.gridOptions && inst.gridOptions.api);
				} catch (e) {}
				return inst;
			}
			W.prototype = G.prototype;
			for (var k in G) {
				try {
					W[k] = G[k];
				} catch (e) {}
			}
			try {
				A.Grid = W;
			} catch (e) {}
		}
		try {
			A.__obb = 1;
		} catch (e) {}
	}

	setInterval(wrapAg, 20);

	function unwrap(v) {
		if (!v) return null;
		var seen = [
			v,
			v.api,
			v.gridApi,
			v.gridOptions && v.gridOptions.api,
			v.gridOptions && v.gridOptions.gridApi,
		];
		for (var i = 0; i < seen.length; i++) {
			var a = seen[i];
			if (a && typeof a.forEachNodeAfterFilterAndSort === 'function') return a;
		}
		return null;
	}

	function domApi() {
		var nodes = document.querySelectorAll('ag-grid-angular,.ag-root-wrapper,.ag-root,.ag-body');
		for (var i = 0; i < nodes.length; i++) {
			var el = nodes[i];
			for (var d = 0; d < 4 && el && el.getAttribute; d++, el = el.parentNode) {
				var a = unwrap(el.__ag_grid_instance);
				if (a) return a;
				for (var k in el) {
					try {
						var got = unwrap(el[k]);
						if (got) return got;
					} catch (e) {}
				}
			}
		}
		return null;
	}

	function gridApi() {
		var best = null;
		var rows = -1;
		for (var i = 0; i < apis.length; i++) {
			var a = apis[i];
			try {
				if (a.isDestroyed && a.isDestroyed()) continue;
				var n = 0;
				a.forEachNodeAfterFilterAndSort(function () {
					n++;
				});
				if (n > rows) {
					rows = n;
					best = a;
				}
			} catch (e) {}
		}
		return best || domApi();
	}

	function fromGrid() {
		var api = gridApi();
		if (!api || !api.getAllDisplayedColumns) return null;
		var cols = api.getAllDisplayedColumns() || [];
		if (!cols.length) return null;

		var head = [];
		var fields = [];
		var defs = [];
		for (var i = 0; i < cols.length; i++) {
			var def = cols[i].getColDef ? cols[i].getColDef() : {};
			var id = cols[i].getColId ? cols[i].getColId() : '';
			var h =
				def.headerName !== undefined && def.headerName !== null ? String(def.headerName) : String(id);
			if (h.toLowerCase() === 'pin' || h.toLowerCase() === 'api') continue;
			head.push(h);
			fields.push(def.field || id);
			defs.push(def);
		}
		if (!fields.length) return null;

		var body = [];
		api.forEachNodeAfterFilterAndSort(function (node) {
			if (!node || !node.data) return;
			var row = [];
			for (var j = 0; j < fields.length; j++) {
				var v = resolve(fields[j], node.data);
				if ((v === undefined || v === null) && typeof defs[j].valueGetter === 'function') {
					try {
						v = defs[j].valueGetter({ data: node.data, node: node, colDef: defs[j] });
					} catch (e) {}
				}
				row.push(v === undefined ? null : v);
			}
			body.push(row);
		});
		return body.length ? records(head, body) : null;
	}

	function fromHighcharts() {
		var H = window.Highcharts;
		if (!H || !H.charts || !H.charts.length) return null;

		var best = null;
		var bestPoints = 0;

		for (var i = 0; i < H.charts.length; i++) {
			var chart = H.charts[i];
			if (!chart || !chart.renderTo) continue;
			if (!(chart.renderTo.offsetParent || chart.renderTo.getClientRects().length)) continue;
			var series = chart.series || [];
			var visible = [];
			var maxLen = 0;
			for (var s = 0; s < series.length; s++) {
				var sr = series[s];
				if (!sr || sr.visible === false || !sr.data || !sr.data.length) continue;
				visible.push(sr);
				if (sr.data.length > maxLen) maxLen = sr.data.length;
			}
			if (!visible.length || maxLen <= 0) continue;
			if (maxLen > bestPoints) {
				bestPoints = maxLen;
				best = { chart: chart, series: visible, rows: maxLen };
			}
		}

		if (!best) return null;

		var cats = [];
		try {
			cats = (best.chart.xAxis && best.chart.xAxis[0] && best.chart.xAxis[0].categories) || [];
		} catch (e) {
			cats = [];
		}

		var head = ['category'];
		for (var h = 0; h < best.series.length; h++) {
			head.push(best.series[h].name || 'series_' + (h + 1));
		}

		var body = [];
		for (var r = 0; r < best.rows; r++) {
			var row = [];
			var p0 = best.series[0].data[r];
			var cat = cats[r];
			if (cat === undefined || cat === null) {
				if (p0 && p0.category !== undefined) cat = p0.category;
				else if (p0 && p0.x !== undefined) cat = p0.x;
				else cat = r;
			}
			row.push(cat);
			for (var s2 = 0; s2 < best.series.length; s2++) {
				var pt = best.series[s2].data[r];
				row.push(pt ? (pt.y !== undefined ? pt.y : pt) : null);
			}
			body.push(row);
		}

		return body.length ? records(head, body) : null;
	}

	function fromEcharts() {
		var E = window.echarts;
		if (!E || typeof E.getInstanceByDom !== 'function') return null;

		var nodes = document.querySelectorAll('[data-zr-dom-id],.echarts,.echarts-for-react,canvas');
		var best = null;
		var bestPoints = 0;

		for (var i = 0; i < nodes.length; i++) {
			var inst = null;
			try {
				inst = E.getInstanceByDom(nodes[i]);
			} catch (e) {}
			if (!inst) continue;

			var option = null;
			try {
				option = inst.getOption ? inst.getOption() : null;
			} catch (e) {}
			if (!option || !option.series || !option.series.length) continue;

			var series = option.series;
			var maxLen = 0;
			for (var s = 0; s < series.length; s++) {
				var d = series[s] && series[s].data;
				if (d && d.length && d.length > maxLen) maxLen = d.length;
			}
			if (maxLen > bestPoints) {
				bestPoints = maxLen;
				best = option;
			}
		}

		if (!best || !best.series || !best.series.length) return null;

		var cats = [];
		var xAxis = best.xAxis;
		if (xAxis && xAxis.length && xAxis[0] && xAxis[0].data) cats = xAxis[0].data;

		var head = ['category'];
		for (var h = 0; h < best.series.length; h++) {
			head.push(best.series[h].name || 'series_' + (h + 1));
		}

		var rows = 0;
		for (var s2 = 0; s2 < best.series.length; s2++) {
			var d2 = best.series[s2] && best.series[s2].data;
			if (d2 && d2.length > rows) rows = d2.length;
		}

		var body = [];
		for (var r = 0; r < rows; r++) {
			var row = [];
			row.push(cats[r] !== undefined ? cats[r] : r);
			for (var s3 = 0; s3 < best.series.length; s3++) {
				var dd = best.series[s3] && best.series[s3].data ? best.series[s3].data[r] : null;
				row.push(dd && dd.value !== undefined ? dd.value : dd);
			}
			body.push(row);
		}

		return body.length ? records(head, body) : null;
	}

	function fromTable() {
		var all = document.querySelectorAll('table');
		var best = null;
		for (var i = 0; i < all.length; i++) {
			var t = all[i];
			if (t.rows.length < 2 || !t.offsetParent) continue;
			if (!best || t.rows.length > best.rows.length) best = t;
		}
		if (!best) return null;

		var head = [];
		var body = [];
		var first = best.rows[0];
		for (var c = 0; c < first.cells.length; c++) head.push(txt(first.cells[c]));
		for (var r = 1; r < best.rows.length; r++) {
			var cells = best.rows[r].cells;
			var row = [];
			for (var k2 = 0; k2 < cells.length; k2++) row.push(txt(cells[k2]));
			body.push(row);
		}
		return body.length ? records(head, body) : null;
	}

	function stateUrl(v, seq) {
		return (
			stateSink +
			'?obb_browser=' +
			encodeURIComponent(browser) +
			'&obb_user=' +
			encodeURIComponent(user) +
			'&obb_view=' +
			encodeURIComponent(v) +
			'&obb_seq=' +
			String(seq)
		);
	}

	function controlKey(el, index) {
		return String(el.name || el.id || el.getAttribute('data-name') || el.getAttribute('aria-label') || index);
	}

	function controlVal(el) {
		var tag = (el.tagName || '').toLowerCase();
		if (tag === 'select') {
			var selected = [];
			for (var i = 0; i < el.options.length; i++) {
				if (el.options[i].selected) selected.push(el.options[i].value || el.options[i].text || '');
			}
			return el.multiple ? selected : selected[0] || '';
		}
		if (tag === 'input') {
			var type = (el.type || '').toLowerCase();
			if (type === 'checkbox' || type === 'radio') return !!el.checked;
			return el.value;
		}
		if (tag === 'textarea') return el.value;
		if ((el.getAttribute('role') || '').toLowerCase() === 'slider') {
			return el.getAttribute('aria-valuenow') || el.getAttribute('value') || '';
		}
		if (el.classList && el.classList.contains('ui-slider-handle')) {
			return el.getAttribute('aria-valuenow') || el.style.left || '';
		}
		return el.value !== undefined ? el.value : txt(el);
	}

	function activeLabels(selectors, cap) {
		var out = [];
		var nodes = document.querySelectorAll(selectors);
		for (var i = 0; i < nodes.length && out.length < cap; i++) {
			var label = txt(nodes[i]);
			if (label) out.push(label);
		}
		return out;
	}

	function stateSnapshot(v) {
		var controls = {};
		var nodes = document.querySelectorAll('input,select,textarea,[role="slider"],.ui-slider-handle');
		for (var i = 0; i < nodes.length && i < 500; i++) {
			var key = controlKey(nodes[i], i);
			if (!key) continue;
			controls[key] = controlVal(nodes[i]);
		}
		var nav = activeLabels('.tab.selected,.tab.active,li.active,[aria-selected="true"]', 100);
		return {
			path: location.pathname,
			search: location.search,
			hash: location.hash,
			view: v,
			title: document.title || '',
			controls: controls,
			active: nav,
		};
	}

	var last = '';
	var lastState = '';
	var canTrackState = typeof document.addEventListener === 'function';

	function pushState(v, seq) {
		if (!canTrackState) return;
		var state = stateSnapshot(v);
		var body = JSON.stringify(state);
		var stamp = v + '|' + body;
		if (stamp === lastState) return;
		lastState = stamp;
		fetch(stateUrl(v, seq), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: body,
		}).catch(function () {});
	}

	function grab() {
		var v = view();
		var seq = Date.now();
		pushState(v, seq);

		var rows = null;
		try {
			rows = fromSlick();
		} catch (e) {}
		if (!rows) {
			try {
				rows = fromGrid();
			} catch (e) {}
		}
		if (!rows) {
			try {
				rows = fromHighcharts();
			} catch (e) {}
		}
		if (!rows) {
			try {
				rows = fromEcharts();
			} catch (e) {}
		}
		if (!rows) {
			try {
				rows = fromTable();
			} catch (e) {}
		}
		if (!rows || !rows.length) return;

		var body = JSON.stringify(rows);
		var stamp = v + '|' + body;
		if (stamp === last) return;
		last = stamp;

		if (up) up.postMessage({ type: 'eia:table', rows: rows }, '*');

		var q =
			sink +
			'?obb_browser=' +
			encodeURIComponent(browser) +
			'&obb_user=' +
			encodeURIComponent(user) +
			'&obb_view=' +
			encodeURIComponent(v) +
			'&obb_seq=' +
			String(seq);

		fetch(q, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: body,
		}).catch(function () {});
	}

	var timer = null;

	function schedule() {
		clearTimeout(timer);
		timer = setTimeout(grab, 500);
	}

	new MutationObserver(schedule).observe(document.documentElement, {
		childList: true,
		subtree: true,
		characterData: true,
	});

	setInterval(grab, 2000);
	if (canTrackState) {
		document.addEventListener('click', schedule, true);
		document.addEventListener('change', schedule, true);
		document.addEventListener('input', schedule, true);
		document.addEventListener('mouseup', schedule, true);
		document.addEventListener('keyup', schedule, true);
	}
	window.addEventListener('load', schedule);
	window.addEventListener('hashchange', schedule);
	window.addEventListener('popstate', schedule);
	schedule();
})();
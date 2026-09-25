(function () {
  "use strict";

  var J = window.json_data || {};
  var FIELDS = J.fields || [];
  var OPERATORS = J.operators || {};
  var COLUMN_DEFS_BY_ASSET = J.columnDefsByAsset || {};
  var ASSET_DEFAULTS = J.assetDefaults || {};
  var GRID_ID = J.resultsGridId;
  var TRANSPORT = J.transport || "iframe";
  var ADD_MODAL = J.addFilterModalId;
  var SAVE_MODAL = J.saveModalId;
  var DELETE_MODAL = J.deleteModalId;
  var PRESET_SELECT = J.presetSelectId;

  var STATE = {
    asset: J.defaultAsset,
    sortField: J.defaultSort,
    sortType: "DESC",
    limit: 100,
    conditions: [],
    draft: { param: "", operator: "", value: null },
    saveName: "",
    preset: "",
    rows: []
  };

  function el(id) {
    return document.getElementById(id);
  }

  function emit(event, payload) {
    if (window.pywry && window.pywry.emit) window.pywry.emit(event, payload || {});
  }

  function on(event, handler) {
    if (window.pywry && window.pywry.on) window.pywry.on(event, handler);
  }

  function setToolbar(id, value, options) {
    var tb = window.__PYWRY_TOOLBAR__;
    if (tb && tb.setValue) tb.setValue(id, value, options ? { options: options } : {});
  }

  function fieldByParam(param) {
    for (var i = 0; i < FIELDS.length; i += 1) {
      if (FIELDS[i].param === param) return FIELDS[i];
    }
    return null;
  }

  function setStatus(text) {
    var node = el("tmx-status");
    if (node) node.textContent = text;
  }

  function setCount(text) {
    var node = el("tmx-count");
    if (node) node.textContent = text;
  }

  function config() {
    return {
      asset_type: STATE.asset,
      sort_by: STATE.sortField,
      sort_order: STATE.sortType,
      limit: STATE.limit,
      conditions: STATE.conditions
    };
  }

  function pruneEmptyColumns(rows, columns) {
    if (!columns || !columns.length || !rows || !rows.length) return columns || [];
    var keep = { symbol: true, name: true };
    rows.forEach(function (row) {
      columns.forEach(function (column) {
        var v = row[column.field];
        if (v === null || v === undefined) return;
        if (typeof v === "string" && !v.trim()) return;
        keep[column.field] = true;
      });
    });
    return columns.filter(function (column) {
      return keep[column.field];
    });
  }

  function setResults(rows, columns) {
    rows = rows || [];
    STATE.rows = rows;
    var base = columns || COLUMN_DEFS_BY_ASSET[STATE.asset] || [];
    emit("grid:update-grid", {
      columnDefs: pruneEmptyColumns(rows, base),
      data: rows,
      gridId: GRID_ID
    });
    setCount(rows.length ? rows.length + (rows.length === 1 ? " row" : " rows") : "");
    setStatus(rows.length ? "" : "No matches for this configuration.");
  }

  function operatorLabel(field, operator) {
    var choices = (field && field.operators) || OPERATORS[field && field.type] || [];
    for (var i = 0; i < choices.length; i += 1) {
      if (choices[i].value === operator) return choices[i].label;
    }
    return operator;
  }

  function conditionValue(value) {
    if (!Array.isArray(value)) return String(value);
    var low = value[0];
    var high = value[1];
    if (low !== null && low !== undefined && high !== null && high !== undefined) {
      return low + " – " + high;
    }
    return String(low === null || low === undefined ? high : low);
  }

  function renderConditions() {
    var host = el("tmx-conditions");
    if (!host) return;
    host.innerHTML = "";
    if (!STATE.conditions.length) {
      host.innerHTML = '<span class="tmx-empty">No filters applied.</span>';
      return;
    }
    STATE.conditions.forEach(function (condition, index) {
      var field = fieldByParam(condition.param);
      var chip = document.createElement("span");
      chip.className = "tmx-chip";
      chip.textContent =
        (field ? field.label : condition.param) +
        " " +
        operatorLabel(field, condition.operator) +
        " " +
        conditionValue(condition.value);
      var close = document.createElement("button");
      close.type = "button";
      close.textContent = "×";
      close.addEventListener("click", function () {
        STATE.conditions.splice(index, 1);
        renderConditions();
      });
      chip.appendChild(close);
      host.appendChild(chip);
    });
  }

  function categoryFields(category) {
    return assetFields().filter(function (f) {
      return f.category === category;
    });
  }

  function renderValueInput(field) {
    var host = el("tmx-mf-value");
    if (!host) return;
    host.innerHTML = "";
    if (!field) return;

    if (field.type === "range") {
      var lo = document.createElement("input");
      var hi = document.createElement("input");
      lo.type = hi.type = "number";
      lo.step = hi.step = "any";
      lo.placeholder = "min";
      hi.placeholder = "max";
      lo.className = hi.className = "tmx-mf-number";
      function sync() {
        STATE.draft.value = [lo.value === "" ? null : Number(lo.value),
                             hi.value === "" ? null : Number(hi.value)];
      }
      lo.addEventListener("input", sync);
      hi.addEventListener("input", sync);
      host.appendChild(lo);
      host.appendChild(hi);
      sync();
      return;
    }

    var select = document.createElement("select");
    select.className = "tmx-mf-select";
    var options =
      field.type === "boolean"
        ? [{ label: "Yes", value: "true" }, { label: "No", value: "false" }]
        : field.options || [];
    options.forEach(function (option) {
      var node = document.createElement("option");
      node.value = option.value;
      node.textContent = option.label;
      select.appendChild(node);
    });
    select.addEventListener("change", function () {
      STATE.draft.value = field.type === "boolean" ? select.value === "true" : select.value;
    });
    host.appendChild(select);
    STATE.draft.value =
      field.type === "boolean" ? select.value === "true" : select.value;
  }

  function pickField(param) {
    var field = fieldByParam(param);
    STATE.draft.param = param;
    var operators = field ? field.operators || OPERATORS[field.type] || [] : [];
    STATE.draft.operator = operators.length ? operators[0].value : "is";
    setToolbar("tmx-mf-operator", STATE.draft.operator, operators);
    renderValueInput(field);
  }

  function addFilter() {
    if (!STATE.draft.param) return;
    STATE.conditions = STATE.conditions.filter(function (c) {
      return c.param !== STATE.draft.param;
    });
    STATE.conditions.push({
      param: STATE.draft.param,
      operator: STATE.draft.operator,
      value: STATE.draft.value
    });
    renderConditions();
    emit("modal:close:" + ADD_MODAL, {});
  }

  function root() {
    return window.location.pathname.replace(/\/+$/, "").replace(/\/view$/, "");
  }

  function assetSpec(asset) {
    return ASSET_DEFAULTS[asset || STATE.asset] || {};
  }

  function assetFields(asset) {
    var allowed = assetSpec(asset).fields;
    if (!allowed) return FIELDS;
    return FIELDS.filter(function (field) {
      return allowed.indexOf(field.param) >= 0;
    });
  }

  function applyAssetDefaults() {
    var spec = assetSpec();
    var allowed = spec.fields;

    if (allowed) {
      STATE.conditions = STATE.conditions.filter(function (condition) {
        return allowed.indexOf(condition.param) >= 0;
      });
    }

    STATE.sortField = spec.sort_by || STATE.sortField;
    STATE.limit = spec.limit || STATE.limit;
    setToolbar("tmx-sort-field", STATE.sortField, spec.sort_fields);
    setToolbar("tmx-limit", STATE.limit);
    renderConditions();
  }

  function apply() {
    var cfg = config();
    setStatus("Screening…");
    if (TRANSPORT === "bridge") {
      emit("screener:run", { config: JSON.stringify(cfg), limit: STATE.limit });
      return;
    }
    fetch(
      root() +
        "/run?limit=" +
        encodeURIComponent(STATE.limit) +
        "&config=" +
        encodeURIComponent(JSON.stringify(cfg))
    )
      .then(function (response) {
        return response.json();
      })
      .then(function (payload) {
        if (payload.error) {
          setStatus(payload.error);
          setResults([], payload.columns);
          return;
        }
        setResults(payload.rows, payload.columns);
      })
      .catch(function () {
        setStatus("The screen could not be run.");
      });
  }

  function reset() {
    STATE.conditions = [];
    STATE.draft = { param: "", operator: "", value: null };
    renderConditions();
    apply();
  }

  function refreshPresets(presets) {
    var options = [{ label: "- Presets -", value: "" }].concat(
      (presets || []).map(function (p) {
        return { label: p.label, value: p.name };
      })
    );
    setToolbar(PRESET_SELECT, "", options);
  }

  function loadPreset(name) {
    if (!name) return;
    STATE.preset = name;
    fetch(root() + "/presets/load?name=" + encodeURIComponent(name))
      .then(function (r) {
        return r.json();
      })
      .then(function (payload) {
        var cfg = payload.config || {};
        STATE.asset = cfg.asset_type || STATE.asset;
        STATE.sortField = cfg.sort_by || STATE.sortField;
        STATE.limit = cfg.limit || STATE.limit;
        STATE.conditions = cfg.conditions || [];
        setToolbar("tmx-asset", STATE.asset);
        setToolbar("tmx-sort-field", STATE.sortField);
        setToolbar("tmx-limit", STATE.limit);
        renderConditions();
        apply();
      });
  }

  function savePreset() {
    if (!STATE.saveName) return;
    fetch(
      root() +
        "/presets/save?name=" +
        encodeURIComponent(STATE.saveName) +
        "&config=" +
        encodeURIComponent(JSON.stringify(config())),
      { method: "POST" }
    )
      .then(function (r) {
        return r.json();
      })
      .then(function (payload) {
        refreshPresets(payload.presets);
        emit("modal:close:" + SAVE_MODAL, {});
      });
  }

  function deletePreset() {
    if (!STATE.preset) return;
    fetch(
      root() + "/presets/delete?name=" + encodeURIComponent(STATE.preset),
      { method: "POST" }
    )
      .then(function (r) {
        return r.json();
      })
      .then(function (payload) {
        STATE.preset = "";
        refreshPresets(payload.presets);
        emit("modal:close:" + DELETE_MODAL, {});
      });
  }

  on("screener:asset", function (d) {
    STATE.asset = d.value;
    applyAssetDefaults();
    apply();
  });
  on("screener:sortfield", function (d) {
    STATE.sortField = d.value;
  });
  on("screener:sorttype", function (d) {
    STATE.sortType = d.value;
  });
  on("screener:limit", function (d) {
    STATE.limit = Number(d.value) || 100;
  });
  on("screener:open-add-filter", function () {
    emit("modal:open:" + ADD_MODAL, {});
  });
  on("screener:mf-category", function (d) {
    var entries = categoryFields(d.value).map(function (f) {
      return { label: f.label, value: f.param };
    });
    setToolbar("tmx-mf-field", entries.length ? entries[0].value : "", entries);
    if (entries.length) pickField(entries[0].value);
  });
  on("screener:mf-field", function (d) {
    pickField(d.value);
  });
  on("screener:mf-operator", function (d) {
    STATE.draft.operator = d.value;
  });
  on("screener:add-filter", addFilter);
  on("screener:apply", apply);
  on("screener:reset", reset);
  on("screener:preset-pick", function (d) {
    loadPreset(d.value);
  });
  on("screener:preset-new", reset);
  on("screener:preset-saveas", function () {
    emit("modal:open:" + SAVE_MODAL, {});
  });
  on("screener:save-name", function (d) {
    STATE.saveName = d.value;
  });
  on("screener:preset-do-save", savePreset);
  on("screener:preset-delete-click", function () {
    var msg = el("tmx-delete-msg");
    if (msg) msg.textContent = 'Delete "' + (STATE.preset || "this preset") + '"?';
    emit("modal:open:" + DELETE_MODAL, {});
  });
  on("screener:preset-do-delete", deletePreset);
  on("screener:results", function (d) {
    setResults((d && d.rows) || [], d && d.columns);
  });

  window.__OPENBB_WIDGETS__ = [
    {
      widgetId: "tmx-screener-results",
      name: "TMX Screener Results",
      description: "The rows the current screen returned.",
      category: "Equity",
      dataType: "table"
    }
  ];

  window.addEventListener("message", function (event) {
    var data = event.data;
    if (!data || data.type !== "openbb-request") return;
    var target = window.top || window.parent;
    if (!target || target === window) return;
    if (data.widgetId !== null && data.widgetId !== "tmx-screener-results") return;
    target.postMessage(
      {
        type: "openbb-data",
        widgetId: "tmx-screener-results",
        dataType: "table",
        data: STATE.rows
      },
      "*"
    );
  });

  renderConditions();
  apply();
})();

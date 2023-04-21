function TableProcessor(data) {
  const parsedData = JSON.parse(data);
  console.log(parsedData);
  const processedData = processData(parsedData);
  console.log(processedData);
  const body = document.getElementsByTagName("body")[0];
  const table = new Tabulator("#example-table", {
    height: body.clientHeight - 54,
    layout: "fitColumns",
    data: processedData.data,
    columns: processedData.columns,
  });

  const div = document.createElement("div");
  div.innerHTML = `
    <div style="margin-top:10px;">
  <select id="filter-field">
    <option></option>
    ${processedData.columns.map((column) => {
      return `<option value="${column.field}">${column.title}</option>`;
    })}
  </select>

  <select id="filter-type">
    <option value="=">=</option>
    <option value="<"><</option>
    <option value="<="><=</option>
    <option value=">">></option>
    <option value=">=">>=</option>
    <option value="!=">!=</option>
    <option value="like">like</option>
  </select>

  <input id="filter-value" type="text" placeholder="value to filter">

  <button id="filter-clear">Clear Filter</button>
</div>

    `;
  body.appendChild(div);
  const filterField = document.getElementById("filter-field");
  const filterType = document.getElementById("filter-type");
  const filterValue = document.getElementById("filter-value");
  const filterClear = document.getElementById("filter-clear");

  filterField.addEventListener("change", function (e) {
    table.setFilter(filterField.value, filterType.value, filterValue.value);
  });

  filterType.addEventListener("change", function (e) {
    table.setFilter(filterField.value, filterType.value, filterValue.value);
  });

  filterValue.addEventListener("keyup", function (e) {
    table.setFilter(filterField.value, filterType.value, filterValue.value);
  });

  filterClear.addEventListener("click", function (e) {
    table.clearFilter();
  });
}

function processData(data) {
  /*
    data is coming as {
        columns: ["Name", "Age"],
        data: ["John", 30]
    }
    */
  /*
        final data should be {
            columns: [
                {
                    title: "Name",
                    field: "name",
                    sorter: "string",
                },
                {
                    title: "Age",
                    field: "age",
                    sorter: "number",
                }
            ],
            data: {
                name: "John",
                age: "30",
            }
        }
    */
  const columns = data.columns.map((column) => {
    return {
      title: column,
      field: column,
      sorter: column.includes("Change"),
      /*formatter: (cell) => {
        if (column.startsWith("Change")) {
          if (cell.getValue() > 0) {
            return `<span style="color: green">${cell.getValue()}</span>`;
          } else {
            return `<span style="color: red">${cell.getValue()}</span>`;
          }
        } else {
          return cell.getValue();
        }
      },*/
    };
  });
  const finalData = data.data.map((row) => {
    const obj = {};
    row.forEach((item, index) => {
      obj[data.columns[index]] = item;
    });
    return obj;
  });
  return {
    columns,
    data: finalData,
  };
}

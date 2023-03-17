import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  Row,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import { rankItem } from "@tanstack/match-sorter-utils";
import { utils, writeFile } from "xlsx";
import { useDrag, useDrop } from "react-dnd";
import clsx from "clsx";
import { FC, useEffect, useMemo, useReducer, useRef, useState } from "react";
import { useVirtual } from "react-virtual";
import domtoimage from "dom-to-image";
import Chart from "./Chart";
import Select from "./Select";

function formatNumberMagnitude(number: number) {
  if (number < 10) {
    return number.toFixed(4);
  } else if (number < 100) {
    return number.toFixed(3);
  } else if (number < 1000) {
    return number.toFixed(2);
  }
  const abs = Math.abs(number);
  if (abs >= 1000000000000) {
    return `${(number / 1000000000).toFixed(2)}T`;
  } else if (abs >= 1000000000) {
    return `${(number / 1000000000).toFixed(2)}B`;
  } else if (abs >= 1000000) {
    return `${(number / 1000000).toFixed(2)}M`;
  } else if (abs >= 1000) {
    return `${(number / 1000).toFixed(2)}K`;
  } else {
    return number.toFixed(2);
  }
}

const FONT_SIZES_CLASSES = {
  small: {
    overall: "text-sm",
    header: "text-sm",
    cell: "text-xs",
  },
  medium: {
    overall: "text-base",
    header: "text-base",
    cell: "text-sm",
  },
  large: {
    overall: "text-base",
    header: "text-lg",
    cell: "text-base",
  },
};

const reorderColumn = (
  draggedColumnId: string,
  targetColumnId: string,
  columnOrder: string[]
) => {
  columnOrder.splice(
    columnOrder.indexOf(targetColumnId),
    0,
    columnOrder.splice(columnOrder.indexOf(draggedColumnId), 1)[0] as string
  );
  return [...columnOrder];
};

const DraggableColumnHeader: FC<{
  header: any;
  table: any;
  advanced: boolean;
}> = ({ header, table, advanced }) => {
  const { getState, setColumnOrder } = table;
  const { columnOrder } = getState();
  const { column } = header;

  const [, dropRef] = useDrop({
    accept: "column",
    drop: (draggedColumn: any) => {
      const newColumnOrder = reorderColumn(
        draggedColumn.id,
        column.id,
        columnOrder
      );
      setColumnOrder(newColumnOrder);
    },
  });

  const [{ isDragging }, dragRef, previewRef] = useDrag({
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
    item: () => column,
    type: "column",
  });

  return (
    <th
      className="h-[70px] relative"
      colSpan={header.colSpan}
      style={{ /* width: header.getSize(),*/ opacity: isDragging ? 0.5 : 1 }}
      ref={dropRef}
    >
      <div ref={previewRef} className="space-y-2">
        {header.isPlaceholder ? null : (
          <>
            <div
              {...{
                className: clsx(
                  "font-bold uppercase text-white tracking-widest tracking-normal flex gap-2 whitespace-nowrap justify-between",
                  {
                    "cursor-pointer select-none": header.column.getCanSort(),
                  }
                ),
                onClick: header.column.getToggleSortingHandler(),
              }}
            >
              <div className="flex gap-2">
                {flexRender(
                  header.column.columnDef.header,
                  header.getContext()
                )}
                {header.column.getCanSort() && (
                  <div className="flex flex-col gap-1 items-center justify-center">
                    <button
                      className={clsx({
                        "text-[#669DCB]": header.column.getIsSorted() === "asc",
                        "text-grey-600": header.column.getIsSorted() !== "asc",
                      })}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="11"
                        height="5"
                        fill="none"
                        viewBox="0 0 11 5"
                      >
                        <path fill="currentColor" d="M10.333 5l-5-5-5 5"></path>
                      </svg>
                    </button>
                    <button
                      className={clsx({
                        "text-[#669DCB]":
                          header.column.getIsSorted() === "desc",
                        "text-grey-600": header.column.getIsSorted() !== "desc",
                      })}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="11"
                        height="5"
                        fill="none"
                        viewBox="0 0 11 5"
                      >
                        <path fill="currentColor" d="M.333 0l5 5 5-5"></path>
                      </svg>
                    </button>
                  </div>
                )}
              </div>
              {advanced && column.id !== "select" && (
                <button ref={dragRef}>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="17"
                    height="16"
                    fill="none"
                    viewBox="0 0 17 16"
                  >
                    <path
                      stroke="#fff"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M3.667 6l-2 2 2 2M6.333 3.333l2-2 2 2M10.333 12.667l-2 2-2-2M13 6l2 2-2 2M1.667 8H15M8.333 1.333v13.334"
                    ></path>
                  </svg>
                </button>
              )}
            </div>
            {advanced && header.column.getCanFilter() ? (
              <div>
                <Filter
                  column={header.column}
                  table={table}
                  numberOfColumns={columnOrder.length}
                />
              </div>
            ) : null}
          </>
        )}
      </div>
      {/* <div
        className="absolute right-0 top-0 h-full w-1 bg-blue-300 select-none touch-none hover:bg-blue-500 cursor-col-resize"
        onMouseDown={header.getResizeHandler()}
        onTouchStart={header.getResizeHandler()}
            />*/}
    </th>
  );
};

function isEqual(a: any, b: any) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length !== b.length) return false;

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

export const fuzzyFilter = (row, columnId, value, addMeta) => {
  const itemRank = rankItem(row.getValue(columnId), value);
  addMeta(itemRank);
  return itemRank;
};

export default function Table({ data, columns }: any) {
  const [fontSize, setFontSize] = useState("medium");

  const increaseFontSize = () => {
    if (fontSize === "small") {
      setFontSize("medium");
    } else if (fontSize === "medium") {
      setFontSize("large");
    }
  };

  const decreaseFontSize = () => {
    if (fontSize === "large") {
      setFontSize("medium");
    } else if (fontSize === "medium") {
      setFontSize("small");
    }
  };

  const [advanced, setAdvanced] = useState(false);
  const rerender = useReducer(() => ({}), {})[1];
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const rtColumns = useMemo(
    () => [
      {
        id: "select",
        size: 1,
        disableSortBy: true,
        header: ({ table }) => (
          <IndeterminateCheckbox
            {...{
              checked: table.getIsAllRowsSelected(),
              indeterminate: table.getIsSomeRowsSelected(),
              onChange: table.getToggleAllRowsSelectedHandler(),
            }}
          />
        ),
        cell: ({ row }) => (
          <div className="px-1">
            <IndeterminateCheckbox
              {...{
                checked: row.getIsSelected(),
                disabled: !row.getCanSelect(),
                indeterminate: row.getIsSomeSelected(),
                onChange: row.getToggleSelectedHandler(),
              }}
            />
          </div>
        ),
      },
      ...columns.map((column: any) => ({
        accessorKey: column,
        id: column,
        header: column,
        footer: column,
        cell: ({ row }: any) => {
          const value = row.original[column];
          const valueType = typeof value;
          const probablyDate =
            column.toLowerCase().includes("date") ||
            column.toLowerCase() === "index";
          const probablyLink =
            valueType === "string" && value.startsWith("http");

          //TODO - Parse as HTML to make links work if string doesn't start with http
          //TODO - Max Column Size
          if (probablyLink) {
            return (
              <a
                className="_hyper-link"
                href={value}
                target="_blank"
                rel="noreferrer"
              >
                {value}
              </a>
            );
          }
          if (probablyDate) {
            if (typeof value === "string") {
              return <p>{value}</p>;
            }

            try {
              var dateFormatted = new Date(value).toISOString();

              // TODO - Remove 00:00:00 from date

              dateFormatted =
                dateFormatted.split("T")[0] +
                " " +
                dateFormatted.split("T")[1].split(".")[0];
              return <p>{dateFormatted}</p>;
            } catch (e) {
              return <p>{value}</p>;
            }
          }
          const valueFormatted =
            valueType === "number" ? formatNumberMagnitude(value) : value;
          return (
            <p
              className={clsx("whitespace-nowrap", {
                "text-[#16A34A]": value > 0,
                "text-[#F87171]": value < 0,
                "text-[#404040]": value === 0,
              })}
            >
              {value !== 0
                ? value > 0
                  ? `${valueFormatted}`
                  : `${valueFormatted}`
                : valueFormatted}
            </p>
          );
        },
      })),
    ],
    []
  );

  const [columnOrder, setColumnOrder] = useState(
    rtColumns.map((column) => column.id as string)
  );
  const [columnVisibility, setColumnVisibility] = useState({});

  const resetOrder = () =>
    setColumnOrder(columns.map((column) => column.id as string));

  const needsReorder = useMemo(() => {
    const currentOrder = columnOrder.map((columnId) => columnId);
    const defaultOrder = rtColumns.map((column) => column.id as string);
    return !isEqual(currentOrder, defaultOrder);
  }, [columnOrder, rtColumns]);

  const table = useReactTable({
    data,
    columns: rtColumns,
    defaultColumn: {
      minSize: 0,
      size: 0,
      maxSize: 20,
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    /*enableColumnResizing: true,
    columnResizeMode: "onChange",
    onColumnVisibilityChange: setColumnVisibility,*/
    onColumnOrderChange: setColumnOrder,
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    state: {
      sorting,
      globalFilter,
      columnOrder,
      //columnVisibility,
    },
  });

  const tableContainerRef = useRef<HTMLDivElement>(null);
  const { rows } = table.getRowModel();
  const rowVirtualizer = useVirtual({
    parentRef: tableContainerRef,
    size: rows.length,
    overscan: 10,
  });
  const { virtualItems: virtualRows, totalSize } = rowVirtualizer;

  const paddingTop = virtualRows.length > 0 ? virtualRows?.[0]?.start || 0 : 0;
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows?.[virtualRows.length - 1]?.end || 0)
      : 0;

  const saveToFile = (blob, fileName) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadData = (type: "csv" | "xlsx") => {
    const headers = columns;
    const rows = data.map((row) => headers.map((column) => row[column]));
    const csvData = [headers, ...rows];
    if (type === "csv") {
      const csvContent = csvData.map((e) => e.join(",")).join("\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      saveToFile(blob, `${window.title}.csv`);
    } else {
      const wb = utils.book_new();
      const ws = utils.aoa_to_sheet(csvData);
      utils.book_append_sheet(wb, ws, "Sheet1");
      writeFile(wb, `${window.title}.xlsx`);
    }
  };

  const downloadImage = () => {
    const table = document.getElementById("table");
    domtoimage.toBlob(table).then(function (blob) {
      saveToFile(blob, `${window.title}.png`);
    });
  };

  const [dialog, setDialog] = useState(null);

  return (
    <>
      {dialog && (
        <>
          <div
            onClick={() => setDialog(null)}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 backdrop-filter backdrop-blur-sm"
          />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-grey-500">
            <Chart values={dialog.values} />
          </div>
        </>
      )}
      <div ref={tableContainerRef} className={clsx("overflow-auto")}>
        <div className="flex gap-2 px-6 items-center justify-between h-[70px] border-grey-400 border-b">
          <div className="flex gap-[14px]">
            <input
              id="advanced"
              type="checkbox"
              checked={advanced}
              onChange={() => setAdvanced(!advanced)}
            />
            <label htmlFor="advanced">Advanced</label>
          </div>

          {advanced && (
            <>
              <DebouncedInput
                id="search"
                value={globalFilter ?? ""}
                onChange={(value) => setGlobalFilter(String(value))}
                placeholder="Search..."
              />
              {needsReorder && (
                <button onClick={() => resetOrder()} className="_btn">
                  Reset Order
                </button>
              )}
              <Select
                label="Font size"
                placeholder="Select font size"
                groups={[
                  {
                    label: "Font size",
                    items: [
                      {
                        label: "100%",
                        value: 1,
                      },
                      {
                        label: "125%",
                        value: 1.25,
                      },
                      {
                        label: "150%",
                        value: 1.5,
                      },
                      {
                        label: "175%",
                        value: 1.75,
                      },
                      {
                        label: "200%",
                        value: 2,
                      },
                    ],
                  },
                ]}
              />
              <Select
                label="Filter"
                placeholder="Select filter"
                groups={[
                  {
                    label: "Filter",
                    items: [
                      {
                        label: "Toggle All",
                        value: "toggleAll",
                      },
                      ...table.getAllLeafColumns().map((column) => {
                        return {
                          label: column.id,
                          value: column.id,
                        };
                      }),
                    ],
                  },
                ]}
              />
              {/*
              <div className="p-2 border border-black shadow rounded grid grid-cols-4">
              <div className="px-1 border-b border-black">
              <label>
              <input
              type="checkbox"
              checked={table.getIsAllColumnsVisible()}
              onChange={table.getToggleAllColumnsVisibilityHandler()}
              className="mr-1"
              />
              Toggle All
              </label>
              </div>
                {table.getAllLeafColumns().map((column) => {
                  return (
                    <div key={column.id} className="px-1">
                    <label>
                    <input
                    type="checkbox"
                    checked={column.getIsVisible()}
                    onChange={column.getToggleVisibilityHandler()}
                    className="mr-1"
                    />
                    {column.id}
                      </label>
                    </div>
                  );
                })}
              </div>
              */}
            </>
          )}
        </div>
        <table
          id="table"
          className={clsx("text-sm")}
          /*style={{
          width: table.getCenterTotalSize(),
        }}*/
        >
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className={clsx("!h-10 text-left")}>
                {headerGroup.headers.map((header) => {
                  return (
                    <DraggableColumnHeader
                      advanced={advanced}
                      key={header.id}
                      header={header}
                      table={table}
                    />
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {paddingTop > 0 && (
              <tr>
                <td style={{ height: `${paddingTop}px` }} />
              </tr>
            )}
            {virtualRows.map((virtualRow, idx) => {
              const row = rows[virtualRow.index];
              return (
                <tr key={row.id} className="!h-[64px] border-b border-grey-400">
                  {row.getVisibleCells().map((cell) => {
                    return (
                      <td
                        key={cell.id}
                        className={clsx("whitespace-nowrap truncate", {
                          "bg-grey-850": idx % 2 === 0,
                          "bg-[#202020]": idx % 2 === 1,
                        })}
                        /*style={{
                          width: cell.column.getSize(),
                        }}*/
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
            {paddingBottom > 0 && (
              <tr>
                <td style={{ height: `${paddingBottom}px` }} />
              </tr>
            )}
          </tbody>
          <tfoot>
            {table.getFooterGroups().map((footerGroup) => (
              <tr key={footerGroup.id}>
                {footerGroup.headers.map((header) => (
                  <th
                    style={{ width: header.getSize() }}
                    key={header.id}
                    colSpan={header.colSpan}
                    className="text-grey-500 bg-grey-850 font-normal text-left h-[64px]"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.footer,
                          header.getContext()
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </tfoot>
        </table>
        <div className="flex gap-10 items-center py-2 h-[120px] px-6">
          {advanced && (
            <div className="flex items-center gap-2">
              <button
                className={clsx("px-2", {
                  "text-grey-700": !table.getCanPreviousPage(),
                  "text-white": table.getCanPreviousPage(),
                })}
                onClick={() => table.setPageIndex(0)}
                disabled={!table.getCanPreviousPage()}
              >
                {"<<"}
              </button>
              <button
                className={clsx("px-2", {
                  "text-grey-700": !table.getCanPreviousPage(),
                  "text-white": table.getCanPreviousPage(),
                })}
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                {"<"}
              </button>
              <button
                className={clsx("px-2", {
                  "text-grey-700": !table.getCanNextPage(),
                  "text-white": table.getCanNextPage(),
                })}
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                {">"}
              </button>
              <button
                className={clsx("px-2", {
                  "text-grey-700": !table.getCanNextPage(),
                  "text-white": table.getCanNextPage(),
                })}
                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                disabled={!table.getCanNextPage()}
              >
                {">>"}
              </button>
              <span className="flex items-center gap-1">
                <div>Page</div>
                <strong>
                  {table.getState().pagination.pageIndex + 1} of{" "}
                  {table.getPageCount()}
                </strong>
              </span>
              <span className="flex items-center gap-1">
                | Go to page:
                <input
                  type="number"
                  defaultValue={table.getState().pagination.pageIndex + 1}
                  onChange={(e) => {
                    const page = e.target.value
                      ? Number(e.target.value) - 1
                      : 0;
                    table.setPageIndex(page);
                  }}
                  className="_input"
                />
              </span>
              <Select
                label="Rows per page:"
                placeholder="Select rows per page"
                groups={[
                  {
                    label: "Rows per page", // TODO: generate number automatically
                    items: [10, 20, 30, 40, 50].map((pageSize) => ({
                      label: `Show ${pageSize}`,
                      value: pageSize,
                    })),
                  },
                ]}
              />
              {/*
              <select
              className="_input bg-gray-600"
              value={table.getState().pagination.pageSize}
              onChange={(e) => {
                table.setPageSize(Number(e.target.value));
              }}
              >
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                Show {pageSize}
                </option>
                ))}
                </select>
              */}
            </div>
          )}
          <button className="_btn" onClick={() => downloadImage()}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
              />
            </svg>
            Download as png
          </button>
          <button className="_btn" onClick={() => downloadData("csv")}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
              />
            </svg>
            Export to csv
          </button>
          <button className="_btn" onClick={() => downloadData("xlsx")}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
              />
            </svg>
            Export to xlsx
          </button>

          <button
            className="_btn"
            onClick={() => {
              const selectedRows = table.getSelectedRowModel().flatRows;
              const values = selectedRows.map((row) =>
                Object.values(row.original)
              );
              setDialog({
                values,
              });
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"
              />
            </svg>
            Generate chart
          </button>
        </div>
      </div>
    </>
  );
}

function Filter({
  column,
  table,
  numberOfColumns,
}: {
  column: any;
  table: any;
  numberOfColumns: number;
}) {
  const firstValue = table
    .getPreFilteredRowModel()
    .flatRows[0]?.getValue(column.id);

  const columnFilterValue = column.getFilterValue();

  const isProbablyDate =
    column.id.toLowerCase().includes("date") ||
    column.id.toLowerCase() === "index";

  if (isProbablyDate) {
    function getTime(value) {
      if (!value) return null;
      const date = new Date(value);
      const year = date.getFullYear();
      const month =
        date.getMonth() + 1 > 9
          ? date.getMonth() + 1
          : `0${date.getMonth() + 1}`;
      const day = date.getDate() > 9 ? date.getDate() : `0${date.getDate()}`;
      return `${year}-${month}-${day}`;
    }

    return (
      <div className="flex space-x-2">
        <input
          type="date"
          value={getTime((columnFilterValue as [string, string])?.[0]) ?? ""}
          onChange={(e) => {
            const value = new Date(e.target.value).getTime();
            column.setFilterValue((old: [string, string]) => [value, old?.[1]]);
          }}
          placeholder={`Start date`}
          className="_input"
        />
        <input
          type="date"
          value={getTime((columnFilterValue as [string, string])?.[1]) ?? ""}
          onChange={(e) => {
            const value = new Date(e.target.value).getTime();
            column.setFilterValue((old: [string, string]) => [old?.[0], value]);
          }}
          placeholder={`End date`}
          className="_input"
        />
      </div>
    );
  }

  return typeof firstValue === "number" ? (
    <div
      className={clsx("flex space-x-2", {
        "flex-col": numberOfColumns > 4,
        "flex-row": numberOfColumns <= 4,
      })}
    >
      <input
        type="number"
        value={(columnFilterValue as [number, number])?.[0] ?? ""}
        onChange={(e) =>
          column.setFilterValue((old: [number, number]) => [
            e.target.value,
            old?.[1],
          ])
        }
        placeholder={`Min`}
        className="_input"
      />
      <input
        type="number"
        value={(columnFilterValue as [number, number])?.[1] ?? ""}
        onChange={(e) =>
          column.setFilterValue((old: [number, number]) => [
            old?.[0],
            e.target.value,
          ])
        }
        placeholder={`Max`}
        className="_input"
      />
    </div>
  ) : (
    <input
      type="text"
      value={(columnFilterValue ?? "") as string}
      onChange={(e) => column.setFilterValue(e.target.value)}
      placeholder={`Search...`}
      className="_input"
    />
  );
}

type Props = {
  value: string | number;
  onChange: (value: string | number) => void;
  debounce?: number;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange">;

const DebouncedInput: FC<Props> = ({
  value: initialValue,
  onChange,
  debounce = 500,
  ...props
}) => {
  const [value, setValue] = useState<number | string>(initialValue);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) =>
    setValue(event.target.value);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(value);
    }, debounce);

    return () => clearTimeout(timeout);
  }, [value]);

  return (
    <div className="relative group">
      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        <svg
          aria-hidden="true"
          className="w-5 h-5 text-grey-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          ></path>
        </svg>
      </div>
      <input
        {...props}
        className="bg-grey-900 h-[36px] border-[1.5px] border-grey-700 rounded p-3 pl-10 max-w-[216px]"
        value={value}
        onChange={handleInputChange}
      />
    </div>
  );
};

function IndeterminateCheckbox({
  indeterminate,
  className = "",
  ...rest
}: { indeterminate?: boolean } & HTMLProps<HTMLInputElement>) {
  const ref = useRef<HTMLInputElement>(null!);

  useEffect(() => {
    if (typeof indeterminate === "boolean") {
      ref.current.indeterminate = !rest.checked && indeterminate;
    }
  }, [ref, indeterminate]);

  return (
    <input
      type="checkbox"
      ref={ref}
      className={className + " cursor-pointer"}
      {...rest}
    />
  );
}

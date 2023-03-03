//@ts-nocheckdd
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

import { useDrag, useDrop } from "react-dnd";
import clsx from "clsx";
import { FC, useEffect, useMemo, useReducer, useRef, useState } from "react";
import { useVirtual } from "react-virtual";

function formatNumberMagnitude(number: number) {
  if (number < 10) {
    return number.toFixed(4);
  } else if (number < 100) {
    return number.toFixed(3);
  } else if (number < 1000) {
    return number.toFixed(2);
  }
  const abs = Math.abs(number);
  if (abs >= 1000000000) {
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
      className="bg-grey-800 pb-4"
      colSpan={header.colSpan}
      style={{ width: header.getSize(), opacity: isDragging ? 0.5 : 1 }}
      ref={dropRef}
    >
      <div ref={previewRef}>
        {header.isPlaceholder ? null : (
          <>
            <div
              {...{
                className: clsx(
                  "font-bold uppercase text-white my-2 tracking-normal flex gap-2",
                  {
                    "cursor-pointer select-none": header.column.getCanSort(),
                  }
                ),
                onClick: header.column.getToggleSortingHandler(),
              }}
            >
              {flexRender(header.column.columnDef.header, header.getContext())}
              <span className="w-4">
                {{
                  asc: "🔼",
                  desc: "🔽",
                }[header.column.getIsSorted() as string] ?? null}
              </span>
              {advanced && <button ref={dragRef}>🟰</button>}
            </div>
            {advanced && header.column.getCanFilter() ? (
              <div>
                <Filter column={header.column} table={table} />
              </div>
            ) : null}
          </>
        )}
      </div>
    </th>
  );
};

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

  const [advanced, setAdvanced] = useState(true);
  const rerender = useReducer(() => ({}), {})[1];
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const rtColumns = useMemo(
    () =>
      columns.map((column: any) => ({
        accessorKey: column,
        id: column,
        header: column,
        footer: column,
        cell: ({ row }: any) => {
          const value = row.original[column];
          const valueFormatted =
            typeof value === "number" ? formatNumberMagnitude(value) : value;
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
    []
  );

  const [columnOrder, setColumnOrder] = useState(
    rtColumns.map((column) => column.id as string)
  );

  const resetOrder = () =>
    setColumnOrder(columns.map((column) => column.id as string));

  const table = useReactTable({
    data,
    columns: rtColumns,
    state: {
      sorting,
      globalFilter,
      columnOrder,
    },
    onColumnOrderChange: setColumnOrder,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onGlobalFilterChange: setGlobalFilter,
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

  return (
    <div
      ref={tableContainerRef}
      className={clsx("overflow-auto max-w-full max-h-full")}
    >
      <div className="flex gap-2 items-center justify-between h-20">
        <div className="flex gap-10">
          <svg
            viewBox="0 0 126 34"
            width="126"
            height="34"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-labelledby="OpenBB"
          >
            <title id="OpenBB">OpenBB</title>
            <g fill="currentColor">
              <path d="M60.707 1.416h-9.285v4.25h9.285v1.42h-7.854v4.25h9.283V1.423h-1.428l-.001-.007Zm0 7.793v.707H54.28V8.5h6.427v.709Zm0-5.668v.71h-7.854V2.831h7.855l-.001.71ZM69.99 11.333h2.852V7.087H64.99V5.671h9.285V1.42H63.562v9.913h6.428Zm-5-7.791v-.709h7.852V4.25H64.99v-.709Zm2.858 6.375H64.99V8.5h6.438v1.417h-3.58ZM63.563 0h-1.428v1.416h1.428V0ZM78.519 22.72v8.459l-.712-.704-.71-.706-.71-.704-.71-.706-.712-.704-.712-.705-.71-.704-.71-.706-.71-.706-.712-.704-.71-.704-.711-.705h-1.422V33.998h1.422V24.834l.711.706.71.706.711.704.71.705.712.704.71.706.71.704.712.706.71.704.712.705.71.706.71.704.71.704h.712V22.721H78.52ZM101.402 26.95h-1.421v-4.23h-8.528V34h11.374v-7.057h-1.422l-.003.007Zm-8.528-.71v-2.11h5.685v2.82h-5.685v-.71Zm8.528 2.82v3.528h-8.528v-4.227h8.528v.699ZM124.986 26.95h-2.131v-4.23h-8.529V34h11.37v-7.057l-.71.007Zm-9.239-.71v-2.11h5.687v2.82h-5.687v-.71Zm8.53 2.82v3.528h-8.53v-4.227h8.53v.699ZM55.732 22.72H45.78v11.278H57.15V32.59H47.204v-2.821H55.728v-1.41h-8.524V24.13H57.15V22.721h-1.418ZM9.95 22.72H.003V34h11.372V22.72H9.95Zm0 2.116v7.754H1.423v-8.46H9.95v.706ZM32.855 22.721h-9.949v11.28h1.422V29.77h9.948v-7.057h-1.421v.008Zm0 2.116v3.528h-8.527v-4.234h8.527v.706Z"></path>
            </g>
          </svg>
          <div>
            <label htmlFor="advanced">Advanced</label>
            <input
              id="advanced"
              type="checkbox"
              checked={advanced}
              onChange={() => setAdvanced(!advanced)}
            />
          </div>
        </div>
        {advanced && (
          <>
            <div className="p-2 flex gap-2">
              <label htmlFor="search">Search:</label>
              <DebouncedInput
                id="search"
                value={globalFilter ?? ""}
                onChange={(value) => setGlobalFilter(String(value))}
                className="_input"
                placeholder="Search all columns..."
              />
            </div>
            <button onClick={() => resetOrder()} className="_btn">
              Reset Order
            </button>
            <div className="flex gap-2">
              <button onClick={decreaseFontSize} className="_btn">
                Decrease font
              </button>
              <button onClick={increaseFontSize} className="_btn">
                Increase font
              </button>
            </div>
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
          </>
        )}
      </div>
      <table
        className={clsx("w-full my-4", FONT_SIZES_CLASSES[fontSize].overall)}
      >
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr
              key={headerGroup.id}
              className={clsx(
                "!h-10 text-left",
                FONT_SIZES_CLASSES[fontSize].header
              )}
            >
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
              <tr key={row.id} className="!h-10">
                {row.getVisibleCells().map((cell) => {
                  return (
                    <td
                      key={cell.id}
                      className={clsx("bg-grey-800", {
                        "bg-white/5": idx % 2 === 0,
                      })}
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
                  key={header.id}
                  colSpan={header.colSpan}
                  className="text-white font-normal text-left opacity-50"
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
      <div className="flex gap-10 items-center py-2">
        {advanced && (
          <div className="flex items-center gap-2">
            <button
              className="_icon-btn"
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
            >
              {"<<"}
            </button>
            <button
              className="_icon-btn"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              {"<"}
            </button>
            <button
              className="_icon-btn"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              {">"}
            </button>
            <button
              className="_icon-btn"
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
                  const page = e.target.value ? Number(e.target.value) - 1 : 0;
                  table.setPageIndex(page);
                }}
                className="border p-1 rounded w-16"
              />
            </span>
            <select
              className="_input"
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
          </div>
        )}
        <button className="_btn">
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
        <button className="_btn">
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
      </div>
    </div>
  );
}

function Filter({ column, table }: { column: any; table: any }) {
  const firstValue = table
    .getPreFilteredRowModel()
    .flatRows[0]?.getValue(column.id);

  const columnFilterValue = column.getFilterValue();

  return typeof firstValue === "number" ? (
    <div className="flex space-x-2">
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

  return <input {...props} value={value} onChange={handleInputChange} />;
};

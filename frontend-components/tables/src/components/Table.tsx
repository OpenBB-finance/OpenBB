//@ts-nocheck
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
import {
  rankItem,
  compareItems,
  RankingInfo,
} from '@tanstack/match-sorter-utils'

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

export const fuzzyFilter = (
  row,
  columnId,
  value,
  addMeta
) => {
  // Rank the item
  const itemRank = rankItem(row.getValue(columnId), value)

  // Store the ranking info
  addMeta(itemRank)

  // Return if the item should be filtered in/out
  return itemRank
}

export default function Table({ data, columns }: any) {
  const [advanced, setAdvanced] = useState(true)
  const rerender = useReducer(() => ({}), {})[1];
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('')
  const rtColumns = useMemo(
    () =>
      columns.map((column: any) => ({
        accessorKey: column,
        header: column,
        cell: ({ row }: any) => {
          const value = row.original[column];
          const valueFormatted = typeof (value) === "number" ? formatNumberMagnitude(value) : value;
          return (
            <p
              className={clsx("text-xs whitespace-nowrap", {
                "text-[#16A34A]": value > 0,
                "text-[#F87171]": value < 0,
                "text-[#404040]": value === 0,
              })}
            >
              {value !== 0 ? (value > 0 ? `${valueFormatted}` : `${valueFormatted}`) : valueFormatted}
            </p>
          );
        },
      })),
    []
  );

  const table = useReactTable({
    data,
    columns: rtColumns,
    state: {
      sorting,
      globalFilter,
    },
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
      className="overflow-auto max-w-full max-h-full"
    >
      <div className="flex gap-2 items-center justify-between">
        <div>
          <label htmlFor="advanced">Advanced</label>
          <input id="advanced" type="checkbox" checked={advanced} onChange={() => setAdvanced(!advanced)} />
        </div>
        {advanced && <>
          <div className="p-2">
            Search:
            <DebouncedInput
              value={globalFilter ?? ''}
              onChange={value => setGlobalFilter(String(value))}
              className="mx-1 p-2 font-lg shadow border border-block"
              placeholder="Search all columns..."
            />
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
            {table.getAllLeafColumns().map(column => {
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
              )
            })}
          </div>
        </>}
      </div>
      <table className="text-xs w-full mt-2">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="!h-10 text-left">
              {headerGroup.headers.map((header) => {
                return (
                  <th
                    className="bg-grey-800 pb-4"
                    key={header.id}
                    colSpan={header.colSpan}
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder ? null : (
                      <>
                        <div
                          {...{
                            className: clsx(
                              "font-bold uppercase text-white mb-2 tracking-normal",
                              {
                                "cursor-pointer select-none":
                                  header.column.getCanSort(),
                              }
                            ),
                            onClick: header.column.getToggleSortingHandler(),
                          }}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {{
                            asc: " 🔼",
                            desc: " 🔽",
                          }[header.column.getIsSorted() as string] ?? null}
                        </div>
                        {advanced && header.column.getCanFilter() ? (
                          <div>
                            <Filter column={header.column} table={table} />
                          </div>
                        ) : null}
                      </>
                    )}
                  </th>
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
            const row = rows[virtualRow.index]
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
      </table>
      {advanced &&
        <div className="flex items-center gap-2">
          <button
            className="border rounded p-1"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            {'<<'}
          </button>
          <button
            className="border rounded p-1"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            {'<'}
          </button>
          <button
            className="border rounded p-1"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            {'>'}
          </button>
          <button
            className="border rounded p-1"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            {'>>'}
          </button>
          <span className="flex items-center gap-1">
            <div>Page</div>
            <strong>
              {table.getState().pagination.pageIndex + 1} of{' '}
              {table.getPageCount()}
            </strong>
          </span>
          <span className="flex items-center gap-1">
            | Go to page:
            <input
              type="number"
              defaultValue={table.getState().pagination.pageIndex + 1}
              onChange={e => {
                const page = e.target.value ? Number(e.target.value) - 1 : 0
                table.setPageIndex(page)
              }}
              className="border p-1 rounded w-16"
            />
          </span>
          <select
            value={table.getState().pagination.pageSize}
            onChange={e => {
              table.setPageSize(Number(e.target.value))
            }}
          >
            {[10, 20, 30, 40, 50].map(pageSize => (
              <option key={pageSize} value={pageSize}>
                Show {pageSize}
              </option>
            ))}
          </select>
        </div>}
    </div>
  );
}


function Filter({
  column,
  table,
}: {
  column: any
  table: any
}) {
  const firstValue = table
    .getPreFilteredRowModel()
    .flatRows[0]?.getValue(column.id)

  const columnFilterValue = column.getFilterValue()

  return typeof firstValue === 'number' ? (
    <div className="flex space-x-2">
      <input
        type="number"
        value={(columnFilterValue as [number, number])?.[0] ?? ''}
        onChange={e =>
          column.setFilterValue((old: [number, number]) => [
            e.target.value,
            old?.[1],
          ])
        }
        placeholder={`Min`}
        className="w-24 border shadow rounded"
      />
      <input
        type="number"
        value={(columnFilterValue as [number, number])?.[1] ?? ''}
        onChange={e =>
          column.setFilterValue((old: [number, number]) => [
            old?.[0],
            e.target.value,
          ])
        }
        placeholder={`Max`}
        className="w-24 border shadow rounded"
      />
    </div>
  ) : (
    <input
      type="text"
      value={(columnFilterValue ?? '') as string}
      onChange={e => column.setFilterValue(e.target.value)}
      placeholder={`Search...`}
      className="w-36 border shadow rounded"
    />
  )
}

type Props = {
  value: string | number
  onChange: (value: string | number) => void
  debounce?: number
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'>


const DebouncedInput: FC<Props> = ({
  value: initialValue,
  onChange,
  debounce = 500,
  ...props
}) => {
  const [value, setValue] = useState<number | string>(initialValue)

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) =>
    setValue(event.target.value)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(value)
    }, debounce)

    return () => clearTimeout(timeout)
  }, [value])

  return <input {...props} value={value} onChange={handleInputChange} />
}
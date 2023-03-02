import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  Row,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import clsx from "clsx";
import { useMemo, useReducer, useRef, useState } from "react";
import { useVirtual } from "react-virtual";

type Data = {
  symbol: string;
  name: string;
  lastPrice: number;
  change: number;
  changePercent: number;
};

export default function Table({ data, columns }: any) {
  const rerender = useReducer(() => ({}), {})[1];

  const [sorting, setSorting] = useState<SortingState>([]);
  const rtColumns = useMemo<ColumnDef<Data>[]>(
    () =>
      columns.map((column: any) => ({ accessorKey: column, header: column })),
    /* {
          accessorKey: "symbol",
          header: "Symbol",
          cell: ({ row }) => (
            <div className="flex flex-col max-w-[137px]">
              <p className="text-[#0088CC] font-bold uppercase text-xs truncate">
                {row.original.symbol}
              </p>
              <p className="text-[#808080] text-xs whitespace-nowrap truncate">
                {row.original.name}
              </p>
            </div>
          ),
        },
        {
          accessorKey: "lastPrice",
          header: "Last Price",
        },
        {
          accessorKey: "change",
          header: "Change",
          cell: ({ row }) => {
            const value = row.original.change;
            return (
              <p
                className={clsx("text-xs whitespace-nowrap", {
                  "text-[#16A34A]": value > 0,
                  "text-[#F87171]": value < 0,
                  "text-[#404040]": value === 0,
                })}
              >
                {value !== 0 ? (value > 0 ? `+${value}` : `${value}`) : value}
              </p>
            );
          },
        },
        {
          accessorKey: "changePercent",
          header: "% Change",
          cell: ({ row }) => {
            const value = row.original.changePercent;
            return (
              <p
                className={clsx("text-xs whitespace-nowrap", {
                  "text-[#16A34A]": value > 0,
                  "text-[#F87171]": value < 0,
                  "text-[#404040]": value === 0,
                })}
              >
                {value !== 0
                  ? value > 0
                    ? `+${value}%`
                    : `${value}%`
                  : `${value}%`}
              </p>
            );
          },
        },
      ],*/
    []
  );

  const table = useReactTable({
    data,
    columns: rtColumns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
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
      <table className="text-xs">
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id} className="!h-10 text-left">
              {headerGroup.headers.map((header) => {
                return (
                  <th
                    className="bg-grey-800"
                    key={header.id}
                    colSpan={header.colSpan}
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        {...{
                          className: clsx(
                            "text-xs font-normal capitalize text-[#808080] tracking-normal",
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
          {virtualRows.map((virtualRow) => {
            const row = rows[virtualRow.index] as Row<Data>;
            return (
              <tr key={row.id} className="!h-10">
                {row.getVisibleCells().map((cell) => {
                  return (
                    <td key={cell.id} className="bg-grey-800">
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
    </div>
  );
}

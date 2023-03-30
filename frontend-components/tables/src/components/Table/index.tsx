import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from "@tanstack/react-table";
import clsx from "clsx";
import { useMemo, useRef, useState } from "react";
import { useVirtual } from "react-virtual";
import Select from "../Select";
import { formatNumberMagnitude, fuzzyFilter, isEqual } from "../../utils/utils";
import DraggableColumnHeader from "./ColumnHeader";
import Pagination from "./Pagination";
import Export from "./Export";
import Timestamp from "./Timestamp";
import FilterColumns from "./FilterColumns";
import xss from "xss";
import useLocalStorage from "../../utils/useLocalStorage";
import Toast from "../Toast";
import { MoonIcon, SunIcon } from "@radix-ui/react-icons";
import useDarkMode from "../../utils/useDarkMode";

const date = new Date();

const MAX_COLUMNS = 50;
export const DEFAULT_ROWS_PER_PAGE = 30;

function getCellWidth(row, column) {
  try {
    const indexLabel = row.hasOwnProperty("index")
      ? "index"
      : row.hasOwnProperty("Index")
      ? "Index"
      : null;
    const indexValue = indexLabel ? row[indexLabel] : null;
    const value = row[column];
    const valueType = typeof value;
    const probablyDate =
      column.toLowerCase().includes("date") ||
      column.toLowerCase() === "index" ||
      (indexValue &&
        typeof indexValue == "string" &&
        (indexValue.toLowerCase().includes("date") ||
          indexValue.toLowerCase().includes("day") ||
          indexValue.toLowerCase().includes("time") ||
          indexValue.toLowerCase().includes("timestamp") ||
          indexValue.toLowerCase().includes("year") ||
          indexValue.toLowerCase().includes("month") ||
          indexValue.toLowerCase().includes("week") ||
          indexValue.toLowerCase().includes("hour") ||
          indexValue.toLowerCase().includes("minute")));

    const probablyLink = valueType === "string" && value.startsWith("http");
    if (probablyLink) {
      return value?.toString().length ?? 0;
    }
    if (probablyDate) {
      if (typeof value === "string") {
        return value?.toString().length ?? 0;
      }
      try {
        const date = new Date(value);
        let dateFormatted = "";
        if (
          date.getUTCHours() === 0 &&
          date.getUTCMinutes() === 0 &&
          date.getUTCSeconds() === 0 &&
          date.getMilliseconds() === 0
        ) {
          dateFormatted = date.toISOString().split("T")[0];
        } else {
          dateFormatted = date.toISOString();
          dateFormatted =
            dateFormatted.split("T")[0] +
            " " +
            dateFormatted.split("T")[1].split(".")[0];
        }

        return dateFormatted?.toString().length ?? 0;
      } catch (e) {
        return value?.toString().length ?? 0;
      }
    }
    if (valueType === "number") {
      return value?.toString().length ?? 0;
    } else {
      return value?.toString().length ?? 0;
    }
  } catch (e) {
    return 0;
  }
}

export default function Table({
  data,
  columns,
  title,
  initialTheme,
}: {
  data: any[];
  columns: any[];
  title: string;
  initialTheme: "light" | "dark";
}) {
  const [colorTheme, setTheme] = useDarkMode(initialTheme);
  const [darkMode, setDarkMode] = useState(
    colorTheme === "dark" ? true : false
  );
  const toggleDarkMode = (checked: boolean) => {
    setTheme(colorTheme);
    setDarkMode(checked);
  };
  const [currentPage, setCurrentPage] = useLocalStorage(
    "rowsPerPage",
    DEFAULT_ROWS_PER_PAGE
  );
  const [advanced, setAdvanced] = useLocalStorage("advanced", false);
  const [colors, setColors] = useLocalStorage("colors", false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [fontSize, setFontSize] = useLocalStorage("fontSize", "1");
  const [open, setOpen] = useState(columns.length > MAX_COLUMNS);
  const defaultVisibleColumns = columns.reduce((acc, cur, idx) => {
    acc[cur] = idx < MAX_COLUMNS ? true : false;
    return acc;
  }, {});
  const [columnVisibility, setColumnVisibility] = useState(
    defaultVisibleColumns
  );

  const getColumnWidth = (rows, accessor, headerText) => {
    const maxWidth = 400;
    const magicSpacing = 12;
    const cellLength = Math.max(
      ...rows.map((row) => getCellWidth(row, accessor)),
      headerText.length + 8
    );
    return Math.min(maxWidth, cellLength * magicSpacing);
  };

  const rtColumns = useMemo(
    () => [
      ...columns.map((column: any, index: number) => ({
        accessorKey: column,
        id: column,
        header: column,
        size: getColumnWidth(data, column, column),
        footer: column,
        cell: ({ row }: any) => {
          const indexLabel = row.original.hasOwnProperty("index")
            ? "index"
            : row.original.hasOwnProperty("Index")
            ? "Index"
            : null;
          const indexValue = indexLabel ? row.original[indexLabel] : null;
          const value = row.original[column];
          const valueType = typeof value;
          const probablyDate =
            column.toLowerCase().includes("date") ||
            column.toLowerCase() === "index" ||
            (indexValue &&
              typeof indexValue == "string" &&
              (indexValue.toLowerCase().includes("date") ||
                indexValue.toLowerCase().includes("day") ||
                indexValue.toLowerCase().includes("time") ||
                indexValue.toLowerCase().includes("timestamp") ||
                indexValue.toLowerCase().includes("year") ||
                indexValue.toLowerCase().includes("month") ||
                indexValue.toLowerCase().includes("week") ||
                indexValue.toLowerCase().includes("hour") ||
                indexValue.toLowerCase().includes("minute")));

          const probablyLink =
            valueType === "string" && value.startsWith("http");

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
              const date = new Date(value);
              let dateFormatted = "";
              if (
                date.getUTCHours() === 0 &&
                date.getUTCMinutes() === 0 &&
                date.getUTCSeconds() === 0 &&
                date.getMilliseconds() === 0
              ) {
                dateFormatted = date.toISOString().split("T")[0];
              } else {
                dateFormatted = date.toISOString();
                dateFormatted =
                  dateFormatted.split("T")[0] +
                  " " +
                  dateFormatted.split("T")[1].split(".")[0];
              }

              return <p>{dateFormatted}</p>;
            } catch (e) {
              return <p>{value}</p>;
            }
          }
          if (valueType === "number") {
            const valueFormatted = formatNumberMagnitude(value);
            return (
              <p
                className={clsx("whitespace-nowrap", {
                  "text-black dark:text-white": !colors,
                  "text-[#16A34A]": value > 0 && colors,
                  "text-[#F87171]": value < 0 && colors,
                  "text-[#404040]": value === 0 && colors,
                })}
              >
                {value !== 0
                  ? value > 0
                    ? `${valueFormatted}`
                    : `${valueFormatted}`
                  : valueFormatted}
              </p>
            );
          } else if (valueType === "string") {
            return <div dangerouslySetInnerHTML={{ __html: xss(value) }} />;
          }
          return <p>{value}</p>;
        },
      })),
    ],
    [advanced, colors]
  );

  const [columnOrder, setColumnOrder] = useState(
    rtColumns.map((column) => column.id as string)
  );

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
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    columnResizeMode: "onChange",
    onColumnVisibilityChange: setColumnVisibility,
    onColumnOrderChange: setColumnOrder,
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    state: {
      sorting,
      globalFilter,
      columnOrder,
      columnVisibility,
    },
    initialState: {
      pagination: {
        pageIndex: 0,
        pageSize: currentPage,
      },
    },
  });

  const tableContainerRef = useRef<HTMLDivElement>(null);
  const { rows } = table.getRowModel();

  // virtualization is making a visual bug where the rows keep switching the colors, disabling it for now

  /*const rowVirtualizer = useVirtual({
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
*/

  // also disabling generating a chart for now, will come back to it later
  //const [dialog, setDialog] = useState(null);

  const visibleColumns = table.getVisibleFlatColumns();

  return (
    <>
      <Toast
        toast={{
          id: "max-columns",
          title: "Max 12 columns are visible by default",
          description:
            "You can change this by clicking on advanced and then top right 'Filter' button",
          status: "info",
        }}
        open={open}
        setOpen={setOpen}
      />

      {/*dialog && (
        <>
          <div
            onClick={() => setDialog(null)}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 backdrop-filter backdrop-blur-sm"
          />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-grey-500">
            <Chart values={dialog.values} />
          </div>
        </>
      )*/}
      <div
        ref={tableContainerRef}
        className={clsx("overflow-x-hidden h-screen")}
      >
        <div className="bg-white/70 dark:bg-grey-900/70 backdrop-filter backdrop-blur flex gap-2 px-6 items-center justify-between pt-4 ">
          <div className="flex gap-10 items-center">
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
              <div className="flex gap-[14px]">
                <input
                  id="colors"
                  type="checkbox"
                  checked={colors}
                  onChange={() => setColors(!colors)}
                />
                <label htmlFor="colors">Colors</label>
              </div>
            )}
            {/*advanced && (
              <DebouncedInput
                id="search"
                value={globalFilter ?? ""}
                onChange={(value) => setGlobalFilter(String(value))}
                placeholder="Search..."
              />
            )*/}
          </div>

          {advanced && (
            <div className="flex gap-10 items-center">
              {needsReorder && (
                <button onClick={() => resetOrder()} className="_btn h-9">
                  Reset Order
                </button>
              )}
              <button
                onClick={() => {
                  toggleDarkMode(!darkMode);
                }}
              >
                {darkMode ? (
                  <MoonIcon className="w-4 h-4" />
                ) : (
                  <SunIcon className="w-4 h-4" />
                )}
              </button>
              <Select
                labelType="row"
                value={fontSize}
                onChange={setFontSize}
                label="Font size"
                placeholder="Select font size"
                groups={[
                  {
                    label: "Font size",
                    items: [
                      {
                        label: "50%",
                        value: "0.5",
                      },
                      {
                        label: "75%",
                        value: "0.75",
                      },
                      {
                        label: "100%",
                        value: "1",
                      },
                      {
                        label: "125%",
                        value: "1.25",
                      },
                      {
                        label: "150%",
                        value: "1.5",
                      },
                      {
                        label: "175%",
                        value: "1.75",
                      },
                      {
                        label: "200%",
                        value: "2",
                      },
                    ],
                  },
                ]}
              />
              <FilterColumns table={table} label="Filter" />
            </div>
          )}
        </div>
        <div className="relative p-6 mb-20" id="table">
          <div className="absolute -inset-0.5 bg-gradient-to-r rounded-md blur-md from-[#072e49]/30 via-[#0d345f]/30 to-[#0d3362]/30"></div>
          <div
            className={
              "border border-grey-500/60 dark:border-grey-200/60 bg-white dark:bg-grey-900 rounded overflow-hidden relative z-20"
            }
          >
            <div
              className="_header relative gap-4 py-2 text-center text-xs flex items-center justify-between px-4 text-white"
              style={{
                fontSize: `${Number(fontSize) * 100}%`,
              }}
            >
              <div className="w-1/3">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="64"
                  height="40"
                  fill="none"
                  viewBox="0 0 64 40"
                >
                  <path
                    fill="#fff"
                    d="M61.283 3.965H33.608v27.757h25.699V19.826H37.561v-3.965H63.26V3.965h-1.977zM39.538 23.792h15.815v3.965H37.561v-3.965h1.977zM59.306 9.913v1.983H37.561V7.931h21.745v1.982zM33.606 0h-3.954v3.965H33.606V0zM25.7 3.966H0V15.86h25.7v3.965H3.953v11.896h25.7V3.966h-3.955zm0 21.808v1.983H7.907v-3.965h17.791v1.982zm0-15.86v1.982H3.953V7.931h21.745v1.982zM37.039 35.693v2.952l-.246-.246-.245-.245-.245-.247-.245-.246-.246-.246-.245-.245-.245-.247-.247-.246-.245-.246-.245-.246-.245-.246-.246-.246h-.49v3.936h.49v-3.198l.246.246.245.246.245.246.245.246.246.246.246.246.245.247.246.245.245.246.245.247.245.246.246.245.245.246h.245v-3.936h-.49zM44.938 37.17h-.491v-1.477h-2.944v3.937h3.93v-2.46h-.495zm-2.944-.246v-.739h1.962v.984h-1.962v-.245zm2.944.984v1.23h-2.944V37.66h2.944v.247zM52.835 37.17h-.49v-1.477h-2.946v3.937h3.925v-2.46h-.489zm-2.944-.246v-.739h1.963v.984h-1.965l.002-.245zm2.944.984v1.23H49.89V37.66h2.946v.247zM29.174 35.693H25.739v3.936H29.663v-.491H26.229v-.984h2.943v-.493H26.229v-1.476h3.434v-.492h-.489zM13.37 35.693H9.934v3.937h3.925v-3.937h-.49zm0 .738v2.709h-2.945v-2.955h2.943l.001.246zM21.276 35.693h-3.435v3.937h.491v-1.476h3.434v-2.461h-.49zm0 .738v1.23h-2.944v-1.476h2.944v.246z"
                  ></path>
                </svg>
              </div>
              <p className="font-bold w-1/3 flex flex-col gap-0.5 items-center">
                {title}
                {/* {source && (
                  <span className="font-normal text-[10px]">{`[${source}]`}</span>
                )} */}
              </p>
              <p className="w-1/3 text-right text-xs">
                {new Intl.DateTimeFormat("en-GB", {
                  dateStyle: "full",
                  timeStyle: "long",
                })
                  .format(date)
                  .replace(/:\d\d /, " ")}
              </p>
              {/* {source && typeof source === "string" && source.includes("*") && (
                <p className="text-[8px] absolute bottom-0 right-4">
                  *not affiliated
                </p>
              )} */}
            </div>
            <div className="overflow-x-auto">
              <table
                className="text-sm"
                style={{
                  fontSize: `${Number(fontSize) * 100}%`,
                }}
                /*style={{
        width: table.getCenterTotalSize(),
      }}*/
              >
                <thead>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <tr
                      key={headerGroup.id}
                      className={clsx("!h-10 text-left")}
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
                  {/*paddingTop > 0 && (
                    <tr>
                      <td style={{ height: `${paddingTop}px` }}></td>
                    </tr>
                  )*/}
                  {table.getRowModel().rows.map((row, idx) => {
                    //const row = rows[virtualRow.index];
                    return (
                      <tr
                        key={row.id}
                        className="!h-[64px] border-b border-grey-400"
                      >
                        {row.getVisibleCells().map((cell) => {
                          return (
                            <td
                              key={cell.id}
                              className={clsx(
                                "whitespace-nowrap overflow-auto p-4",
                                {
                                  "bg-grey-100 dark:bg-grey-850": idx % 2 === 0,
                                  "bg-grey-200 dark:bg-[#202020]":
                                    idx % 2 === 1,
                                }
                              )}
                              style={{
                                width: cell.column.getSize(),
                              }}
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
                  {/*paddingBottom > 0 && (
                    <tr>
                      <td style={{ height: `${paddingBottom}px` }} />
                    </tr>
                  )*/}
                </tbody>
                {rows.length > 30 && visibleColumns.length > 4 && (
                  <tfoot>
                    {table.getFooterGroups().map((footerGroup) => (
                      <tr key={footerGroup.id}>
                        {footerGroup.headers.map((header) => (
                          <th
                            key={header.id}
                            colSpan={header.colSpan}
                            className="text-grey-500 bg-grey-100 dark:bg-grey-850 font-normal text-left text-sm h-10 p-4"
                            style={{
                              width: header.getSize(),
                            }}
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
                )}
              </table>
            </div>
          </div>
        </div>
        <div className="fixed bg-white/70 dark:bg-grey-900/70 backdrop-filter backdrop-blur z-20 bottom-0 left-0 w-full flex gap-10 justify-between py-4 px-6">
          <Export columns={columns} data={data} />
          <div className="flex items-center gap-10">
            <Pagination
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              table={table}
            />
            <Timestamp />
          </div>
          {/*
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
          </button>*/}
        </div>
      </div>
    </>
  );
}

/* {
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
            },*/

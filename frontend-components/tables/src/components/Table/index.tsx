import * as DialogPrimitive from "@radix-ui/react-dialog";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  Column,
  Row,
} from "@tanstack/react-table";
import clsx from "clsx";
import { useEffect, useMemo, useRef, useState } from "react";
import xss from "xss";
import useDarkMode from "../../utils/useDarkMode";
import useLocalStorage from "../../utils/useLocalStorage";
import {
  formatNumber,
  formatNumberMagnitude,
  formatNumberNoMagnitude,
  fuzzyFilter,
  includesDateNames,
  includesPriceNames,
  isEqual,
} from "../../utils/utils";
import CloseIcon from "../Icons/Close";
import Select from "../Select";
import Toast from "../Toast";
import DraggableColumnHeader, {
  isoYearRegex,
  magnitudeRegex,
} from "./ColumnHeader";
import DownloadFinishedDialog from "./DownloadFinishedDialog";
import Export from "./Export";
import FilterColumns from "./FilterColumns";
import Pagination, { validatePageSize } from "./Pagination";

const date = new Date();

const MAX_COLUMNS = 50;
export const DEFAULT_ROWS_PER_PAGE = 30;

//@ts-ignore
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
    const only_numbers = value?.toString().replace(/[^0-9]/g, "");

    const probablyDate =
      only_numbers?.length >= 4 &&
      (includesDateNames(column) ||
        column.toLowerCase() === "index" ||
        (indexValue &&
          typeof indexValue === "string" &&
          (indexValue.toLowerCase().includes("date") ||
            indexValue.toLowerCase().includes("day") ||
            indexValue.toLowerCase().includes("time") ||
            indexValue.toLowerCase().includes("timestamp") ||
            indexValue.toLowerCase().includes("year") ||
            indexValue.toLowerCase().includes("month") ||
            indexValue.toLowerCase().includes("week") ||
            indexValue.toLowerCase().includes("hour") ||
            indexValue.toLowerCase().includes("minute"))));

    const probablyLink = valueType === "string" && value.startsWith("http");

    if (probablyLink || !probablyDate) {
      return value?.toString().length ?? 0;
    }
    if (
      probablyDate &&
      !isNaN(new Date(value).getTime()) &&
      !isoYearRegex.test(value?.toString())
    ) {
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
          dateFormatted = `${dateFormatted.split("T")[0]} ${
            dateFormatted.split("T")[1].split(".")[0]
          }`;
        }

        return dateFormatted?.toString().length ?? 0;
      } catch (e) {
        return value?.toString().length ?? 0;
      }
    }

    return value?.toString().length ?? 0;
  } catch (e) {
    return 0;
  }
}

export const EXPORT_TYPES = ["csv", "xlsx", "png"];
export default function Table({
  data,
  columns,
  title,
  initialTheme,
  cmd = "",
}: {
  data: any[];
  columns: any[];
  title: string;
  initialTheme: "light" | "dark";
  cmd?: string;
}) {
  const [type, setType] = useLocalStorage("exportType", EXPORT_TYPES[0]);
  const [downloadFinished, setDownloadFinished] = useState(false);
  const [colorTheme, setTheme] = useDarkMode(initialTheme);
  const [darkMode, setDarkMode] = useState(
    colorTheme === "dark" ? true : false,
  );
  const toggleDarkMode = (checked: boolean) => {
    //@ts-ignore
    setTheme(colorTheme);
    setDarkMode(checked);
  };

  const [currentPage, setCurrentPage] = useLocalStorage(
    "rowsPerPage",
    DEFAULT_ROWS_PER_PAGE,
    validatePageSize,
  );
  const [advanced, setAdvanced] = useLocalStorage("advanced", false);
  const [colors, setColors] = useLocalStorage("colors", false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [fontSize, setFontSize] = useLocalStorage("fontSize", "1");
  const [open, setOpen] = useState(false);
  const defaultVisibleColumns = columns.reduce((acc, cur, idx) => {
    acc[cur] = idx < MAX_COLUMNS ? true : false;
    return acc;
  }, {});
  const [columnVisibility, setColumnVisibility] = useState(
    defaultVisibleColumns,
  );

  //@ts-ignore
  const getColumnWidth = (rows, accessor, headerText) => {
    const maxWidth = 200;
    const magicSpacing = 12;
    const cellLength = Math.max(
      //@ts-ignore
      ...rows.map((row) => getCellWidth(row, accessor)),
      headerText?.length ? headerText?.length + 8 : 0,
    );
    return Math.min(maxWidth, cellLength * magicSpacing);
  };

  const rtColumns = useMemo(
    () => [
      ...columns.map((column: any, index: number) => ({
        accessorKey: column,
        accessorFn: (row: any) => {
          const indexLabel = row.hasOwnProperty("index")
            ? "index"
            : row.hasOwnProperty("Index")
            ? "Index"
            : columns[0];
          const indexValue = indexLabel ? row[indexLabel] : null;
          const value = row[column];
          const only_numbers =
            value?.toString()?.split(".")?.[0]?.replace(/[^0-9]/g, "") ?? "";
          const probablyDate =
            only_numbers?.length >= 4 &&
            (includesDateNames(column) ||
              column.toLowerCase() === "index" ||
              (indexValue &&
                typeof indexValue === "string" &&
                (indexValue.toLowerCase().includes("date") ||
                  indexValue.toLowerCase().includes("time") ||
                  indexValue.toLowerCase().includes("timestamp") ||
                  indexValue.toLowerCase().includes("year") ||
                  indexValue.toLowerCase().includes("month") ||
                  indexValue.toLowerCase().includes("week") ||
                  indexValue.toLowerCase().includes("hour") ||
                  indexValue.toLowerCase().includes("minute"))));

          if (
            probablyDate &&
            value?.length === 4 &&
            isoYearRegex.test(value?.toString())
          )
            return value;

          if (probablyDate) {
            if (typeof value === "number") return value;
            return new Date(value).getTime();
          }
          return value;
        },
        id: column,
        header: column,
        size: getColumnWidth(data, column, column),
        footer: column,
        cell: ({ row }: any) => {
          const indexLabel = row.original.hasOwnProperty("index")
            ? "index"
            : row.original.hasOwnProperty("Index")
            ? "Index"
            : columns[0];
          const indexValue = indexLabel ? row.original[indexLabel] : null;
          const value = row.original[column];
          const valueType = typeof value;
          const only_numbers =
            value?.toString()?.split(".")?.[0]?.replace(/[^0-9]/g, "") ?? "";
          const probablyDate =
            only_numbers?.length >= 4 &&
            (includesDateNames(column) ||
              column.toLowerCase() === "index" ||
              (indexValue &&
                typeof indexValue === "string" &&
                (indexValue.toLowerCase().includes("date") ||
                  indexValue.toLowerCase().includes("time") ||
                  indexValue.toLowerCase().includes("timestamp") ||
                  indexValue.toLowerCase().includes("year"))));

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
                {value?.length > 25 ? `${value.substring(0, 25)}...` : value}
              </a>
            );
          }

          if (
            probablyDate &&
            value?.length === 4 &&
            isoYearRegex.test(value?.toString())
          ) {
            return <p>{value}</p>;
          }
          if (probablyDate && !isNaN(new Date(value).getTime())) {
            if (typeof value === "string") {
              const date = value.split("T")[0];
              const time = value.split("T")[1]?.split(".")[0];
              if (time === "00:00:00") {
                return <p>{date}</p>;
              }
              return (
                <p>
                  {date} {time}
                </p>
              );
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
                dateFormatted = `${dateFormatted.split("T")[0]} ${
                  dateFormatted.split("T")[1].split(".")[0]
                }`;
              }

              return <p>{dateFormatted}</p>;
            } catch (e) {
              return <p>{value}</p>;
            }
          }
          if (
            valueType === "number" ||
            magnitudeRegex.test(value?.toString())
          ) {
            let valueFormatted = formatNumberMagnitude(value, column);
            const valueFormattedNoMagnitude = Number(
              formatNumberNoMagnitude(value),
            );

            if (
              typeof indexValue === "string" &&
              includesPriceNames(indexValue)
            ) {
              valueFormatted = Number(formatNumberNoMagnitude(value));
              const maxFixed = valueFormatted < 2 ? 4 : 2;
              valueFormatted = valueFormatted.toLocaleString("en-US", {
                maximumFractionDigits: maxFixed,
                minimumFractionDigits: 2,
              });
            }

            return (
              <p
                className={clsx("whitespace-nowrap", {
                  "text-black dark:text-white": !colors,
                  "text-[#16A34A]": valueFormattedNoMagnitude > 0 && colors,
                  "text-[#F87171]": valueFormattedNoMagnitude < 0 && colors,
                  "text-[#404040]": valueFormattedNoMagnitude === 0 && colors,
                })}
                title={formatNumber(value).toString() ?? ""}
              >
                {valueFormattedNoMagnitude !== 0
                  ? valueFormattedNoMagnitude > 0
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
    [advanced, colors],
  );

  const [lockFirstColumn, setLockFirstColumn] = useState(false);

  const [columnOrder, setColumnOrder] = useState(
    rtColumns.map((column) => column.id as string),
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
        pageSize:
          typeof currentPage === "string"
            ? currentPage.includes("All")
              ? data?.length
              : parseInt(currentPage)
            : currentPage,
      },
    },
  });

  const tableContainerRef = useRef<HTMLDivElement>(null);
  const { rows } = table.getRowModel();
  const visibleColumns = table.getVisibleFlatColumns();

  const [downloadFinishedDialogOpen, setDownloadFinishedDialogOpen] =
    useState(false);

  useEffect(() => {
    if (downloadFinished) {
      setDownloadFinished(false);
      setDownloadFinishedDialogOpen(true);
    }
  }, [downloadFinished]);

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
      <DownloadFinishedDialog
        open={downloadFinishedDialogOpen}
        close={() => setDownloadFinishedDialogOpen(false)}
      />

      <div
        ref={tableContainerRef}
        className={clsx("overflow-x-hidden h-screen")}
      >
        <div className="relative p-4" id="table">
          <div className="absolute -inset-0.5 bg-gradient-to-r rounded-md blur-md from-[#072e49]/30 via-[#0d345f]/30 to-[#0d3362]/30" />
          <div
            className={
              "border border-grey-500/60 dark:border-grey-200/60 bg-white dark:bg-grey-900 rounded overflow-hidden relative z-20"
            }
          >
            <div
              className="_header relative gap-4 py-2 text-center text-xs flex items-center justify-between px-4 text-white"
              style={{
                fontSize: `${Number(fontSize) * 90}%`,
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
                  />
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
                <br />
                <span className="text-grey-400">{cmd}</span>
              </p>
              {/* {source && typeof source === "string" && source.includes("*") && (
                <p className="text-[8px] absolute bottom-0 right-4">
                  *not affiliated
                </p>
              )} */}
            </div>
            <div className="overflow-auto max-h-[calc(100vh-170px)] smh:max-h-[calc(100vh-95px)]">
              <table className="text-sm relative">
                <thead
                  className="sticky top-0 bg-white dark:bg-grey-900"
                  style={{
                    fontSize: `${Number(fontSize) * 100}%`,
                  }}
                >
                  {table.getHeaderGroups().map((headerGroup, idx) => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map((header, idx2) => {
                        return (
                          <DraggableColumnHeader
                            setLockFirstColumn={setLockFirstColumn}
                            lockFirstColumn={lockFirstColumn}
                            idx={idx2}
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
                  {table.getRowModel().rows.map((row, idx) => {
                    return (
                      <tr
                        key={row.id}
                        className="!h-[64px] border-b border-grey-400"
                        style={{
                          fontSize: `${Number(fontSize) * 100}%`,
                        }}
                      >
                        {row.getVisibleCells().map((cell, idx2) => {
                          return (
                            <td
                              key={cell.id}
                              className={clsx(
                                "whitespace-normal p-4 text-black dark:text-white",
                                {
                                  "bg-white dark:bg-grey-850": idx % 2 === 0,
                                  "bg-grey-100 dark:bg-[#202020]":
                                    idx % 2 === 1,
                                  "sticky left-0 z-10":
                                    idx2 === 0 && lockFirstColumn,
                                },
                              )}
                              style={{
                                width: cell.column.getSize(),
                              }}
                            >
                              {flexRender(
                                cell.column.columnDef.cell,
                                cell.getContext(),
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
                {rows?.length > 30 && visibleColumns?.length > 4 && (
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
                              fontSize: `${Number(fontSize) * 100}%`,
                            }}
                          >
                            {header.isPlaceholder
                              ? null
                              : flexRender(
                                  header.column.columnDef.footer,
                                  header.getContext(),
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
        <div className="smh:hidden flex max-h-[68px] overflow-x-auto bg-white/70 dark:bg-grey-900/70 backdrop-filter backdrop-blur z-20 bottom-0 left-0 w-full gap-10 justify-between py-4 px-4 text-sm">
          <div className="flex items-center gap-10">
            <DialogPrimitive.Root>
              <DialogPrimitive.Trigger className="_btn">
                Settings
              </DialogPrimitive.Trigger>
              <DialogPrimitive.Portal>
                <DialogPrimitive.Overlay className="_modal-overlay" />
                <DialogPrimitive.Content className="_modal">
                  <DialogPrimitive.Close className="absolute top-[40px] right-[46px] text-grey-200 hover:text-white rounded-[4px] focus:outline focus:outline-2 focus:outline-grey-500">
                    <CloseIcon className="w-6 h-6" />
                  </DialogPrimitive.Close>
                  <DialogPrimitive.Title className="uppercase font-bold tracking-widest">
                    Settings
                  </DialogPrimitive.Title>
                  <div className="grid grid-cols-2 gap-2 mt-10 text-sm">
                    {needsReorder && (
                      <button onClick={() => resetOrder()} className="_btn h-9">
                        Reset Order
                      </button>
                    )}
                    <Select
                      labelType="row"
                      value={!darkMode ? "dark" : "light"}
                      onChange={(value) => {
                        toggleDarkMode(value !== "dark");
                      }}
                      label="Theme"
                      placeholder="Select theme"
                      groups={[
                        {
                          label: "Theme",
                          items: [
                            {
                              label: "Dark",
                              value: "dark",
                            },
                            {
                              label: "Light",
                              value: "light",
                            },
                          ],
                        },
                      ]}
                    />
                    <Select
                      labelType="row"
                      value={type}
                      onChange={(value) => {
                        setType(value);
                      }}
                      label="Export type"
                      placeholder="Select export type"
                      groups={[
                        {
                          label: "Export type",
                          items: EXPORT_TYPES.map((type) => ({
                            label: type,
                            value: type,
                          })),
                        },
                      ]}
                    />
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
                    <div className="flex gap-2 items-center">
                      <Select
                        labelType="row"
                        value={advanced ? "advanced" : "simple"}
                        onChange={(value) => {
                          setAdvanced(value === "advanced");
                        }}
                        label="Type"
                        placeholder="Select type"
                        groups={[
                          {
                            label: "Type",
                            items: [
                              {
                                label: "Simple",
                                value: "simple",
                              },
                              {
                                label: "Advanced",
                                value: "advanced",
                              },
                            ],
                          },
                        ]}
                      />
                    </div>
                    <div className="flex gap-2 items-center">
                      <label htmlFor="colors">Colors</label>
                      <input
                        id="colors"
                        type="checkbox"
                        checked={colors}
                        onChange={() => setColors(!colors)}
                      />
                    </div>
                  </div>
                </DialogPrimitive.Content>
              </DialogPrimitive.Portal>
            </DialogPrimitive.Root>
            <FilterColumns onlyIconTrigger table={table} label="" />
          </div>
          <Pagination
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            table={table}
          />
          <Export
            setType={setType}
            type={type}
            columns={columns}
            data={data}
            downloadFinished={setDownloadFinished}
          />
        </div>
      </div>
    </>
  );
}

import { flexRender } from "@tanstack/react-table";
import clsx from "clsx";
import { FC } from "react";
import { formatNumberMagnitude, includesDateNames } from "../../utils/utils";
import { useDrag, useDrop } from "react-dnd";
import * as ContextMenuPrimitive from "@radix-ui/react-context-menu";

export const magnitudeRegex = new RegExp("^([0-9]+)(\\s)([kKmMbBtT])$");

function Filter({
  column,
  table,
  numberOfColumns,
}: {
  column: any;
  table: any;
  numberOfColumns: number;
}) {
  const values = table
    .getPreFilteredRowModel()
    .flatRows.map((row: { getValue: (arg0: any) => any }) =>
      row.getValue(column.id)
    );

  const areAllValuesString = values.every(
    (value: null) => typeof value === "string" || value === null
  );

  const areAllValuesNumber = values.every(
    (value: null | number | string) =>
      typeof value === "number" ||
      magnitudeRegex.test(value as string) ||
      value === null ||
      value === ""
  );

  const valuesContainStringWithSpaces = values.some(
    (value: string | string[]) =>
      typeof value === "string" && value.includes(" ")
  );

  const columnFilterValue = column.getFilterValue();

  const isProbablyDate = values.every((value: string) => {
    if (typeof value !== "string") return false;
    const only_numbers = value?.replace(/[^0-9]/g, "").trim();
    return (
      only_numbers?.length >= 4 &&
      (includesDateNames(column.id) ||
        (column.id.toLowerCase() === "index" && !valuesContainStringWithSpaces))
    );
  });

  if (isProbablyDate) {
    function getTime(value: string | number | Date) {
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
      <div className="flex gap-2 h-10">
        <input
          type="datetime-local"
          value={getTime((columnFilterValue as [string, string])?.[0]) ?? ""}
          onChange={(e) => {
            const value = new Date(e.target.value).getTime();
            column.setFilterValue((old: [string, string]) => [value, old?.[1]]);
          }}
          placeholder={`Start date`}
          className="_input"
        />
        <input
          type="datetime-local"
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

  if (areAllValuesNumber) {
    return (
      <div className="flex gap-0.5 h-10">
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
          className="_input p-0.5"
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
          className="_input p-0.5"
        />
      </div>
    );
  }
  if (areAllValuesString) {
    return (
      <div className="h-10">
        <input
          type="text"
          value={(columnFilterValue ?? "") as string}
          onChange={(e) => column.setFilterValue(e.target.value)}
          placeholder={`Search...`}
          className="_input"
        />
      </div>
    );
  }
  return <div className="h-10"></div>;
}

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
  idx: number;
  lockFirstColumn: boolean;
  setLockFirstColumn: (value: boolean) => void;
}> = ({
  header,
  table,
  advanced,
  idx,
  lockFirstColumn,
  setLockFirstColumn,
}) => {
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

  const renderField = () => (
    <div ref={previewRef} className="flex gap-1 flex-col">
      {header.isPlaceholder ? null : (
        <>
          <div className="font-bold uppercase text-grey-700 dark:text-white tracking-widest flex gap-2 whitespace-nowrap justify-between">
            <div
              onClick={column.getToggleSortingHandler()}
              className={clsx("flex gap-1", {
                "cursor-pointer select-none": column.getCanSort(),
              })}
            >
              {flexRender(column.columnDef.header, header.getContext())}
              {column.getCanSort() && (
                <div className="flex flex-col gap-0.5 items-center justify-center">
                  <button
                    className={clsx({
                      "text-[#669DCB]": column.getIsSorted() === "asc",
                      "text-grey-600": column.getIsSorted() !== "asc",
                    })}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="8"
                      height="4"
                      fill="none"
                      viewBox="0 0 11 5"
                    >
                      <path fill="currentColor" d="M10.333 5l-5-5-5 5"></path>
                    </svg>
                  </button>
                  <button
                    className={clsx({
                      "text-[#669DCB]": header.column.getIsSorted() === "desc",
                      "text-grey-600": header.column.getIsSorted() !== "desc",
                    })}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="8"
                      height="4"
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
              <button
                ref={dragRef}
                className="text-grey-600 hover:text-grey-800 dark:hover:text-white"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="17"
                  height="16"
                  fill="none"
                  viewBox="0 0 17 16"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.667 6l-2 2 2 2M6.333 3.333l2-2 2 2M10.333 12.667l-2 2-2-2M13 6l2 2-2 2M1.667 8H15M8.333 1.333v13.334"
                  ></path>
                </svg>
              </button>
            )}
          </div>
          {advanced && column.getCanFilter() ? (
            <div>
              <Filter
                column={column}
                table={table}
                numberOfColumns={columnOrder?.length ?? 0}
              />
            </div>
          ) : null}
        </>
      )}
    </div>
  );

  return (
    <th
      className={clsx("h-[70px] p-4 sticky", {
        "left-0 z-50 bg-white dark:bg-grey-900": idx === 0 && lockFirstColumn,
      })}
      colSpan={header.colSpan}
      style={{ width: header.getSize(), opacity: isDragging ? 0.5 : 1 }}
      ref={dropRef}
    >
      {idx === 0 ? (
        <ContextMenuPrimitive.Root>
          <ContextMenuPrimitive.Trigger asChild>
            {renderField()}
          </ContextMenuPrimitive.Trigger>
          <ContextMenuPrimitive.Portal>
            <ContextMenuPrimitive.Content className="bg-white text-black dark:text-white dark:bg-grey-900 border border-grey-200 dark:border-grey-800 rounded-md shadow-lg p-2 z-50 text-xs">
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => {
                    setLockFirstColumn(!lockFirstColumn);
                  }}
                  className="hover:bg-grey-300 dark:hover:bg-grey-800 rounded-md p-2"
                >
                  {lockFirstColumn ? "Unlock" : "Lock"} first column
                </button>
              </div>
            </ContextMenuPrimitive.Content>
          </ContextMenuPrimitive.Portal>
        </ContextMenuPrimitive.Root>
      ) : (
        renderField()
      )}
      <button
        className="resizer bg-grey-300/20 dark:hover:bg-white absolute top-0 right-0 w-0.5 h-full"
        onMouseDown={header.getResizeHandler()}
        onTouchStart={header.getResizeHandler()}
      ></button>
    </th>
  );
};

export default DraggableColumnHeader;

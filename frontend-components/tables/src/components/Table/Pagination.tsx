import clsx from "clsx";
import { useState } from "react";
import { DEFAULT_ROWS_PER_PAGE } from ".";
import useLocalStorage from "../../utils/useLocalStorage";
import Select from "../Select";

export default function Pagination({ table }: { table: any }) {
  const [currentPage, setCurrentPage] = useLocalStorage(
    "rowsPerPage",
    DEFAULT_ROWS_PER_PAGE
  );
  const totalRows = table.getFilteredRowModel().rows.length;

  return (
    <div className="flex items-center gap-8">
      <Select
        value={currentPage}
        onChange={(value) => {
          setCurrentPage(value);
          if (value === `All (${totalRows})`) table.setPageSize(totalRows);
          else table.setPageSize(value);
        }}
        labelType="row"
        label="Rows per page"
        placeholder="Select rows per page"
        groups={[
          {
            label: "Rows per page", // TODO: generate number automatically
            items: [10, 20, 30, 40, 50, `All (${totalRows})`].map(
              (pageSize) => ({
                label: `${pageSize}`,
                value: pageSize,
              })
            ),
          },
        ]}
      />
      <span className="flex items-center gap-1">
        <strong>{table.getState().pagination.pageIndex + 1}</strong>
        of
        <strong>{table.getPageCount()}</strong>
      </span>
      {/*<span className="flex items-center gap-1">
          | Go to page:
          <input
            type="number"
            defaultValue={table.getState().pagination.pageIndex + 1}
            onChange={(e) => {
              const page = e.target.value ? Number(e.target.value) - 1 : 0;
              table.setPageIndex(page);
            }}
            className="_input"
          />
          </span>*/}
      <div>
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
      </div>
    </div>
  );
}

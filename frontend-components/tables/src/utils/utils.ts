import { rankItem } from "@tanstack/match-sorter-utils";
import domtoimage from "dom-to-image";
import { utils, writeFile } from "xlsx";

export function formatNumberMagnitude(number: number) {
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

export function isEqual(a: any, b: any) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length !== b.length) return false;

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

export const fuzzyFilter = (
  row: any,
  columnId: string,
  value: string,
  addMeta: any
): any => {
  const itemRank = rankItem(row.getValue(columnId), value);
  addMeta(itemRank);
  return itemRank;
};

export const saveToFile = (blob: Blob, fileName: string) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", fileName);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadData = (type: "csv" | "xlsx", columns: any, data: any) => {
  const headers = columns;
  const rows = data.map((row: any) =>
    headers.map((column: any) => row[column])
  );
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

export const downloadImage = (id: string) => {
  const table = document.getElementById(id);
  domtoimage.toBlob(table).then(function (blob) {
    saveToFile(blob, `${window.title}.png`);
  });
};

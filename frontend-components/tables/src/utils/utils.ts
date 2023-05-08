import { rankItem } from "@tanstack/match-sorter-utils";
import domtoimage from "dom-to-image";
import { utils, writeFile } from "xlsx";

export function formatNumberMagnitude(number: number) {
  if (number % 1 !== 0) {
    const decimalPlaces = Math.max(2, number.toString().split(".")[1].length);
    const toFixed = Math.min(4, decimalPlaces);
    if (number < 1000) {
      return number.toFixed(toFixed) || 0;
    }
  }

  if (number > 1000) {
    const magnitude = Math.min(4, Math.floor(Math.log10(Math.abs(number)) / 3));
    const suffix = ["", "K", "M", "B", "T"][magnitude];
    const formatted = (number / 10 ** (magnitude * 3)).toFixed(2);
    return `${formatted} ${suffix}`;
  }

  return number;
}

export function includesDateNames(column: string) {
  return ["date", "day", "time", "timestamp", "year"].some((dateName) =>
    column.toLowerCase().includes(dateName)
  );
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

const exportNativeFileSystem = async ({
  fileHandle,
  blob,
}: {
  fileHandle?: FileSystemFileHandle | null;
  blob: Blob;
}) => {
  if (!fileHandle) {
    throw new Error("Cannot access filesystem");
  }

  await writeFileHandler({ fileHandle, blob });
};

const writeFileHandler = async ({
  fileHandle,
  blob,
}: {
  fileHandle: FileSystemFileHandle;
  blob: Blob;
}) => {
  const writer = await fileHandle.createWritable();
  await writer.write(blob);
  await writer.close();
};

const IMAGE_TYPE: FilePickerAcceptType[] = [
  {
    description: "PNG Image",
    accept: {
      "image/png": [".png"],
    },
  },
  {
    description: "JPEG Image",
    accept: {
      "image/jpeg": [".jpeg"],
    },
  },
];

const getNewFileHandle = ({
  filename,
  is_image,
}: {
  filename: string;
  is_image?: boolean;
}): Promise<FileSystemFileHandle | null> => {
  if ("showSaveFilePicker" in window) {
    const opts: SaveFilePickerOptions = {
      suggestedName: filename,
      types: is_image
        ? IMAGE_TYPE
        : [
            {
              description: "CSV File",
              accept: {
                "image/csv": [".csv"],
              },
            },
          ],
      excludeAcceptAllOption: true,
    };

    return showSaveFilePicker(opts);
  }

  return new Promise((resolve) => {
    resolve(null);
  });
};

export const saveToFile = (
  blob: Blob,
  fileName: string,
  fileHandle?: FileSystemFileHandle
) => {
  try {
    exportNativeFileSystem({ fileHandle, blob });
  } catch (error) {
    console.error("oops, something went wrong!", error);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
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
    const filename = `${window.title}.csv`;

    getNewFileHandle({
      filename: filename,
    }).then((fileHandle) => {
      // @ts-ignore
      saveToFile(blob, filename, fileHandle);
    });
    return;
  }

  const wb = utils.book_new();
  const ws = utils.aoa_to_sheet(csvData);
  utils.book_append_sheet(wb, ws, "Sheet1");
  writeFile(wb, `${window.title}.xlsx`);
};

export const downloadImage = (id: string) => {
  const table = document.getElementById(id);
  const filename = `${window.title}.png`;
  getNewFileHandle({
    filename: filename,
    is_image: true,
  }).then((fileHandle) => {
    // @ts-ignore
    domtoimage.toBlob(table).then(function (blob) {
      // @ts-ignore
      saveToFile(blob, filename, fileHandle);
    });
  });
};

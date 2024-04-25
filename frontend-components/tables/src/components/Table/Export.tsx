import { useState } from "react";
import { downloadData, downloadImage } from "../../utils/utils";
import * as RadioGroup from "@radix-ui/react-radio-group";
import useLocalStorage from "../../utils/useLocalStorage";
import { EXPORT_TYPES } from ".";
import Select from "../Select";

export default function Export({
  columns,
  data,
  type,
  setType,
  downloadFinished,
}: {
  columns: any;
  data: any;
  type: any;
  setType: any;
  downloadFinished: (change: boolean) => void;
}) {
  const onExport = () => {
    switch (type) {
      case "csv":
        downloadData("csv", columns, data, downloadFinished);
        break;
      case "xlsx":
        downloadData("xlsx", columns, data, downloadFinished);
        break;
      case "png":
        downloadImage("table", downloadFinished);
        break;
    }
  };
  return (
    <div className="flex gap-2 items-center">
      <Select
        labelType="row"
        value={type}
        onChange={(value) => {
          setType(value);
        }}
        label="Type"
        placeholder="Select type"
        groups={[
          {
            label: "Type",
            items: EXPORT_TYPES.map((type) => ({
              label: type,
              value: type,
            })),
          },
        ]}
      />
      <button onClick={onExport} className="_btn">
        Export
      </button>
    </div>
  );
}

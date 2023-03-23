import { useState } from "react";
import { downloadData, downloadImage } from "../../utils/utils";
import * as RadioGroup from "@radix-ui/react-radio-group";
import useLocalStorage from "../../utils/useLocalStorage";
const types = ["csv", "xlsx", "png"];

export default function Export({ columns, data }: { columns: any; data: any }) {
  const [type, setType] = useLocalStorage("exportType", types[0]);

  const onExport = () => {
    switch (type) {
      case "csv":
        downloadData("csv", columns, data);
        break;
      case "xlsx":
        downloadData("xlsx", columns, data);
        break;
      case "png":
        downloadImage("table");
        break;
    }
  };
  return (
    <div className="flex gap-6 items-center">
      <p>Export:</p>
      <RadioGroup.Root
        onValueChange={setType}
        defaultValue={type}
        className="flex gap-4"
        aria-label={"Export"}
      >
        {types.map((key) => (
          <div key={key} className="flex items-center gap-2 cursor-pointer">
            <RadioGroup.Item
              className="bg-black border-white border-2 w-5 h-5 rounded-full outline-none"
              value={key}
              id={key}
            >
              <RadioGroup.Indicator className="flex items-center justify-center w-full h-full relative after:content-[''] after:block after:w-[11px] after:h-[11px] after:rounded-[50%] after:bg-white" />
            </RadioGroup.Item>
            <label
              className="text-white text-sm leading-none uppercase"
              htmlFor={key}
            >
              {key}
            </label>
          </div>
        ))}
      </RadioGroup.Root>
      <button onClick={onExport} className="_btn">
        Export
      </button>
    </div>
  );
}

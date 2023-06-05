//@ts-nocheck
import { useEffect, useState } from "react";
import Table from "./components/Table";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import {
  cryptoData,
  incomeData,
  longIncomeData,
  performanceData,
} from "./data/mockup";

declare global {
  [(Exposed = Window), SecureContext];
  interface Window {
    json_data: any;
    title: string;
    download_path: string;
    pywry: any;
  }
}

function App() {
  const [data, setData] = useState(
    process.env.NODE_ENV === "production" ? null : JSON.parse(cryptoData)
  );
  const [title, setTitle] = useState("Interactive Table");
  // const [source, setSource] = useState("");

  if (process.env.NODE_ENV === "production") {
    useEffect(() => {
      const interval = setInterval(() => {
        if (window.json_data) {
          const data = JSON.parse(window.json_data);
          console.log(data);
          setData(data);
          if (data.title && typeof data.title === "string") {
            setTitle(data.title);
          }
          // if (data.source && typeof data.source === "string") {
          //   setSource(data.source);
          // }
          clearInterval(interval);
        }
      }, 100);
      return () => clearInterval(interval);
    }, []);
  }

  const transformData = (data: any) => {
    if (!data) return null;

    const filename = data.title?.replace(/<b>|<\/b>/g, "").replace(/ /g, "_");
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const time = new Date().toISOString().slice(11, 19).replace(/:/g, "");
    window.title = `openbb_${filename}_${date}_${time}`;

    const columns = data.columns;
    const index = data.index;
    const newData = data.data;
    const transformedData = newData.map((row: any, index: number) => {
      const transformedRow = {};
      row.forEach((value: any, index: number) => {
        //@ts-ignore
        transformedRow[columns[index]] = value ? value : value === 0 ? 0 : "";
      });
      return transformedRow;
    });
    return {
      columns,
      data: transformedData,
    };
  };

  const transformedData = transformData(data);

  return (
    <div className="relative h-full bg-white dark:bg-black text-black dark:text-white">
      <DndProvider backend={HTML5Backend}>
        {transformedData && (
          <Table
            // source={source}
            title={title}
            data={transformedData.data}
            columns={transformedData.columns}
            initialTheme={
              data.theme &&
              typeof data.theme === "string" &&
              data.theme === "dark"
                ? "dark"
                : "light"
            }
            cmd={data?.command_location ?? ""}
          />
        )}
      </DndProvider>
    </div>
  );
}

export default App;

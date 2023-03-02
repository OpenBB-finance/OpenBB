//@ts-nocheck
import { useEffect, useState } from "react";
import Table from "./components/Table";

const initialData = `{"columns":["Symbol","Name","Volume [$]","Market Cap","Market Cap Rank","7D Change [%]","24H Change [%]"],"index":[9,8,7,6,5,4,3,2,1,0],"data":[["matic","Polygon",487054135,10832041871,10,-14.3323903999,-2.9677182818],["doge","Dogecoin",292736178,11116247356,9,-6.0637573097,-2.1958656896],["ada","Cardano",241919093,12174316846,8,-10.5683442051,-3.9165127851],["okb","OKB",52096829,12290634852,7,-4.8276398627,-2.6583191451],["xrp","XRP",944570004,19197674600,6,-4.8056681632,-1.4419913323],["usdc","USD Coin",3369974783,43047984937,5,0.0005749401,-0.0587269814],["bnb","BNB",465652231,46975107428,4,-4.7958076661,-1.695860693],["usdt","Tether",35315314190,71189424205,3,0.0959589786,-0.0019112058],["eth","Ethereum",7875243850,195977340994,2,-1.0417421953,-1.9131562346],["btc","Bitcoin",28378471211,449716820631,1,-3.5895241329,-1.8652798103]]}`;
declare global {
  interface Window {
    plotly_figure: any;
  }
}

function App() {
  const [data, setData] = useState(JSON.parse(initialData));

  useEffect(() => {
    /*const interval = setInterval(() => {
      if (window.plotly_figure) {
        setData(JSON.parse(window.plotly_figure));
        clearInterval(interval);
      }
    }, 100);
    return () => clearInterval(interval);*/
  }, []);

  const transformData = (data: any) => {
    const columns = data.columns;
    const index = data.index;
    const newData = data.data;
    const transformedData = newData.map((row: any, index: number) => {
      const transformedRow = {};
      row.forEach((value: any, index: number) => {
        //@ts-ignore
        transformedRow[columns[index]] = value;
      });
      return transformedRow;
    });
    return transformedData;
  };

  return (
    <div className="App">
      <h1>Hello from react wowoowow</h1>
      {data && <Table data={transformData(data)} columns={data.columns} />}
    </div>
  );
}

export default App;

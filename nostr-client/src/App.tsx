import { useState } from "react";
import GlobalFeed from "./components/GlobalFeed";

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="App">
      <h1>ALLOOO NOSTR</h1>
      <div>
        <GlobalFeed />
      </div>
    </div>
  );
}

export default App;

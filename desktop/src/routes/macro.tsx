import { createFileRoute } from "@tanstack/react-router";
import MacroPage from "../components/macro/MacroPage";

export const Route = createFileRoute("/macro")({
  component: MacroPage,
});

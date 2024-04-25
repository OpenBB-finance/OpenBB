import * as ToastPrimitive from "@radix-ui/react-toast";
import { clsx } from "clsx";
import CloseIcon from "./Icons/Close";
import CloseCircleIcon from "./Icons/CloseCircle";
import InfoIcon from "./Icons/Info";
import SuccessIcon from "./Icons/Success";
import WarningIcon from "./Icons/Warning";

const Toast = ({
  toast,
  open,
  setOpen,
}: {
  toast: {
    id: string;
    title: string;
    description?: string;
    status: "success" | "error" | "info" | "warning";
    preventClose?: boolean;
  };
  open: boolean;
  setOpen: (open: boolean) => void;
}) => {
  return (
    <ToastPrimitive.Provider>
      <ToastPrimitive.Root
        open={open}
        onOpenChange={(open) => {
          if (!toast.preventClose) {
            setOpen(open);
          }
        }}
        className={clsx(
          "z-50 fixed bottom-4 md:left-1/2 md:-translate-x-[50%] inset-x-4 w-auto shadow-lg md:max-w-[658px] duration-300",
          "radix-state-open:animate-fade-in",
          "radix-state-closed:animate-toast-hide",
          "radix-swipe-end:animate-toast-swipe-out",
          "translate-x-radix-toast-swipe-move-x",
          "radix-swipe-cancel:translate-x-0 radix-swipe-cancel:duration-200 radix-swipe-cancel:ease-[ease]",
          "px-[40px] md:px-[58px] py-6 flex flex-col border rounded-[4px]",
          {
            "bg-green-100 text-green-600 border-green-600":
              toast.status === "success",
            "bg-red-200 text-red-600 border-red-600": toast.status === "error",
            "bg-blue-100 text-blue-700 border-blue-600":
              toast.status === "info",
            "bg-orange-200 text-orange-600 border-orange-600":
              toast.status === "warning",
          },
          {
            "h-[72px]": !toast.description,
          }
          /*"focus:outline-none focus-visible:ring focus-visible:ring-purple-500 focus-visible:ring-opacity-75"*/
        )}
      >
        {toast.status === "success" ? (
          <SuccessIcon className="absolute left-[8px] md:left-[25px] top-[25px]" />
        ) : toast.status === "warning" ? (
          <WarningIcon className="absolute left-[8px] md:left-[25px] top-[25px]" />
        ) : toast.status === "error" ? (
          <CloseCircleIcon className="absolute left-[8px] md:left-[25px] top-[25px]" />
        ) : (
          <InfoIcon className="absolute left-[8px] md:left-[25px] top-[25px]" />
        )}
        <ToastPrimitive.Title className="text-grey-900 font-bold text-sm">
          {toast.title}
        </ToastPrimitive.Title>
        {toast.description && (
          <ToastPrimitive.Description className="mt-2 text-[10px] md:text-xs text-grey-800">
            {toast.description}
          </ToastPrimitive.Description>
        )}
        {/*action && (
          <ToastPrimitive.Action
            altText="view now"
            className="_btn-tertiary mt-2 h-8 text-xs"
            onClick={(e) => {
              e.preventDefault();
              action();
            }}
          >
            {actionLabel}
          </ToastPrimitive.Action>
        )*/}
        <ToastPrimitive.Close className="absolute top-7 right-5 md:right-7">
          <CloseIcon className="w-4 h-4 text-grey-900" />
        </ToastPrimitive.Close>
      </ToastPrimitive.Root>
      <ToastPrimitive.Viewport />
    </ToastPrimitive.Provider>
  );
};

export default Toast;

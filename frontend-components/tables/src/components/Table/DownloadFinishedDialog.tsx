import * as DialogPrimitive from "@radix-ui/react-dialog";
import CloseIcon from "../Icons/Close";

export default function DownloadFinishedDialog({
  open,
  close,
}: {
  open: boolean;
  close: () => void;
}) {
  const userHomeDir = window.download_path || "~/OpenBBUserData/exports";
  return (
    <DialogPrimitive.Root open={open} onOpenChange={close}>
      <div id="loading" className="saving">
        <div id="loading_text" className="loading_text" />
        <div id="loader" className="loader" />
      </div>
      <DialogPrimitive.Overlay onClick={close} className="_modal-overlay" />
      <DialogPrimitive.Content className="_modal">
        <DialogPrimitive.Close>
          <CloseIcon />
        </DialogPrimitive.Close>
        <DialogPrimitive.Close
          className="_modal-close"
          onClick={close}
          style={{ float: "right", marginTop: 20 }}
        >
          <CloseIcon className="w-6 h-6" />
        </DialogPrimitive.Close>
        <DialogPrimitive.Title className="_modal-title">
          Success
        </DialogPrimitive.Title>
        <div
          id="popup_title"
          className="popup_content"
          style={{ padding: "0px 2px 2px 5px", marginTop: 5 }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 0,
              fontSize: 14,
            }}
          >
            <div>
              <label htmlFor="title_text">
                <b>{window.title}</b> has been downloaded to
                <br />
                <br />
                <a
                  style={{ color: "#FFDD00", marginTop: 15 }}
                  href={`${userHomeDir}`}
                  onClick={(e) => {
                    e.preventDefault();
                    window.pywry.open_file(userHomeDir);
                  }}
                >
                  {userHomeDir}
                </a>
              </label>
            </div>
          </div>
          <div style={{ float: "right", marginTop: 20 }}>
            <button
              className="_btn"
              style={{
                padding: "8px 16px",
                width: "100%",
              }}
              onClick={close}
            >
              Close
            </button>
          </div>
        </div>
      </DialogPrimitive.Content>
    </DialogPrimitive.Root>
  );
}

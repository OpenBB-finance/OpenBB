import CommonDialog from "../Dialogs/CommonDialog";

export default function DownloadFinishedDialog({
  open,
  close,
}: {
  open: boolean;
  close: () => void;
}) {
  const userHomeDir = window.download_path || "~/OpenBBUserData/exports";
  return (
    <CommonDialog title="Success" description="" open={open} close={close}>
      <div
        id="popup_title"
        className="popup_content"
        style={{ padding: "0px 2px 2px 5px", marginTop: 5 }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
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
    </CommonDialog>
  );
}

import CommonDialog from "../Dialogs/CommonDialog";

export default function AlertDialog({
	title,
	content,
	open,
	close,
}: {
	title: string;
	content: string;
	open: boolean;
	close: () => void;
}) {
	return (
		<CommonDialog title={title} description="" open={open} close={close}>
			<div
				id="popup_title"
				className="popup_content"
				style={{ padding: "0px 2px 2px 5px", marginTop: 5 }}
			>
				<div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
					<div>
						<label htmlFor="title_text">{content}</label>
					</div>
				</div>
				<div style={{ float: "right", marginTop: 20 }}>
					<button
						type="button"
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

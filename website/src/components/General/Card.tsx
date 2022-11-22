import clsx from "clsx";
import React from "react"
import ChevronRightIcon from "../Icons/ChevronRight";

interface CardProps {
	title: string
	description: string
	className?: string
	type?: "terminal" | "sdk"
}

export default function Card({ title, description, className = "mb-8", type = "terminal" }: CardProps) {
	return (
		<div style={{
			backgroundImage: type === "terminal" ? "url('/img/terminal_bg.png')" : "url('/img/sdk_bg.png')",
			backgroundRepeat: "no-repeat",
			backgroundSize: "100% 130%",
		}} className={clsx("shadow-sm group !no-underline text-grey-900 dark:text-white hover:text-grey-900 dark:hover:border-white hover:border-grey-900 dark:hover:!text-white relative w-full max-w-full p-8 rounded-lg border border-grey-400 bg-white dark:bg-grey-900", className)}>
			<p className="uppercase tracking-widest font-bold text-lg">
				{title}
			</p>
			<p className="text-sm dark:text-grey-300">
				{description}
			</p>
			{false && (<p
				className={clsx(
					"mt-auto inline-flex items-center gap-2 font-normal",
				)}
			>
				See more
				<ChevronRightIcon className="group-hover:translate-x-2 tw-transition w-3" />
			</p>)}
		</div>
	);
}
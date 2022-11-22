const disabledCss = {
	"code::before": false,
	"code::after": false,
	"blockquote p:first-of-type::before": false,
	"blockquote p:last-of-type::after": false,
	pre: false,
	code: false,
	'pre code': false,
	'code::before': false,
	'code::after': false
}

module.exports = {
	darkMode: ['class', '[data-theme="dark"]'],
	content: ["./src/**/*.{js,jsx,ts,tsx}"],
	theme: {
		extend: {
			typography: {
				DEFAULT: { css: disabledCss },
				sm: { css: disabledCss },
				lg: { css: disabledCss },
				xl: { css: disabledCss },
				'2xl': { css: disabledCss },
			},
			colors: {
				"grey-50": "#f6f6f6ff",
				"grey-100": "#eaeaeaff",
				"grey-200": "#dcdcdcff",
				"grey-300": "#c8c8c8ff",
				"grey-400": "#a2a2a2ff",
				"grey-500": "#808080ff",
				"grey-600": "#5a5a5aff",
				"grey-700": "#474747ff",
				"grey-800": "#2a2a2aff",
				"grey-850": "#131313ff",
				"grey-900": "#070707ff",
			},
			animation: {
				// Dropdown menu
				"scale-in": "scale-in 0.2s ease-in-out",
				"slide-down": "slide-down 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
				"slide-up": "slide-up 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
				// Tooltip
				"slide-up-fade": "slide-up-fade 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
				"slide-right-fade":
					"slide-right-fade 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
				"slide-down-fade": "slide-down-fade 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
				"slide-left-fade": "slide-left-fade 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
				// Navigation menu
				"enter-from-right": "enter-from-right 0.25s ease",
				"enter-from-left": "enter-from-left 0.25s ease",
				"exit-to-right": "exit-to-right 0.25s ease",
				"exit-to-left": "exit-to-left 0.25s ease",
				"scale-in-content": "scale-in-content 0.2s ease",
				"scale-out-content": "scale-out-content 0.2s ease",
				"fade-in": "fade-in 0.2s ease",
				"fade-out": "fade-out 0.2s ease",
				// Toast
				"toast-hide": "toast-hide 100ms ease-in forwards",
				"toast-slide-in-right":
					"toast-slide-in-right 150ms cubic-bezier(0.16, 1, 0.3, 1)",
				"toast-slide-in-bottom":
					"toast-slide-in-bottom 150ms cubic-bezier(0.16, 1, 0.3, 1)",
				"toast-swipe-out": "toast-swipe-out 100ms ease-out forwards",
			},
		},
	},
	plugins: [
		require('@tailwindcss/typography'),
		require("tailwindcss-radix")()
	],
};
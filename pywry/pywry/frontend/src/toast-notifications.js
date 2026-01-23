/**
 * PyWry Toast Notification System
 *
 * Provides typed, styled toast notifications that work identically across
 * all rendering paths: native window, notebook, and browser.
 *
 * Alert Types:
 * - info: Auto-dismiss 5s, blue
 * - success: Auto-dismiss 3s, green
 * - warning: Persist until clicked, amber
 * - error: Persist until clicked, red
 * - confirm: Two buttons (Cancel/Confirm), purple
 *
 * Keyboard: Escape key dismisses all alerts
 */

(function() {
    'use strict';

    var toastIdCounter = 0;

    window.PYWRY_TOAST = {
        _initialized: true,

        // Type configurations with escaped unicode icons
        types: {
            info:    { icon: '\u2139\uFE0F', color: '#0ea5e9', autoDismiss: 5000 },  // ℹ️
            success: { icon: '\u2705',       color: '#22c55e', autoDismiss: 3000 },  // ✅
            warning: { icon: '\u26A0\uFE0F', color: '#f59e0b', autoDismiss: null },  // ⚠️
            error:   { icon: '\u26D4',       color: '#ef4444', autoDismiss: null },  // ⛔
            confirm: { icon: '\u2753',       color: '#6366f1', autoDismiss: null }   // ❓
        },

        maxVisible: 3,
        defaultPosition: 'top-right',

        /**
         * Get or create the toast state for a widget container
         * @param {HTMLElement} widget - Widget container element
         * @returns {Object} Toast state object
         * @private
         */
        _getWidgetState: function(widget) {
            if (!widget._pywryToastState) {
                widget._pywryToastState = {
                    activeToasts: [],
                    container: null,
                    overlay: null
                };
            }
            return widget._pywryToastState;
        },

        /**
         * Show a toast notification
         * @param {Object} options - Toast options
         * @param {string} options.message - Message text (required)
         * @param {string} [options.type='info'] - Alert type
         * @param {string} [options.title] - Optional title
         * @param {number} [options.duration] - Override auto-dismiss duration
         * @param {string} [options.position] - Position override
         * @param {HTMLElement} options.container - Target widget container (REQUIRED)
         * @returns {string} Toast ID
         */
        show: function(options) {
            var self = this;
            var type = options.type || 'info';
            var typeConfig = this.types[type] || this.types.info;
            var message = options.message || '';
            var title = options.title || '';
            var duration = options.duration !== undefined ? options.duration : typeConfig.autoDismiss;
            var position = options.position || this.defaultPosition;
            var widget = options.container || document.querySelector('.pywry-widget') || document.body;

            // Get widget-specific state
            var state = this._getWidgetState(widget);

            // Create toast container if needed
            var toastContainer = this._ensureContainer(position, widget, state);

            // Limit visible toasts for THIS widget
            while (state.activeToasts.length >= this.maxVisible) {
                this._dismissFromState(state.activeToasts[0].id, state);
            }

            // Create toast element
            var id = 'pywry-toast-' + (++toastIdCounter);
            var toast = document.createElement('div');
            toast.id = id;
            toast.className = 'pywry-toast pywry-toast--' + type;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
            toast.setAttribute('data-widget-toast', 'true');

            // Build content
            var html = '<div class="pywry-toast__icon">' + typeConfig.icon + '</div>';
            html += '<div class="pywry-toast__content">';
            if (title) {
                html += '<div class="pywry-toast__title">' + this._escapeHtml(title) + '</div>';
            }
            html += '<div class="pywry-toast__message">' + this._escapeHtml(message) + '</div>';
            html += '</div>';
            html += '<button class="pywry-toast__close" aria-label="Dismiss">\u00D7</button>';

            toast.innerHTML = html;

            // Click to dismiss - pass state
            toast.querySelector('.pywry-toast__close').addEventListener('click', function(e) {
                e.stopPropagation();
                self._dismissFromState(id, state);
            });

            // Click anywhere on toast to dismiss (except confirm)
            if (type !== 'confirm') {
                toast.style.cursor = 'pointer';
                toast.addEventListener('click', function() {
                    self._dismissFromState(id, state);
                });
            }

            // Add to DOM - prepend to keep new toasts at top
            if (toastContainer.firstChild) {
                toastContainer.insertBefore(toast, toastContainer.firstChild);
            } else {
                toastContainer.appendChild(toast);
            }

            // Store reference in widget-specific state (prepend to keep order)
            var toastObj = {
                id: id,
                element: toast,
                type: type,
                timerId: null
            };
            state.activeToasts.unshift(toastObj);

            // Auto-dismiss
            if (duration && duration > 0) {
                toastObj.timerId = setTimeout(function() {
                    self._dismissFromState(id, state);
                }, duration);
            }

            return id;
        },

        /**
         * Show a confirmation toast with buttons
         * @param {Object} options - Confirm options
         * @param {string} options.message - Message text
         * @param {string} [options.title] - Optional title
         * @param {Function} options.onConfirm - Callback when confirmed
         * @param {Function} options.onCancel - Callback when cancelled
         * @param {string} [options.confirmText='Confirm'] - Confirm button text
         * @param {string} [options.cancelText='Cancel'] - Cancel button text
         * @param {HTMLElement} options.container - Target widget container (REQUIRED)
         * @returns {string} Toast ID
         */
        confirm: function(options) {
            var self = this;
            var typeConfig = this.types.confirm;
            var message = options.message || '';
            var title = options.title || '';
            var confirmText = options.confirmText || 'Confirm';
            var cancelText = options.cancelText || 'Cancel';
            var position = options.position || this.defaultPosition;
            var widget = options.container || document.querySelector('.pywry-widget') || document.body;

            // Get widget-specific state
            var state = this._getWidgetState(widget);

            // Create blocking overlay for confirm dialog
            var overlay = this._ensureOverlay(widget, state);
            overlay.classList.add('pywry-toast-overlay--visible');

            // Create toast container if needed
            var toastContainer = this._ensureContainer(position, widget, state);
            toastContainer.classList.add('pywry-toast-container--blocking');

            // Limit visible toasts for THIS widget
            while (state.activeToasts.length >= this.maxVisible) {
                this._dismissFromState(state.activeToasts[0].id, state);
            }

            // Create toast element
            var id = 'pywry-toast-' + (++toastIdCounter);
            var toast = document.createElement('div');
            toast.id = id;
            toast.className = 'pywry-toast pywry-toast--confirm';
            toast.setAttribute('role', 'alertdialog');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('data-widget-toast', 'true');

            // Build content
            var html = '<div class="pywry-toast__icon">' + typeConfig.icon + '</div>';
            html += '<div class="pywry-toast__content">';
            if (title) {
                html += '<div class="pywry-toast__title">' + this._escapeHtml(title) + '</div>';
            }
            html += '<div class="pywry-toast__message">' + this._escapeHtml(message) + '</div>';
            html += '<div class="pywry-toast__buttons">';
            html += '<button class="pywry-toast__btn pywry-toast__btn--cancel">' + this._escapeHtml(cancelText) + '</button>';
            html += '<button class="pywry-toast__btn pywry-toast__btn--confirm">' + this._escapeHtml(confirmText) + '</button>';
            html += '</div>';
            html += '</div>';

            toast.innerHTML = html;

            // Button handlers - pass state
            toast.querySelector('.pywry-toast__btn--cancel').addEventListener('click', function(e) {
                e.stopPropagation();
                self._dismissFromState(id, state);
                if (options.onCancel) {
                    options.onCancel();
                }
            });

            toast.querySelector('.pywry-toast__btn--confirm').addEventListener('click', function(e) {
                e.stopPropagation();
                self._dismissFromState(id, state);
                if (options.onConfirm) {
                    options.onConfirm();
                }
            });

            // Add to DOM - prepend to keep new toasts at top
            if (toastContainer.firstChild) {
                toastContainer.insertBefore(toast, toastContainer.firstChild);
            } else {
                toastContainer.appendChild(toast);
            }

            // Store reference in widget-specific state (prepend to keep order)
            var toastObj = {
                id: id,
                element: toast,
                type: 'confirm',
                timerId: null,
                onCancel: options.onCancel,
                overlay: overlay
            };
            state.activeToasts.unshift(toastObj);

            return id;
        },

        /**
         * Dismiss a toast from a specific widget's state
         * @param {string} id - Toast ID to dismiss
         * @param {Object} state - Widget-specific state object
         * @private
         */
        _dismissFromState: function(id, state) {
            var index = -1;
            var toastObj = null;

            for (var i = 0; i < state.activeToasts.length; i++) {
                if (state.activeToasts[i].id === id) {
                    index = i;
                    toastObj = state.activeToasts[i];
                    break;
                }
            }

            if (index === -1 || !toastObj) {
                return;
            }

            // Clear auto-dismiss timer
            if (toastObj.timerId) {
                clearTimeout(toastObj.timerId);
            }

            // Remove from tracking
            state.activeToasts.splice(index, 1);

            // Hide overlay if this was a confirm toast
            if (toastObj.overlay) {
                toastObj.overlay.classList.remove('pywry-toast-overlay--visible');
            }

            // Remove blocking class if no more confirm toasts
            var hasConfirmToasts = state.activeToasts.some(function(t) { return t.type === 'confirm'; });
            if (!hasConfirmToasts && state.container) {
                state.container.classList.remove('pywry-toast-container--blocking');
            }

            // Remove element immediately
            var element = toastObj.element;
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }

            // Remove toast container if empty
            if (state.container && state.container.children.length === 0) {
                if (state.container.parentNode) {
                    state.container.parentNode.removeChild(state.container);
                }
                state.container = null;
            }

            // Remove overlay if no toasts left
            if (state.overlay && state.activeToasts.length === 0) {
                if (state.overlay.parentNode) {
                    state.overlay.parentNode.removeChild(state.overlay);
                }
                state.overlay = null;
            }
        },

        /**
         * Dismiss a specific toast by ID (searches all widgets)
         * @param {string} id - Toast ID to dismiss
         */
        dismiss: function(id) {
            // Find the toast element and its parent widget
            var toastElement = document.getElementById(id);
            if (toastElement) {
                var widget = toastElement.closest('.pywry-widget');
                if (widget && widget._pywryToastState) {
                    this._dismissFromState(id, widget._pywryToastState);
                }
            }
        },

        /**
         * Dismiss all visible toasts in a specific widget
         * @param {HTMLElement} widget - Widget container
         */
        dismissAllInWidget: function(widget) {
            if (!widget || !widget._pywryToastState) return;
            var state = widget._pywryToastState;
            var toastsCopy = state.activeToasts.slice();
            for (var i = 0; i < toastsCopy.length; i++) {
                var toastObj = toastsCopy[i];
                if (toastObj.type === 'confirm' && toastObj.onCancel) {
                    toastObj.onCancel();
                }
                this._dismissFromState(toastObj.id, state);
            }
        },

        /**
         * Ensure toast container exists for a specific widget
         * @param {string} position - Container position
         * @param {HTMLElement} widget - Widget container element
         * @param {Object} state - Widget-specific state object
         * @returns {HTMLElement} The toast container element
         * @private
         */
        _ensureContainer: function(position, widget, state) {
            // Check if this widget already has a toast container in state
            if (state.container && widget.contains(state.container)) {
                return state.container;
            }

            // Check if there's an existing container in DOM
            var existingContainer = widget.querySelector('.pywry-toast-container');
            if (existingContainer) {
                state.container = existingContainer;
                return existingContainer;
            }

            // Create new container for this widget
            var newContainer = document.createElement('div');
            newContainer.className = 'pywry-toast-container pywry-toast-container--' + position;
            newContainer.setAttribute('aria-label', 'Notifications');
            widget.appendChild(newContainer);
            state.container = newContainer;

            // Set up escape key handler on widget if not already done
            if (!widget._pywryEscapeHandler) {
                var self = this;
                widget._pywryEscapeHandler = function(e) {
                    if (e.key === 'Escape') {
                        self.dismissAllInWidget(widget);
                    }
                };
                widget.setAttribute('tabindex', '-1');
                widget.addEventListener('keydown', widget._pywryEscapeHandler);
            }

            return newContainer;
        },

        /**
         * Ensure overlay exists for blocking confirm dialogs
         * @param {HTMLElement} widget - Widget container element
         * @param {Object} state - Widget-specific state object
         * @returns {HTMLElement} The overlay element
         * @private
         */
        _ensureOverlay: function(widget, state) {
            // Check if this widget already has an overlay in state
            if (state.overlay && widget.contains(state.overlay)) {
                return state.overlay;
            }

            // Check if there's an existing overlay in DOM
            var existingOverlay = widget.querySelector('.pywry-toast-overlay');
            if (existingOverlay) {
                state.overlay = existingOverlay;
                return existingOverlay;
            }

            // Create new overlay for this widget
            var newOverlay = document.createElement('div');
            newOverlay.className = 'pywry-toast-overlay';
            widget.appendChild(newOverlay);
            state.overlay = newOverlay;
            return newOverlay;
        },

        /**
         * Escape HTML entities
         * @param {string} text - Text to escape
         * @returns {string} Escaped text
         * @private
         */
        _escapeHtml: function(text) {
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

})();

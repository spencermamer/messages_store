import "./styles.css";
import { LitElement, html } from "lit";
import { customElement, state, property } from "lit/decorators.js";
import "./list";
import "./modal";
import "./notification";

declare global {
	interface HTMLElementTagNameMap {
		"notices-store": NoticesStore; // Renamed tag
	}
}

@customElement("notices-store") // Renamed component
export class NoticesStore extends LitElement { // Renamed class
	// Assuming originalMessage becomes originalNoticeContent or similar for the object structure
	@state() allNotices: Array<{ 
		slug: string; 
		notice: string; 
		originalNoticeContent: string[]; 
		priority?: number; 
		audience?: string; 
		expiration_date?: string | null; 
		acknowledged?: boolean | number; 
	}> = [];
	@state() notices: Array<{ 
		slug: string; 
		notice: string; 
		originalNoticeContent: string[]; 
		priority?: number; 
		audience?: string; 
		expiration_date?: string | null; 
		acknowledged?: boolean | number; 
	}> = [];
	@state() notice: { 
		slug: string; 
		notice: string; 
		originalNoticeContent: string[]; 
		priority?: number; 
		audience?: string; 
		expiration_date?: string | null; 
		acknowledged?: boolean | number; 
	} = { slug: "", notice: "", originalNoticeContent: [""], priority: 3, audience: 'all', expiration_date: null, acknowledged: 0 };
	@state() isModalOpen = false;
	@state() notification: { message: string; type: string } | null = null; // 'message' here is generic notification text, not an entity
	@state() searchTerm = "";
	@state() sortOrder: "asc" | "desc" = "asc";
	@state() groupNotices = true; // Renamed from groupMessages

	@property({ type: Object }) hass;

	createRenderRoot() {
		return this;
	}

	async connectedCallback() {
		super.connectedCallback();
		this.loadConfig();
		await this.loadNotices(); // Renamed from loadMessages
		document.addEventListener("keydown", this.handleKeyDown);
	}

	disconnectedCallback() {
		document.removeEventListener("keydown", this.handleKeyDown);
		super.disconnectedCallback();
	}

	handleKeyDown = (e: KeyboardEvent) => {
		if (e.ctrlKey && e.altKey && e.key === "+") {
			this.addModal(); 
		} 
	};

	loadConfig() {
		const config = localStorage.getItem("notices-store-config"); // Renamed item
		if (config) {
			this.groupNotices = JSON.parse(config).groupNotices; // Renamed property
		}
	}

	saveConfig() {
		localStorage.setItem(
			"notices-store-config", // Renamed item
			JSON.stringify({ groupNotices: this.groupNotices }) // Renamed property
		);
	}

	async loadNotices() { // Renamed from loadMessages
		// Service name updated from get_messages to get_notices
		const response = await this.callService("messages_store", "get_notices"); 
		this.allNotices = this.processNotices(response?.data); // Renamed from allMessages and processMessages
		this.filterNotices(); // Renamed from filterMessages
	}

	processNotices(data) { 
		let processedNotices: Array<{ 
			slug: string; 
			notice: string; 
			originalNoticeContent: string[]; 
			priority?: number; 
			audience?: string; 
			expiration_date?: string | null; 
			acknowledged?: boolean | number; 
		}> = [];

		if (Array.isArray(data)) {
			data.forEach((item) => { 
				// The backend now returns individual notices, not grouped, and 'notice' is a string.
				// 'originalNoticeContent' will be derived if needed, or simply be [item.notice]
				// For now, assume data items from get_notices are already structured with all fields.
				// If item.notice is an array (from older data or bulk add format), handle it.
				let noticeContentForDisplay = "";
				let originalContentArray: string[] = [];

				if (typeof item.notice === 'string') {
					noticeContentForDisplay = item.notice;
					originalContentArray = [item.notice]; // Or split if it contains TAG_SEPARATOR_MESSAGE
				} else if (Array.isArray(item.notice)) {
					// This case might be less frequent now if backend returns single string from DB
					noticeContentForDisplay = item.notice[0] || ""; 
					originalContentArray = item.notice;
				}
				
				// If grouping is active, we might still only take the first line for display if item.notice was an array.
				// However, the main purpose of `originalNoticeContent` is for editing.
				// The backend `get_notices` now returns individual notices with all fields.
				// The concept of "grouping" here might need re-evaluation based on backend changes.
				// For now, we'll assume `item.notice` is the primary content string.
				// And `originalNoticeContent` is for the modal to edit potentially multiple lines.
				// Let's assume backend now sends item.notice as string and potentially item.originalNoticeContent if different.
				// Or, if `item.notice` can still be an array from `get_notices` (e.g. for `force_random: false` and multiple items)
				
				// Simplified assumption: backend `get_notices` returns each notice object with all its fields.
				// `item.notice` is the string content. `item.originalNoticeContent` needs to be constructed if not directly provided.
				// The `processNotices` was originally designed to handle `item.notice` being an array for multi-line messages.
				// Let's stick to that logic for `originalNoticeContent`.
				
				const currentNoticeContent = Array.isArray(item.notice) ? item.notice : [String(item.notice)];

				if (this.groupNotices && Array.isArray(item.notice) && item.notice.length > 0) {
					processedNotices.push({
						slug: item.slug,
						notice: item.notice[0], 
						originalNoticeContent: item.notice, 
						priority: item.priority,
						audience: item.audience,
						expiration_date: item.expiration_date,
						acknowledged: item.acknowledged
					});
				} else if (!Array.isArray(item.notice)) { // Single string notice from backend
					processedNotices.push({
						slug: item.slug,
						notice: String(item.notice),
						originalNoticeContent: [String(item.notice)],
						priority: item.priority,
						audience: item.audience,
						expiration_date: item.expiration_date,
						acknowledged: item.acknowledged
					});
				}
				else { // Ungrouped or single item in array
					currentNoticeContent.forEach((singleNoticeText) => {
						processedNotices.push({
							slug: item.slug,
							notice: singleNoticeText.trim(),
							originalNoticeContent: currentNoticeContent,
							priority: item.priority,
							audience: item.audience,
							expiration_date: item.expiration_date,
							acknowledged: item.acknowledged
						});
					});
				}
			});
		}
		return processedNotices;
	}

	sortNotices() { 
		this.notices.sort((a, b) => { // Renamed from messages
			const compare = a.slug.localeCompare(b.slug);
			return this.sortOrder === "asc" ? compare : -compare;
		});
	}

	toggleSortOrder() {
		this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
		this.sortNotices(); // Renamed from sortMessages
	}

	toggleGroupNotices() { // Renamed from toggleGroupMessages
		this.groupNotices = !this.groupNotices; // Renamed from groupMessages
		this.saveConfig();
		this.loadNotices(); // Renamed from loadMessages
	}

	async callService(domain, service, data = {}, target = {}) {
		try {
			const response = await this.hass.connection.sendMessagePromise({
				type: "execute_script",
				sequence: [
					{
						service: `${domain}.${service}`,
						data,
						target,
						response_variable: "service_result",
					},
					{ stop: "done", response_variable: "service_result" },
				],
			});
			return response.response;
		} catch (error: any) {
			this.showNotification(error.message, "error"); // 'message' here is generic error text
		}
	}

	handleSearch(e) {
		this.searchTerm = e.target.value;
		this.filterNotices(); // Renamed from filterMessages
	}

	filterNotices() { // Renamed from filterMessages
		const term = this.searchTerm.toLowerCase();
		if (!term) {
			this.notices = [...this.allNotices]; // Renamed from messages and allMessages
		} else {
			this.notices = this.allNotices.filter( // Renamed from messages and allMessages
				(item: { slug: string; notice: string }) => // Renamed msg to item, notice to notice
					item.slug.toLowerCase().includes(term) ||
					item.notice.toLowerCase().includes(term) // Renamed notice to notice
			);
		}
		this.sortNotices(); // Renamed from sortMessages
	}

	editModal(item) { // Renamed msg to item
		item = item.detail;
		this.notice = item; // Renamed from message
		this.isModalOpen = true;
	}

	addModal() {
		this.notice = { 
			slug: "", 
			notice: "", 
			originalNoticeContent: [""], 
			priority: 3, 
			audience: 'all', 
			expiration_date: null, 
			acknowledged: 0 // Or false, depending on how you want to handle it (0 for DB)
		};
		this.isModalOpen = true;
	}

	closeModal() {
		this.isModalOpen = false;
	}

	async saveNotice(e) { // Renamed from saveMessage
		const { slug, notice, service, priority, audience, expiration_date } = e.detail; 
		const response = await this.callService("messages_store", service, { 
			slug,
			notice: notice, 
			priority,
			audience,
			expiration_date 
		});
		this.showNotification(
			response.message, 
			response.status ? "success" : "error"
		);
		if (response.status) {
			this.closeModal();
			await this.loadNotices(); // Renamed from loadMessages
			this.filterNotices(); // Renamed from filterMessages
		}
	}

	async deleteNotice(e) { // Renamed from deleteMessage
		const slug = e.detail;
		const response = await this.callService(
			"messages_store", // domain kept as messages_store
			"delete_notice", // Service name updated
			{ slug }
		);
		this.showNotification(
			response.message, // 'message' here is generic response text
			response.status ? "success" : "error"
		);
		if (response.status) {
			await this.loadNotices(); // Renamed from loadMessages
			this.filterNotices(); // Renamed from filterMessages
		}
	}

	async handleAcknowledgeNotice(e) {
		const { slug, acknowledged } = e.detail;
		const response = await this.callService(
			"messages_store", 
			"acknowledge_notice",
			{ slug, acknowledged }
		);

		this.showNotification(
			response.message,
			response.status ? "success" : "error"
		);

		if (response.status) {
			await this.loadNotices();
			// No need to call filterNotices() separately if loadNotices() already calls it.
		}
	}

	showNotification(notificationText, type) { // Renamed message to notificationText for clarity
		this.notification = { message: notificationText, type }; // 'message' property of notification object
		setTimeout(() => (this.notification = null), 10000);
	}

	render() {
		return html`
			<div class="min-h-screen p-4 dark:bg-zinc-900 dark:text-white">
				<div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4">
					<h1 class="text-2xl font-bold mb-4 sm:mb-0">Notices Store</h1> 
					<div class="flex flex-col sm:flex-row sm:items-center">
						<label class="inline-flex items-center mb-4 sm:mb-0 sm:mr-4">
							<input
								type="checkbox"
								class="form-checkbox"
								.checked=${this.groupNotices} 
								@click=${this.toggleGroupNotices} 
							/>
							<span class="ml-2">Group slugs</span>
						</label>
						<button
							class="bg-zinc-500 text-white font-bold px-4 py-2 rounded"
							@click=${this.addModal}
						>
							Add Notice 
						</button>
					</div>
				</div>
				<input
					class="w-full text-sm outline-none border-b-2 border-zinc-600 bg-zinc-800 focus:border-zinc-500 focus:outline-none p-2 text-white mb-4"
					type="text"
					placeholder="Search notices..." 
					@input=${this.handleSearch}
				/>

				<div class="overflow-x-auto">
					${this.notices.length > 0 
						? html`
								<notices-store-list 
									.notices=${this.notices} 
									@edit=${this.editModal}
									@delete=${this.deleteNotice} 
									@save=${this.saveNotice} 
									@sort=${this.toggleSortOrder}
									@acknowledge-toggle=${this.handleAcknowledgeNotice}
									.sortOrder=${this.sortOrder}
								></notices-store-list>
								<div class="mt-4 text-sm text-gray-500">
									Total Notices: ${this.notices.length} 
								</div>
							`
						: html`
								<div class="mt-4 text-sm text-gray-500">
									No notices found. 
								</div>
							`}
				</div>
				${this.isModalOpen
					? html`
							<notices-store-modal 
								.hass=${this.hass}
								.allNotices=${this.allNotices} 
								.initialSlug=${this.notice.slug} 
								.initialNoticeContents=${this.notice.originalNoticeContent}
								.initialPriority=${this.notice.priority}
								.initialAudience=${this.notice.audience}
								.initialExpirationDate=${this.notice.expiration_date}
								.initialAcknowledged=${this.notice.acknowledged}
								@save=${this.saveNotice} 
								@close=${this.closeModal}
							></notices-store-modal>
						`
					: ""}
				${this.notification
					? html`
							<notices-store-notification 
								.message=${this.notification.message} 
								.type=${this.notification.type}
								@close=${() => (this.notification = null)}
							></notices-store-notification>
						`
					: ""}
			</div>
		`;
	}
}
